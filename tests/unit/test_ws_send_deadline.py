"""``send_command``'s timeout budget must cover the outbound write, not just the wait.

``GodotWebSocketServer.send_command`` does ``await ws.send(...)`` and only then
``asyncio.wait_for(future, timeout=timeout)``. If the transport is write-paused
(TCP backpressure from a stalled editor, a full send buffer), the ``send`` itself
never returns, so the per-command deadline never starts counting and the MCP tool
call hangs for as long as the editor is wedged.

Both tests below assert the acceptance criterion — ``send_command`` raises its own
``TimeoutError`` within roughly ``timeout`` seconds even when the write never
completes — rather than characterising today's behaviour.
"""

from __future__ import annotations

import asyncio
import contextlib
import time

import pytest

from godot_ai.sessions.registry import Session, SessionRegistry
from godot_ai.transport.websocket import GodotWebSocketServer

## Short command budget, generous backstop. The gap between them is what makes
## "the deadline fired" distinguishable from "the suite rescued a hang".
_COMMAND_TIMEOUT_S = 0.2
_BACKSTOP_S = 2.0
_BUDGET_CEILING_S = 1.0


class StalledConnection:
    """Stand-in for ``ServerConnection`` whose ``send`` never completes.

    Models a write-paused transport: the coroutine is entered (so the payload
    was handed to the transport) and then parks forever on an Event nothing
    sets. ``send_command`` only ever touches ``.send`` on the connection it
    pulls out of ``_connections``, so nothing else needs faking.
    """

    def __init__(self) -> None:
        self.send_entered = asyncio.Event()
        self._never_set = asyncio.Event()

    async def send(self, _payload: str) -> None:
        self.send_entered.set()
        await self._never_set.wait()


def _server_with_stalled_write(session_id: str) -> tuple[GodotWebSocketServer, StalledConnection]:
    """Construct the server the way ``tests/conftest.py::harness`` does — registry
    plus port — but never call ``start()``: this test is about ``send_command``'s
    deadline, not about binding a socket. The fake is published through the
    same one-table membership transition as a real acknowledged peer.
    """
    server = GodotWebSocketServer(SessionRegistry(), port=19998)
    ws = StalledConnection()
    session = Session(
        session_id=session_id,
        godot_version="4.7",
        project_path="/tmp/test",
        plugin_version="4.0.0",
    )
    assert server.registry.reserve_connection(session, ws)
    server.registry.publish_connection(session_id, ws)
    return server, ws


async def _settle(coro) -> tuple[BaseException | None, float]:
    """Run ``coro`` under a backstop and return ``(exception, elapsed)``.

    The backstop must NOT be an ``asyncio.wait_for``/``pytest.raises(TimeoutError)``
    pair: since 3.11 ``asyncio.TimeoutError`` *is* ``TimeoutError``, so the rescue
    timeout would satisfy the assertion and the test would go green on exactly the
    hang it exists to catch. Instead a hang is turned into an explicit failure and
    the raised exception is handed back for inspection.
    """
    task = asyncio.create_task(coro)
    started = time.monotonic()
    done, _pending = await asyncio.wait({task}, timeout=_BACKSTOP_S)
    elapsed = time.monotonic() - started
    if not done:
        task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await task
        pytest.fail(
            f"send_command never returned: still running {elapsed:.2f}s after a "
            f"{_COMMAND_TIMEOUT_S}s budget, because the timeout wraps only the "
            "response wait and not the `await ws.send(...)` before it"
        )
    return task.exception(), elapsed


async def test_send_command_deadline_covers_a_stalled_write() -> None:
    session_id = "stalled-writer"
    server, ws = _server_with_stalled_write(session_id)

    exc, elapsed = await _settle(
        server.send_command(
            session_id=session_id,
            command="save_scene",
            timeout=_COMMAND_TIMEOUT_S,
        )
    )

    assert ws.send_entered.is_set(), "the fake never saw the write — test wired up wrong"
    assert isinstance(exc, TimeoutError), (
        f"expected send_command to raise TimeoutError on a write-paused transport, got {exc!r}"
    )
    assert "timed out after" in str(exc), (
        f"expected send_command's own timeout message, got {str(exc)!r}"
    )
    assert elapsed < _BUDGET_CEILING_S, (
        f"deadline fired {elapsed:.2f}s in, well past the {_COMMAND_TIMEOUT_S}s budget"
    )


