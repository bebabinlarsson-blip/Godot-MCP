"""Unit tests for PromotedToolRegistrar — first-class registration of
promoted custom tools, capped and synced on every catalog mutation."""

from __future__ import annotations

import pytest

from godot_ai.services.custom_tool_service import (
    CustomToolDefinition,
    CustomToolService,
)
from godot_ai.services.promoted_tools import (
    MAX_PROMOTED_TOOLS,
    PROMOTED_PREFIX,
    PromotedToolRegistrar,
)


class _FakeLocalProvider:
    def __init__(self, tools: dict[str, object]) -> None:
        self.tools = tools

    def remove_tool(self, name: str, version: str | None = None) -> None:
        self.tools.pop(name, None)


class _FakeMcp:
    def __init__(self) -> None:
        self.tools: dict[str, object] = {}
        self.hidden: set[str] = set()
        self.local_provider = _FakeLocalProvider(self.tools)

    def add_tool(self, tool):
        self.tools[tool.name] = tool
        return tool

    def remove_tool(self, name: str, version: str | None = None) -> None:
        raise AssertionError("deprecated FastMCP.remove_tool() must not be used")

    def set_hidden_tools(self, names: set[str]) -> None:
        self.hidden = set(names)


@pytest.fixture()
def stack():
    ## Save/restore the process singleton so this fixture's catalog and
    ## registrar hook can't leak into later tests, even on failure.
    previous = CustomToolService._instance
    CustomToolService._instance = None
    service = CustomToolService.get_instance()
    mcp = _FakeMcp()
    registrar = PromotedToolRegistrar(
        mcp, service, set_hidden_tools=mcp.set_hidden_tools
    )
    try:
        yield service, mcp, registrar
    finally:
        CustomToolService._instance = previous


def _tool(name: str, promoted: bool = True, **extra) -> CustomToolDefinition:
    return CustomToolDefinition(name=name, description=f"desc {name}", promoted=promoted, **extra)


def test_promoted_tool_registered_with_schema(stack) -> None:
    service, mcp, _ = stack
    schema = {"type": "object", "properties": {"scene": {"type": "string"}}, "required": ["scene"]}
    service.update_session_tools("s1", [_tool("gdunit_run", params_schema=schema)])
    name = PROMOTED_PREFIX + "gdunit_run"
    assert name in mcp.tools
    ## The addon's schema passes through VERBATIM — no lossy signature
    ## synthesis (contrast: unity-mcp collapses types to bare primitives).
    assert mcp.tools[name].parameters == schema
    assert "desc gdunit_run" in mcp.tools[name].description


def test_unpromoted_tools_stay_behind_custom_manage(stack) -> None:
    service, mcp, _ = stack
    service.update_session_tools("s1", [_tool("plain", promoted=False)])
    assert mcp.tools == {}


def test_disabled_promotion_stays_callable_but_hidden(stack) -> None:
    service, mcp, _ = stack
    service.update_session_tools("s1", [_tool("a")])
    assert PROMOTED_PREFIX + "a" in mcp.tools
    service.update_session_tools("s1", [_tool("a", enabled=False)])
    assert PROMOTED_PREFIX + "a" in mcp.tools
    assert mcp.hidden == {PROMOTED_PREFIX + "a"}


def test_promotion_follows_catalog_removal(stack) -> None:
    service, mcp, _ = stack
    service.update_session_tools("s1", [_tool("a")])
    ## Empty snapshot means the addon unregistered the definition entirely,
    ## so no stale-call tombstone remains.
    service.update_session_tools("s1", [])
    assert mcp.tools == {}
    assert mcp.hidden == set()


def test_promotion_follows_session_disconnect(stack) -> None:
    service, mcp, _ = stack
    service.update_session_tools("s1", [_tool("a")])
    service.remove_session("s1")
    assert mcp.tools == {}


