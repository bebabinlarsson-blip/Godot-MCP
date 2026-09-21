"""MCP tool for 2D and 3D character controller scaffolding."""

from __future__ import annotations

from fastmcp import FastMCP

from godot_ai.handlers import character as character_handlers
from godot_ai.tools._meta_tool import register_manage_tool

_DESCRIPTION = """\
2D and 3D Character Controller Scaffolding.

Ops:
  • scaffold_2d(parent_path="", name="Player", genre="platformer", speed=200.0,
                 jump_velocity=-350.0, acceleration=1200.0, friction=1000.0,
                 coyote_time=0.12, jump_buffering=0.1, attach_camera=True,
                 script_path="")
        Instantly scaffold a complete 2D player character (CharacterBody2D) with
        CollisionShape2D, placeholder graphics, optional follow camera with
        screen shake, and production-ready controller script with coyote time,
        jump buffering, floor snapping, and move_and_slide().
        Genres: 'platformer' (gravity, jump) | 'topdown' (4/8-way movement).

  • scaffold_3d(parent_path="", name="Player3D", genre="first_person", speed=5.0,
                 sprint_speed=8.0, jump_velocity=4.5, mouse_sensitivity=0.002,
                 script_path="")
        Instantly scaffold a complete 3D player character (CharacterBody3D) with
        CapsuleShape3D, CapsuleMesh, and Camera3D with mouse-look capture,
        sprinting, jumping, gravity, and move_and_slide().
        Genres: 'first_person' (head-mounted camera) | 'third_person' (SpringArm3D).
"""


def register_character_tools(mcp: FastMCP) -> None:
    register_manage_tool(
        mcp,
        tool_name="character_manage",
        description=_DESCRIPTION,
        ops={
            "scaffold_2d": character_handlers.character_scaffold_2d,
            "scaffold_3d": character_handlers.character_scaffold_3d,
        },
    )
