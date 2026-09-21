"""Handler functions routing Path and Curve commands to the connected Godot runtime."""

from __future__ import annotations

from typing import Any

from godot_ai.handlers._readiness import require_writable_async
from godot_ai.runtime.direct import DirectRuntime


async def path_create_curve_2d(
    runtime: DirectRuntime,
    points: list[Any] | None = None,
    closed: bool = False,
    save_path: str = "",
) -> dict[str, Any]:
    """Create a Curve2D resource with Bezier control points."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "points": points or [],
        "closed": closed,
        "save_path": save_path,
    }
    return await runtime.send_command("path_create_curve_2d", params, timeout=10.0)


async def path_create_curve_3d(
    runtime: DirectRuntime,
    points: list[Any] | None = None,
    closed: bool = False,
    save_path: str = "",
) -> dict[str, Any]:
    """Create a Curve3D resource with Bezier control points."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "points": points or [],
        "closed": closed,
        "save_path": save_path,
    }
    return await runtime.send_command("path_create_curve_3d", params, timeout=10.0)


async def path_scaffold_path(
    runtime: DirectRuntime,
    parent_path: str = "",
    type: str = "Path3D",
    name: str = "Path",
    with_follow: bool = True,
    loop: bool = True,
) -> dict[str, Any]:
    """Scaffold a Path2D or Path3D node with an optional PathFollow child."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "parent_path": parent_path,
        "type": type,
        "name": name,
        "with_follow": with_follow,
        "loop": loop,
    }
    return await runtime.send_command("path_scaffold_path", params, timeout=10.0)


async def path_sample_baked_points(
    runtime: DirectRuntime,
    path_node_path: str,
    interval: float = 1.0,
) -> dict[str, Any]:
    """Sample baked positions along a Path2D or Path3D at fixed intervals."""
    params: dict[str, Any] = {
        "path_node_path": path_node_path,
        "interval": interval,
    }
    return await runtime.send_command("path_sample_baked_points", params, timeout=10.0)


async def path_generate_spline(
    runtime: DirectRuntime,
    shape: str = "circle",
    is_3d: bool = True,
    radius: float = 5.0,
    points_count: int = 16,
    save_path: str = "",
) -> dict[str, Any]:
    """Procedurally generate standard spline curves (circle, sine, spiral, rect, s_curve)."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "shape": shape,
        "is_3d": is_3d,
        "radius": radius,
        "points_count": points_count,
        "save_path": save_path,
    }
    return await runtime.send_command("path_generate_spline", params, timeout=10.0)
