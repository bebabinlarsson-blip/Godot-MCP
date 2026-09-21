"""Handler functions routing EditorPlugin and Addon commands to the connected Godot runtime."""

from __future__ import annotations

from typing import Any

from godot_ai.handlers._readiness import require_writable_async
from godot_ai.runtime.direct import DirectRuntime


async def plugin_list_plugins(
    runtime: DirectRuntime,
    addons_dir: str = "res://addons",
) -> dict[str, Any]:
    """Scan res://addons and list all installed editor plugins and statuses."""
    params: dict[str, Any] = {"addons_dir": addons_dir}
    return await runtime.send_command("plugin_list_plugins", params, timeout=10.0)


async def plugin_set_plugin_enabled(
    runtime: DirectRuntime,
    plugin_name: str,
    enabled: bool = True,
) -> dict[str, Any]:
    """Enable or disable an editor plugin in ProjectSettings."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "plugin_name": plugin_name,
        "enabled": enabled,
    }
    return await runtime.send_command("plugin_set_plugin_enabled", params, timeout=10.0)


async def plugin_scaffold_plugin(
    runtime: DirectRuntime,
    plugin_id: str = "my_custom_addon",
    plugin_name: str = "My Custom Addon",
    description: str = "A custom Godot EditorPlugin",
    author: str = "Developer",
    version: str = "1.0.0",
    with_dock: bool = True,
) -> dict[str, Any]:
    """Generate complete scaffolding for a new custom EditorPlugin."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "plugin_id": plugin_id,
        "plugin_name": plugin_name,
        "description": description,
        "author": author,
        "version": version,
        "with_dock": with_dock,
    }
    return await runtime.send_command("plugin_scaffold_plugin", params, timeout=10.0)
