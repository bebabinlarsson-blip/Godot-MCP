"""Handler functions routing Multiplayer commands to the connected Godot runtime."""

from __future__ import annotations

from typing import Any

from godot_ai.handlers._readiness import require_writable_async
from godot_ai.runtime.direct import DirectRuntime


async def multiplayer_scaffold_network_manager(
    runtime: DirectRuntime,
    save_path: str = "res://scripts/network_manager.gd",
    default_port: int = 8910,
    max_clients: int = 32,
    as_autoload: bool = False,
    autoload_name: str = "NetworkManager",
) -> dict[str, Any]:
    """Scaffold a high-level ENetMultiplayerPeer network manager script."""
    await require_writable_async(runtime)
    return await runtime.send_command(
        "multiplayer_scaffold_network_manager",
        {
            "save_path": save_path,
            "default_port": default_port,
            "max_clients": max_clients,
            "as_autoload": as_autoload,
            "autoload_name": autoload_name,
        },
        timeout=15.0,
    )


async def multiplayer_scaffold_spawner(
    runtime: DirectRuntime,
    parent_path: str = "",
    spawner_name: str = "MultiplayerSpawner",
    spawn_path: str = "..",
    spawnable_scenes: list[str] | None = None,
    auto_spawn: bool = True,
) -> dict[str, Any]:
    """Scaffold and attach a MultiplayerSpawner node."""
    await require_writable_async(runtime)
    return await runtime.send_command(
        "multiplayer_scaffold_spawner",
        {
            "parent_path": parent_path,
            "spawner_name": spawner_name,
            "spawn_path": spawn_path,
            "spawnable_scenes": spawnable_scenes or [],
            "auto_spawn": auto_spawn,
        },
        timeout=15.0,
    )


async def multiplayer_scaffold_synchronizer(
    runtime: DirectRuntime,
    parent_path: str = "",
    synchronizer_name: str = "MultiplayerSynchronizer",
    root_path: str = "..",
    properties: list[str | dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Scaffold and attach a MultiplayerSynchronizer with SceneReplicationConfig."""
    await require_writable_async(runtime)
    return await runtime.send_command(
        "multiplayer_scaffold_synchronizer",
        {
            "parent_path": parent_path,
            "synchronizer_name": synchronizer_name,
            "root_path": root_path,
            "properties": properties or [":position", ":rotation"],
        },
        timeout=15.0,
    )


async def multiplayer_get_network_status(
    runtime: DirectRuntime,
) -> dict[str, Any]:
    """Query current runtime MultiplayerAPI status and peer topology."""
    return await runtime.send_command(
        "multiplayer_get_network_status",
        {},
        timeout=10.0,
    )
