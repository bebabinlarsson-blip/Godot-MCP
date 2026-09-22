"""Handler functions routing texture and image management commands to Godot runtime."""

from __future__ import annotations

from typing import Any

from godot_ai.handlers._readiness import require_writable_async
from godot_ai.handlers._target import target_params
from godot_ai.runtime.direct import DirectRuntime


async def gradient_texture_create(
    runtime: DirectRuntime,
    stops: list[dict[str, Any]],
    width: int = 256,
    height: int = 1,
    fill: str = "linear",
    path: str = "",
    property: str = "",
    resource_path: str = "",
    overwrite: bool = False,
) -> dict[str, Any]:
    """Create a procedural GradientTexture2D and assign or save."""
    await require_writable_async(runtime)
    params = {"stops": stops, "width": width, "height": height, "fill": fill}
    params.update(target_params(path, property, resource_path, overwrite))
    return await runtime.send_command("gradient_texture_create", params)


async def noise_texture_create(
    runtime: DirectRuntime,
    noise_type: str = "simplex_smooth",
    width: int = 512,
    height: int = 512,
    frequency: float = 0.01,
    seed: int = 0,
    fractal_octaves: int = 0,
    path: str = "",
    property: str = "",
    resource_path: str = "",
    overwrite: bool = False,
) -> dict[str, Any]:
    """Create a procedural NoiseTexture2D and assign or save."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "noise_type": noise_type,
        "width": width,
        "height": height,
        "frequency": frequency,
        "seed": seed,
    }
    if fractal_octaves > 0:
        params["fractal_octaves"] = fractal_octaves
    params.update(target_params(path, property, resource_path, overwrite))
    return await runtime.send_command("noise_texture_create", params)


async def texture_create_image(
    runtime: DirectRuntime,
    width: int = 64,
    height: int = 64,
    use_mipmaps: bool = False,
    format: str = "rgba8",
    fill_color: str | None = None,
    save_path: str = "",
) -> dict[str, Any]:
    """Create a new Image resource and optionally fill color and save to disk."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "width": width,
        "height": height,
        "use_mipmaps": use_mipmaps,
        "format": format,
        "save_path": save_path,
    }
    if fill_color is not None:
        params["fill_color"] = fill_color
    return await runtime.send_command("texture_create_image", params, timeout=10.0)


async def texture_create_atlas(
    runtime: DirectRuntime,
    atlas_path: str,
    region_rect: list[float] | None = None,
    filter_clip: bool = False,
    save_path: str = "",
) -> dict[str, Any]:
    """Create an AtlasTexture referencing a region of an existing texture."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "atlas_path": atlas_path,
        "region_rect": region_rect or [0, 0, 32, 32],
        "filter_clip": filter_clip,
        "save_path": save_path,
    }
    return await runtime.send_command("texture_create_atlas", params, timeout=10.0)


async def texture_get_texture_info(
    runtime: DirectRuntime,
    path: str,
) -> dict[str, Any]:
    """Get metadata for a texture or image resource."""
    params: dict[str, Any] = {"path": path}
    return await runtime.send_command("texture_get_texture_info", params, timeout=10.0)


async def texture_create_curve_texture(
    runtime: DirectRuntime,
    points: list[list[float]] | None = None,
    width: int = 256,
    save_path: str = "",
) -> dict[str, Any]:
    """Create a CurveTexture resource from control points."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "points": points or [[0.0, 0.0], [1.0, 1.0]],
        "width": width,
        "save_path": save_path,
    }
    return await runtime.send_command("texture_create_curve_texture", params, timeout=10.0)
