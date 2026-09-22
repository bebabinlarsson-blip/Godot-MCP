"""Handler functions routing sprite management commands to Godot runtime."""

from __future__ import annotations

from typing import Any

from godot_ai.handlers._readiness import require_writable_async
from godot_ai.runtime.direct import DirectRuntime


async def sprite_create_sprite_frames(
    runtime: DirectRuntime,
    animations: list[dict[str, Any]] | None = None,
    save_path: str = "",
) -> dict[str, Any]:
    """Create a new SpriteFrames resource with named animations."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "animations": animations or [{"name": "default", "fps": 5.0, "loop": True}],
        "save_path": save_path,
    }
    return await runtime.send_command("sprite_create_sprite_frames", params, timeout=10.0)


async def sprite_scaffold_animated_sprite(
    runtime: DirectRuntime,
    parent_path: str = "",
    sprite_type: str = "2d",
    sprite_frames_path: str = "",
    node_name: str = "AnimatedSprite",
) -> dict[str, Any]:
    """Scaffold an AnimatedSprite2D or AnimatedSprite3D in current scene."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "parent_path": parent_path,
        "sprite_type": sprite_type,
        "sprite_frames_path": sprite_frames_path,
        "node_name": node_name,
    }
    return await runtime.send_command(
        "sprite_scaffold_animated_sprite", params, timeout=10.0
    )


async def sprite_scaffold_multimesh(
    runtime: DirectRuntime,
    parent_path: str = "",
    mesh_type: str = "box",
    instance_count: int = 100,
    is_2d: bool = False,
    node_name: str = "MultiMeshInstance",
) -> dict[str, Any]:
    """Scaffold a MultiMeshInstance2D or MultiMeshInstance3D with instances."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "parent_path": parent_path,
        "mesh_type": mesh_type,
        "instance_count": instance_count,
        "is_2d": is_2d,
        "node_name": node_name,
    }
    return await runtime.send_command("sprite_scaffold_multimesh", params, timeout=10.0)


async def sprite_configure_line_2d(
    runtime: DirectRuntime,
    node_path: str,
    points: list[list[float]] | None = None,
    width: float = 10.0,
    default_color: str = "#ffffff",
) -> dict[str, Any]:
    """Configure points and styling of a Line2D node."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "node_path": node_path,
        "points": points or [],
        "width": width,
        "default_color": default_color,
    }
    return await runtime.send_command("sprite_configure_line_2d", params, timeout=10.0)
