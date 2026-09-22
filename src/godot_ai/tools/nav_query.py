"""MCP tool for Godot navigation queries, navigation links, and obstacles."""

from __future__ import annotations

from fastmcp import FastMCP

from godot_ai.handlers import nav_query as nav_query_handlers
from godot_ai.tools._meta_tool import register_manage_tool

_DESCRIPTION = """\
Navigation Queries and Spatial Pathfinding Management.

Ops:
  * query_path_2d(start=[0,0], end=[0,0], optimize=True)
        Query 2D navigation path between start and end coordinates.

  * query_path_3d(start=[0,0,0], end=[0,0,0], optimize=True)
        Query 3D navigation path between start and end coordinates.

  * scaffold_nav_link(parent_path="", start_position=None, end_position=None,
                      bidirectional=True, is_3d=False, node_name="NavLink")
        Scaffold a 2D or 3D NavigationLink connecting disjoint navmesh areas.

  * scaffold_nav_obstacle(parent_path="", radius=32.0, is_3d=False, node_name="NavObstacle")
        Scaffold a 2D or 3D NavigationObstacle for avoidance navigation.

  * get_nav_map_info(is_3d=False)
        Inspect navigation map cell size, margins, and properties.
"""


def register_nav_query_tools(mcp: FastMCP) -> None:
    register_manage_tool(
        mcp,
        tool_name="nav_query_manage",
        description=_DESCRIPTION,
        ops={
            "query_path_2d": nav_query_handlers.nav_query_query_path_2d,
            "query_path_3d": nav_query_handlers.nav_query_query_path_3d,
            "scaffold_nav_link": nav_query_handlers.nav_query_scaffold_nav_link,
            "scaffold_nav_obstacle": nav_query_handlers.nav_query_scaffold_nav_obstacle,
            "get_nav_map_info": nav_query_handlers.nav_query_get_nav_map_info,
        },
        read_resource_forms={
            "query_path_2d": None,
            "query_path_3d": None,
            "get_nav_map_info": None,
        },
    )
