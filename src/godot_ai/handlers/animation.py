"""Shared handlers for AnimationPlayer authoring (tracks, keyframes, autoplay)."""

from __future__ import annotations

from typing import Any

from godot_ai.handlers._readiness import require_writable_async
from godot_ai.runtime.direct import DirectRuntime


async def animation_player_create(
    runtime: DirectRuntime,
    parent_path: str,
    name: str = "AnimationPlayer",
) -> dict:
    await require_writable_async(runtime)
    return await runtime.send_command(
        "animation_player_create",
        {"parent_path": parent_path, "name": name},
    )


async def animation_create(
    runtime: DirectRuntime,
    player_path: str,
    name: str,
    length: float,
    loop_mode: str = "none",
    overwrite: bool = False,
) -> dict:
    await require_writable_async(runtime)
    params: dict = {
        "player_path": player_path,
        "name": name,
        "length": length,
        "loop_mode": loop_mode,
    }
    if overwrite:
        params["overwrite"] = True
    return await runtime.send_command("animation_create", params)


async def animation_add_property_track(
    runtime: DirectRuntime,
    player_path: str,
    animation_name: str,
    track_path: str,
    keyframes: list[dict],
    interpolation: str = "linear",
) -> dict:
    await require_writable_async(runtime)
    return await runtime.send_command(
        "animation_add_property_track",
        {
            "player_path": player_path,
            "animation_name": animation_name,
            "track_path": track_path,
            "keyframes": keyframes,
            "interpolation": interpolation,
        },
    )


async def animation_add_method_track(
    runtime: DirectRuntime,
    player_path: str,
    animation_name: str,
    target_node_path: str,
    keyframes: list[dict],
) -> dict:
    await require_writable_async(runtime)
    return await runtime.send_command(
        "animation_add_method_track",
        {
            "player_path": player_path,
            "animation_name": animation_name,
            "target_node_path": target_node_path,
            "keyframes": keyframes,
        },
    )


async def animation_set_autoplay(
    runtime: DirectRuntime,
    player_path: str,
    animation_name: str = "",
) -> dict:
    await require_writable_async(runtime)
    return await runtime.send_command(
        "animation_set_autoplay",
        {"player_path": player_path, "animation_name": animation_name},
    )


async def animation_play(
    runtime: DirectRuntime,
    player_path: str,
    animation_name: str = "",
) -> dict:
    return await runtime.send_command(
        "animation_play",
        {"player_path": player_path, "animation_name": animation_name},
    )


async def animation_stop(
    runtime: DirectRuntime,
    player_path: str,
) -> dict:
    return await runtime.send_command(
        "animation_stop",
        {"player_path": player_path},
    )


async def animation_list(
    runtime: DirectRuntime,
    player_path: str,
) -> dict:
    return await runtime.send_command(
        "animation_list",
        {"player_path": player_path},
    )


async def animation_get(
    runtime: DirectRuntime,
    player_path: str,
    animation_name: str,
) -> dict:
    return await runtime.send_command(
        "animation_get",
        {"player_path": player_path, "animation_name": animation_name},
    )


async def animation_delete(
    runtime: DirectRuntime,
    player_path: str,
    animation_name: str,
) -> dict:
    await require_writable_async(runtime)
    return await runtime.send_command(
        "animation_delete",
        {"player_path": player_path, "animation_name": animation_name},
    )


async def animation_validate(
    runtime: DirectRuntime,
    player_path: str,
    animation_name: str,
) -> dict:
    # Read-only — no require_writable.
    return await runtime.send_command(
        "animation_validate",
        {"player_path": player_path, "animation_name": animation_name},
    )


async def animation_create_simple(
    runtime: DirectRuntime,
    player_path: str,
    name: str,
    tweens: list[dict[str, Any]],
    length: float | None = None,
    loop_mode: str = "none",
    overwrite: bool = False,
) -> dict:
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "player_path": player_path,
        "name": name,
        "tweens": tweens,
        "loop_mode": loop_mode,
    }
    if length is not None:
        params["length"] = length
    if overwrite:
        params["overwrite"] = True
    return await runtime.send_command("animation_create_simple", params)


async def animation_preset_fade(
    runtime: DirectRuntime,
    player_path: str,
    target_path: str,
    mode: str = "in",
    duration: float = 0.5,
    animation_name: str = "",
    overwrite: bool = False,
) -> dict:
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "player_path": player_path,
        "target_path": target_path,
        "mode": mode,
        "duration": duration,
    }
    if animation_name:
        params["animation_name"] = animation_name
    if overwrite:
        params["overwrite"] = True
    return await runtime.send_command("animation_preset_fade", params)


async def animation_preset_slide(
    runtime: DirectRuntime,
    player_path: str,
    target_path: str,
    direction: str = "left",
    mode: str = "in",
    distance: float | None = None,
    duration: float = 0.4,
    animation_name: str = "",
    overwrite: bool = False,
) -> dict:
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "player_path": player_path,
        "target_path": target_path,
        "direction": direction,
        "mode": mode,
        "duration": duration,
    }
    if distance is not None:
        params["distance"] = distance
    if animation_name:
        params["animation_name"] = animation_name
    if overwrite:
        params["overwrite"] = True
    return await runtime.send_command("animation_preset_slide", params)


