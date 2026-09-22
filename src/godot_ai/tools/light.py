"""MCP tool for Godot lights, shadows, decals, and reflection/GI probes."""

from __future__ import annotations

from fastmcp import FastMCP

from godot_ai.handlers import light as light_handlers
from godot_ai.tools._meta_tool import register_manage_tool

_DESCRIPTION = """\
2D and 3D Lighting, Shadow Tuning, Decal Projection, and Reflection/GI Probes.

Ops:
  * scaffold_light_3d(type="DirectionalLight3D", parent_path="", name="Light3D",
                      color=None, energy=1.0, shadows=True, range=5.0,
                      attenuation=1.0, spot_angle=45.0)
        Scaffold a DirectionalLight3D, OmniLight3D, or SpotLight3D node.

  * scaffold_light_2d(type="PointLight2D", parent_path="", name="Light2D",
                      color=None, energy=1.0, shadows=False)
        Scaffold a PointLight2D or DirectionalLight2D node.

  * scaffold_decal(parent_path="", name="Decal", size=None, texture_albedo="")
        Scaffold a Decal node with projection volume and albedo texture.

  * scaffold_probe(type="ReflectionProbe", parent_path="", name="Probe", size=None)
        Scaffold a ReflectionProbe, LightmapGI, or VoxelGI node.

  * set_light_properties(light_path, color=None, energy=None, shadows=None,
                         volumetric_fog_energy=None)
        Update lighting parameters on an existing 2D or 3D light node.

  * get_light_info(light_path)
        Inspect light energy, color, and shadow properties.
"""


def register_light_tools(mcp: FastMCP) -> None:
    register_manage_tool(
        mcp,
        tool_name="light_manage",
        description=_DESCRIPTION,
        ops={
            "scaffold_light_3d": light_handlers.light_scaffold_light_3d,
            "scaffold_light_2d": light_handlers.light_scaffold_light_2d,
            "scaffold_decal": light_handlers.light_scaffold_decal,
            "scaffold_probe": light_handlers.light_scaffold_probe,
            "set_light_properties": light_handlers.light_set_light_properties,
            "get_light_info": light_handlers.light_get_light_info,
        },
        read_resource_forms={
            "get_light_info": None,
        },
    )
