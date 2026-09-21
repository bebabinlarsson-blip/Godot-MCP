"""MCP tool for dialogue system scaffolding and narrative tree generation."""

from __future__ import annotations

from fastmcp import FastMCP

from godot_ai.handlers import dialogue as dialogue_handlers
from godot_ai.tools._meta_tool import register_manage_tool

_DESCRIPTION = """\
Dialogue and Narrative System Management.

Ops:
  • scaffold_system(name="DialogueManager", script_path="res://scripts/dialogue_manager.gd",
                     scene_path="res://scenes/dialogue_box.tscn", register_autoload=True,
                     typewriter_speed=0.03)
        Scaffold a complete dialogue manager singleton and UI box with typewriter
        animation, BBCode rich text, continue indicator, branching choice buttons,
        and event signals (dialogue_started, line_displayed, choice_selected, dialogue_ended).

  • create_dialogue(path="res://dialogues/dialogue.json", dialogue_id="intro_conversation",
                     nodes={}, overwrite=False)
        Create a structured branching dialogue graph with speakers, text lines,
        choice options, and next-node pointers.
"""


def register_dialogue_tools(mcp: FastMCP) -> None:
    register_manage_tool(
        mcp,
        tool_name="dialogue_manage",
        description=_DESCRIPTION,
        ops={
            "scaffold_system": dialogue_handlers.dialogue_scaffold_system,
            "create_dialogue": dialogue_handlers.dialogue_create,
        },
    )
