"""Shared handlers for 2D and 3D navigation and pathfinding tools."""

from __future__ import annotations

from typing import Any

from godot_ai.handlers._readiness import require_writable_async
from godot_ai.runtime.direct import DirectRuntime


async def navigation_setup_region_2d(
    runtime: DirectRuntime,
    parent_path: str = "",
    name: str = "NavigationRegion2D",
    polygon: list[list[float]] | None = None,
    cell_size: float = 1.0,
    agent_radius: float = 10.0,
    parsed_geometry_type: str = "mesh_instances_and_colliders",
) -> dict:
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "parent_path": parent_path,
        "name": name,
        "cell_size": cell_size,
        "agent_radius": agent_radius,
        "parsed_geometry_type": parsed_geometry_type,
    }
    if polygon is not None:
        params["polygon"] = polygon
    return await runtime.send_command("navigation_setup_region_2d", params)


async def navigation_attach_agent_2d(
    runtime: DirectRuntime,
    node_path: str,
    agent_name: str = "NavigationAgent2D",
    radius: float = 16.0,
    max_speed: float = 150.0,
    path_desired_distance: float = 20.0,
    target_desired_distance: float = 20.0,
    avoidance_enabled: bool = True,
) -> dict:
    await require_writable_async(runtime)
    return await runtime.send_command(
        "navigation_attach_agent_2d",
        {
            "node_path": node_path,
            "agent_name": agent_name,
            "radius": radius,
            "max_speed": max_speed,
            "path_desired_distance": path_desired_distance,
            "target_desired_distance": target_desired_distance,
            "avoidance_enabled": avoidance_enabled,
        },
    )


async def navigation_bake_2d(
    runtime: DirectRuntime,
    region_path: str,
    on_thread: bool = False,
) -> dict:
    await require_writable_async(runtime)
    return await runtime.send_command(
        "navigation_bake_2d",
        {"region_path": region_path, "on_thread": on_thread},
        timeout=30.0,
    )


async def navigation_setup_region_3d(
    runtime: DirectRuntime,
    parent_path: str = "",
    name: str = "NavigationRegion3D",
    cell_size: float = 0.25,
    cell_height: float = 0.25,
    agent_radius: float = 0.5,
    agent_height: float = 1.8,
) -> dict:
    await require_writable_async(runtime)
    return await runtime.send_command(
        "navigation_setup_region_3d",
        {
            "parent_path": parent_path,
            "name": name,
            "cell_size": cell_size,
            "cell_height": cell_height,
            "agent_radius": agent_radius,
            "agent_height": agent_height,
        },
    )


async def navigation_attach_agent_3d(
    runtime: DirectRuntime,
    node_path: str,
    agent_name: str = "NavigationAgent3D",
    radius: float = 0.5,
    height: float = 1.8,
    max_speed: float = 5.0,
    path_desired_distance: float = 1.0,
    target_desired_distance: float = 1.0,
    avoidance_enabled: bool = True,
) -> dict:
    await require_writable_async(runtime)
    return await runtime.send_command(
        "navigation_attach_agent_3d",
        {
            "node_path": node_path,
            "agent_name": agent_name,
            "radius": radius,
            "height": height,
            "max_speed": max_speed,
            "path_desired_distance": path_desired_distance,
            "target_desired_distance": target_desired_distance,
            "avoidance_enabled": avoidance_enabled,
        },
    )


async def navigation_bake_3d(
    runtime: DirectRuntime,
    region_path: str,
    on_thread: bool = False,
) -> dict:
    await require_writable_async(runtime)
    return await runtime.send_command(
        "navigation_bake_3d",
        {"region_path": region_path, "on_thread": on_thread},
        timeout=30.0,
    )
