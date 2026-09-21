"""Handler functions routing Tween commands to the connected Godot runtime."""

from __future__ import annotations

from typing import Any

from godot_ai.handlers._readiness import require_writable_async
from godot_ai.runtime.direct import DirectRuntime


async def tween_create(
    runtime: DirectRuntime,
    node_path: str = "",
    property: str = "",
    target_value: Any = None,
    duration: float = 0.5,
    trans_type: str = "linear",
    ease_type: str = "in_out",
    delay: float = 0.0,
    relative: bool = False,
) -> dict[str, Any]:
    """Execute a tween interpolating a node property."""
    await require_writable_async(runtime)
    return await runtime.send_command(
        "tween_create",
        {
            "node_path": node_path,
            "property": property,
            "target_value": target_value,
            "duration": duration,
            "trans_type": trans_type,
            "ease_type": ease_type,
            "delay": delay,
            "relative": relative,
        },
        timeout=15.0,
    )


async def tween_preset_animation(
    runtime: DirectRuntime,
    node_path: str = "",
    preset: str = "punch_scale",
    duration: float = 0.3,
    **kwargs: Any,
) -> dict[str, Any]:
    """Execute a procedural game-feel animation recipe on a node."""
    await require_writable_async(runtime)
    payload: dict[str, Any] = {
        "node_path": node_path,
        "preset": preset,
        "duration": duration,
    }
    payload.update(kwargs)
    return await runtime.send_command(
        "tween_preset_animation",
        payload,
        timeout=15.0,
    )


async def tween_generate_code(
    runtime: DirectRuntime,
    target_var: str = "self",
    property: str = "position",
    target_value: str = "Vector2(100, 100)",
    duration: float = 0.5,
    trans_type: str = "linear",
    ease_type: str = "in_out",
    delay: float = 0.0,
    relative: bool = False,
) -> dict[str, Any]:
    """Generate GDScript code for a Tween animation."""
    return await runtime.send_command(
        "tween_generate_code",
        {
            "target_var": target_var,
            "property": property,
            "target_value": target_value,
            "duration": duration,
            "trans_type": trans_type,
            "ease_type": ease_type,
            "delay": delay,
            "relative": relative,
        },
        timeout=10.0,
    )
