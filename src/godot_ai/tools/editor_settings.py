"""MCP tool for Godot EditorSettings and configuration."""

from __future__ import annotations

from fastmcp import FastMCP

from godot_ai.handlers import editor_settings as editor_settings_handlers
from godot_ai.tools._meta_tool import register_manage_tool

_DESCRIPTION = """\
Editor Settings and Configuration Management.

Ops:
  * get_setting(setting_name)
        Get an editor setting value by its configuration key path.

  * set_setting(setting_name, value)
        Set an editor setting value.

  * list_settings(prefix="")
        List available editor setting key paths matching an optional prefix.

  * get_editor_paths()
        Get standard Godot editor directory paths from EditorPaths.
"""


def register_editor_settings_tools(mcp: FastMCP) -> None:
    register_manage_tool(
        mcp,
        tool_name="editor_settings_manage",
        description=_DESCRIPTION,
        ops={
            "get_setting": editor_settings_handlers.editor_settings_get_setting,
            "set_setting": editor_settings_handlers.editor_settings_set_setting,
            "list_settings": editor_settings_handlers.editor_settings_list_settings,
            "get_editor_paths": editor_settings_handlers.editor_settings_get_editor_paths,
        },
        read_resource_forms={
            "get_setting": None,
            "list_settings": None,
            "get_editor_paths": None,
        },
    )
