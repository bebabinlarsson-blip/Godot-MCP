"""Handler functions routing headless CLI and script execution commands to Godot."""

from __future__ import annotations

from typing import Any

from godot_ai.handlers._readiness import require_writable_async
from godot_ai.runtime.direct import DirectRuntime


async def headless_run_script(
    runtime: DirectRuntime,
    script_path: str = "",
    inline_code: str = "",
) -> dict[str, Any]:
    """Execute a GDScript file or inline code snippet in headless mode."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "script_path": script_path,
        "inline_code": inline_code,
    }
    return await runtime.send_command("headless_run_script", params, timeout=30.0)


async def headless_run_headless_scene(
    runtime: DirectRuntime,
    scene_path: str,
    quit_after_frames: int = 60,
) -> dict[str, Any]:
    """Execute a scene headlessly for testing or headless game simulation."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "scene_path": scene_path,
        "quit_after_frames": quit_after_frames,
    }
    return await runtime.send_command("headless_run_headless_scene", params, timeout=30.0)


async def headless_export_project_cli(
    runtime: DirectRuntime,
    preset: str,
    output_path: str,
    is_debug: bool = False,
) -> dict[str, Any]:
    """Trigger a headless project export via Godot CLI preset."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "preset": preset,
        "output_path": output_path,
        "is_debug": is_debug,
    }
    return await runtime.send_command("headless_export_project_cli", params, timeout=60.0)


async def headless_reimport_assets_cli(
    runtime: DirectRuntime,
) -> dict[str, Any]:
    """Reimport modified assets via a headless editor pass."""
    await require_writable_async(runtime)
    return await runtime.send_command("headless_reimport_assets_cli", {}, timeout=30.0)


async def headless_get_engine_info(
    runtime: DirectRuntime,
) -> dict[str, Any]:
    """Inspect Godot engine version, platform, and headless CLI capabilities."""
    return await runtime.send_command("headless_get_engine_info", {}, timeout=10.0)
