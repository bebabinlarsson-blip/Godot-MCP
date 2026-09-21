"""Handler functions routing Skeleton3D and rigging commands to the connected Godot runtime."""

from __future__ import annotations

from typing import Any

from godot_ai.handlers._readiness import require_writable_async
from godot_ai.runtime.direct import DirectRuntime


async def skeleton_get_skeleton_info(
    runtime: DirectRuntime,
    skeleton_path: str = "",
) -> dict[str, Any]:
    """Inspect bone hierarchy, rest transforms, and pose transforms."""
    params: dict[str, Any] = {"skeleton_path": skeleton_path}
    return await runtime.send_command("skeleton_get_skeleton_info", params, timeout=10.0)


async def skeleton_set_bone_pose(
    runtime: DirectRuntime,
    skeleton_path: str,
    bone_name: str,
    position: list[float] | None = None,
    rotation: list[float] | None = None,
    scale: list[float] | None = None,
) -> dict[str, Any]:
    """Set position, rotation, or scale for a specific bone."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "skeleton_path": skeleton_path,
        "bone_name": bone_name,
    }
    if position is not None:
        params["position"] = position
    if rotation is not None:
        params["rotation"] = rotation
    if scale is not None:
        params["scale"] = scale
    return await runtime.send_command("skeleton_set_bone_pose", params, timeout=10.0)


async def skeleton_scaffold_bone_attachment(
    runtime: DirectRuntime,
    skeleton_path: str,
    bone_name: str,
    name: str = "BoneAttachment3D",
) -> dict[str, Any]:
    """Scaffold a BoneAttachment3D node attached to a designated bone."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "skeleton_path": skeleton_path,
        "bone_name": bone_name,
        "name": name,
    }
    return await runtime.send_command(
        "skeleton_scaffold_bone_attachment", params, timeout=10.0
    )


async def skeleton_scaffold_ragdoll(
    runtime: DirectRuntime,
    skeleton_path: str,
    collision_layer: int = 1,
    collision_mask: int = 1,
    total_mass: float = 70.0,
) -> dict[str, Any]:
    """Generate PhysicalBone3D nodes for all bones in a Skeleton3D."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "skeleton_path": skeleton_path,
        "collision_layer": collision_layer,
        "collision_mask": collision_mask,
        "total_mass": total_mass,
    }
    return await runtime.send_command("skeleton_scaffold_ragdoll", params, timeout=10.0)
