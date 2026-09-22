"""MCP tool for cloud tunnel status and ChatGPT Action metadata."""

from __future__ import annotations

from fastmcp import FastMCP

from godot_ai.handlers import cloud as cloud_handlers
from godot_ai.tools._meta_tool import register_manage_tool

_DESCRIPTION = """\
Cloud Bridge and ChatGPT Tunnel Management.

Ops:
  * get_tunnel_status()
        Check cloud tunnel and REST gateway operational status.

  * get_action_schema_url(host="http://127.0.0.1:8000")
        Get OpenAPI schema URL and setup instructions for ChatGPT Custom GPT.

  * test_cloud_connection()
        Test round-trip responsiveness between Godot editor and gateway.
"""


def register_cloud_tools(mcp: FastMCP) -> None:
    register_manage_tool(
        mcp,
        tool_name="cloud_manage",
        description=_DESCRIPTION,
        ops={
            "get_tunnel_status": cloud_handlers.cloud_get_tunnel_status,
            "get_action_schema_url": cloud_handlers.cloud_get_action_schema_url,
            "test_cloud_connection": cloud_handlers.cloud_test_cloud_connection,
        },
        read_resource_forms={
            "get_tunnel_status": None,
            "get_action_schema_url": None,
            "test_cloud_connection": None,
        },
    )
