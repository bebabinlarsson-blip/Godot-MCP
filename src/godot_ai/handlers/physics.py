"""Handler functions routing Physics commands to the connected Godot runtime."""

from __future__ import annotations

from godot_ai.handlers._readiness import require_writable_async
from godot_ai.runtime.direct import DirectRuntime


async def physics_raycast_2d(
    runtime: DirectRuntime,
    from_pos: list[float] | None = None,
    to_pos: list[float] | None = None,
    collision_mask: int = 4294967295,
    collide_with_bodies: bool = True,
    collide_with_areas: bool = False,
    hit_from_inside: bool = False,
) -> dict:
    """Perform a 2D raycast query directly through the active World2D physics space."""
    return await runtime.send_command(
        "physics_raycast_2d",
        {
            "from_pos": from_pos or [0, 0],
            "to_pos": to_pos or [0, 100],
            "collision_mask": collision_mask,
            "collide_with_bodies": collide_with_bodies,
            "collide_with_areas": collide_with_areas,
            "hit_from_inside": hit_from_inside,
        },
        timeout=10.0,
    )


async def physics_raycast_3d(
    runtime: DirectRuntime,
    from_pos: list[float] | None = None,
    to_pos: list[float] | None = None,
    collision_mask: int = 4294967295,
    collide_with_bodies: bool = True,
    collide_with_areas: bool = False,
    hit_from_inside: bool = False,
) -> dict:
    """Perform a 3D raycast query directly through the active World3D physics space."""
    return await runtime.send_command(
        "physics_raycast_3d",
        {
            "from_pos": from_pos or [0, 10, 0],
            "to_pos": to_pos or [0, -10, 0],
            "collision_mask": collision_mask,
            "collide_with_bodies": collide_with_bodies,
            "collide_with_areas": collide_with_areas,
            "hit_from_inside": hit_from_inside,
        },
        timeout=10.0,
    )


async def physics_query_point_2d(
    runtime: DirectRuntime,
    point: list[float] | None = None,
    collision_mask: int = 4294967295,
    max_results: int = 32,
    collide_with_bodies: bool = True,
    collide_with_areas: bool = False,
) -> dict:
    """Query intersecting colliders at a given 2D world point."""
    return await runtime.send_command(
        "physics_query_point_2d",
        {
            "point": point or [0, 0],
            "collision_mask": collision_mask,
            "max_results": max_results,
            "collide_with_bodies": collide_with_bodies,
            "collide_with_areas": collide_with_areas,
        },
        timeout=10.0,
    )


async def physics_scaffold_sensor(
    runtime: DirectRuntime,
    parent_path: str = "",
    target_position: list[float] | None = None,
    is_2d: bool = True,
    sensor_name: str = "RaySensor",
    collision_mask: int = 1,
    enabled: bool = True,
) -> dict:
    """Scaffold and attach a RayCast2D or RayCast3D sensor to a node."""
    await require_writable_async(runtime)
    return await runtime.send_command(
        "physics_scaffold_sensor",
        {
            "parent_path": parent_path,
            "target_position": target_position,
            "is_2d": is_2d,
            "sensor_name": sensor_name,
            "collision_mask": collision_mask,
            "enabled": enabled,
        },
        timeout=15.0,
    )
