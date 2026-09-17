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
  * instantiate_prefab(scene_path, parent_path="", node_name="", position=None)
        Instantiate any .tscn prefab directly into the edited scene.
  * shader_create(shader_path, shader_type="canvas_item", code="", target_node_path="")
        Create a new GDShader and optionally assign it as a ShaderMaterial to a node.
  * mesh_primitive(primitive_type="box", node_name="", parent_path="", size=None, albedo_color=None, position=None)
        Create a 3D primitive mesh (box, sphere, cylinder, plane, capsule, prism).
  * collision_shape(parent_path, shape_type="box", is_2d=True, size=None, radius=16.0, height=32.0, node_name="CollisionShape")
        Create a 2D or 3D CollisionShape and attach it to a physics body.
  * preset_motion(preset="pulse", target_node_path="", animation_player_path="", anim_name="", duration=1.0, loop=True)
        Inject procedural motion presets (pulse, fade_in, fade_out, slide_in) into an AnimationPlayer.
  * ping()
        Quick diagnostic ping returning engine version, process frames, and memory metrics.
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

    @mcp.tool(meta=DEFER_META)
    async def scene_instantiate_prefab(
        ctx: Context,
        scene_path: str,
        parent_path: str = "",
        node_name: str = "",
        position: list[float] | None = None,
        session_id: str = "",
    ) -> dict:
        """Instantiate a .tscn scene file directly into the active scene hierarchy."""
        runtime = DirectRuntime.from_context(ctx, session_id=session_id or None)
        return await omni_handlers.scene_instantiate_prefab(
            runtime,
            scene_path=scene_path,
            parent_path=parent_path,
            node_name=node_name,
            position=position,
        )

    @mcp.tool(meta=DEFER_META)
    async def mesh_create_primitive(
        ctx: Context,
        primitive_type: str = "box",
        node_name: str = "",
        parent_path: str = "",
        size: list[float] | None = None,
        albedo_color: list[float] | None = None,
        position: list[float] | None = None,
        session_id: str = "",
    ) -> dict:
        """Create a 3D PrimitiveMesh (box, sphere, cylinder, plane, capsule, prism) with material and transform."""
        runtime = DirectRuntime.from_context(ctx, session_id=session_id or None)
        return await omni_handlers.mesh_create_primitive(
            runtime,
            primitive_type=primitive_type,
            node_name=node_name,
            parent_path=parent_path,
            size=size,
            albedo_color=albedo_color,
            position=position,
        )

    @mcp.tool(meta=DEFER_META)
    async def collision_shape_create(
        ctx: Context,
        parent_path: str,
        shape_type: str = "box",
        is_2d: bool = True,
        size: list[float] | None = None,
        radius: float = 16.0,
        height: float = 32.0,
        node_name: str = "CollisionShape",
        session_id: str = "",
    ) -> dict:
        """Create and attach a 2D or 3D CollisionShape with predefined geometry to a physics body."""
        runtime = DirectRuntime.from_context(ctx, session_id=session_id or None)
        return await omni_handlers.collision_shape_create(
            runtime,
            parent_path=parent_path,
            shape_type=shape_type,
            is_2d=is_2d,
            size=size,
            radius=radius,
            height=height,
            node_name=node_name,
        )

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
            "instantiate_prefab": omni_handlers.scene_instantiate_prefab,
            "shader_create": omni_handlers.shader_create,
            "mesh_primitive": omni_handlers.mesh_create_primitive,
            "collision_shape": omni_handlers.collision_shape_create,
            "preset_motion": omni_handlers.animation_preset_motion,
            "ping": omni_handlers.mcp_ping,
        },
    )
