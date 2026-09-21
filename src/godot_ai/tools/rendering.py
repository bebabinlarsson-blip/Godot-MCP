"""MCP tool for Godot WorldEnvironment, post-processing, and lighting presets."""

from __future__ import annotations

from fastmcp import FastMCP

from godot_ai.handlers import rendering as rendering_handlers
from godot_ai.tools._meta_tool import register_manage_tool

_DESCRIPTION = """\
WorldEnvironment, Post-Processing Effects, CameraAttributes, and Lighting Presets.

Ops:
  * scaffold_world_environment(parent_path="", sky_mode="procedural",
                               tonemap_mode="aces", name="WorldEnvironment")
        Scaffold a WorldEnvironment node with sky and tonemapping.

  * set_environment_effects(node_path="", glow_enabled=None, glow_intensity=None,
                            ssr_enabled=None, ssao_enabled=None, ssil_enabled=None,
                            sdfgi_enabled=None, volumetric_fog_enabled=None,
                            volumetric_fog_density=None)
        Configure post-processing and volumetric lighting effects.

  * set_camera_attributes(camera_path, attributes_type="practical",
                          auto_exposure_enabled=None, dof_blur_far_enabled=None,
                          dof_blur_far_distance=None)
        Configure CameraAttributes on a Camera3D node.

  * apply_lighting_preset(preset="outdoor_sunny", node_path="")
        Apply a visual lighting preset to the environment.

  * get_environment_info(node_path="")
        Read active environment properties, background mode, and post-processing toggles.
"""


def register_rendering_tools(mcp: FastMCP) -> None:
    register_manage_tool(
        mcp,
        tool_name="rendering_manage",
        description=_DESCRIPTION,
        ops={
            "scaffold_world_environment": rendering_handlers.rendering_scaffold_world_environment,
            "set_environment_effects": rendering_handlers.rendering_set_environment_effects,
            "set_camera_attributes": rendering_handlers.rendering_set_camera_attributes,
            "apply_lighting_preset": rendering_handlers.rendering_apply_lighting_preset,
            "get_environment_info": rendering_handlers.rendering_get_environment_info,
        },
        read_resource_forms={
            "get_environment_info": None,
        },
    )
