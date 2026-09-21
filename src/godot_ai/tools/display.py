"""MCP tool for Godot DisplayServer and Window management."""

from __future__ import annotations

from fastmcp import FastMCP

from godot_ai.handlers import display as display_handlers
from godot_ai.tools._meta_tool import register_manage_tool

_DESCRIPTION = """\
DisplayServer Configuration, Window Controls, and SubWindow Scaffolding.

Ops:
  * set_mode(mode="windowed", borderless=None, always_on_top=None)
        Set window mode (windowed, fullscreen, exclusive_fullscreen, maximized, minimized).

  * get_display_info()
        Read active screen dimensions, window geometry, refresh rate, VSync, and mouse mode.

  * set_window_rect(size=None, position=None)
        Resize and reposition the active window.

  * set_vsync(vsync_mode="enabled")
        Configure VSync (disabled, enabled, adaptive, mailbox).

  * set_mouse_mode(mouse_mode="visible")
        Set mouse capture mode (visible, hidden, captured, confined, confined_hidden).

  * scaffold_subwindow(parent_path="", window_type="Window", name="SubWindow",
                       title="Window", size=[400, 300], transient=true, exclusive=false)
        Scaffold a Window, AcceptDialog, or ConfirmationDialog in the scene.
"""


def register_display_tools(mcp: FastMCP) -> None:
    register_manage_tool(
        mcp,
        tool_name="display_manage",
        description=_DESCRIPTION,
        ops={
            "set_mode": display_handlers.display_set_mode,
            "get_display_info": display_handlers.display_get_display_info,
            "set_window_rect": display_handlers.display_set_window_rect,
            "set_vsync": display_handlers.display_set_vsync,
            "set_mouse_mode": display_handlers.display_set_mouse_mode,
            "scaffold_subwindow": display_handlers.display_scaffold_subwindow,
        },
        read_resource_forms={
            "get_display_info": None,
        },
    )
