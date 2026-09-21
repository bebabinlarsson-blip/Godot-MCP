"""Shared handlers for character controller scaffolding tools."""

from __future__ import annotations

from typing import Any

from godot_ai.handlers._readiness import require_writable_async
from godot_ai.runtime.direct import DirectRuntime


async def character_scaffold_2d(
    runtime: DirectRuntime,
    parent_path: str = "",
    name: str = "Player",
    genre: str = "platformer",
    speed: float = 200.0,
    jump_velocity: float = -350.0,
    acceleration: float = 1200.0,
    friction: float = 1000.0,
    coyote_time: float = 0.12,
    jump_buffering: float = 0.1,
    attach_camera: bool = True,
    script_path: str = "",
) -> dict:
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "parent_path": parent_path,
        "name": name,
        "genre": genre,
        "speed": speed,
        "jump_velocity": jump_velocity,
        "acceleration": acceleration,
        "friction": friction,
        "coyote_time": coyote_time,
        "jump_buffering": jump_buffering,
        "attach_camera": attach_camera,
        "script_path": script_path,
    }
    return await runtime.send_command("character_scaffold_2d", params)


async def character_scaffold_3d(
    runtime: DirectRuntime,
    parent_path: str = "",
    name: str = "Player3D",
    genre: str = "first_person",
    speed: float = 5.0,
    sprint_speed: float = 8.0,
    jump_velocity: float = 4.5,
    mouse_sensitivity: float = 0.002,
    script_path: str = "",
) -> dict:
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "parent_path": parent_path,
        "name": name,
        "genre": genre,
        "speed": speed,
        "sprint_speed": sprint_speed,
        "jump_velocity": jump_velocity,
        "mouse_sensitivity": mouse_sensitivity,
        "script_path": script_path,
    }
    return await runtime.send_command("character_scaffold_3d", params)
