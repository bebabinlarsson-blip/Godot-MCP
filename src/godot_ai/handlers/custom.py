from godot_ai.godot_client.client import GodotCommandError
from godot_ai.handlers._readiness import require_writable_async
from godot_ai.runtime.direct import DirectRuntime
from godot_ai.services.custom_tool_service import CustomToolService


async def custom_list(runtime: DirectRuntime) -> dict:
    service = CustomToolService.get_instance()
    ## "Active session only": list the tools of the editor this call will
    ## dispatch to, so the catalog matches what invoke can actually reach.
    ## With NO active session, return empty rather than falling through to
    ## the merged cross-session view — listing another editor's tools here
    ## would advertise names that invoke cannot dispatch.
    session_id = runtime.active_session_id
    if session_id is None:
        return {"tool_count": 0, "tools": [], "note": "no active Godot session"}
    tools = service.get_tools(session_id=session_id)
    return {
        "tool_count": len(tools),
        "tools": [t.model_dump() for t in tools],
    }


async def custom_invoke(
    runtime: DirectRuntime,
    tool_name: str,
    params: dict | None = None,
) -> dict:
    service = CustomToolService.get_instance()
    ## Resolve the dispatch target ONCE and use it for both lookup and
    ## send_command, so the definition we validate against belongs to the
    ## same editor we route to (active session, or per-call pin).
    session_id = runtime.active_session_id
    if session_id is None:
        ## Never fall through to the merged cross-session lookup: a tool
        ## validated against one editor while dispatch has no target (or a
        ## different one) is exactly the session confusion the per-session
        ## catalog exists to prevent.
        raise GodotCommandError(
            code="UNKNOWN_COMMAND",
            message=f"Custom tool '{tool_name}': no active Godot session to dispatch to",
        )
    definition = service.get_tool(
        tool_name, session_id=session_id, include_disabled=True
    )
    if definition is None:
        raise GodotCommandError(
            code="UNKNOWN_COMMAND",
            message=f"Custom tool '{tool_name}' not found in session {session_id}",
        )
    if not definition.enabled:
        raise GodotCommandError(
            code="CUSTOM_TOOL_DISABLED",
            message=f"Custom tool '{tool_name}' is disabled",
        )
    ## Gate only write-flagged tools, mirroring the plugin-side wrapper —
    ## a read-only custom tool (requires_writable=false) must stay
    ## invokable while the editor is playing/importing, per the spec
    ## contract in mcp_custom_tool_spec.gd.
    if definition.requires_writable:
        await require_writable_async(runtime)
    ## The plugin honors spec.timeout_ms (500..120000) for deferred
    ## replies; the server-side future must outlive that budget or every
    ## slow custom tool fails here at the 5s default while the editor is
    ## still working. +2s margin covers transport latency.
    timeout_ms = definition.timeout_ms if definition.timeout_ms else 4500
    # Route to plugin as "custom_tool:<name>"
    return await runtime.send_command(
        f"custom_tool:{tool_name}",
        params=params or {},
        session_id=session_id,
        timeout=timeout_ms / 1000.0 + 2.0,
    )
