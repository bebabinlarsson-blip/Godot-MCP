"""Handler functions routing Profiler and Diagnostics commands to the connected Godot runtime."""

from __future__ import annotations

from typing import Any

from godot_ai.runtime.direct import DirectRuntime


async def profiler_get_monitors(
    runtime: DirectRuntime,
) -> dict[str, Any]:
    """Read real-time Godot engine Performance monitors."""
    return await runtime.send_command(
        "profiler_get_monitors",
        {},
        timeout=10.0,
    )


async def profiler_get_memory_info(
    runtime: DirectRuntime,
) -> dict[str, Any]:
    """Read detailed memory allocation metrics and node/resource counts."""
    return await runtime.send_command(
        "profiler_get_memory_info",
        {},
        timeout=10.0,
    )


async def profiler_get_render_info(
    runtime: DirectRuntime,
) -> dict[str, Any]:
    """Read render pipeline metrics including draw calls, primitives, and VRAM."""
    return await runtime.send_command(
        "profiler_get_render_info",
        {},
        timeout=10.0,
    )


async def profiler_get_physics_info(
    runtime: DirectRuntime,
) -> dict[str, Any]:
    """Read 2D and 3D physics server statistics."""
    return await runtime.send_command(
        "profiler_get_physics_info",
        {},
        timeout=10.0,
    )
