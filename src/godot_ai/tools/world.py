"""MCP tool for Godot WorldEnvironment, Sky materials, and post-processing."""

from __future__ import annotations

from fastmcp import FastMCP

from godot_ai.handlers import world as world_handlers
from godot_ai.tools._meta_tool import register_manage_tool

_DESCRIPTION = """\
WorldEnvironment, Sky, and Post-Processing Management.

Ops:
  * configure_world_environment(node_path="", properties={})
        Configure properties of WorldEnvironment and its Environment resource.

  * create_sky_material(node_path="", sky_type="procedural", sky_top_color="",
                        ground_bottom_color="", texture_path="")
        Create and assign procedural or panorama sky material to Environment.

  * set_volumetric_fog(node_path="", enabled=True, density=None, albedo=None,
                       emission=None, anisotropy=None, length=None)
        Enable and configure volumetric fog parameters on Environment.

  * configure_camera_attributes(node_path="", attribute_type="practical", properties={})
        Configure CameraAttributesPractical or CameraAttributesPhysical.

  * get_world_info(node_path="")
        Inspect active world environment, fog, sky, and post-processing settings.
"""


def register_world_tools(mcp: FastMCP) -> None:
    register_manage_tool(
        mcp,
        tool_name="world_manage",
        description=_DESCRIPTION,
        ops={
            "configure_world_environment": world_handlers.world_configure_world_environment,
            "create_sky_material": world_handlers.world_create_sky_material,
            "set_volumetric_fog": world_handlers.world_set_volumetric_fog,
            "configure_camera_attributes": world_handlers.world_configure_camera_attributes,
            "get_world_info": world_handlers.world_get_world_info,
        },
        read_resource_forms={
            "get_world_info": None,
        },
    )
