"""Handler functions routing physics joint commands to Godot runtime."""

from __future__ import annotations

from typing import Any

from godot_ai.handlers._readiness import require_writable_async
from godot_ai.runtime.direct import DirectRuntime


async def joint_scaffold_joint_2d(
    runtime: DirectRuntime,
    parent_path: str = "",
    joint_type: str = "pin",
    node_a_path: str = "",
    node_b_path: str = "",
    node_name: str = "Joint2D",
) -> dict[str, Any]:
    """Scaffold a 2D physics joint (pin, groove, damped_spring)."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "parent_path": parent_path,
        "joint_type": joint_type,
        "node_a_path": node_a_path,
        "node_b_path": node_b_path,
        "node_name": node_name,
    }
    return await runtime.send_command("joint_scaffold_joint_2d", params, timeout=10.0)


async def joint_scaffold_joint_3d(
    runtime: DirectRuntime,
    parent_path: str = "",
    joint_type: str = "pin",
    node_a_path: str = "",
    node_b_path: str = "",
    node_name: str = "Joint3D",
) -> dict[str, Any]:
    """Scaffold a 3D physics joint (pin, hinge, slider, cone_twist, generic_6dof)."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "parent_path": parent_path,
        "joint_type": joint_type,
        "node_a_path": node_a_path,
        "node_b_path": node_b_path,
        "node_name": node_name,
    }
    return await runtime.send_command("joint_scaffold_joint_3d", params, timeout=10.0)


async def joint_configure_joint(
    runtime: DirectRuntime,
    joint_path: str,
    properties: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Configure properties and parameters of a physics joint node."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "joint_path": joint_path,
        "properties": properties or {},
    }
    return await runtime.send_command("joint_configure_joint", params, timeout=10.0)


async def joint_get_joint_info(
    runtime: DirectRuntime,
    joint_path: str,
) -> dict[str, Any]:
    """Inspect connected nodes and properties of a physics joint node."""
    params: dict[str, Any] = {"joint_path": joint_path}
    return await runtime.send_command("joint_get_joint_info", params, timeout=10.0)
