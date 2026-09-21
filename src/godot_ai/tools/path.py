"""MCP tool for Godot Path, Curve, and Spline management."""

from __future__ import annotations

from fastmcp import FastMCP

from godot_ai.handlers import path as path_handlers
from godot_ai.tools._meta_tool import register_manage_tool

_DESCRIPTION = """\
Path2D/Path3D Curves, Splines, and Patrol Route Automation.

Ops:
  * create_curve_2d(points=None, closed=false, save_path="")
        Create a Curve2D resource with Bezier control points.

  * create_curve_3d(points=None, closed=false, save_path="")
        Create a Curve3D resource with Bezier control points.

  * scaffold_path(parent_path="", type="Path3D", name="Path", with_follow=true, loop=true)
        Scaffold a Path2D or Path3D node with an optional PathFollow child.

  * sample_baked_points(path_node_path, interval=1.0)
        Sample baked positions along a Path2D or Path3D at fixed intervals.

  * generate_spline(shape="circle", is_3d=true, radius=5.0, points_count=16, save_path="")
        Procedurally generate standard spline curves (circle, sine, spiral, rect, s_curve).
"""


def register_path_tools(mcp: FastMCP) -> None:
    register_manage_tool(
        mcp,
        tool_name="path_manage",
        description=_DESCRIPTION,
        ops={
            "create_curve_2d": path_handlers.path_create_curve_2d,
            "create_curve_3d": path_handlers.path_create_curve_3d,
            "scaffold_path": path_handlers.path_scaffold_path,
            "sample_baked_points": path_handlers.path_sample_baked_points,
            "generate_spline": path_handlers.path_generate_spline,
        },
        read_resource_forms={
            "sample_baked_points": None,
        },
    )
