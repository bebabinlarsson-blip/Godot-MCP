"""MCP tool for Physics queries, raycasting, and sensor scaffolding."""

from __future__ import annotations

from fastmcp import FastMCP

from godot_ai.handlers import physics as physics_handlers
from godot_ai.tools._meta_tool import register_manage_tool

_DESCRIPTION = """\
Physics Queries, Raycasting, and Sensor Scaffolding.

Ops:
  * raycast_2d(from_pos=[0, 0], to_pos=[0, 100], collision_mask=4294967295,
               collide_with_bodies=True, collide_with_areas=False, hit_from_inside=False)
        Perform a 2D raycast query directly through the active World2D physics space,
        returning collision point, normal, collider path, and shape.

  * raycast_3d(from_pos=[0, 10, 0], to_pos=[0, -10, 0], collision_mask=4294967295,
               collide_with_bodies=True, collide_with_areas=False, hit_from_inside=False)
        Perform a 3D raycast query directly through the active World3D physics space,
        returning collision point, normal, collider path, and shape.

  * query_point_2d(point=[0, 0], collision_mask=4294967295, max_results=32,
                   collide_with_bodies=True, collide_with_areas=False)
        Query intersecting physics bodies and areas overlapping a 2D world coordinate.

  * scaffold_sensor(parent_path="", target_position=[0, 50], is_2d=True,
                    sensor_name="GroundSensor", collision_mask=1, enabled=True)
        Instantiate and attach a RayCast2D or RayCast3D sensor to a character or node.

  * query_point_3d(point=[0, 0, 0], collision_mask=4294967295, max_results=32,
                   collide_with_bodies=True, collide_with_areas=False)
        Query intersecting physics bodies and areas overlapping a 3D world coordinate.

  * shapecast_scaffold(parent_path="", shape_type="sphere", radius=1.0,
                       is_2d=False, sensor_name="ShapeCast", collision_mask=1)
        Create a ShapeCast2D or ShapeCast3D node with the specified collision shape.

  * set_layer_names(layer_type="2d_physics", layers={"1": "Environment", "2": "Player"})
        Set project-wide layer names (layer_type: 2d_physics | 3d_physics |
        2d_render | 3d_render).

  * get_layer_names(layer_type="all")
        Get configured layer names (layer_type: 2d_physics | 3d_physics |
        2d_render | 3d_render | all).
"""


def register_physics_tools(mcp: FastMCP) -> None:
    register_manage_tool(
        mcp,
        tool_name="physics_manage",
        description=_DESCRIPTION,
        ops={
            "raycast_2d": physics_handlers.physics_raycast_2d,
            "raycast_3d": physics_handlers.physics_raycast_3d,
            "query_point_2d": physics_handlers.physics_query_point_2d,
            "scaffold_sensor": physics_handlers.physics_scaffold_sensor,
            "query_point_3d": physics_handlers.physics_query_point_3d,
            "shapecast_scaffold": physics_handlers.physics_shapecast_scaffold,
            "set_layer_names": physics_handlers.physics_set_layer_names,
            "get_layer_names": physics_handlers.physics_get_layer_names,
        },
        read_resource_forms={
            "raycast_2d": None,
            "raycast_3d": None,
            "query_point_2d": None,
            "query_point_3d": None,
            "get_layer_names": None,
        },
    )
