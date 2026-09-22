"""Handler functions routing Global Illumination and Decal commands to Godot."""

from __future__ import annotations

from typing import Any

from godot_ai.handlers._readiness import require_writable_async
from godot_ai.runtime.direct import DirectRuntime


async def gi_create_decal(
    runtime: DirectRuntime,
    parent_path: str = "",
    name: str = "Decal",
    size: list[float] | None = None,
    texture_albedo: str = "",
) -> dict[str, Any]:
    """Create a Decal node under parent."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "parent_path": parent_path,
        "name": name,
        "size": size or [2.0, 2.0, 2.0],
        "texture_albedo": texture_albedo,
    }
    return await runtime.send_command("gi_create_decal", params, timeout=10.0)


async def gi_configure_decal(
    runtime: DirectRuntime,
    node_path: str = "",
    size: list[float] | None = None,
    texture_albedo: str | None = None,
    texture_normal: str | None = None,
    texture_orm: str | None = None,
    emission_energy: float | None = None,
    upper_fade: float | None = None,
    lower_fade: float | None = None,
) -> dict[str, Any]:
    """Configure properties of a Decal node."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {"node_path": node_path}
    if size is not None:
        params["size"] = size
    if texture_albedo is not None:
        params["texture_albedo"] = texture_albedo
    if texture_normal is not None:
        params["texture_normal"] = texture_normal
    if texture_orm is not None:
        params["texture_orm"] = texture_orm
    if emission_energy is not None:
        params["emission_energy"] = emission_energy
    if upper_fade is not None:
        params["upper_fade"] = upper_fade
    if lower_fade is not None:
        params["lower_fade"] = lower_fade
    return await runtime.send_command("gi_configure_decal", params, timeout=10.0)


async def gi_create_reflection_probe(
    runtime: DirectRuntime,
    parent_path: str = "",
    name: str = "ReflectionProbe",
    size: list[float] | None = None,
    update_mode: str = "once",
) -> dict[str, Any]:
    """Create a ReflectionProbe node under parent."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "parent_path": parent_path,
        "name": name,
        "size": size or [20.0, 20.0, 20.0],
        "update_mode": update_mode,
    }
    return await runtime.send_command("gi_create_reflection_probe", params, timeout=10.0)


async def gi_create_voxel_gi(
    runtime: DirectRuntime,
    parent_path: str = "",
    name: str = "VoxelGI",
    size: list[float] | None = None,
    subdivide: int = 1,
) -> dict[str, Any]:
    """Create a VoxelGI node under parent."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "parent_path": parent_path,
        "name": name,
        "size": size or [20.0, 20.0, 20.0],
        "subdivide": subdivide,
    }
    return await runtime.send_command("gi_create_voxel_gi", params, timeout=10.0)


async def gi_create_lightmap_gi(
    runtime: DirectRuntime,
    parent_path: str = "",
    name: str = "LightmapGI",
    bounces: int = 3,
) -> dict[str, Any]:
    """Create a LightmapGI node under parent."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "parent_path": parent_path,
        "name": name,
        "bounces": bounces,
    }
    return await runtime.send_command("gi_create_lightmap_gi", params, timeout=10.0)


async def gi_get_gi_info(
    runtime: DirectRuntime,
    node_path: str = "",
) -> dict[str, Any]:
    """Inspect Decal, ReflectionProbe, VoxelGI, or LightmapGI properties."""
    params: dict[str, Any] = {"node_path": node_path}
    return await runtime.send_command("gi_get_gi_info", params, timeout=10.0)
