"""MCP tool for Godot viewport capture and MovieWriter automation."""

from __future__ import annotations

from fastmcp import FastMCP

from godot_ai.handlers import recording as recording_handlers
from godot_ai.tools._meta_tool import register_manage_tool

_DESCRIPTION = """\
Viewport Capture, Image Export, and MovieWriter Recording Automation.

Ops:
  * capture_viewport(target_path="res://screenshot.png", viewport_path="")
        Capture current frame from a Viewport and save to PNG.

  * configure_movie_writer(movie_file="res://movie.avi", fps=60, quality=0.8)
        Configure MovieWriter settings in ProjectSettings.

  * get_writer_status()
        Check if MovieWriter mode is active and inspect configured output file.
"""


def register_recording_tools(mcp: FastMCP) -> None:
    register_manage_tool(
        mcp,
        tool_name="recording_manage",
        description=_DESCRIPTION,
        ops={
            "capture_viewport": recording_handlers.recording_capture_viewport,
            "configure_movie_writer": recording_handlers.recording_configure_movie_writer,
            "get_writer_status": recording_handlers.recording_get_writer_status,
        },
        read_resource_forms={
            "get_writer_status": None,
        },
    )
