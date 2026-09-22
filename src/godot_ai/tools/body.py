"""MCP tool for Godot 2D and 3D physics body management."""

from __future__ import annotations

from fastmcp import FastMCP

from godot_ai.handlers import body as body_handlers
from godot_ai.tools._meta_tool import register_manage_tool

_DESCRIPTION = """\
Physics Body & Collision Management (2D and 3D).

Ops:
  * configure_body(node_path, properties={})
        Configure physics parameters of a body (mass, gravity_scale, damping).

  * apply_impulse(node_path, impulse=[0,0], position=None)
        Apply an impulse to a 2D or 3D RigidBody.

  * set_collision_layer_mask(node_path, collision_layer=None, collision_mask=None,
                             collision_priority=None)
        Set collision layers and masks for a 2D or 3D collision object.

  * scaffold_character_body(parent_path="", node_name="Player", is_3d=False)
        Scaffold a CharacterBody2D or CharacterBody3D with collision shape.

  * get_body_info(node_path)
        Inspect collision layers, mass, and properties of a physics body.
"""


def register_body_tools(mcp: FastMCP) -> None:
    register_manage_tool(
        mcp,
        tool_name="body_manage",
        description=_DESCRIPTION,
        ops={
            "configure_body": body_handlers.body_configure_body,
            "apply_impulse": body_handlers.body_apply_impulse,
            "set_collision_layer_mask": body_handlers.body_set_collision_layer_mask,
            "scaffold_character_body": body_handlers.body_scaffold_character_body,
            "get_body_info": body_handlers.body_get_body_info,
        },
        read_resource_forms={
            "get_body_info": None,
        },
    )
