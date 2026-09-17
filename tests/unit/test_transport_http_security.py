"""HTTP authentication and finite-work boundary tests."""

from __future__ import annotations

import asyncio
import json
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
import uvicorn
from uvicorn.server import ServerState

from godot_ai import asgi
from godot_ai.transport.security import BoundedHTTPMiddleware, CapabilityAuthMiddleware

CAPABILITY = "c" * 32


def _scope(*headers: tuple[bytes, bytes], path: str = "/mcp") -> dict:
    return {
        "type": "http",
        "method": "POST",
        "path": path,
        "headers": list(headers),
    }


async def _call(app, scope: dict, messages: list[dict] | None = None) -> list[dict]:
    incoming = list(messages or [{"type": "http.request", "body": b""}])
    sent: list[dict] = []

    async def receive() -> dict:
        return incoming.pop(0) if incoming else {"type": "http.disconnect"}

    async def send(message: dict) -> None:
        sent.append(message)

    await app(scope, receive, send)
    return sent


def _error_code(messages: list[dict]) -> str:
    return json.loads(messages[-1]["body"])["error"]["code"]


@pytest.mark.asyncio
async def test_capability_auth_rejects_missing_wrong_and_duplicate_headers() -> None:
    called = False

    async def endpoint(_scope, _receive, _send) -> None:
        nonlocal called
        called = True

    app = CapabilityAuthMiddleware(endpoint, CAPABILITY)
    cases = (
        _scope(),
        _scope((b"authorization", b"Bearer wrong")),
        _scope(
            (b"authorization", f"Bearer {CAPABILITY}".encode()),
            (b"authorization", f"Bearer {CAPABILITY}".encode()),
        ),
    )
    for scope in cases:
        response = await _call(app, scope)
        assert response[0]["status"] == 401
        assert _error_code(response) == "TRANSPORT_AUTH_REQUIRED"
    assert not called


@pytest.mark.asyncio
async def test_capability_auth_passes_one_exact_bearer_value() -> None:
    called = False

    async def endpoint(_scope, _receive, _send) -> None:
        nonlocal called
        called = True

    app = CapabilityAuthMiddleware(endpoint, CAPABILITY)
    await _call(app, _scope((b"authorization", f"bearer {CAPABILITY}".encode())))
    assert called


@pytest.mark.asyncio
async def test_body_limit_counts_chunks_without_trusting_content_length() -> None:
    called = False

    async def endpoint(_scope, _receive, _send) -> None:
        nonlocal called
        called = True

    app = BoundedHTTPMiddleware(endpoint, max_body_bytes=4)
    response = await _call(
        app,
        _scope(),
        [
            {"type": "http.request", "body": b"abc", "more_body": True},
            {"type": "http.request", "body": b"de", "more_body": False},
        ],
    )
    assert response[0]["status"] == 413
    assert _error_code(response) == "REQUEST_BODY_TOO_LARGE"
    assert not called


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("headers", "status", "code"),
    [
        ([(b"content-length", b"nope")], 400, "INVALID_CONTENT_LENGTH"),
        (
            [(b"content-length", b"1"), (b"content-length", b"1")],
            400,
            "INVALID_CONTENT_LENGTH",
        ),
        ([(b"content-length", b"5")], 413, "REQUEST_BODY_TOO_LARGE"),
        ([(b"content-length", b"9" * 5000)], 413, "REQUEST_BODY_TOO_LARGE"),
    ],
)
async def test_content_length_is_unambiguous_and_bounded(headers, status, code) -> None:
    async def endpoint(_scope, _receive, _send) -> None:
        raise AssertionError("rejected request reached endpoint")

    response = await _call(BoundedHTTPMiddleware(endpoint, max_body_bytes=4), _scope(*headers))
    assert response[0]["status"] == status
    assert _error_code(response) == code


@pytest.mark.asyncio
async def test_body_deadline_rejects_a_drip_feed() -> None:
    async def endpoint(_scope, _receive, _send) -> None:
        raise AssertionError("timed-out request reached endpoint")

    async def receive() -> dict:
        await asyncio.Event().wait()
        raise AssertionError

    sent: list[dict] = []

    async def send(message: dict) -> None:
        sent.append(message)

    app = BoundedHTTPMiddleware(endpoint, body_timeout_seconds=0.001)
    await app(_scope(), receive, send)
    assert sent[0]["status"] == 408
    assert _error_code(sent) == "REQUEST_BODY_TIMEOUT"


