"""Handler functions routing physics body commands to Godot runtime."""

from __future__ import annotations

from typing import Any

from godot_ai.handlers._readiness import require_writable_async
from godot_ai.runtime.direct import DirectRuntime


async def body_configure_body(
    runtime: DirectRuntime,
    node_path: str,
    properties: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Configure physics parameters of a body (mass, gravity_scale, damping)."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "node_path": node_path,
        "properties": properties or {},
    }
    return await runtime.send_command("body_configure_body", params, timeout=10.0)


async def body_apply_impulse(
    runtime: DirectRuntime,
    node_path: str,
    impulse: list[float] | None = None,
    position: list[float] | None = None,
) -> dict[str, Any]:
    """Apply an impulse to a 2D or 3D RigidBody."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "node_path": node_path,
        "impulse": impulse or [0.0, 0.0],
        "position": position,
    }
    return await runtime.send_command("body_apply_impulse", params, timeout=10.0)


async def body_set_collision_layer_mask(
    runtime: DirectRuntime,
    node_path: str,
    collision_layer: int | None = None,
    collision_mask: int | None = None,
    collision_priority: float | None = None,
) -> dict[str, Any]:
    """Set collision layers and masks for a 2D or 3D collision object."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {"node_path": node_path}
    if collision_layer is not None:
        params["collision_layer"] = collision_layer
    if collision_mask is not None:
        params["collision_mask"] = collision_mask
    if collision_priority is not None:
        params["collision_priority"] = collision_priority
    return await runtime.send_command("body_set_collision_layer_mask", params, timeout=10.0)


async def body_scaffold_character_body(
    runtime: DirectRuntime,
    parent_path: str = "",
    node_name: str = "Player",
    is_3d: bool = False,
) -> dict[str, Any]:
    """Scaffold a CharacterBody2D or CharacterBody3D with collision shape."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "parent_path": parent_path,
        "node_name": node_name,
        "is_3d": is_3d,
    }
    return await runtime.send_command("body_scaffold_character_body", params, timeout=10.0)


async def body_get_body_info(
    runtime: DirectRuntime,
    node_path: str,
) -> dict[str, Any]:
    """Inspect collision layers, mass, and properties of a physics body."""
    params: dict[str, Any] = {"node_path": node_path}
    return await runtime.send_command("body_get_body_info", params, timeout=10.0)
