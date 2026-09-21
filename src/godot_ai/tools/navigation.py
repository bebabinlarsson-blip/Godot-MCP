"""MCP tool for 2D and 3D navigation and pathfinding.

Covers NavigationRegion2D, NavigationAgent2D, NavigationRegion3D, NavigationAgent3D,
and in-editor polygon/mesh baking.
"""

from __future__ import annotations

from fastmcp import FastMCP

from godot_ai.handlers import navigation as nav_handlers
from godot_ai.tools._meta_tool import register_manage_tool

_DESCRIPTION = """\
2D and 3D Navigation and Pathfinding.

Ops:
  • setup_region_2d(parent_path="", name="NavigationRegion2D", polygon=None,
                     cell_size=1.0, agent_radius=10.0,
                     parsed_geometry_type="mesh_instances_and_colliders")
        Setup NavigationRegion2D with NavigationPolygon, boundary vertices,
        and geometry parsing configuration in one undo action.
  • attach_agent_2d(node_path, agent_name="NavigationAgent2D", radius=16.0,
                     max_speed=150.0, path_desired_distance=20.0,
                     target_desired_distance=20.0, avoidance_enabled=True)
        Attach and configure NavigationAgent2D under character/enemy node.
  • bake_2d(region_path, on_thread=False)
        Trigger in-editor baking of 2D navigation polygon.
  • setup_region_3d(parent_path="", name="NavigationRegion3D", cell_size=0.25,
                     cell_height=0.25, agent_radius=0.5, agent_height=1.8)
        Setup NavigationRegion3D with NavigationMesh in one undo action.
  • attach_agent_3d(node_path, agent_name="NavigationAgent3D", radius=0.5,
                     height=1.8, max_speed=5.0, path_desired_distance=1.0,
                     target_desired_distance=1.0, avoidance_enabled=True)
        Attach and configure NavigationAgent3D under character/enemy node.
  • bake_3d(region_path, on_thread=False)
        Trigger in-editor baking of 3D navigation mesh.
"""


def register_navigation_tools(mcp: FastMCP) -> None:
    register_manage_tool(
        mcp,
        tool_name="navigation_manage",
        description=_DESCRIPTION,
        ops={
            "setup_region_2d": nav_handlers.navigation_setup_region_2d,
            "attach_agent_2d": nav_handlers.navigation_attach_agent_2d,
            "bake_2d": nav_handlers.navigation_bake_2d,
            "setup_region_3d": nav_handlers.navigation_setup_region_3d,
            "attach_agent_3d": nav_handlers.navigation_attach_agent_3d,
            "bake_3d": nav_handlers.navigation_bake_3d,
        },
    )
