"""MCP tool for Godot background asynchronous resource loading."""

from __future__ import annotations

from fastmcp import FastMCP

from godot_ai.handlers import loader as loader_handlers
from godot_ai.tools._meta_tool import register_manage_tool

_DESCRIPTION = """\
Asynchronous Threaded Resource Loading, Progress Polling, and Loading Screen Scaffolding.

Ops:
  * start_load(path, type_hint="", use_sub_threads=false, cache_mode=1)
        Begin background asynchronous loading of a scene or resource.

  * get_status(path)
        Poll progress percentage (0.0 - 1.0) and status (in_progress, loaded, failed).

  * get_resource(path)
        Retrieve confirmation and metadata for a loaded resource.

  * scaffold_loading_screen(save_path="res://scripts/loading_screen.gd")
        Scaffold a complete asynchronous loading screen script.
"""


def register_loader_tools(mcp: FastMCP) -> None:
    register_manage_tool(
        mcp,
        tool_name="loader_manage",
        description=_DESCRIPTION,
        ops={
            "start_load": loader_handlers.loader_start_load,
            "get_status": loader_handlers.loader_get_status,
            "get_resource": loader_handlers.loader_get_resource,
            "scaffold_loading_screen": loader_handlers.loader_scaffold_loading_screen,
        },
        read_resource_forms={
            "start_load": None,
            "get_status": None,
            "get_resource": None,
        },
    )
