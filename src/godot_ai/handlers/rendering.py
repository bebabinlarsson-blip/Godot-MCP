"""Handler functions routing Rendering and WorldEnvironment commands
to the connected Godot runtime.
"""

from __future__ import annotations

from typing import Any

from godot_ai.handlers._readiness import require_writable_async
from godot_ai.runtime.direct import DirectRuntime


async def rendering_scaffold_world_environment(
    runtime: DirectRuntime,
    parent_path: str = "",
    sky_mode: str = "procedural",
    tonemap_mode: str = "aces",
    name: str = "WorldEnvironment",
) -> dict[str, Any]:
    """Scaffold a WorldEnvironment node with sky and tonemapping."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "parent_path": parent_path,
        "sky_mode": sky_mode,
        "tonemap_mode": tonemap_mode,
        "name": name,
    }
    return await runtime.send_command(
        "rendering_scaffold_world_environment", params, timeout=10.0
    )


async def rendering_set_environment_effects(
    runtime: DirectRuntime,
    node_path: str = "",
    glow_enabled: bool | None = None,
    glow_intensity: float | None = None,
    ssr_enabled: bool | None = None,
    ssao_enabled: bool | None = None,
    ssil_enabled: bool | None = None,
    sdfgi_enabled: bool | None = None,
    volumetric_fog_enabled: bool | None = None,
    volumetric_fog_density: float | None = None,
) -> dict[str, Any]:
    """Configure post-processing and volumetric lighting effects."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {"node_path": node_path}
    if glow_enabled is not None:
        params["glow_enabled"] = glow_enabled
    if glow_intensity is not None:
        params["glow_intensity"] = glow_intensity
    if ssr_enabled is not None:
        params["ssr_enabled"] = ssr_enabled
    if ssao_enabled is not None:
        params["ssao_enabled"] = ssao_enabled
    if ssil_enabled is not None:
        params["ssil_enabled"] = ssil_enabled
    if sdfgi_enabled is not None:
        params["sdfgi_enabled"] = sdfgi_enabled
    if volumetric_fog_enabled is not None:
        params["volumetric_fog_enabled"] = volumetric_fog_enabled
    if volumetric_fog_density is not None:
        params["volumetric_fog_density"] = volumetric_fog_density
    return await runtime.send_command(
        "rendering_set_environment_effects", params, timeout=10.0
    )


async def rendering_set_camera_attributes(
    runtime: DirectRuntime,
    camera_path: str,
    attributes_type: str = "practical",
    auto_exposure_enabled: bool | None = None,
    dof_blur_far_enabled: bool | None = None,
    dof_blur_far_distance: float | None = None,
) -> dict[str, Any]:
    """Configure CameraAttributes on a Camera3D node."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "camera_path": camera_path,
        "attributes_type": attributes_type,
    }
    if auto_exposure_enabled is not None:
        params["auto_exposure_enabled"] = auto_exposure_enabled
    if dof_blur_far_enabled is not None:
        params["dof_blur_far_enabled"] = dof_blur_far_enabled
    if dof_blur_far_distance is not None:
        params["dof_blur_far_distance"] = dof_blur_far_distance
    return await runtime.send_command(
        "rendering_set_camera_attributes", params, timeout=10.0
    )


async def rendering_apply_lighting_preset(
    runtime: DirectRuntime,
    preset: str = "outdoor_sunny",
    node_path: str = "",
) -> dict[str, Any]:
    """Apply a visual lighting preset to the environment."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "preset": preset,
        "node_path": node_path,
    }
    return await runtime.send_command(
        "rendering_apply_lighting_preset", params, timeout=10.0
    )


async def rendering_get_environment_info(
    runtime: DirectRuntime,
    node_path: str = "",
) -> dict[str, Any]:
    """Read active environment properties, background mode, and post-processing toggles."""
    params: dict[str, Any] = {"node_path": node_path}
    return await runtime.send_command(
        "rendering_get_environment_info", params, timeout=10.0
    )
