"""MCP tool for Finite State Machine (FSM) scaffolding."""

from __future__ import annotations

from fastmcp import FastMCP

from godot_ai.handlers import fsm as fsm_handlers
from godot_ai.tools._meta_tool import register_manage_tool

_DESCRIPTION = """\
Finite State Machine (FSM) Management.

Ops:
  • scaffold_fsm(target_node_path="", name="StateMachine", script_dir="res://scripts/fsm/",
                  preset="enemy_ai", custom_states=[], initial_state="")
        Scaffold a modular node-based finite state machine architecture with base
        State class and StateMachine controller.
        Presets:
          - 'enemy_ai': Idle, Patrol, Chase, Attack, Hurt, Dead states.
          - 'character': Idle, Move, Jump, Fall states.
          - 'custom': Generates scripts for names listed in custom_states.
        If target_node_path is specified, attaches the StateMachine and child State
        nodes directly to the target node in the active scene.
"""


def register_fsm_tools(mcp: FastMCP) -> None:
    register_manage_tool(
        mcp,
        tool_name="fsm_manage",
        description=_DESCRIPTION,
        ops={
            "scaffold_fsm": fsm_handlers.fsm_scaffold_fsm,
        },
    )
