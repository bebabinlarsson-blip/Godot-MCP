"""MCP tool for Godot AudioServer bus effects management."""

from __future__ import annotations

from fastmcp import FastMCP

from godot_ai.handlers import audio_effect as audio_effect_handlers
from godot_ai.tools._meta_tool import register_manage_tool

_DESCRIPTION = """\
AudioServer DSP Bus Effects Management.

Ops:
  * add_effect_to_bus(bus_name="Master", effect_class="AudioEffectReverb", at_position=-1,
                      properties={})
        Add an AudioEffect to an audio bus at the specified index.

  * configure_effect(bus_name="Master", effect_index=0, enabled=None, properties={})
        Configure parameters and enable state of an audio bus effect.

  * remove_effect(bus_name="Master", effect_index=0)
        Remove an audio effect from a bus by index.

  * list_bus_effects(bus_name="Master")
        List all audio effects assigned to an audio bus.
"""


def register_audio_effect_tools(mcp: FastMCP) -> None:
    register_manage_tool(
        mcp,
        tool_name="audio_effect_manage",
        description=_DESCRIPTION,
        ops={
            "add_effect_to_bus": audio_effect_handlers.audio_effect_add_effect_to_bus,
            "configure_effect": audio_effect_handlers.audio_effect_configure_effect,
            "remove_effect": audio_effect_handlers.audio_effect_remove_effect,
            "list_bus_effects": audio_effect_handlers.audio_effect_list_bus_effects,
        },
        read_resource_forms={
            "list_bus_effects": None,
        },
    )
