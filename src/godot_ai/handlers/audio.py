"""Shared handlers for AudioStreamPlayer authoring — streams, playback, preview."""

from __future__ import annotations

from typing import Any

from godot_ai.handlers._readiness import require_writable_async
from godot_ai.runtime.direct import DirectRuntime


async def audio_player_create(
    runtime: DirectRuntime,
    parent_path: str,
    name: str = "AudioStreamPlayer",
    type: str = "1d",
) -> dict:
    await require_writable_async(runtime)
    return await runtime.send_command(
        "audio_player_create",
        {"parent_path": parent_path, "name": name, "type": type},
    )


async def audio_player_set_stream(
    runtime: DirectRuntime,
    player_path: str,
    stream_path: str,
) -> dict:
    await require_writable_async(runtime)
    return await runtime.send_command(
        "audio_player_set_stream",
        {"player_path": player_path, "stream_path": stream_path},
    )


async def audio_player_set_playback(
    runtime: DirectRuntime,
    player_path: str,
    volume_db: float | None = None,
    pitch_scale: float | None = None,
    autoplay: bool | None = None,
    bus: str | None = None,
) -> dict:
    await require_writable_async(runtime)
    params: dict[str, Any] = {"player_path": player_path}
    if volume_db is not None:
        params["volume_db"] = volume_db
    if pitch_scale is not None:
        params["pitch_scale"] = pitch_scale
    if autoplay is not None:
        params["autoplay"] = autoplay
    if bus is not None:
        params["bus"] = bus
    return await runtime.send_command("audio_player_set_playback", params)


async def audio_play(
    runtime: DirectRuntime,
    player_path: str,
    from_position: float = 0.0,
) -> dict:
    return await runtime.send_command(
        "audio_play",
        {"player_path": player_path, "from_position": from_position},
    )


async def audio_stop(runtime: DirectRuntime, player_path: str) -> dict:
    return await runtime.send_command("audio_stop", {"player_path": player_path})


async def audio_list(
    runtime: DirectRuntime,
    root: str = "res://",
    include_duration: bool = True,
) -> dict:
    return await runtime.send_command(
        "audio_list",
        {"root": root, "include_duration": include_duration},
    )


async def audio_generate_procedural_sfx(
    runtime: DirectRuntime,
    preset: str = "jump",
    dest_path: str = "",
    duration: float = 0.0,
    sample_rate: int = 22050,
) -> dict:
    """Synthesize a procedural retro/chiptune sound effect directly to a .wav file."""
    await require_writable_async(runtime)
    return await runtime.send_command(
        "audio_generate_procedural_sfx",
        {
            "preset": preset,
            "dest_path": dest_path,
            "duration": duration,
            "sample_rate": sample_rate,
        },
    )


async def audio_scaffold_buses(
    runtime: DirectRuntime,
    volumes: dict[str, float] | None = None,
) -> dict:
    """Configure standard Master, Music, SFX, and UI audio buses in AudioServer."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {}
    if volumes is not None:
        params["volumes"] = volumes
    return await runtime.send_command("audio_scaffold_buses", params)


async def audio_scaffold_music_player(
    runtime: DirectRuntime,
    parent_path: str = "",
    name: str = "MusicPlayer",
    stream_path: str = "",
    autoplay: bool = True,
    volume_db: float = 0.0,
    bus: str = "Music",
    loop: bool = True,
) -> dict:
    """Scaffold a background music player AudioStreamPlayer routed to Music bus."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "parent_path": parent_path,
        "name": name,
        "stream_path": stream_path,
        "autoplay": autoplay,
        "volume_db": volume_db,
        "bus": bus,
        "loop": loop,
    }
    return await runtime.send_command("audio_scaffold_music_player", params)


async def audio_scaffold_sound_manager(
    runtime: DirectRuntime,
    name: str = "SoundManager",
    script_path: str = "res://scripts/sound_manager.gd",
    pool_size: int = 16,
    bus: str = "SFX",
    register_autoload: bool = True,
) -> dict:
    """Scaffold a multi-channel sound effect manager singleton with pooling."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "name": name,
        "script_path": script_path,
        "pool_size": pool_size,
        "bus": bus,
        "register_autoload": register_autoload,
    }
    return await runtime.send_command("audio_scaffold_sound_manager", params)


async def audio_bus_list(
    runtime: DirectRuntime,
) -> dict:
    """List all audio buses and their configured effects in AudioServer."""
    return await runtime.send_command("audio_bus_list", {}, timeout=10.0)


async def audio_bus_add(
    runtime: DirectRuntime,
    name: str = "",
    send: str = "Master",
    volume_db: float = 0.0,
    at_pos: int = -1,
) -> dict:
    """Add a new audio bus to AudioServer."""
    await require_writable_async(runtime)
    return await runtime.send_command(
        "audio_bus_add",
        {"name": name, "send": send, "volume_db": volume_db, "at_pos": at_pos},
        timeout=10.0,
    )


async def audio_bus_remove(
    runtime: DirectRuntime,
    bus: str | int = "",
) -> dict:
    """Remove an audio bus from AudioServer by name or index."""
    await require_writable_async(runtime)
    return await runtime.send_command("audio_bus_remove", {"bus": bus}, timeout=10.0)


async def audio_bus_set_properties(
    runtime: DirectRuntime,
    bus: str | int = "",
    volume_db: float | None = None,
    send: str | None = None,
    solo: bool | None = None,
    mute: bool | None = None,
    bypass_effects: bool | None = None,
) -> dict:
    """Update properties on an audio bus in AudioServer."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {"bus": bus}
    if volume_db is not None:
        params["volume_db"] = volume_db
    if send is not None:
        params["send"] = send
    if solo is not None:
        params["solo"] = solo
    if mute is not None:
        params["mute"] = mute
    if bypass_effects is not None:
        params["bypass_effects"] = bypass_effects
    return await runtime.send_command("audio_bus_set_properties", params, timeout=10.0)


async def audio_bus_add_effect(
    runtime: DirectRuntime,
    bus: str | int = "Master",
    effect_type: str = "reverb",
    params: dict | None = None,
    at_pos: int = -1,
) -> dict:
    """Instantiate and attach a DSP effect to an audio bus."""
    await require_writable_async(runtime)
    return await runtime.send_command(
        "audio_bus_add_effect",
        {
            "bus": bus,
            "effect_type": effect_type,
            "params": params or {},
            "at_pos": at_pos,
        },
        timeout=10.0,
    )


async def audio_bus_save_layout(
    runtime: DirectRuntime,
    path: str = "res://default_bus_layout.tres",
) -> dict:
    """Save active AudioServer bus layout to a .tres resource."""
    await require_writable_async(runtime)
    return await runtime.send_command("audio_bus_save_layout", {"path": path}, timeout=10.0)
