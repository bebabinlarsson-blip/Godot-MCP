"""MCP tool for Godot 2D and 3D occlusion culling."""

from __future__ import annotations

from fastmcp import FastMCP

from godot_ai.handlers import occluder as occluder_handlers
from godot_ai.tools._meta_tool import register_manage_tool

_DESCRIPTION = """\
Occlusion Culling Management.

Ops:
  * scaffold_occluder_3d(parent_path="", occluder_type="box", size=[1.0,1.0,1.0],
                         node_name="OccluderInstance3D")
        Scaffold a 3D occlusion culling node (box, sphere, quad).

  * scaffold_occluder_2d(parent_path="", polygon_points=[[-16,-16],[16,-16],[16,16],[-16,16]],
                         closed=True, node_name="LightOccluder2D")
        Scaffold a 2D light/occlusion polygon node in current scene.

  * get_occluder_info(occluder_path)
        Inspect occluder node and attached occluder resource.
"""


def register_occluder_tools(mcp: FastMCP) -> None:
    register_manage_tool(
        mcp,
        tool_name="occluder_manage",
        description=_DESCRIPTION,
        ops={
            "scaffold_occluder_3d": occluder_handlers.occluder_scaffold_occluder_3d,
            "scaffold_occluder_2d": occluder_handlers.occluder_scaffold_occluder_2d,
            "get_occluder_info": occluder_handlers.occluder_get_occluder_info,
        },
        read_resource_forms={
            "get_occluder_info": None,
        },
    )
