"""MCP tool for Godot input simulation, macro replay, and virtual controller."""

from __future__ import annotations

from fastmcp import FastMCP

from godot_ai.handlers import input_event as input_event_handlers
from godot_ai.tools._meta_tool import register_manage_tool

_DESCRIPTION = """\
Input Event Simulation, Macro Replay, and Virtual Actions.

Ops:
  * simulate_action(action, pressed=True, strength=1.0)
        Simulate an input action press or release in the running game or editor.

  * simulate_key(key, pressed=True, echo=False, shift=False, ctrl=False, alt=False)
        Simulate a keyboard key event (e.g. 'W', 'Space', 'Escape', or keycode).

  * simulate_mouse_button(button_index=1, pressed=True, position=[0.0, 0.0])
        Simulate a mouse button press or release at coordinates (1=Left, 2=Right, 3=Middle).

  * simulate_mouse_motion(position=[0.0, 0.0], relative=[0.0, 0.0], velocity=[0.0, 0.0])
        Simulate a mouse cursor motion event.

  * replay_macro(events=[])
        Replay a sequential list of input events for automated gameplay testing.

  * get_input_state(action)
        Inspect whether an input action is pressed and its current strength.
"""


def register_input_event_tools(mcp: FastMCP) -> None:
    register_manage_tool(
        mcp,
        tool_name="input_event_manage",
        description=_DESCRIPTION,
        ops={
            "simulate_action": input_event_handlers.input_event_simulate_action,
            "simulate_key": input_event_handlers.input_event_simulate_key,
            "simulate_mouse_button": input_event_handlers.input_event_simulate_mouse_button,
            "simulate_mouse_motion": input_event_handlers.input_event_simulate_mouse_motion,
            "replay_macro": input_event_handlers.input_event_replay_macro,
            "get_input_state": input_event_handlers.input_event_get_input_state,
        },
        read_resource_forms={
            "get_input_state": None,
        },
    )
