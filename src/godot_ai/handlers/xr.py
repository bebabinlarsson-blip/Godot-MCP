"""Handler functions routing AR/VR OpenXR commands to Godot."""

from __future__ import annotations

from typing import Any

from godot_ai.handlers._readiness import require_writable_async
from godot_ai.runtime.direct import DirectRuntime


async def xr_scaffold_xr_rig(
    runtime: DirectRuntime,
    parent_path: str = "",
    rig_name: str = "XROrigin3D",
) -> dict[str, Any]:
    """Scaffold complete OpenXR player hierarchy (origin, camera, controllers)."""
    await require_writable_async(runtime)
    return await runtime.send_command(
        "xr_scaffold_xr_rig",
        {"parent_path": parent_path, "rig_name": rig_name},
        timeout=15.0,
    )


async def xr_get_xr_status(
    runtime: DirectRuntime,
) -> dict[str, Any]:
    """Query active XRServer interfaces and OpenXR initialization status."""
    return await runtime.send_command("xr_get_xr_status", {}, timeout=10.0)


async def xr_generate_xr_startup_script(
    runtime: DirectRuntime,
    save_path: str = "res://scripts/xr_initializer.gd",
) -> dict[str, Any]:
    """Generate an OpenXR initialization bootstrap script."""
    await require_writable_async(runtime)
    return await runtime.send_command(
        "xr_generate_xr_startup_script",
        {"save_path": save_path},
        timeout=15.0,
    )
