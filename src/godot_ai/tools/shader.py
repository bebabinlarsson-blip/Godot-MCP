"""MCP tool for Shader system management and visual effect presets."""

from __future__ import annotations

from fastmcp import FastMCP

from godot_ai.handlers import shader as shader_handlers
from godot_ai.tools._meta_tool import register_manage_tool

_DESCRIPTION = """\
Shader System and Visual Effect Management.

Ops:
  * create(path="res://shaders/custom.gdshader", shader_type="canvas_item",
           code="", overwrite=False)
        Create a new .gdshader resource with boilerplate for canvas_item, spatial,
        particles, sky, or fog.

  * apply_preset(preset="outline_2d", target_node_path="", shader_path="", params={})
        Compile and apply production shader presets:
          - outline_2d: Dynamic sprite border outline (outline_color, outline_width).
          - hit_flash: Combat damage flash effect (flash_color, flash_modifier).
          - dissolve_2d: Burning noise dissolve effect (dissolve_amount, burn_color, burn_size).
          - water_2d: Wave distortion and reflection (water_tint, wave_speed, wave_freq, wave_amp).
          - foliage_wind: Vertex displacement wind sway (wind_speed, wind_strength).
          - crt_scanline: Retro CRT monitor scanlines, curvature, and vignette.
          - hologram_glitch: Sci-fi holographic glitch and scanlines (holo_color, scanline_density).
        Optionally assign directly to target node's material.

  * set_param(param="outline_width", value=2.0, target_node_path="", material_path="")
        Set a uniform parameter on a ShaderMaterial by target node or material path.

  * get_params(target_node_path="", material_path="")
        Inspect shader code and parameters from a target node or material path.
"""


def register_shader_tools(mcp: FastMCP) -> None:
    register_manage_tool(
        mcp,
        tool_name="shader_manage",
        description=_DESCRIPTION,
        ops={
            "create": shader_handlers.shader_create,
            "apply_preset": shader_handlers.shader_apply_preset,
            "set_param": shader_handlers.shader_set_param,
            "get_params": shader_handlers.shader_get_params,
        },
        read_resource_forms={
            "get_params": None,
        },
    )
