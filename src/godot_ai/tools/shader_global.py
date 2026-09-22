"""MCP tool for Godot global shader parameters."""

from __future__ import annotations

from fastmcp import FastMCP

from godot_ai.handlers import shader_global as shader_global_handlers
from godot_ai.tools._meta_tool import register_manage_tool

_DESCRIPTION = """\
Global Shader Parameters, Uniform Variables, and Project-Wide Shader Settings.

Ops:
  * list_globals()
        List all global shader parameters defined in RenderingServer.

  * set_global(name, value)
        Set or update runtime value of a global shader parameter.

  * add_global(name, type="float", value=None)
        Define a new global shader parameter in ProjectSettings (shader_globals/).

  * remove_global(name)
        Remove a global shader parameter definition.
"""


def register_shader_global_tools(mcp: FastMCP) -> None:
    register_manage_tool(
        mcp,
        tool_name="shader_global_manage",
        description=_DESCRIPTION,
        ops={
            "list_globals": shader_global_handlers.shader_global_list_globals,
            "set_global": shader_global_handlers.shader_global_set_global,
            "add_global": shader_global_handlers.shader_global_add_global,
            "remove_global": shader_global_handlers.shader_global_remove_global,
        },
        read_resource_forms={
            "list_globals": None,
        },
    )
