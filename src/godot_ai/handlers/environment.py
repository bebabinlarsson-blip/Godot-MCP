"""Shared handlers for environment tools."""

from __future__ import annotations

from godot_ai.handlers._readiness import require_writable_async
from godot_ai.handlers._target import target_params
from godot_ai.runtime.direct import DirectRuntime


async def environment_create(
    runtime: DirectRuntime,
    path: str = "",
    preset: str = "default",
    properties: dict | None = None,
    sky: bool | dict | None = None,
    resource_path: str = "",
    overwrite: bool = False,
) -> dict:
    await require_writable_async(runtime)
    params: dict = {"preset": preset}
    # environment_create has no `property` param (path targets the whole
    # WorldEnvironment node) — pass "" to the shared helper.
    params.update(target_params(path, "", resource_path, overwrite))
    if properties:
        params["properties"] = properties
    if sky is not None:
        params["sky"] = sky
    return await runtime.send_command("environment_create", params)


async def environment_setup_3d(
    runtime: DirectRuntime,
    preset: str = "daylight",
    parent_path: str = "",
    create_sun: bool = True,
    volumetric_fog: bool = False,
    glow: bool = False,
) -> dict:
    await require_writable_async(runtime)
    params: dict = {
        "preset": preset,
        "parent_path": parent_path,
        "create_sun": create_sun,
        "volumetric_fog": volumetric_fog,
        "glow": glow,
    }
    return await runtime.send_command("environment_setup_3d", params)


async def environment_setup_2d(
    runtime: DirectRuntime,
    preset: str = "dungeon",
    parent_path: str = "",
    add_torch_to: str = "",
    torch_energy: float = 1.2,
    torch_radius: float = 2.0,
    shadows: bool = True,
) -> dict:
    await require_writable_async(runtime)
    params: dict = {
        "preset": preset,
        "parent_path": parent_path,
        "add_torch_to": add_torch_to,
        "torch_energy": torch_energy,
        "torch_radius": torch_radius,
        "shadows": shadows,
    }
    return await runtime.send_command("environment_setup_2d", params)


