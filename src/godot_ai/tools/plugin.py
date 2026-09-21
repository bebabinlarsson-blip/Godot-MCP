"""MCP tool for Godot editor plugin and addon management."""

from __future__ import annotations

from fastmcp import FastMCP

from godot_ai.handlers import plugin as plugin_handlers
from godot_ai.tools._meta_tool import register_manage_tool

_DESCRIPTION = """\
EditorPlugin Discovery, Addon Enable/Disable, and Custom Plugin Scaffolding.

Ops:
  * list_plugins(addons_dir="res://addons")
        Scan res://addons and list all installed editor plugins and statuses.

  * set_plugin_enabled(plugin_name, enabled=true)
        Enable or disable an editor plugin in ProjectSettings.

  * scaffold_plugin(plugin_id="my_custom_addon", plugin_name="My Custom Addon",
                    description="A custom Godot EditorPlugin", author="Developer",
                    version="1.0.0", with_dock=true)
        Generate complete scaffolding for a new custom EditorPlugin.
"""


def register_plugin_tools(mcp: FastMCP) -> None:
    register_manage_tool(
        mcp,
        tool_name="plugin_manage",
        description=_DESCRIPTION,
        ops={
            "list_plugins": plugin_handlers.plugin_list_plugins,
            "set_plugin_enabled": plugin_handlers.plugin_set_plugin_enabled,
            "scaffold_plugin": plugin_handlers.plugin_scaffold_plugin,
        },
        read_resource_forms={
            "list_plugins": None,
        },
    )
