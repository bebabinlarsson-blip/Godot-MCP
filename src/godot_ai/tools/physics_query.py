"""MCP tool for Godot direct physics space state queries and raycasts."""

from __future__ import annotations

from fastmcp import FastMCP

from godot_ai.handlers import physics_query as physics_query_handlers
from godot_ai.tools._meta_tool import register_manage_tool

_DESCRIPTION = """\
Direct 2D and 3D Physics Space State Raycasts, Point Overlaps, and Shape Queries.

Ops:
  * intersect_ray_3d(from_pos=[0.0, 0.0, 0.0], to_pos=[0.0, -10.0, 0.0],
                     collision_mask=0xFFFFFFFF, collide_with_bodies=True,
                     collide_with_areas=False)
        Cast a ray in 3D world space and return hit position, normal, and collider.

  * intersect_ray_2d(from_pos=[0.0, 0.0], to_pos=[0.0, 100.0],
                     collision_mask=0xFFFFFFFF, collide_with_bodies=True,
                     collide_with_areas=False)
        Cast a ray in 2D world space and return hit position, normal, and collider.

  * intersect_point_3d(position=[0.0, 0.0, 0.0], max_results=32, collision_mask=0xFFFFFFFF)
        Query 3D colliders overlapping a point in world space.

  * intersect_point_2d(position=[0.0, 0.0], max_results=32, collision_mask=0xFFFFFFFF)
        Query 2D colliders overlapping a point in world space.

  * intersect_shape_3d(shape_type="sphere", radius=1.0, max_results=32)
        Query 3D colliders overlapping a shape in world space.

  * cast_motion_3d(shape_type="sphere", radius=1.0, motion=[0.0, -1.0, 0.0])
        Simulate shape motion to determine safe and unsafe collision fractions.
"""


def register_physics_query_tools(mcp: FastMCP) -> None:
    register_manage_tool(
        mcp,
        tool_name="physics_query_manage",
        description=_DESCRIPTION,
        ops={
            "intersect_ray_3d": physics_query_handlers.physics_query_intersect_ray_3d,
            "intersect_ray_2d": physics_query_handlers.physics_query_intersect_ray_2d,
            "intersect_point_3d": physics_query_handlers.physics_query_intersect_point_3d,
            "intersect_point_2d": physics_query_handlers.physics_query_intersect_point_2d,
            "intersect_shape_3d": physics_query_handlers.physics_query_intersect_shape_3d,
            "cast_motion_3d": physics_query_handlers.physics_query_cast_motion_3d,
        },
        read_resource_forms={
            "intersect_ray_3d": None,
            "intersect_ray_2d": None,
            "intersect_point_3d": None,
            "intersect_point_2d": None,
            "intersect_shape_3d": None,
            "cast_motion_3d": None,
        },
    )
