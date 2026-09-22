"""MCP tool for Godot font and label styling management."""

from __future__ import annotations

from fastmcp import FastMCP

from godot_ai.handlers import font as font_handlers
from godot_ai.tools._meta_tool import register_manage_tool

_DESCRIPTION = """\
Font and Label Styling Management.

Ops:
  * create_system_font(font_names=["Sans-Serif"], italic=False, weight=400, save_path="")
        Create a SystemFont resource and optionally save to disk.

  * create_font_variation(base_font_path, variation_embolden=0.0, save_path="")
        Create a FontVariation resource derived from a base font.

  * create_label_settings(font_path="", font_size=16, font_color="#ffffff",
                          outline_size=0, outline_color="#000000",
                          shadow_size=0, shadow_color="#000000", save_path="")
        Create a LabelSettings resource with font styling options.

  * get_font_info(font_path)
        Inspect metadata and properties of a font resource.
"""


def register_font_tools(mcp: FastMCP) -> None:
    register_manage_tool(
        mcp,
        tool_name="font_manage",
        description=_DESCRIPTION,
        ops={
            "create_system_font": font_handlers.font_create_system_font,
            "create_font_variation": font_handlers.font_create_font_variation,
            "create_label_settings": font_handlers.font_create_label_settings,
            "get_font_info": font_handlers.font_get_font_info,
        },
        read_resource_forms={
            "get_font_info": None,
        },
    )
