"""Handler functions routing input simulation and replay commands to Godot."""

from __future__ import annotations

from typing import Any

from godot_ai.handlers._readiness import require_writable_async
from godot_ai.runtime.direct import DirectRuntime


async def input_event_simulate_action(
    runtime: DirectRuntime,
    action: str,
    pressed: bool = True,
    strength: float = 1.0,
) -> dict[str, Any]:
    """Simulate an input action press or release in the running game or editor."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "action": action,
        "pressed": pressed,
        "strength": strength,
    }
    return await runtime.send_command("input_event_simulate_action", params, timeout=5.0)


async def input_event_simulate_key(
    runtime: DirectRuntime,
    key: str | int,
    pressed: bool = True,
    echo: bool = False,
    shift: bool = False,
    ctrl: bool = False,
    alt: bool = False,
) -> dict[str, Any]:
    """Simulate a keyboard key event."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "key": key,
        "pressed": pressed,
        "echo": echo,
        "shift": shift,
        "ctrl": ctrl,
        "alt": alt,
    }
    return await runtime.send_command("input_event_simulate_key", params, timeout=5.0)


async def input_event_simulate_mouse_button(
    runtime: DirectRuntime,
    button_index: int = 1,
    pressed: bool = True,
    position: list[float] | None = None,
) -> dict[str, Any]:
    """Simulate a mouse button press or release at screen position."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "button_index": button_index,
        "pressed": pressed,
        "position": position or [0.0, 0.0],
    }
    return await runtime.send_command("input_event_simulate_mouse_button", params, timeout=5.0)


async def input_event_simulate_mouse_motion(
    runtime: DirectRuntime,
    position: list[float] | None = None,
    relative: list[float] | None = None,
    velocity: list[float] | None = None,
) -> dict[str, Any]:
    """Simulate a mouse cursor motion event."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "position": position or [0.0, 0.0],
        "relative": relative or [0.0, 0.0],
        "velocity": velocity or [0.0, 0.0],
    }
    return await runtime.send_command("input_event_simulate_mouse_motion", params, timeout=5.0)


async def input_event_replay_macro(
    runtime: DirectRuntime,
    events: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Replay a sequence of recorded input events."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {"events": events or []}
    return await runtime.send_command("input_event_replay_macro", params, timeout=15.0)


async def input_event_get_input_state(
    runtime: DirectRuntime,
    action: str,
) -> dict[str, Any]:
    """Inspect whether an action is pressed and its current strength."""
    params: dict[str, Any] = {"action": action}
    return await runtime.send_command("input_event_get_input_state", params, timeout=5.0)
