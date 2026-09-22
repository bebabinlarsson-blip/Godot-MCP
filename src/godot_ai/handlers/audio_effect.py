"""Handler functions routing AudioServer effect commands to Godot runtime."""

from __future__ import annotations

from typing import Any

from godot_ai.handlers._readiness import require_writable_async
from godot_ai.runtime.direct import DirectRuntime


async def audio_effect_add_effect_to_bus(
    runtime: DirectRuntime,
    bus_name: str = "Master",
    effect_class: str = "AudioEffectReverb",
    at_position: int = -1,
    properties: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Add an AudioEffect to an audio bus at the specified index."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "bus_name": bus_name,
        "effect_class": effect_class,
        "at_position": at_position,
        "properties": properties or {},
    }
    return await runtime.send_command("audio_effect_add_effect_to_bus", params, timeout=10.0)


async def audio_effect_configure_effect(
    runtime: DirectRuntime,
    bus_name: str = "Master",
    effect_index: int = 0,
    enabled: bool | None = None,
    properties: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Configure parameters and enable state of an audio bus effect."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "bus_name": bus_name,
        "effect_index": effect_index,
        "properties": properties or {},
    }
    if enabled is not None:
        params["enabled"] = enabled
    return await runtime.send_command("audio_effect_configure_effect", params, timeout=10.0)


async def audio_effect_remove_effect(
    runtime: DirectRuntime,
    bus_name: str = "Master",
    effect_index: int = 0,
) -> dict[str, Any]:
    """Remove an audio effect from a bus by index."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "bus_name": bus_name,
        "effect_index": effect_index,
    }
    return await runtime.send_command("audio_effect_remove_effect", params, timeout=10.0)


async def audio_effect_list_bus_effects(
    runtime: DirectRuntime,
    bus_name: str = "Master",
) -> dict[str, Any]:
    """List all audio effects assigned to an audio bus."""
    params: dict[str, Any] = {"bus_name": bus_name}
    return await runtime.send_command("audio_effect_list_bus_effects", params, timeout=10.0)
