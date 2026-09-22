"""Handler functions routing world environment, sky, and fog commands to Godot."""

from __future__ import annotations

from typing import Any

from godot_ai.handlers._readiness import require_writable_async
from godot_ai.runtime.direct import DirectRuntime


async def world_configure_world_environment(
    runtime: DirectRuntime,
    node_path: str = "",
    properties: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Configure properties of WorldEnvironment and its Environment resource."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "node_path": node_path,
        "properties": properties or {},
    }
    return await runtime.send_command("world_configure_world_environment", params, timeout=10.0)


async def world_create_sky_material(
    runtime: DirectRuntime,
    node_path: str = "",
    sky_type: str = "procedural",
    sky_top_color: str = "",
    ground_bottom_color: str = "",
    texture_path: str = "",
) -> dict[str, Any]:
    """Create and assign procedural or panorama sky material to Environment."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "node_path": node_path,
        "sky_type": sky_type,
        "sky_top_color": sky_top_color,
        "ground_bottom_color": ground_bottom_color,
        "texture_path": texture_path,
    }
    return await runtime.send_command("world_create_sky_material", params, timeout=10.0)


async def world_set_volumetric_fog(
    runtime: DirectRuntime,
    node_path: str = "",
    enabled: bool = True,
    density: float | None = None,
    albedo: str | None = None,
    emission: str | None = None,
    anisotropy: float | None = None,
    length: float | None = None,
) -> dict[str, Any]:
    """Enable and configure volumetric fog parameters on Environment."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "node_path": node_path,
        "enabled": enabled,
    }
    if density is not None:
        params["density"] = density
    if albedo is not None:
        params["albedo"] = albedo
    if emission is not None:
        params["emission"] = emission
    if anisotropy is not None:
        params["anisotropy"] = anisotropy
    if length is not None:
        params["length"] = length
    return await runtime.send_command("world_set_volumetric_fog", params, timeout=10.0)


async def world_configure_camera_attributes(
    runtime: DirectRuntime,
    node_path: str = "",
    attribute_type: str = "practical",
    properties: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Configure CameraAttributesPractical or CameraAttributesPhysical."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "node_path": node_path,
        "attribute_type": attribute_type,
        "properties": properties or {},
    }
    return await runtime.send_command("world_configure_camera_attributes", params, timeout=10.0)


async def world_get_world_info(
    runtime: DirectRuntime,
    node_path: str = "",
) -> dict[str, Any]:
    """Inspect active world environment, fog, sky, and post-processing settings."""
    params: dict[str, Any] = {"node_path": node_path}
    return await runtime.send_command("world_get_world_info", params, timeout=10.0)
