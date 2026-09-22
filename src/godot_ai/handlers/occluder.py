"""Handler functions routing occlusion culling commands to Godot runtime."""

from __future__ import annotations

from typing import Any

from godot_ai.handlers._readiness import require_writable_async
from godot_ai.runtime.direct import DirectRuntime


async def occluder_scaffold_occluder_3d(
    runtime: DirectRuntime,
    parent_path: str = "",
    occluder_type: str = "box",
    size: list[float] | None = None,
    node_name: str = "OccluderInstance3D",
) -> dict[str, Any]:
    """Scaffold a 3D occlusion culling node (box, sphere, quad)."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "parent_path": parent_path,
        "occluder_type": occluder_type,
        "size": size or [1.0, 1.0, 1.0],
        "node_name": node_name,
    }
    return await runtime.send_command(
        "occluder_scaffold_occluder_3d", params, timeout=10.0
    )


async def occluder_scaffold_occluder_2d(
    runtime: DirectRuntime,
    parent_path: str = "",
    polygon_points: list[list[float]] | None = None,
    closed: bool = True,
    node_name: str = "LightOccluder2D",
) -> dict[str, Any]:
    """Scaffold a 2D light/occlusion polygon node in current scene."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "parent_path": parent_path,
        "polygon_points": polygon_points or [[-16, -16], [16, -16], [16, 16], [-16, 16]],
        "closed": closed,
        "node_name": node_name,
    }
    return await runtime.send_command(
        "occluder_scaffold_occluder_2d", params, timeout=10.0
    )


async def occluder_get_occluder_info(
    runtime: DirectRuntime,
    occluder_path: str,
) -> dict[str, Any]:
    """Inspect occluder node and attached occluder resource."""
    params: dict[str, Any] = {"occluder_path": occluder_path}
    return await runtime.send_command("occluder_get_occluder_info", params, timeout=10.0)
