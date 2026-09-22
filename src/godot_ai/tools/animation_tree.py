"""MCP tool for Godot AnimationTree state machines and blend trees."""

from __future__ import annotations

from fastmcp import FastMCP

from godot_ai.handlers import animation_tree as animation_tree_handlers
from godot_ai.tools._meta_tool import register_manage_tool

_DESCRIPTION = """\
AnimationTree State Machine and Blend Tree Management.

Ops:
  * scaffold_state_machine(parent_path="", anim_player_path="", node_name="AnimationTree")
        Scaffold an AnimationTree with an AnimationNodeStateMachine root.

  * add_state(tree_path, state_name, animation_name="", position=[0,0])
        Add an animation state node into an AnimationNodeStateMachine.

  * add_transition(tree_path, from_state, to_state, auto_advance=False)
        Add a transition between two states in an AnimationNodeStateMachine.

  * scaffold_blend_tree(parent_path="", anim_player_path="", node_name="AnimationTreeBlend")
        Scaffold an AnimationTree with an AnimationNodeBlendTree root.

  * get_tree_info(tree_path)
        Inspect root node configuration and status of an AnimationTree.
"""


def register_animation_tree_tools(mcp: FastMCP) -> None:
    register_manage_tool(
        mcp,
        tool_name="animation_tree_manage",
        description=_DESCRIPTION,
        ops={
            "scaffold_state_machine": (
                animation_tree_handlers.animation_tree_scaffold_state_machine
            ),
            "add_state": animation_tree_handlers.animation_tree_add_state,
            "add_transition": animation_tree_handlers.animation_tree_add_transition,
            "scaffold_blend_tree": (
                animation_tree_handlers.animation_tree_scaffold_blend_tree
            ),
            "get_tree_info": animation_tree_handlers.animation_tree_get_tree_info,
        },
        read_resource_forms={
            "get_tree_info": None,
        },
    )
