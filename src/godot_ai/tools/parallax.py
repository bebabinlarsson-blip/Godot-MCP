"""MCP tool for Godot Parallax2D and CanvasLayer management."""

from __future__ import annotations

from fastmcp import FastMCP

from godot_ai.handlers import parallax as parallax_handlers
from godot_ai.tools._meta_tool import register_manage_tool

_DESCRIPTION = """\
Parallax and Canvas Layer Management.

Ops:
  * scaffold_parallax(parent_path="", scroll_scale=[1.0,1.0], repeat_size=[0.0,0.0],
                      node_name="Parallax2D")
        Scaffold a Parallax2D node for background layer scrolling.

  * scaffold_canvas_layer(parent_path="", layer=1, follow_viewport=False,
                          node_name="CanvasLayer")
        Scaffold a CanvasLayer node in the scene tree.

  * scaffold_visibility_notifier(parent_path="", is_2d=True, rect_size=[100.0,100.0],
                                 node_name="VisibilityNotifier")
        Scaffold a VisibleOnScreenNotifier2D or 3D node.

  * get_parallax_info(node_path)
        Inspect properties of a parallax or canvas layer node.
"""


def register_parallax_tools(mcp: FastMCP) -> None:
    register_manage_tool(
        mcp,
        tool_name="parallax_manage",
        description=_DESCRIPTION,
        ops={
            "scaffold_parallax": parallax_handlers.parallax_scaffold_parallax,
            "scaffold_canvas_layer": (
                parallax_handlers.parallax_scaffold_canvas_layer
            ),
            "scaffold_visibility_notifier": (
                parallax_handlers.parallax_scaffold_visibility_notifier
            ),
            "get_parallax_info": parallax_handlers.parallax_get_parallax_info,
        },
        read_resource_forms={
            "get_parallax_info": None,
        },
    )
