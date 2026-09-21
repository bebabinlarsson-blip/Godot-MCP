"""Handler functions routing ResourceLoader background loading commands to Godot."""

from __future__ import annotations

from typing import Any

from godot_ai.handlers._readiness import require_writable_async
from godot_ai.runtime.direct import DirectRuntime


async def loader_start_load(
    runtime: DirectRuntime,
    path: str,
    type_hint: str = "",
    use_sub_threads: bool = False,
    cache_mode: int = 1,
) -> dict[str, Any]:
    """Start asynchronous background loading for a resource or scene."""
    return await runtime.send_command(
        "loader_start_load",
        {
            "path": path,
            "type_hint": type_hint,
            "use_sub_threads": use_sub_threads,
            "cache_mode": cache_mode,
        },
        timeout=10.0,
    )


async def loader_get_status(
    runtime: DirectRuntime,
    path: str,
) -> dict[str, Any]:
    """Poll progress percentage and status of a threaded background load."""
    return await runtime.send_command(
        "loader_get_status",
        {"path": path},
        timeout=10.0,
    )


async def loader_get_resource(
    runtime: DirectRuntime,
    path: str,
) -> dict[str, Any]:
    """Retrieve metadata of a completed threaded resource."""
    return await runtime.send_command(
        "loader_get_resource",
        {"path": path},
        timeout=10.0,
    )


async def loader_scaffold_loading_screen(
    runtime: DirectRuntime,
    save_path: str = "res://scripts/loading_screen.gd",
) -> dict[str, Any]:
    """Generate a responsive asynchronous loading screen script."""
    await require_writable_async(runtime)
    return await runtime.send_command(
        "loader_scaffold_loading_screen",
        {"save_path": save_path},
        timeout=15.0,
    )
