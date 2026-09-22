"""Handler functions routing System, OS, Time, and Engine commands
to the connected Godot runtime.
"""

from __future__ import annotations

from typing import Any

from godot_ai.handlers._readiness import require_writable_async
from godot_ai.runtime.direct import DirectRuntime


async def system_get_system_info(
    runtime: DirectRuntime,
) -> dict[str, Any]:
    """Inspect OS name, processor count, device model, video adapter, and locale."""
    return await runtime.send_command("system_get_system_info", {}, timeout=10.0)


async def system_get_time(
    runtime: DirectRuntime,
) -> dict[str, Any]:
    """Query current Unix epoch, ISO 8601 string, timezone offset, and datetime."""
    return await runtime.send_command("system_get_time", {}, timeout=10.0)


async def system_set_time_scale(
    runtime: DirectRuntime,
    time_scale: float = 1.0,
) -> dict[str, Any]:
    """Accelerate or slow down the game engine time scale."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {"time_scale": time_scale}
    return await runtime.send_command("system_set_time_scale", params, timeout=10.0)


async def system_get_clipboard(
    runtime: DirectRuntime,
) -> dict[str, Any]:
    """Retrieve text from the system clipboard."""
    return await runtime.send_command("system_get_clipboard", {}, timeout=10.0)


async def system_set_clipboard(
    runtime: DirectRuntime,
    text: str = "",
) -> dict[str, Any]:
    """Set text into the system clipboard."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {"text": text}
    return await runtime.send_command("system_set_clipboard", params, timeout=10.0)


async def system_get_env(
    runtime: DirectRuntime,
    var_name: str,
) -> dict[str, Any]:
    """Read a process environment variable."""
    params: dict[str, Any] = {"var_name": var_name}
    return await runtime.send_command("system_get_env", params, timeout=10.0)


async def system_set_env(
    runtime: DirectRuntime,
    var_name: str,
    value: str = "",
) -> dict[str, Any]:
    """Set a process environment variable."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "var_name": var_name,
        "value": value,
    }
    return await runtime.send_command("system_set_env", params, timeout=10.0)
