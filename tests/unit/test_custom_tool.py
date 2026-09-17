"""Unit tests for CustomToolService: catalog semantics + list_changed broadcast.

The broadcast path uses a stand-in for ``mcp.server.session.ServerSession``
because the real session is hard to construct outside a live transport —
the service only needs ``await session.send_tool_list_changed()`` on it,
and a ``WeakSet``-eligible plain class is enough to exercise every branch.
"""

from __future__ import annotations

import asyncio

import pytest

from godot_ai.services.custom_tool_service import (
    CustomToolDefinition,
    CustomToolService,
)


class _MockMcpSession:
    """Stand-in for ServerSession — records send calls, optionally raises."""

    def __init__(self) -> None:
        self.send_calls: int = 0
        self.raise_on_send: Exception | None = None

    async def send_tool_list_changed(self) -> None:
        if self.raise_on_send is not None:
            raise self.raise_on_send
        self.send_calls += 1


@pytest.fixture(autouse=True)
def fresh_service() -> CustomToolService:
    """Each test gets a brand-new singleton (catalog empty, no sessions)."""
    CustomToolService._instance = None
    return CustomToolService.get_instance()


def _tool(name: str, **extra) -> CustomToolDefinition:
    return CustomToolDefinition(name=name, description=f"desc {name}", **extra)


# --- singleton ---


def test_singleton_constructs_on_first_access(fresh_service) -> None:
    CustomToolService._instance = None
    a = CustomToolService.get_instance()
    b = CustomToolService.get_instance()
    assert a is b


# --- catalog ---


def test_update_and_get_tools(fresh_service) -> None:
    fresh_service.update_session_tools("s1", [_tool("t1"), _tool("t2")])
    names = {t.name for t in fresh_service.get_tools()}
    assert names == {"t1", "t2"}
    assert fresh_service.get_tool("t1") is not None
    assert fresh_service.get_tool("missing") is None


def test_remove_session_returns_bool(fresh_service) -> None:
    fresh_service.update_session_tools("s1", [_tool("t1")])
    assert fresh_service.remove_session("s1") is True
    assert fresh_service.get_tools() == []
    ## Second removal: nothing left to drop.
    assert fresh_service.remove_session("s1") is False


def test_get_tools_merges_across_sessions(fresh_service) -> None:
    fresh_service.update_session_tools("s1", [_tool("a")])
    fresh_service.update_session_tools("s2", [_tool("b")])
    names = {t.name for t in fresh_service.get_tools()}
    assert names == {"a", "b"}


def test_get_tools_first_seen_wins_on_collision(fresh_service) -> None:
    ## Cross-session name collisions keep the first-seen definition. The
    ## catalog entry is descriptive (invoke routes through the active
    ## session anyway), but the merge must be deterministic — not
    ## "whichever dict iteration order happened last".
    from_a = _tool("dup", source="addon-A")
    from_b = _tool("dup", source="addon-B")
    fresh_service.update_session_tools("s1", [from_a])
    fresh_service.update_session_tools("s2", [from_b])
    merged = fresh_service.get_tools()
    assert len(merged) == 1
    assert merged[0].source == "addon-A"


# --- session-scoped catalog (the "Active session only" contract) ---


def test_get_tools_scoped_to_session(fresh_service) -> None:
    fresh_service.update_session_tools("s1", [_tool("a"), _tool("b")])
    fresh_service.update_session_tools("s2", [_tool("c")])
    ## s1 sees only its own tools, never s2's — no cross-session leakage.
    names = {t.name for t in fresh_service.get_tools(session_id="s1")}
    assert names == {"a", "b"}


def test_get_tools_scoped_unknown_session_empty(fresh_service) -> None:
    fresh_service.update_session_tools("s1", [_tool("a")])
    ## An unknown/disconnected session exposes nothing.
    assert fresh_service.get_tools(session_id="nope") == []


def test_get_tool_scoped_resolves_owning_session(fresh_service) -> None:
    ## Same name in two sessions: scoped lookup returns the requested
    ## session's definition, not the first-seen one — invoke validates
    ## against the same editor it dispatches to.
    from_a = _tool("dup", source="addon-A")
    from_b = _tool("dup", source="addon-B")
    fresh_service.update_session_tools("s1", [from_a])
    fresh_service.update_session_tools("s2", [from_b])
    assert fresh_service.get_tool("dup", session_id="s2").source == "addon-B"
    assert fresh_service.get_tool("dup", session_id="s1").source == "addon-A"


def test_get_tool_scoped_unknown_session_none(fresh_service) -> None:
    fresh_service.update_session_tools("s1", [_tool("a")])
    ## A tool that exists in s1 must NOT resolve for s2 — otherwise invoke
    ## would dispatch a tool the target editor doesn't actually have.
    assert fresh_service.get_tool("a", session_id="s2") is None


def test_update_session_tools_empty_list_clears(fresh_service) -> None:
    fresh_service.update_session_tools("s1", [_tool("t1")])
    assert fresh_service.get_tool("t1") is not None
    ## Empty snapshot = "I have no tools now", not "ignore this".
    fresh_service.update_session_tools("s1", [])
    assert fresh_service.get_tools() == []
    ## And the session entry is gone, so remove_session reports nothing.
    assert fresh_service.remove_session("s1") is False


def test_get_tool_returns_none_for_unknown(fresh_service) -> None:
    assert fresh_service.get_tool("nope") is None


# --- list_changed broadcast ---


async def test_notify_tools_change_broadcasts_to_all_sessions(fresh_service) -> None:
    s1, s2 = _MockMcpSession(), _MockMcpSession()
    fresh_service.track_mcp_session(s1)
    fresh_service.track_mcp_session(s2)
    await fresh_service.notify_tools_change()
    assert s1.send_calls == 1
    assert s2.send_calls == 1


async def test_notify_tools_change_dead_session_discarded(fresh_service) -> None:
    ## A session that raises on send (torn down between snapshot and send)
    ## must not block the rest of the broadcast, and must be evicted so the
    ## next broadcast doesn't retry a corpse.
    alive = _MockMcpSession()
    dead = _MockMcpSession()
    dead.raise_on_send = ConnectionError("session gone")
    fresh_service.track_mcp_session(alive)
    fresh_service.track_mcp_session(dead)
    await fresh_service.notify_tools_change()
    assert alive.send_calls == 1
    assert dead not in fresh_service._mcp_sessions


async def test_notify_tools_change_noop_when_no_sessions(fresh_service) -> None:
    ## No tracked sessions — must not raise.
    await fresh_service.notify_tools_change()


async def test_notify_tools_change_stalled_session_discarded(fresh_service) -> None:
    ## A stalled MCP transport (send never completes) must be timed out
    ## and discarded, and must NOT block the other clients' sends.
    fresh_service.notify_timeout_s = 0.05

    class _Stalled(_MockMcpSession):
        async def send_tool_list_changed(self) -> None:
            await asyncio.sleep(10)  # never completes within the cap

    stalled = _Stalled()
    alive = _MockMcpSession()
    fresh_service.track_mcp_session(stalled)
    fresh_service.track_mcp_session(alive)
    await fresh_service.notify_tools_change()
    assert stalled not in fresh_service._mcp_sessions
    assert alive.send_calls == 1


async def test_track_mcp_session_idempotent(fresh_service) -> None:
    ## WeakSet.add is idempotent — re-tracking the same session must not
    ## double-broadcast.
    s = _MockMcpSession()
    fresh_service.track_mcp_session(s)
    fresh_service.track_mcp_session(s)
    await fresh_service.notify_tools_change()
    assert s.send_calls == 1
