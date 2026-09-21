"""MCP tool for Godot Tween creation, procedural motion recipes, and code generation."""

from __future__ import annotations

from fastmcp import FastMCP

from godot_ai.handlers import tween as tween_handlers
from godot_ai.tools._meta_tool import register_manage_tool

_DESCRIPTION = """\
Procedural Motion, Game-Feel Tween Recipes, and Tween Code Generation.

Ops:
  * create(node_path, property, target_value, duration=0.5, trans_type="linear",
           ease_type="in_out", delay=0.0, relative=false)
        Create and run a Tween interpolating a property on a node.

  * preset_animation(node_path, preset="punch_scale", duration=0.3, ...)
        Execute instant procedural animation presets:
        - punch_scale: impact scale pop and overshoot (punch_factor)
        - shake_2d: screen/node trauma shake with decay (amplitude)
        - float_bob: looping levitation / idle hover (bob_distance, loops)
        - fade: alpha fade (target_alpha)
        - flash_color: flash modulate highlight (flash_color)
        - progress_fill: smooth bar / gauge value fill (target_value)
        - bounce_in: drop into place with bounce ease (drop_offset)
        - spin: rotation spin (revolutions)

  * generate_code(target_var="self", property="position", target_value="Vector2(100, 100)",
                  duration=0.5, trans_type="linear", ease_type="in_out", delay=0.0, relative=false)
        Generate production GDScript Tween code.
"""


def register_tween_tools(mcp: FastMCP) -> None:
    register_manage_tool(
        mcp,
        tool_name="tween_manage",
        description=_DESCRIPTION,
        ops={
            "create": tween_handlers.tween_create,
            "preset_animation": tween_handlers.tween_preset_animation,
            "generate_code": tween_handlers.tween_generate_code,
        },
        read_resource_forms={
            "generate_code": None,
        },
    )