def test_cap_is_deterministic_and_logged_overflow_stays_reachable(stack) -> None:
    service, mcp, _ = stack
    tools = [_tool(f"t{i:02d}") for i in range(MAX_PROMOTED_TOOLS + 3)]
    service.update_session_tools("s1", tools)
    assert len(mcp.tools) == MAX_PROMOTED_TOOLS
    ## Deterministic: sorted names win, not arrival order.
    expected = {PROMOTED_PREFIX + f"t{i:02d}" for i in range(MAX_PROMOTED_TOOLS)}
    assert set(mcp.tools) == expected
    ## Overflow tools remain in the catalog (custom_manage path untouched).
    assert service.get_tool(f"t{MAX_PROMOTED_TOOLS:02d}", session_id="s1") is not None


def test_repush_updates_description_and_schema(stack) -> None:
    service, mcp, _ = stack
    service.update_session_tools("s1", [_tool("a")])
    new_schema = {"type": "object", "properties": {"x": {"type": "integer"}}}
    updated = CustomToolDefinition(
        name="a", description="new words", promoted=True, params_schema=new_schema
    )
    service.update_session_tools("s1", [updated])
    tool = mcp.tools[PROMOTED_PREFIX + "a"]
    assert tool.parameters == new_schema
    assert "new words" in tool.description


def test_sync_failure_does_not_break_catalog_mutation(stack) -> None:
    service, mcp, _ = stack

    def _boom():
        raise RuntimeError("registrar bug")

    service.on_catalog_changed = _boom
    ## Must not raise out of the mutation (the WS receive loop calls this).
    service.update_session_tools("s1", [_tool("a")])
    assert service.get_tool("a", session_id="s1") is not None


def test_registrar_ignores_cross_session_duplicate_names(stack) -> None:
    service, mcp, _ = stack
    service.update_session_tools("s1", [_tool("dup")])
    service.update_session_tools("s2", [_tool("dup")])
    assert list(mcp.tools) == [PROMOTED_PREFIX + "dup"]
    ## One session leaving keeps the name registered for the other.
    service.remove_session("s1")
    assert list(mcp.tools) == [PROMOTED_PREFIX + "dup"]
    service.remove_session("s2")
    assert mcp.tools == {}


def test_cross_session_schema_conflict_excluded_from_promotion(stack) -> None:
    service, mcp, _ = stack
    schema_a = {"type": "object", "properties": {"a": {"type": "string"}}}
    schema_b = {"type": "object", "properties": {"b": {"type": "integer"}}}
    service.update_session_tools("s1", [_tool("clash", params_schema=schema_a)])
    service.update_session_tools("s2", [_tool("clash", params_schema=schema_b)])
    ## Advertising either schema misleads the client whenever the OTHER
    ## session is active — fail closed, keep custom_manage as the path.
    assert PROMOTED_PREFIX + "clash" not in mcp.tools
    ## The conflict clears when one side leaves.
    service.remove_session("s2")
    assert PROMOTED_PREFIX + "clash" in mcp.tools
    assert mcp.tools[PROMOTED_PREFIX + "clash"].parameters == schema_a


def test_identical_schema_duplicates_still_promote(stack) -> None:
    service, mcp, _ = stack
    schema = {"type": "object", "properties": {"x": {"type": "string"}}}
    service.update_session_tools("s1", [_tool("same", params_schema=schema)])
    service.update_session_tools("s2", [_tool("same", params_schema=schema)])
    assert PROMOTED_PREFIX + "same" in mcp.tools


def test_sync_failure_is_contained_and_logged(stack, monkeypatch) -> None:
    service, mcp, registrar = stack

    def _boom():
        raise RuntimeError("sync bug")

    monkeypatch.setattr(service, "get_tools", _boom)
    ## The WS receive loop triggers sync via catalog mutation — a
    ## registrar bug must be swallowed (and logged), never raised.
    registrar.sync()


def test_get_all_tools_session_scope_includes_disabled(stack) -> None:
    service, _, _ = stack
    service.update_session_tools(
        "s1", [_tool("off", promoted=False, enabled=False), _tool("on", promoted=False)]
    )
    names = {t.name for t in service.get_all_tools(session_id="s1")}
    assert names == {"off", "on"}
    assert {t.name for t in service.get_tools(session_id="s1")} == {"on"}
