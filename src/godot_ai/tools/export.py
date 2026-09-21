"""MCP tool for Godot project export and build automation."""

from __future__ import annotations

from fastmcp import FastMCP

from godot_ai.handlers import export as export_handlers
from godot_ai.tools._meta_tool import register_manage_tool

_DESCRIPTION = """\
Project Export Automation, Presets Inspection, and Headless Game Builds.

Ops:
  * list_presets()
        List all configured platform export targets in export_presets.cfg.

  * get_preset_info(preset_name)
        Inspect detailed build settings and options for a specific preset.

  * run_export(preset_name, output_path="", debug=false)
        Execute a headless project export via Godot CLI.
"""


def register_export_tools(mcp: FastMCP) -> None:
    register_manage_tool(
        mcp,
        tool_name="export_manage",
        description=_DESCRIPTION,
        ops={
            "list_presets": export_handlers.export_list_presets,
            "get_preset_info": export_handlers.export_get_preset_info,
            "run_export": export_handlers.export_run_export,
        },
        read_resource_forms={
            "list_presets": None,
            "get_preset_info": None,
        },
    )
