"""MCP tool for Godot AR/VR OpenXR player rigging and tracking."""

from __future__ import annotations

from fastmcp import FastMCP

from godot_ai.handlers import xr as xr_handlers
from godot_ai.tools._meta_tool import register_manage_tool

_DESCRIPTION = """\
AR/VR OpenXR Rigging, Controller Setup, and XRServer Tracking Status.

Ops:
  * scaffold_xr_rig(parent_path="", rig_name="XROrigin3D")
        Scaffold complete OpenXR player hierarchy (origin, camera, left/right controllers).

  * get_xr_status()
        Inspect XRServer active interfaces, tracking status, and OpenXR availability.

  * generate_xr_startup_script(save_path="res://scripts/xr_initializer.gd")
        Generate an OpenXR initialization bootstrap script.
"""


def register_xr_tools(mcp: FastMCP) -> None:
    register_manage_tool(
        mcp,
        tool_name="xr_manage",
        description=_DESCRIPTION,
        ops={
            "scaffold_xr_rig": xr_handlers.xr_scaffold_xr_rig,
            "get_xr_status": xr_handlers.xr_get_xr_status,
            "generate_xr_startup_script": xr_handlers.xr_generate_xr_startup_script,
        },
        read_resource_forms={
            "get_xr_status": None,
        },
    )