async def animation_preset_shake(
    runtime: DirectRuntime,
    player_path: str,
    target_path: str,
    intensity: float | None = None,
    duration: float = 0.3,
    frequency: float = 30.0,
    seed: int = 0,
    animation_name: str = "",
    overwrite: bool = False,
) -> dict:
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "player_path": player_path,
        "target_path": target_path,
        "duration": duration,
        "frequency": frequency,
        "seed": seed,
    }
    if intensity is not None:
        params["intensity"] = intensity
    if animation_name:
        params["animation_name"] = animation_name
    if overwrite:
        params["overwrite"] = True
    return await runtime.send_command("animation_preset_shake", params)


async def animation_preset_pulse(
    runtime: DirectRuntime,
    player_path: str,
    target_path: str,
    from_scale: float = 1.0,
    to_scale: float = 1.1,
    duration: float = 0.4,
    animation_name: str = "",
    overwrite: bool = False,
) -> dict:
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "player_path": player_path,
        "target_path": target_path,
        "from_scale": from_scale,
        "to_scale": to_scale,
        "duration": duration,
    }
    if animation_name:
        params["animation_name"] = animation_name
    if overwrite:
        params["overwrite"] = True
    return await runtime.send_command("animation_preset_pulse", params)


async def animation_preset_spin(
    runtime: DirectRuntime,
    player_path: str,
    target_path: str,
    duration: float = 1.0,
    loops: int = 1,
    clockwise: bool = True,
    axis: str = "y",
    animation_name: str = "",
    loop: bool = True,
    overwrite: bool = False,
) -> dict:
    """Spin target node 360 degrees smoothly."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "player_path": player_path,
        "target_path": target_path,
        "duration": duration,
        "loops": loops,
        "clockwise": clockwise,
        "axis": axis,
        "loop": loop,
    }
    if animation_name:
        params["animation_name"] = animation_name
    if overwrite:
        params["overwrite"] = True
    return await runtime.send_command("animation_preset_spin", params)


async def animation_preset_bounce(
    runtime: DirectRuntime,
    player_path: str,
    target_path: str,
    height: float = 40.0,
    duration: float = 0.6,
    animation_name: str = "",
    loop: bool = False,
    overwrite: bool = False,
) -> dict:
    """Make target node hop / bounce vertically."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "player_path": player_path,
        "target_path": target_path,
        "height": height,
        "duration": duration,
        "loop": loop,
    }
    if animation_name:
        params["animation_name"] = animation_name
    if overwrite:
        params["overwrite"] = True
    return await runtime.send_command("animation_preset_bounce", params)


async def animation_create_spritesheet_track(
    runtime: DirectRuntime,
    player_path: str,
    animation_name: str,
    sprite_path: str,
    hframes: int = 1,
    vframes: int = 1,
    start_frame: int = 0,
    frame_count: int = 1,
    fps: float = 10.0,
    loop: bool = True,
) -> dict:
    """Create a discrete keyframe track for Sprite2D frame stepping from a spritesheet."""
    await require_writable_async(runtime)
    return await runtime.send_command(
        "animation_create_spritesheet_track",
        {
            "player_path": player_path,
            "animation_name": animation_name,
            "sprite_path": sprite_path,
            "hframes": hframes,
            "vframes": vframes,
            "start_frame": start_frame,
            "frame_count": frame_count,
            "fps": fps,
            "loop": loop,
        },
    )


async def animation_create_spritesheet_animation(
    runtime: DirectRuntime,
    target: str,
    texture: str,
    animations: dict[str, list[int]],
    hframes: int = 1,
    vframes: int = 1,
    fps: float = 8.0,
    loop: bool = True,
    sprite_name: str = "Sprite2D",
    player_name: str = "AnimationPlayer",
) -> dict:
    """Scaffold complete spritesheet animations on a target node or scene.

    Configures Sprite2D (texture, hframes, vframes, nearest filter) and builds
    discrete keyframe tracks in AnimationPlayer for all animation states in one atomic call.
    """
    await require_writable_async(runtime)
    return await runtime.send_command(
        "create_spritesheet_animation",
        {
            "target": target,
            "texture": texture,
            "animations": animations,
            "hframes": hframes,
            "vframes": vframes,
            "fps": fps,
            "loop": loop,
            "sprite_name": sprite_name,
            "player_name": player_name,
        },
    )


async def animation_create_animated_sprite(
    runtime: DirectRuntime,
    parent_path: str,
    node_name: str = "AnimatedSprite2D",
    texture_path: str = "",
    animation_name: str = "default",
    hframes: int = 1,
    vframes: int = 1,
    start_frame: int = 0,
    frame_count: int = 1,
    fps: float = 10.0,
    loop: bool = True,
    save_frames_path: str = "",
) -> dict:
    """Create an AnimatedSprite2D node and slice frames into a SpriteFrames resource."""
    await require_writable_async(runtime)
    return await runtime.send_command(
        "animation_create_animated_sprite",
        {
            "parent_path": parent_path,
            "node_name": node_name,
            "texture_path": texture_path,
            "animation_name": animation_name,
            "hframes": hframes,
            "vframes": vframes,
            "start_frame": start_frame,
            "frame_count": frame_count,
            "fps": fps,
            "loop": loop,
            "save_frames_path": save_frames_path,
        },
    )


async def animation_scaffold_state_machine(
    runtime: DirectRuntime,
    parent_path: str,
    player_path: str = "",
    name: str = "AnimationTree",
    states: list[str] | None = None,
) -> dict:
    """Scaffold an AnimationTree with an AnimationNodeStateMachine preset."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "parent_path": parent_path,
        "name": name,
        "player_path": player_path,
    }
    if states is not None:
        params["states"] = states
    return await runtime.send_command("animation_scaffold_state_machine", params)


