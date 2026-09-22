"""Handler functions routing Light, Shadow, Decal, and Probe commands
to the connected Godot runtime.
"""

from __future__ import annotations

from typing import Any

from godot_ai.handlers._readiness import require_writable_async
from godot_ai.runtime.direct import DirectRuntime


async def light_scaffold_light_3d(
    runtime: DirectRuntime,
    type: str = "DirectionalLight3D",
    parent_path: str = "",
    name: str = "Light3D",
    color: list[float] | None = None,
    energy: float = 1.0,
    shadows: bool = True,
    range: float = 5.0,
    attenuation: float = 1.0,
    spot_angle: float = 45.0,
) -> dict[str, Any]:
    """Scaffold a DirectionalLight3D, OmniLight3D, or SpotLight3D node."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "type": type,
        "parent_path": parent_path,
        "name": name,
        "energy": energy,
        "shadows": shadows,
        "range": range,
        "attenuation": attenuation,
        "spot_angle": spot_angle,
    }
    if color is not None:
        params["color"] = color
    return await runtime.send_command("light_scaffold_light_3d", params, timeout=10.0)


async def light_scaffold_light_2d(
    runtime: DirectRuntime,
    type: str = "PointLight2D",
    parent_path: str = "",
    name: str = "Light2D",
    color: list[float] | None = None,
    energy: float = 1.0,
    shadows: bool = False,
) -> dict[str, Any]:
    """Scaffold a PointLight2D or DirectionalLight2D node."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "type": type,
        "parent_path": parent_path,
        "name": name,
        "energy": energy,
        "shadows": shadows,
    }
    if color is not None:
        params["color"] = color
    return await runtime.send_command("light_scaffold_light_2d", params, timeout=10.0)


async def light_scaffold_decal(
    runtime: DirectRuntime,
    parent_path: str = "",
    name: str = "Decal",
    size: list[float] | None = None,
    texture_albedo: str = "",
) -> dict[str, Any]:
    """Scaffold a Decal node with projection size and albedo texture."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "parent_path": parent_path,
        "name": name,
        "size": size or [2.0, 2.0, 2.0],
        "texture_albedo": texture_albedo,
    }
    return await runtime.send_command("light_scaffold_decal", params, timeout=10.0)


async def light_scaffold_probe(
    runtime: DirectRuntime,
    type: str = "ReflectionProbe",
    parent_path: str = "",
    name: str = "Probe",
    size: list[float] | None = None,
) -> dict[str, Any]:
    """Scaffold a ReflectionProbe, LightmapGI, or VoxelGI node."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "type": type,
        "parent_path": parent_path,
        "name": name,
        "size": size or [20.0, 20.0, 20.0],
    }
    return await runtime.send_command("light_scaffold_probe", params, timeout=10.0)


async def light_set_light_properties(
    runtime: DirectRuntime,
    light_path: str,
    color: list[float] | None = None,
    energy: float | None = None,
    shadows: bool | None = None,
    volumetric_fog_energy: float | None = None,
) -> dict[str, Any]:
    """Adjust color, energy, shadow, and fog parameters on a light node."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {"light_path": light_path}
    if color is not None:
        params["color"] = color
    if energy is not None:
        params["energy"] = energy
    if shadows is not None:
        params["shadows"] = shadows
    if volumetric_fog_energy is not None:
        params["volumetric_fog_energy"] = volumetric_fog_energy
    return await runtime.send_command("light_set_light_properties", params, timeout=10.0)


async def light_get_light_info(
    runtime: DirectRuntime,
    light_path: str,
) -> dict[str, Any]:
    """Inspect lighting and shadow properties of a 2D or 3D light node."""
    params: dict[str, Any] = {"light_path": light_path}
    return await runtime.send_command("light_get_light_info", params, timeout=10.0)
