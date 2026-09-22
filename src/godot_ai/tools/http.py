"""MCP tool for Godot in-engine HTTP networking and downloads."""

from __future__ import annotations

from fastmcp import FastMCP

from godot_ai.handlers import http as http_handlers
from godot_ai.tools._meta_tool import register_manage_tool

_DESCRIPTION = """\
In-Engine HTTP Requests, File Downloads, and HTTPRequest Scaffolding.

Ops:
  * scaffold_http_request(parent_path="", name="HTTPRequest", timeout=30.0)
        Scaffold an HTTPRequest node into the scene hierarchy.

  * send_request(url, method="GET", headers=[], body="", timeout=10.0)
        Execute an in-engine REST/HTTP request via Godot's networking stack.

  * download_file(url, target_path, timeout=30.0)
        Download a remote file into the project virtual filesystem (res:// or user://).
"""


def register_http_tools(mcp: FastMCP) -> None:
    register_manage_tool(
        mcp,
        tool_name="http_manage",
        description=_DESCRIPTION,
        ops={
            "scaffold_http_request": http_handlers.http_scaffold_http_request,
            "send_request": http_handlers.http_send_request,
            "download_file": http_handlers.http_download_file,
        },
        read_resource_forms={
            "send_request": None,
        },
    )
