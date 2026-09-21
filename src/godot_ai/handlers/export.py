"""Handler functions routing Project Export commands to Godot."""

from __future__ import annotations

from typing import Any

from godot_ai.handlers._readiness import require_writable_async
from godot_ai.runtime.direct import DirectRuntime


async def export_list_presets(
    runtime: DirectRuntime,
) -> dict[str, Any]:
    """List all export presets configured in export_presets.cfg."""
    return await runtime.send_command("export_list_presets", {}, timeout=10.0)


async def export_get_preset_info(
    runtime: DirectRuntime,
    preset_name: str,
) -> dict[str, Any]:
    """Get detailed configuration and options of an export preset."""
    return await runtime.send_command(
        "export_get_preset_info",
        {"preset_name": preset_name},
        timeout=10.0,
    )


async def export_run_export(
    runtime: DirectRuntime,
    preset_name: str,
    output_path: str = "",
    debug: bool = False,
) -> dict[str, Any]:
    """Run a headless project export for the specified preset."""
    await require_writable_async(runtime)
    return await runtime.send_command(
        "export_run_export",
        {
            "preset_name": preset_name,
            "output_path": output_path,
            "debug": debug,
        },
        timeout=60.0,
    )
