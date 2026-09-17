"""FastMCP Server implementation for Godot Omni.

Provides adaptive tool exposure, universal operation routing, arbitrary GDScript evaluation,
universal object reflection, and editor UI automation.
"""

from __future__ import annotations

import logging
from typing import Any

from fastmcp import Context, FastMCP

from godot_ai.runtime.direct import DirectRuntime
from godot_omni.exposure import AdaptiveExposureEngine, ExposureMode
from godot_omni.registry import get_global_registry

logger = logging.getLogger(__name__)


def create_omni_server(
    exposure_mode: ExposureMode = ExposureMode.AUTO,
    client_hint: str | None = None,
    http_port: int = 8000,
    ws_port: int = 9500,
) -> FastMCP:
    """Creates a FastMCP server configured with Godot Omni tools and adaptive exposure."""
    registry = get_global_registry()
    exposure_engine = AdaptiveExposureEngine(registry)

    mcp = FastMCP(
        "Godot Omni",
        version="5.0.0",
        instructions=(
            "Godot Omni: Universal Godot AI MCP Architecture. Gives agents 100% control "
            "over Godot: 1,763 canonical operations, arbitrary GDScript eval (godot_eval), "
            "universal object reflection (reflection_call, reflection_get/set), "
            "and editor UI automation (ui_semantic_tree, ui_click, ui_type)."
        ),
    )

    # 1. Top-Level Omnipotent Execution Tool (Arbitrary GDScript in Godot Editor)
    @mcp.tool()
    async def godot_eval(
        ctx: Context,
        code: str,
        mode: str = "auto",
        session_id: str = "",
    ) -> dict:
        """Execute arbitrary GDScript code in the live Godot editor process.

        The AI can do literally anything in Godot via this tool:
        query singletons (EditorInterface, ProjectSettings, RenderingServer, PhysicsServer3D, AudioServer),
        create or modify nodes, instantiate and configure resources, inspect scenes,
        or perform batch transformations.

        Args:
            code: The GDScript source to execute.
            mode: 'auto', 'expression', or 'block'.
            session_id: Optional session ID to target.
        """
        runtime = DirectRuntime.from_context(ctx, session_id=session_id or None)
        return await runtime.send_command(
            "omni_eval",
            {"code": code, "mode": mode},
            timeout=30.0,
        )

    # 2. Universal Canonical Operation Executor (1,763 Operations)
    @mcp.tool()
    async def godot_execute(
        ctx: Context,
        operation_id: str,
        parameters: dict[str, Any] | None = None,
        session_id: str = "",
    ) -> dict:
        """Execute any of the 1,763 canonical Godot operations.

        Use godot_search to find operation IDs and godot_describe to see parameter schemas.

        Args:
            operation_id: Canonical operation ID (e.g. 'node.create', 'scene.open', 'shader.set_parameter').
            parameters: Arguments dictionary for the operation.
            session_id: Optional session ID to target.
        """
        op = registry.get(operation_id)
        if not op:
            suggestions = registry.suggest_similar(operation_id)
            hint = f" Did you mean: {', '.join(suggestions)}?" if suggestions else ""
            return {"error": f"Unknown operation '{operation_id}'.{hint}"}

        runtime = DirectRuntime.from_context(ctx, session_id=session_id or None)
        params = parameters or {}

        # Determine wire command name from handler info or canonical mapping
        wire_command = op.handler_info.get("handler") or op.id.replace(".", "_").replace(":", "_")
        return await runtime.send_command(wire_command, params, timeout=20.0)

    # 3. Canonical Registry Search
    @mcp.tool()
    async def godot_search(
        query: str,
        domain: str = "",
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """Search the 1,763 canonical Godot operations using fuzzy ranking and inverted index.

        Args:
            query: Keyword query (e.g. 'shader compile', 'audio player', 'instantiate scene').
            domain: Optional domain filter (e.g. 'node', 'shader', 'physics', 'rendering').
            limit: Maximum results to return (default 20).
        """
        return registry.search(query, domain=domain or None, limit=limit)

    # 4. Canonical Operation Description
    @mcp.tool()
    async def godot_describe(operation_id: str) -> dict[str, Any]:
        """Get full documentation, parameters, types, latency tier, and examples for an operation.

        Args:
            operation_id: Canonical operation ID or alias.
        """
        op = registry.get(operation_id)
        if not op:
            suggestions = registry.suggest_similar(operation_id)
            return {
                "error": f"Operation '{operation_id}' not found.",
                "suggestions": suggestions,
            }
        return op.to_dict()

    # 5. Universal Object Reflection: Call Any Method on Any Object
    @mcp.tool()
    async def reflection_call(
        ctx: Context,
        target: str,
        method: str,
        args: list[Any] | None = None,
        session_id: str = "",
    ) -> dict:
        """Call ANY method on ANY Godot Object (Node, Resource, Singleton, RefCounted).

        Args:
            target: Object reference (obj://session/id handle, instance_id as integer/string, or NodePath).
            method: Method name to call (e.g. 'get_children', 'play', 'set_position').
            args: Method arguments array.
            session_id: Optional session ID to target.
        """
        runtime = DirectRuntime.from_context(ctx, session_id=session_id or None)
        return await runtime.send_command(
            "reflection_call",
            {"target": target, "method": method, "args": args or []},
            timeout=15.0,
        )

    # 6. Universal Object Reflection: Read Any Property
    @mcp.tool()
    async def reflection_get(
        ctx: Context,
        target: str,
        property: str,
        session_id: str = "",
    ) -> dict:
        """Read any property on any Godot Object.

        Args:
            target: Object reference (obj:// handle, instance_id, or NodePath).
            property: Property name to read.
            session_id: Optional session ID to target.
        """
        runtime = DirectRuntime.from_context(ctx, session_id=session_id or None)
        return await runtime.send_command(
            "reflection_get",
            {"target": target, "property": property},
            timeout=10.0,
        )

    # 7. Universal Object Reflection: Write Any Property
    @mcp.tool()
    async def reflection_set(
        ctx: Context,
        target: str,
        property: str,
        value: Any,
        session_id: str = "",
    ) -> dict:
        """Write any property on any Godot Object.

        Args:
            target: Object reference (obj:// handle, instance_id, or NodePath).
            property: Property name to write.
            value: Value to assign.
            session_id: Optional session ID to target.
        """
        runtime = DirectRuntime.from_context(ctx, session_id=session_id or None)
        return await runtime.send_command(
            "reflection_set",
            {"target": target, "property": property, "value": value},
            timeout=10.0,
        )

    # 8. Universal Object Reflection: Inspect Object
    @mcp.tool()
    async def reflection_inspect(
        ctx: Context,
        target: str,
        session_id: str = "",
    ) -> dict:
        """Inspect all methods, properties, and signals on any Godot Object.

        Args:
            target: Object reference (obj:// handle, instance_id, or NodePath).
            session_id: Optional session ID to target.
        """
        runtime = DirectRuntime.from_context(ctx, session_id=session_id or None)
        return await runtime.send_command(
            "reflection_inspect",
            {"target": target},
            timeout=10.0,
        )

    # 9. Semantic UI Control Tree Extraction
    @mcp.tool()
    async def ui_semantic_tree(
        ctx: Context,
        max_depth: int = 8,
        session_id: str = "",
    ) -> dict:
        """Extract the hierarchical GUI Control tree of the Godot Editor.

        Returns all buttons, tabs, input fields, labels, docks, and tree widgets
        with their screen positions, sizes, and accessible text.

        Args:
            max_depth: Maximum recursion depth (default 8).
            session_id: Optional session ID to target.
        """
        runtime = DirectRuntime.from_context(ctx, session_id=session_id or None)
        return await runtime.send_command(
            "ui_semantic_tree",
            {"max_depth": max_depth},
            timeout=15.0,
        )

    # 10. Semantic UI Control Automation: Click
    @mcp.tool()
    async def ui_click(
        ctx: Context,
        text: str = "",
        path: str = "",
        session_id: str = "",
    ) -> dict:
        """Click any button, tab, checkbox, or control in the Godot Editor.

        Args:
            text: Button text, label substring, or tooltip to locate.
            path: Exact Control NodePath relative to editor base.
            session_id: Optional session ID to target.
        """
        runtime = DirectRuntime.from_context(ctx, session_id=session_id or None)
        return await runtime.send_command(
            "ui_click_control",
            {"text": text, "path": path},
            timeout=10.0,
        )

    # 11. Semantic UI Control Automation: Type
    @mcp.tool()
    async def ui_type(
        ctx: Context,
        text: str,
        target: str = "",
        session_id: str = "",
    ) -> dict:
        """Type text into any LineEdit or TextEdit in the Godot Editor.

        Args:
            text: Text to type or inject.
            target: Optional control text or tooltip query to focus before typing.
            session_id: Optional session ID to target.
        """
        runtime = DirectRuntime.from_context(ctx, session_id=session_id or None)
        return await runtime.send_command(
            "ui_type_text",
            {"text": text, "target": target},
            timeout=10.0,
        )

    # 12. Live Server Status
    @mcp.tool()
    async def godot_status(ctx: Context) -> dict:
        """Get live status of Godot editor session, connected clients, and registry."""
        runtime = DirectRuntime.from_context(ctx, session_id=None)
        try:
            editor_state = await runtime.send_command("get_editor_state", {}, timeout=5.0)
        except Exception as exc:
            editor_state = {"error": str(exc), "connected": False}

        return {
            "status": "online",
            "server": "godot-omni 5.0.0",
            "canonical_operations": len(registry.list_all()),
            "distinct_domains": len(registry.list_domains()),
            "editor_state": editor_state,
        }

    return mcp
