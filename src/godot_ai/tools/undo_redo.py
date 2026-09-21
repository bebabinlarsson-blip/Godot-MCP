"""MCP tool for EditorUndoRedoManager history introspection and execution."""

from __future__ import annotations

from fastmcp import FastMCP

from godot_ai.handlers import undo_redo as undo_redo_handlers
from godot_ai.tools._meta_tool import register_manage_tool

_DESCRIPTION = """\
Editor Undo/Redo History Introspection and Transaction Execution.

Ops:
  * get_history()
        Query active action name, undo stack depth, and history IDs.

  * undo()
        Execute an undo action in the active editor.

  * redo()
        Execute a redo action in the active editor.
"""


def register_undo_redo_tools(mcp: FastMCP) -> None:
    register_manage_tool(
        mcp,
        tool_name="undo_redo_manage",
        description=_DESCRIPTION,
        ops={
            "get_history": undo_redo_handlers.undo_redo_get_history,
            "undo": undo_redo_handlers.undo_redo_undo,
            "redo": undo_redo_handlers.undo_redo_redo,
        },
        read_resource_forms={
            "get_history": None,
        },
    )
