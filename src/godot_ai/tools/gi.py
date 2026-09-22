"""MCP tool for Godot Global Illumination, Decals, and Probes."""

from __future__ import annotations

from fastmcp import FastMCP

from godot_ai.handlers import gi as gi_handlers
from godot_ai.tools._meta_tool import register_manage_tool

_DESCRIPTION = """\
Global Illumination, Decal Projections, and Lighting Probes Management.

Ops:
  * create_decal(parent_path="", name="Decal", size=[2.0, 2.0, 2.0], texture_albedo="")
        Create a Decal node under parent with optional albedo texture and dimensions.

  * configure_decal(node_path="", size=None, texture_albedo=None, texture_normal=None,
                    texture_orm=None, emission_energy=None, upper_fade=None, lower_fade=None)
        Configure properties and PBR textures of an existing Decal node.

  * create_reflection_probe(parent_path="", name="ReflectionProbe", size=[20.0, 20.0, 20.0],
                            update_mode="once")
        Create a ReflectionProbe node for local specular reflections.

  * create_voxel_gi(parent_path="", name="VoxelGI", size=[20.0, 20.0, 20.0], subdivide=1)
        Create a VoxelGI node for real-time indirect lighting and ambient bounce.

  * create_lightmap_gi(parent_path="", name="LightmapGI", bounces=3)
        Create a LightmapGI node for high-performance baked lighting.

  * get_gi_info(node_path="")
        Inspect properties and settings of a Decal, ReflectionProbe, VoxelGI, or LightmapGI.
"""


def register_gi_tools(mcp: FastMCP) -> None:
    register_manage_tool(
        mcp,
        tool_name="gi_manage",
        description=_DESCRIPTION,
        ops={
            "create_decal": gi_handlers.gi_create_decal,
            "configure_decal": gi_handlers.gi_configure_decal,
            "create_reflection_probe": gi_handlers.gi_create_reflection_probe,
            "create_voxel_gi": gi_handlers.gi_create_voxel_gi,
            "create_lightmap_gi": gi_handlers.gi_create_lightmap_gi,
            "get_gi_info": gi_handlers.gi_get_gi_info,
        },
        read_resource_forms={
            "get_gi_info": None,
        },
    )