async def test_stalled_write_timeout_pops_the_pending_entry() -> None:
    ## Same contract as TestPendingFutureCleanup in tests/integration/test_websocket.py:
    ## however send_command exits, the request_id must not be left in _pending.
    session_id = "stalled-writer-leak"
    server, _ws = _server_with_stalled_write(session_id)

    exc, _elapsed = await _settle(
        server.send_command(
            session_id=session_id,
            command="save_scene",
            timeout=_COMMAND_TIMEOUT_S,
        )
    )

    assert isinstance(exc, TimeoutError), f"expected a bounded TimeoutError, got {exc!r}"
    assert server.registry.pending_count == 0


async def test_live_connection_write_stall_is_bounded(harness) -> None:
    ## The fake above stands in for ServerConnection; this one pins the same
    ## contract against a real registered connection, monkeypatching only `send`
    ## exactly as test_websocket.py::test_send_failure_pops_pending_entry does
    ## (a raising send there, a never-returning one here).
    session_id = "stalled-live"
    plugin = await harness.connect_plugin(session_id=session_id)
    ws = harness.registry._entries[session_id].peer
    parked = asyncio.Event()

    async def stalling_send(_payload: str) -> None:
        await parked.wait()

    ws.send = stalling_send  # type: ignore[assignment]

    try:
        exc, elapsed = await _settle(
            harness.server.send_command(
                session_id=session_id,
                command="save_scene",
                timeout=_COMMAND_TIMEOUT_S,
            )
        )
        assert isinstance(exc, TimeoutError), (
            f"expected TimeoutError from a write-paused live connection, got {exc!r}"
        )
        assert elapsed < _BUDGET_CEILING_S, (
            f"deadline fired {elapsed:.2f}s in, well past the {_COMMAND_TIMEOUT_S}s budget"
        )
    finally:
        parked.set()
        await plugin.close()


class SilentConnection:
    """Accepts the write, then never answers — the response-leg stall.

    The opposite of ``StalledConnection``: the request genuinely reaches the
    editor, so a timeout here carries no risk of the command executing later.
    """

    async def send(self, _payload: str) -> None:
        return None


async def test_send_leg_and_response_leg_timeouts_are_distinguishable() -> None:
    """A stalled write must not read like an unanswered request.

    `websockets` hands the COMPLETE frame to the transport before awaiting
    `drain()`, so a send-leg timeout leaves a well-formed request buffered that
    the editor executes in full once it drains. An agent that retries on that
    duplicates the mutation — `node_create` twice, `script_create` twice. The
    response leg means the request was delivered and the reply was late, which is
    the ordinary retryable case. The two must not share a message.
    """
    send_leg_id = "write-paused"
    server, _ws = _server_with_stalled_write(send_leg_id)
    send_exc, _ = await _settle(
        server.send_command(
            session_id=send_leg_id, command="node_create", timeout=_COMMAND_TIMEOUT_S
        )
    )
    assert isinstance(send_exc, TimeoutError)
    assert "before the request left the socket" in str(send_exc), (
        "a send-leg timeout must warn that the command may still execute, so an "
        f"agent does not retry an already-queued mutation. Got: {str(send_exc)!r}"
    )

    response_leg_id = "silent-editor"
    server2 = GodotWebSocketServer(SessionRegistry(), port=19997)
    silent = SilentConnection()
    session = Session(
        session_id=response_leg_id,
        godot_version="4.7",
        project_path="/tmp/test",
        plugin_version="4.0.0",
    )
    assert server2.registry.reserve_connection(session, silent)
    server2.registry.publish_connection(response_leg_id, silent)
    resp_exc, _ = await _settle(
        server2.send_command(
            session_id=response_leg_id, command="node_create", timeout=_COMMAND_TIMEOUT_S
        )
    )
    assert isinstance(resp_exc, TimeoutError)
    assert "before the request left the socket" not in str(resp_exc), (
        "a response-leg timeout means the request WAS delivered; it must not carry "
        f"the send-leg warning. Got: {str(resp_exc)!r}"
    )
