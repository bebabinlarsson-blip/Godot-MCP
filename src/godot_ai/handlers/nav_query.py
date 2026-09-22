"""Handler functions routing navigation query commands to Godot runtime."""

from __future__ import annotations

from typing import Any

from godot_ai.handlers._readiness import require_writable_async
from godot_ai.runtime.direct import DirectRuntime


async def nav_query_query_path_2d(
    runtime: DirectRuntime,
    start: list[float] | None = None,
    end: list[float] | None = None,
    optimize: bool = True,
) -> dict[str, Any]:
    """Query 2D navigation path between start and end coordinates."""
    params: dict[str, Any] = {
        "start": start or [0.0, 0.0],
        "end": end or [0.0, 0.0],
        "optimize": optimize,
    }
    return await runtime.send_command("nav_query_query_path_2d", params, timeout=10.0)


async def nav_query_query_path_3d(
    runtime: DirectRuntime,
    start: list[float] | None = None,
    end: list[float] | None = None,
    optimize: bool = True,
) -> dict[str, Any]:
    """Query 3D navigation path between start and end coordinates."""
    params: dict[str, Any] = {
        "start": start or [0.0, 0.0, 0.0],
        "end": end or [0.0, 0.0, 0.0],
        "optimize": optimize,
    }
    return await runtime.send_command("nav_query_query_path_3d", params, timeout=10.0)


async def nav_query_scaffold_nav_link(
    runtime: DirectRuntime,
    parent_path: str = "",
    start_position: list[float] | None = None,
    end_position: list[float] | None = None,
    bidirectional: bool = True,
    is_3d: bool = False,
    node_name: str = "NavLink",
) -> dict[str, Any]:
    """Scaffold a 2D or 3D NavigationLink connecting disjoint navmesh areas."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "parent_path": parent_path,
        "start_position": start_position or ([0.0, 0.0, 0.0] if is_3d else [0.0, 0.0]),
        "end_position": end_position or ([1.0, 0.0, 0.0] if is_3d else [100.0, 0.0]),
        "bidirectional": bidirectional,
        "is_3d": is_3d,
        "node_name": node_name,
    }
    return await runtime.send_command("nav_query_scaffold_nav_link", params, timeout=10.0)


async def nav_query_scaffold_nav_obstacle(
    runtime: DirectRuntime,
    parent_path: str = "",
    radius: float = 32.0,
    is_3d: bool = False,
    node_name: str = "NavObstacle",
) -> dict[str, Any]:
    """Scaffold a 2D or 3D NavigationObstacle for avoidance navigation."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "parent_path": parent_path,
        "radius": radius,
        "is_3d": is_3d,
        "node_name": node_name,
    }
    return await runtime.send_command("nav_query_scaffold_nav_obstacle", params, timeout=10.0)


async def nav_query_get_nav_map_info(
    runtime: DirectRuntime,
    is_3d: bool = False,
) -> dict[str, Any]:
    """Inspect navigation map cell size, margins, and properties."""
    params: dict[str, Any] = {"is_3d": is_3d}
    return await runtime.send_command("nav_query_get_nav_map_info", params, timeout=10.0)
