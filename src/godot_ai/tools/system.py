"""MCP tool for Godot system, OS, time, and engine controls."""

from __future__ import annotations

from fastmcp import FastMCP

from godot_ai.handlers import system as system_handlers
from godot_ai.tools._meta_tool import register_manage_tool

_DESCRIPTION = """\
Operating System Information, Time APIs, Engine Time Scale, Clipboard, and Environment.

Ops:
  * get_system_info()
        Inspect OS name, processor count, device model, video adapter, and locale.

  * get_time()
        Query current Unix epoch, ISO 8601 string, timezone offset, and datetime dict.

  * set_time_scale(time_scale=1.0)
        Accelerate or slow down the game engine time scale.

  * get_clipboard()
        Retrieve text from the system clipboard.

  * set_clipboard(text="")
        Set text into the system clipboard.

  * get_env(var_name)
        Read a process environment variable.

  * set_env(var_name, value="")
        Set a process environment variable.
"""


def register_system_tools(mcp: FastMCP) -> None:
    register_manage_tool(
        mcp,
        tool_name="system_manage",
        description=_DESCRIPTION,
        ops={
            "get_system_info": system_handlers.system_get_system_info,
            "get_time": system_handlers.system_get_time,
            "set_time_scale": system_handlers.system_set_time_scale,
            "get_clipboard": system_handlers.system_get_clipboard,
            "set_clipboard": system_handlers.system_set_clipboard,
            "get_env": system_handlers.system_get_env,
            "set_env": system_handlers.system_set_env,
        },
        read_resource_forms={
            "get_system_info": None,
            "get_time": None,
            "get_clipboard": None,
            "get_env": None,
        },
    )
