"""Handler functions routing Global Shader Parameter commands
to the connected Godot runtime.
"""

from __future__ import annotations

from typing import Any

from godot_ai.handlers._readiness import require_writable_async
from godot_ai.runtime.direct import DirectRuntime


async def shader_global_list_globals(
    runtime: DirectRuntime,
) -> dict[str, Any]:
    """List all global shader parameters defined in RenderingServer."""
    return await runtime.send_command("shader_global_list_globals", {}, timeout=10.0)


async def shader_global_set_global(
    runtime: DirectRuntime,
    name: str,
    value: Any,
) -> dict[str, Any]:
    """Set or update the runtime value of a global shader parameter."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "name": name,
        "value": value,
    }
    return await runtime.send_command("shader_global_set_global", params, timeout=10.0)


async def shader_global_add_global(
    runtime: DirectRuntime,
    name: str,
    type: str = "float",
    value: Any = None,
) -> dict[str, Any]:
    """Add a new global shader parameter definition to ProjectSettings."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "name": name,
        "type": type,
        "value": value,
    }
    return await runtime.send_command("shader_global_add_global", params, timeout=10.0)


async def shader_global_remove_global(
    runtime: DirectRuntime,
    name: str,
) -> dict[str, Any]:
    """Remove a global shader parameter definition from ProjectSettings."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {"name": name}
    return await runtime.send_command("shader_global_remove_global", params, timeout=10.0)
