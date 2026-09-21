"""Shared handlers for dialogue system and narrative scaffolding."""

from __future__ import annotations

from typing import Any

from godot_ai.handlers._readiness import require_writable_async
from godot_ai.runtime.direct import DirectRuntime


async def dialogue_scaffold_system(
    runtime: DirectRuntime,
    name: str = "DialogueManager",
    script_path: str = "res://scripts/dialogue_manager.gd",
    scene_path: str = "res://scenes/dialogue_box.tscn",
    register_autoload: bool = True,
    typewriter_speed: float = 0.03,
) -> dict:
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "name": name,
        "script_path": script_path,
        "scene_path": scene_path,
        "register_autoload": register_autoload,
        "typewriter_speed": typewriter_speed,
    }
    return await runtime.send_command("dialogue_scaffold_system", params)


async def dialogue_create(
    runtime: DirectRuntime,
    path: str = "res://dialogues/dialogue.json",
    dialogue_id: str = "intro_conversation",
    nodes: dict[str, Any] | None = None,
    overwrite: bool = False,
) -> dict:
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "path": path,
        "dialogue_id": dialogue_id,
        "nodes": nodes or {},
        "overwrite": overwrite,
    }
    return await runtime.send_command("dialogue_create", params)
