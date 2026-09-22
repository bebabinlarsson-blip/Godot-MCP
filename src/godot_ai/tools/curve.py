"""MCP tool for Godot curves, splines, gradients, and ramps."""

from __future__ import annotations

from fastmcp import FastMCP

from godot_ai.handlers import curve as curve_handlers
from godot_ai.tools._meta_tool import register_manage_tool

_DESCRIPTION = """\
Curve (1D, 2D, 3D), Splines, Gradients, and Color Ramps Management.

Ops:
  * create_curve_1d(points=[[0.0, 0.0], [1.0, 1.0]], min_value=0.0, max_value=1.0, save_path="")
        Create a 1D interpolation/easing Curve resource.

  * create_curve_2d(points=[[0.0, 0.0], [100.0, 100.0]], in_tangents=[], out_tangents=[],
                    save_path="")
        Create a 2D bezier spline Curve2D resource for paths and animation.

  * create_curve_3d(points=[[0.0, 0.0, 0.0], [0.0, 5.0, 10.0]], in_tangents=[],
                    out_tangents=[], save_path="")
        Create a 3D bezier spline Curve3D resource for 3D paths and rail movement.

  * create_gradient(offsets=[0.0, 1.0], colors=["#000000", "#ffffff"], save_path="")
        Create a multi-stop color ramp Gradient resource.

  * create_gradient_texture(gradient_path="", width=256, is_2d=False, height=256, save_path="")
        Create a GradientTexture1D or GradientTexture2D resource.

  * sample_curve(curve_path, offset=0.5)
        Sample value or baked position on a Curve resource.

  * sample_gradient(gradient_path, offset=0.5)
        Sample RGBA color on a Gradient resource.
"""


def register_curve_tools(mcp: FastMCP) -> None:
    register_manage_tool(
        mcp,
        tool_name="curve_manage",
        description=_DESCRIPTION,
        ops={
            "create_curve_1d": curve_handlers.curve_create_curve_1d,
            "create_curve_2d": curve_handlers.curve_create_curve_2d,
            "create_curve_3d": curve_handlers.curve_create_curve_3d,
            "create_gradient": curve_handlers.curve_create_gradient,
            "create_gradient_texture": curve_handlers.curve_create_gradient_texture,
            "sample_curve": curve_handlers.curve_sample_curve,
            "sample_gradient": curve_handlers.curve_sample_gradient,
        },
        read_resource_forms={
            "sample_curve": None,
            "sample_gradient": None,
        },
    )
