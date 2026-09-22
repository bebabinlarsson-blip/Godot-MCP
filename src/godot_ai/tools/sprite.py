"""MCP tool for Godot sprite, MultiMesh, and Line2D management."""

from __future__ import annotations

from fastmcp import FastMCP

from godot_ai.handlers import sprite as sprite_handlers
from godot_ai.tools._meta_tool import register_manage_tool

_DESCRIPTION = """\
Sprite, MultiMesh, and Line2D Management.

Ops:
  * create_sprite_frames(animations=[{"name":"default","fps":5.0,"loop":true}], save_path="")
        Create a new SpriteFrames resource with named animations.

  * scaffold_animated_sprite(parent_path="", sprite_type="2d", sprite_frames_path="",
                             node_name="AnimatedSprite")
        Scaffold an AnimatedSprite2D or AnimatedSprite3D in current scene.

  * scaffold_multimesh(parent_path="", mesh_type="box", instance_count=100, is_2d=False,
                       node_name="MultiMeshInstance")
        Scaffold a MultiMeshInstance2D or MultiMeshInstance3D with instances.

  * configure_line_2d(node_path, points=[], width=10.0, default_color="#ffffff")
        Configure points and styling of a Line2D node.
"""


def register_sprite_tools(mcp: FastMCP) -> None:
    register_manage_tool(
        mcp,
        tool_name="sprite_manage",
        description=_DESCRIPTION,
        ops={
            "create_sprite_frames": sprite_handlers.sprite_create_sprite_frames,
            "scaffold_animated_sprite": sprite_handlers.sprite_scaffold_animated_sprite,
            "scaffold_multimesh": sprite_handlers.sprite_scaffold_multimesh,
            "configure_line_2d": sprite_handlers.sprite_configure_line_2d,
        },
        read_resource_forms={},
    )
