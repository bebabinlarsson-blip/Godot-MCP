"""MCP tool for Godot image and texture resource management."""

from __future__ import annotations

from fastmcp import FastMCP

from godot_ai.handlers import texture as texture_handlers
from godot_ai.tools._meta_tool import register_manage_tool

_DESCRIPTION = """\
Texture and Image Resource Management.

Ops:
  * create_image(width=64, height=64, use_mipmaps=False, format="rgba8",
                 fill_color=None, save_path="")
        Create a new Image resource and optionally fill color and save to disk.

  * create_atlas(atlas_path, region_rect=[0,0,32,32], filter_clip=False, save_path="")
        Create an AtlasTexture referencing a region of an existing texture.

  * get_texture_info(path)
        Get metadata for a texture or image resource.

  * create_curve_texture(points=[[0.0,0.0],[1.0,1.0]], width=256, save_path="")
        Create a CurveTexture resource from control points.
"""


def register_texture_tools(mcp: FastMCP) -> None:
    register_manage_tool(
        mcp,
        tool_name="texture_manage",
        description=_DESCRIPTION,
        ops={
            "create_image": texture_handlers.texture_create_image,
            "create_atlas": texture_handlers.texture_create_atlas,
            "get_texture_info": texture_handlers.texture_get_texture_info,
            "create_curve_texture": texture_handlers.texture_create_curve_texture,
        },
        read_resource_forms={
            "get_texture_info": None,
        },
    )
