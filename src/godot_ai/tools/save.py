"""MCP tool for save and persistence management."""

from __future__ import annotations

from fastmcp import FastMCP

from godot_ai.handlers import save as save_handlers
from godot_ai.tools._meta_tool import register_manage_tool

_DESCRIPTION = """\
Save Game and Persistence Management.

Ops:
  • scaffold_save_system(name="SaveManager", script_path="res://scripts/save_manager.gd",
                          save_directory="user://saves/", register_autoload=True,
                          enable_encryption=False, encryption_password="")
        Scaffold an atomic, corruption-resistant SaveManager singleton that automatically
        orchestrates saving and loading across all nodes in the 'saveable' group,
        with optional password encryption and slot management.

  • save_slot(slot_name="slot_1", data={}, directory="user://saves/")
        Save arbitrary game state data into a designated slot atomically.

  • load_slot(slot_name="slot_1", directory="user://saves/")
        Load state data from a designated slot.

  • list_slots(directory="user://saves/")
        List all saved game slots, timestamps, and metadata.

  • delete_slot(slot_name="slot_1", directory="user://saves/")
        Delete a save game slot.
"""


def register_save_tools(mcp: FastMCP) -> None:
    register_manage_tool(
        mcp,
        tool_name="save_manage",
        description=_DESCRIPTION,
        ops={
            "scaffold_save_system": save_handlers.save_scaffold_save_system,
            "save_slot": save_handlers.save_save_slot,
            "load_slot": save_handlers.save_load_slot,
            "list_slots": save_handlers.save_list_slots,
            "delete_slot": save_handlers.save_delete_slot,
        },
    )
