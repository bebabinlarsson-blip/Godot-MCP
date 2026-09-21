"""Handler functions routing Shader commands to the connected Godot runtime."""

from __future__ import annotations

from typing import Any

from godot_ai.handlers._readiness import require_writable_async
from godot_ai.runtime.direct import DirectRuntime


async def shader_create(
    runtime: DirectRuntime,
    path: str,
    shader_type: str = "canvas_item",
    code: str = "",
    overwrite: bool = False,
) -> dict:
    """Create a new .gdshader file with specified type and template."""
    await require_writable_async(runtime)
    return await runtime.send_command(
        "shader_create",
        {
            "path": path,
            "shader_type": shader_type,
            "code": code,
            "overwrite": overwrite,
        },
        timeout=15.0,
    )


async def shader_apply_preset(
    runtime: DirectRuntime,
    preset: str,
    target_node_path: str = "",
    shader_path: str = "",
    params: dict[str, Any] | None = None,
) -> dict:
    """Generate, compile, and assign a production game shader preset."""
    await require_writable_async(runtime)
    return await runtime.send_command(
        "shader_apply_preset",
        {
            "preset": preset,
            "target_node_path": target_node_path,
            "shader_path": shader_path,
            "params": params or {},
        },
        timeout=15.0,
    )


async def shader_set_param(
    runtime: DirectRuntime,
    param: str,
    value: Any,
    target_node_path: str = "",
    material_path: str = "",
) -> dict:
    """Set a uniform parameter on a ShaderMaterial."""
    await require_writable_async(runtime)
    return await runtime.send_command(
        "shader_set_param",
        {
            "param": param,
            "value": value,
            "target_node_path": target_node_path,
            "material_path": material_path,
        },
        timeout=15.0,
    )


async def shader_get_params(
    runtime: DirectRuntime,
    target_node_path: str = "",
    material_path: str = "",
) -> dict:
    """Get shader metadata and parameter info from a ShaderMaterial."""
    return await runtime.send_command(
        "shader_get_params",
        {
            "target_node_path": target_node_path,
            "material_path": material_path,
        },
        timeout=10.0,
    )
