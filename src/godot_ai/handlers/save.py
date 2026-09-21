"""Shared handlers for save and persistence management tools."""

from __future__ import annotations

from typing import Any

from godot_ai.handlers._readiness import require_writable_async
from godot_ai.runtime.direct import DirectRuntime


async def save_scaffold_save_system(
    runtime: DirectRuntime,
    name: str = "SaveManager",
    script_path: str = "res://scripts/save_manager.gd",
    save_directory: str = "user://saves/",
    register_autoload: bool = True,
    enable_encryption: bool = False,
    encryption_password: str = "",
) -> dict:
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "name": name,
        "script_path": script_path,
        "save_directory": save_directory,
        "register_autoload": register_autoload,
        "enable_encryption": enable_encryption,
        "encryption_password": encryption_password,
    }
    return await runtime.send_command("save_scaffold_save_system", params)


async def save_save_slot(
    runtime: DirectRuntime,
    slot_name: str = "slot_1",
    data: dict[str, Any] | None = None,
    directory: str = "user://saves/",
) -> dict:
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "slot_name": slot_name,
        "data": data or {},
        "directory": directory,
    }
    return await runtime.send_command("save_save_slot", params)


async def save_load_slot(
    runtime: DirectRuntime,
    slot_name: str = "slot_1",
    directory: str = "user://saves/",
) -> dict:
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "slot_name": slot_name,
        "directory": directory,
    }
    return await runtime.send_command("save_load_slot", params)


async def save_list_slots(
    runtime: DirectRuntime,
    directory: str = "user://saves/",
) -> dict:
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "directory": directory,
    }
    return await runtime.send_command("save_list_slots", params)


async def save_delete_slot(
    runtime: DirectRuntime,
    slot_name: str,
    directory: str = "user://saves/",
) -> dict:
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "slot_name": slot_name,
        "directory": directory,
    }
    return await runtime.send_command("save_delete_slot", params)
