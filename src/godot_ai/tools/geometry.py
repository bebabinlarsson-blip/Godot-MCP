"""MCP tool for 2D constructive solid geometry and 3D procedural mesh generation."""

from __future__ import annotations

from fastmcp import FastMCP

from godot_ai.handlers import geometry as geom_handlers
from godot_ai.tools._meta_tool import register_manage_tool

_DESCRIPTION = """\
Constructive 2D Solid Geometry and Procedural 3D Mesh Generation.

Ops:
  * polygon_boolean(operation="merge", poly_a=[...], poly_b=[...])
        Perform 2D constructive solid polygon operations (merge, clip, intersect, exclude).

  * polygon_offset(polygon=[...], delta=5.0, join_type="square")
        Deflate or inflate a 2D polygon via Geometry2D.offset_polygon.

  * triangulate(polygon=[...])
        Triangulate a 2D polygon into index arrays via Geometry2D.triangulate_polygon.

  * convex_hull(points=[...])
        Compute the 2D convex hull wrapping an arbitrary point set.

  * scaffold_polygon_2d(parent_path="", points=[...], polygon_name="CustomPolygon",
                         is_collision=False, color=[1.0, 1.0, 1.0, 1.0])
        Instantiate and attach a Polygon2D or CollisionPolygon2D to the active scene.

  * generate_mesh(mesh_type="cube", size=[2.0, 2.0, 2.0], dest_path="", parent_path="")
        Generate a procedural 3D mesh via SurfaceTool (cube, plane,
        pyramid) and attach to scene or save.
"""


def register_geometry_tools(mcp: FastMCP) -> None:
    register_manage_tool(
        mcp,
        tool_name="geometry_manage",
        description=_DESCRIPTION,
        ops={
            "polygon_boolean": geom_handlers.geometry_polygon_boolean,
            "polygon_offset": geom_handlers.geometry_polygon_offset,
            "triangulate": geom_handlers.geometry_triangulate,
            "convex_hull": geom_handlers.geometry_convex_hull,
            "scaffold_polygon_2d": geom_handlers.geometry_scaffold_polygon_2d,
            "generate_mesh": geom_handlers.geometry_generate_mesh,
        },
        read_resource_forms={
            "polygon_boolean": None,
            "polygon_offset": None,
            "triangulate": None,
            "convex_hull": None,
        },
    )
