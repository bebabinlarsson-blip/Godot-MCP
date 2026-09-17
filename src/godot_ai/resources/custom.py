from fastmcp import Context

from godot_ai.resources import safe_payload
from godot_ai.runtime.direct import DirectRuntime
from godot_ai.services.custom_tool_service import CustomToolService


def register_custom_tools_resources(mcp) -> None:
    @mcp.resource("godot://custom-tools", mime_type="application/json")
    async def get_custom_tools(ctx: Context) -> dict:
        runtime = DirectRuntime.from_context(ctx)
        return await safe_payload(_resource_data(runtime))


async def _resource_data(runtime: DirectRuntime) -> dict:
    service = CustomToolService.get_instance()
    ## Resources resolve via the active session (AGENTS.md) — scope the
    ## listing the same way custom_list does, including the no-session
    ## case: empty, never the merged cross-session view (those tools
    ## would not be invokable).
    session_id = runtime.active_session_id
    if session_id is None:
        return {"tool_count": 0, "tools": [], "note": "no active Godot session"}
    tools = service.get_tools(session_id=session_id)
    return {
        "tool_count": len(tools),
        "tools": [t.model_dump() for t in tools],
    }
