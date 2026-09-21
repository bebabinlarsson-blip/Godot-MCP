"""MCP tool for Godot Performance monitors, memory analysis, and engine diagnostics."""

from __future__ import annotations

from fastmcp import FastMCP

from godot_ai.handlers import profiler as profiler_handlers
from godot_ai.tools._meta_tool import register_manage_tool

_DESCRIPTION = """\
Engine Diagnostics, Performance Monitors, and Memory Analysis.

Ops:
  * get_monitors()
        Read active Godot Performance monitors (FPS, process time, physics time,
        draw calls, object counts, memory, and audio latency).

  * get_memory_info()
        Read detailed static, peak, message buffer, VRAM, and texture memory breakdown.

  * get_render_info()
        Read render pipeline frame statistics (draw calls, primitive count, render objects, VRAM).

  * get_physics_info()
        Read 2D and 3D physics server stats (active bodies, collision pairs, islands).
"""


def register_profiler_tools(mcp: FastMCP) -> None:
    register_manage_tool(
        mcp,
        tool_name="profiler_manage",
        description=_DESCRIPTION,
        ops={
            "get_monitors": profiler_handlers.profiler_get_monitors,
            "get_memory_info": profiler_handlers.profiler_get_memory_info,
            "get_render_info": profiler_handlers.profiler_get_render_info,
            "get_physics_info": profiler_handlers.profiler_get_physics_info,
        },
        read_resource_forms={
            "get_monitors": "godot://performance",
            "get_memory_info": None,
            "get_render_info": None,
            "get_physics_info": None,
        },
    )
