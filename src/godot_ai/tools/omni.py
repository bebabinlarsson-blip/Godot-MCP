"""MCP tools for Godot Omni: Arbitrary GDScript evaluation, Universal Reflection, and Semantic UI Automation."""

from __future__ import annotations

from typing import Any

from fastmcp import Context, FastMCP

from godot_ai.handlers import omni as omni_handlers
from godot_ai.runtime.direct import DirectRuntime
from godot_ai.tools import DEFER_META
from godot_ai.tools._meta_tool import register_manage_tool

_OMNI_MANAGE_DESCRIPTION = """\
Universal Godot engine control, reflection, script evaluation, and editor UI automation.

Ops:
  * eval(code, mode="auto", inputs={})
        Execute arbitrary GDScript in the Editor process with full permissions.
  * call(target, method, args=[])
        Call ANY method on ANY Godot Object (Node, Resource, Singleton, RefCounted).
  * get(target, property)
        Read any property on any Godot Object.
  * set(target, property, value)
        Write any property on any Godot Object.
  * inspect(target)
        Inspect complete methods, properties, and signals of any Object.
  * instantiate(class_name="", script_path="")
        Instantiate any ClassDB class or GDScript.
  * ui_tree(max_depth=8)
        Extract the full hierarchical semantic UI Control tree of the Editor.
  * ui_click(text="", path="")
        Click any button, tab, checkbox, or control in the Editor.
  * ui_type(text, target="")
        Type text into any LineEdit or TextEdit in the Editor.
"""


def register_omni_tools(mcp: FastMCP) -> None:
    @mcp.tool(meta=DEFER_META)
    async def omni_eval(
        ctx: Context,
        code: str,
        mode: str = "auto",
        session_id: str = "",
    ) -> dict:
        """Execute arbitrary GDScript code in the Godot editor process.

        Gives the AI direct, omnipotent execution capability within Godot:
        access EditorInterface, ProjectSettings, singletons, ClassDB, create nodes,
        instantiate resources, or manipulate scenes on the fly.

        Args:
            code: GDScript code to execute (e.g. 'EditorInterface.get_editor_settings().get_setting(...)').
            mode: 'auto', 'expression', or 'block'.
            session_id: Optional session ID to target.
        """
        runtime = DirectRuntime.from_context(ctx, session_id=session_id or None)
        return await omni_handlers.omni_eval(runtime, code=code, mode=mode)

    register_manage_tool(
        mcp,
        domain="omni",
        description=_OMNI_MANAGE_DESCRIPTION,
        ops={
            "eval": omni_handlers.omni_eval,
            "call": omni_handlers.reflection_call,
            "get": omni_handlers.reflection_get,
            "set": omni_handlers.reflection_set,
            "inspect": omni_handlers.reflection_inspect,
            "instantiate": omni_handlers.reflection_instantiate,
            "ui_tree": omni_handlers.ui_semantic_tree,
            "ui_click": omni_handlers.ui_click_control,
            "ui_type": omni_handlers.ui_type_text,
        },
    )
