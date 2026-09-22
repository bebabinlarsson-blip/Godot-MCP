"""MCP tool for Godot ConfigFile, JSON, and Expression utilities."""

from __future__ import annotations

from fastmcp import FastMCP

from godot_ai.handlers import config as config_handlers
from godot_ai.tools._meta_tool import register_manage_tool

_DESCRIPTION = """\
ConfigFile, JSON, and Expression Utilities.

Ops:
  * config_read(file_path, section="", key="")
        Read values or entire sections from an INI ConfigFile.

  * config_write(file_path, section, key, value)
        Write a section and key value into an INI ConfigFile.

  * json_parse(json_string)
        Parse a JSON string into Godot Variant data structure.

  * json_generate(data, indent="")
        Serialize data into a formatted JSON string.

  * expression_eval(expression_string, input_names=[], input_values=[])
        Evaluate a mathematical or logic expression via Godot Expression.
"""


def register_config_tools(mcp: FastMCP) -> None:
    register_manage_tool(
        mcp,
        tool_name="config_manage",
        description=_DESCRIPTION,
        ops={
            "config_read": config_handlers.config_config_read,
            "config_write": config_handlers.config_config_write,
            "json_parse": config_handlers.config_json_parse,
            "json_generate": config_handlers.config_json_generate,
            "expression_eval": config_handlers.config_expression_eval,
        },
        read_resource_forms={
            "config_read": None,
            "json_parse": None,
            "json_generate": None,
            "expression_eval": None,
        },
    )
