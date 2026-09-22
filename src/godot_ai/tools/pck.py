"""MCP tool for Godot PCK and asset bundle packaging."""

from __future__ import annotations

from fastmcp import FastMCP

from godot_ai.handlers import pck as pck_handlers
from godot_ai.tools._meta_tool import register_manage_tool

_DESCRIPTION = """\
PCK Virtual Package Creation, Dynamic Mounting, and Inspection.

Ops:
  * create_pck(pck_path, files=[], alignment=32)
        Pack a list of project resource files into a standalone .pck package.

  * load_pck(pck_path, replace_files=True)
        Dynamically mount a .pck package into the virtual filesystem.

  * inspect_pck(pck_path)
        Check existence and size in bytes of a .pck package.
"""


def register_pck_tools(mcp: FastMCP) -> None:
    register_manage_tool(
        mcp,
        tool_name="pck_manage",
        description=_DESCRIPTION,
        ops={
            "create_pck": pck_handlers.pck_create_pck,
            "load_pck": pck_handlers.pck_load_pck,
            "inspect_pck": pck_handlers.pck_inspect_pck,
        },
        read_resource_forms={
            "inspect_pck": None,
        },
    )
