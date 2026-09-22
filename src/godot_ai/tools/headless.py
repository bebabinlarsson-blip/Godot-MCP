"""MCP tool for Godot standalone headless execution and CLI operations."""

from __future__ import annotations

from fastmcp import FastMCP

from godot_ai.handlers import headless as headless_handlers
from godot_ai.tools._meta_tool import register_manage_tool

_DESCRIPTION = """\
Standalone Headless Engine & CLI Management.

Ops:
  * run_script(script_path="", inline_code="")
        Execute a GDScript file or inline code snippet in headless mode.

  * run_headless_scene(scene_path, quit_after_frames=60)
        Execute a scene headlessly for testing or headless game simulation.

  * export_project_cli(preset, output_path, is_debug=False)
        Trigger a headless project export via Godot CLI preset.

  * reimport_assets_cli()
        Reimport modified assets via a headless editor pass.

  * get_engine_info()
        Inspect Godot engine version, platform, and headless CLI capabilities.
"""


def register_headless_tools(mcp: FastMCP) -> None:
    register_manage_tool(
        mcp,
        tool_name="headless_manage",
        description=_DESCRIPTION,
        ops={
            "run_script": headless_handlers.headless_run_script,
            "run_headless_scene": headless_handlers.headless_run_headless_scene,
            "export_project_cli": headless_handlers.headless_export_project_cli,
            "reimport_assets_cli": headless_handlers.headless_reimport_assets_cli,
            "get_engine_info": headless_handlers.headless_get_engine_info,
        },
        read_resource_forms={
            "get_engine_info": None,
        },
    )
