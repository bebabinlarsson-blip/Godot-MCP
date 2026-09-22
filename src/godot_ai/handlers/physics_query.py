"""Handler functions routing physics space state query commands to Godot."""

from __future__ import annotations

from typing import Any

from godot_ai.runtime.direct import DirectRuntime


async def physics_query_intersect_ray_3d(
    runtime: DirectRuntime,
    from_pos: list[float] | None = None,
    to_pos: list[float] | None = None,
    collision_mask: int = 0xFFFFFFFF,
    collide_with_bodies: bool = True,
    collide_with_areas: bool = False,
) -> dict[str, Any]:
    """Execute a 3D raycast directly in the active physics space state."""
    params: dict[str, Any] = {
        "from_pos": from_pos or [0.0, 0.0, 0.0],
        "to_pos": to_pos or [0.0, -10.0, 0.0],
        "collision_mask": collision_mask,
        "collide_with_bodies": collide_with_bodies,
        "collide_with_areas": collide_with_areas,
    }
    return await runtime.send_command("physics_query_intersect_ray_3d", params, timeout=5.0)


async def physics_query_intersect_ray_2d(
    runtime: DirectRuntime,
    from_pos: list[float] | None = None,
    to_pos: list[float] | None = None,
    collision_mask: int = 0xFFFFFFFF,
    collide_with_bodies: bool = True,
    collide_with_areas: bool = False,
) -> dict[str, Any]:
    """Execute a 2D raycast directly in the active physics space state."""
    params: dict[str, Any] = {
        "from_pos": from_pos or [0.0, 0.0],
        "to_pos": to_pos or [0.0, 100.0],
        "collision_mask": collision_mask,
        "collide_with_bodies": collide_with_bodies,
        "collide_with_areas": collide_with_areas,
    }
    return await runtime.send_command("physics_query_intersect_ray_2d", params, timeout=5.0)


async def physics_query_intersect_point_3d(
    runtime: DirectRuntime,
    position: list[float] | None = None,
    max_results: int = 32,
    collision_mask: int = 0xFFFFFFFF,
) -> dict[str, Any]:
    """Query 3D colliders overlapping a point in world space."""
    params: dict[str, Any] = {
        "position": position or [0.0, 0.0, 0.0],
        "max_results": max_results,
        "collision_mask": collision_mask,
    }
    return await runtime.send_command("physics_query_intersect_point_3d", params, timeout=5.0)


async def physics_query_intersect_point_2d(
    runtime: DirectRuntime,
    position: list[float] | None = None,
    max_results: int = 32,
    collision_mask: int = 0xFFFFFFFF,
) -> dict[str, Any]:
    """Query 2D colliders overlapping a point in world space."""
    params: dict[str, Any] = {
        "position": position or [0.0, 0.0],
        "max_results": max_results,
        "collision_mask": collision_mask,
    }
    return await runtime.send_command("physics_query_intersect_point_2d", params, timeout=5.0)


async def physics_query_intersect_shape_3d(
    runtime: DirectRuntime,
    shape_type: str = "sphere",
    radius: float = 1.0,
    max_results: int = 32,
) -> dict[str, Any]:
    """Query 3D colliders overlapping a shape in world space."""
    params: dict[str, Any] = {
        "shape_type": shape_type,
        "radius": radius,
        "max_results": max_results,
    }
    return await runtime.send_command("physics_query_intersect_shape_3d", params, timeout=5.0)


async def physics_query_cast_motion_3d(
    runtime: DirectRuntime,
    shape_type: str = "sphere",
    radius: float = 1.0,
    motion: list[float] | None = None,
) -> dict[str, Any]:
    """Simulate motion of a shape to test collision prediction fractions."""
    params: dict[str, Any] = {
        "shape_type": shape_type,
        "radius": radius,
        "motion": motion or [0.0, -1.0, 0.0],
    }
    return await runtime.send_command("physics_query_cast_motion_3d", params, timeout=5.0)
