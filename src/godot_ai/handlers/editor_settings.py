"""Handler functions routing EditorSettings commands to Godot runtime."""

from __future__ import annotations

from typing import Any

from godot_ai.handlers._readiness import require_writable_async
from godot_ai.runtime.direct import DirectRuntime


async def editor_settings_get_setting(
    runtime: DirectRuntime,
    setting_name: str,
) -> dict[str, Any]:
    """Get an editor setting value by its configuration key path."""
    params: dict[str, Any] = {"setting_name": setting_name}
    return await runtime.send_command("editor_settings_get_setting", params, timeout=10.0)


async def editor_settings_set_setting(
    runtime: DirectRuntime,
    setting_name: str,
    value: Any,
) -> dict[str, Any]:
    """Set an editor setting value."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "setting_name": setting_name,
        "value": value,
    }
    return await runtime.send_command("editor_settings_set_setting", params, timeout=10.0)


async def editor_settings_list_settings(
    runtime: DirectRuntime,
    prefix: str = "",
) -> dict[str, Any]:
    """List available editor setting key paths matching an optional prefix."""
    params: dict[str, Any] = {"prefix": prefix}
    return await runtime.send_command("editor_settings_list_settings", params, timeout=10.0)


async def editor_settings_get_editor_paths(
    runtime: DirectRuntime,
) -> dict[str, Any]:
    """Get standard Godot editor directory paths from EditorPaths."""
    return await runtime.send_command("editor_settings_get_editor_paths", {}, timeout=10.0)
