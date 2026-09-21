"""MCP tool for Godot Omni: Universal engine access, reflection, and UI automation."""

from __future__ import annotations

from fastmcp import FastMCP

from godot_ai.handlers import omni as omni_handlers
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
  * mesh_primitive(primitive_type="box", node_name="", parent_path="", size=None,
                   albedo_color=None, position=None)
        Create a 3D primitive mesh (box, sphere, cylinder, plane, capsule, prism).
  * collision_shape(parent_path, shape_type="box", is_2d=True, size=None, radius=16.0,
                    height=32.0, node_name="CollisionShape")
        Create a 2D or 3D CollisionShape and attach it to a physics body.
  * preset_motion(preset="pulse", target_node_path="", animation_player_path="",
                  anim_name="", duration=1.0, loop=True)
        Inject procedural motion presets (pulse, fade_in, fade_out, slide_in).
  * ping()
        Quick diagnostic ping returning engine version, process frames, and memory metrics.
"""


def register_omni_tools(mcp: FastMCP) -> None:
    register_manage_tool(
        mcp,
        tool_name="omni_manage",
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
        read_resource_forms={
            "get": None,
            "inspect": None,
            "ui_tree": None,
            "ping": None,
        },
    )