@pytest.mark.asyncio
async def test_concurrency_limit_rejects_instead_of_queueing() -> None:
    entered = asyncio.Event()
    release = asyncio.Event()

    async def endpoint(_scope, _receive, _send) -> None:
        entered.set()
        await release.wait()

    app = BoundedHTTPMiddleware(endpoint, max_concurrency=1)
    first = asyncio.create_task(_call(app, _scope()))
    await entered.wait()
    second = await _call(app, _scope())
    release.set()
    await first

    assert second[0]["status"] == 503
    assert _error_code(second) == "TRANSPORT_OVERLOADED"


@pytest.mark.asyncio
async def test_session_limit_counts_reservations_and_prunes_terminated() -> None:
    manager = SimpleNamespace(
        _server_instances={
            "dead": SimpleNamespace(is_terminated=True),
            "live": SimpleNamespace(is_terminated=False),
        },
        _session_owners={"dead": object(), "live": object()},
        session_idle_timeout=0,
    )

    class Endpoint:
        session_manager = manager

        async def __call__(self, _scope, _receive, _send) -> None:
            return None

    app = BoundedHTTPMiddleware(Endpoint(), max_sessions=1, session_idle_seconds=7)
    response = await _call(app, _scope())
    assert response[0]["status"] == 503
    assert _error_code(response) == "MCP_SESSION_LIMIT_REACHED"
    assert set(manager._server_instances) == {"live"}
    assert set(manager._session_owners) == {"live"}
    assert manager.session_idle_timeout == 7


def _transport() -> MagicMock:
    transport = MagicMock(spec=asyncio.Transport)
    transport.get_extra_info.side_effect = lambda name, default=None: {
        "peername": ("127.0.0.1", 41000),
        "sockname": ("127.0.0.1", 8000),
        "sslcontext": None,
    }.get(name, default)
    transport.is_closing.return_value = False
    return transport


def _h11_protocol(loop, state: ServerState, *, limit: int = 1):
    async def app(_scope, _receive, _send) -> None:
        return None

    config = uvicorn.Config(app, limit_concurrency=limit, log_config=None)
    return asgi.BoundedH11Protocol(config, state, {}, _loop=loop)


def test_hardened_uvicorn_config_bounds_every_pre_asgi_stage() -> None:
    config = asgi.hardened_uvicorn_config(access_log=False)

    assert config == {
        "access_log": False,
        "http": asgi.BoundedH11Protocol,
        "limit_concurrency": asgi.HTTP_SERVER_CONNECTION_LIMIT,
        "backlog": asgi.HTTP_SERVER_BACKLOG,
        "timeout_keep_alive": asgi.HTTP_SERVER_KEEP_ALIVE_SECONDS,
        "h11_max_incomplete_event_size": asgi.HTTP_SERVER_MAX_INCOMPLETE_EVENT_BYTES,
    }


def test_h11_protocol_rejects_raw_connections_past_the_cap() -> None:
    loop = asyncio.new_event_loop()
    state = ServerState()
    first = _h11_protocol(loop, state)
    second = _h11_protocol(loop, state)
    first_transport, second_transport = _transport(), _transport()
    try:
        first.connection_made(first_transport)
        second.connection_made(second_transport)

        first_transport.abort.assert_not_called()
        second_transport.abort.assert_called_once()
        assert state.connections == {first}
    finally:
        first.connection_lost(None)
        loop.close()


def test_h11_incomplete_header_deadline_closes_the_socket() -> None:
    loop = asyncio.new_event_loop()
    protocol = _h11_protocol(loop, ServerState())
    transport = _transport()
    try:
        protocol.connection_made(transport)
        assert protocol._header_timeout is not None
        protocol._close_incomplete_header()
        transport.close.assert_called_once()
    finally:
        protocol.connection_lost(None)
        loop.close()
