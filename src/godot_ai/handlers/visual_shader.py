"""Handler functions routing VisualShader commands to Godot runtime."""

from __future__ import annotations

from typing import Any

from godot_ai.handlers._readiness import require_writable_async
from godot_ai.runtime.direct import DirectRuntime


async def visual_shader_create_visual_shader(
    runtime: DirectRuntime,
    shader_type: str = "spatial",
    save_path: str = "",
) -> dict[str, Any]:
    """Create a new VisualShader resource for spatial, canvas_item, particles, etc."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "shader_type": shader_type,
        "save_path": save_path,
    }
    return await runtime.send_command(
        "visual_shader_create_visual_shader", params, timeout=10.0
    )


async def visual_shader_add_node(
    runtime: DirectRuntime,
    shader_path: str,
    node_type: str = "VisualShaderNodeColorConstant",
    shader_type_enum: int = 0,
    position: list[float] | None = None,
) -> dict[str, Any]:
    """Add a VisualShaderNode into the visual shader graph."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "shader_path": shader_path,
        "node_type": node_type,
        "shader_type_enum": shader_type_enum,
        "position": position or [0, 0],
    }
    return await runtime.send_command("visual_shader_add_node", params, timeout=10.0)


async def visual_shader_connect_nodes(
    runtime: DirectRuntime,
    shader_path: str,
    shader_type_enum: int = 0,
    from_node: int = 0,
    from_port: int = 0,
    to_node: int = 0,
    to_port: int = 0,
) -> dict[str, Any]:
    """Connect two node ports in a VisualShader graph."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "shader_path": shader_path,
        "shader_type_enum": shader_type_enum,
        "from_node": from_node,
        "from_port": from_port,
        "to_node": to_node,
        "to_port": to_port,
    }
    return await runtime.send_command("visual_shader_connect_nodes", params, timeout=10.0)


async def visual_shader_get_graph(
    runtime: DirectRuntime,
    shader_path: str,
    shader_type_enum: int = 0,
) -> dict[str, Any]:
    """Inspect all nodes and connections in a VisualShader graph."""
    params: dict[str, Any] = {
        "shader_path": shader_path,
        "shader_type_enum": shader_type_enum,
    }
    return await runtime.send_command("visual_shader_get_graph", params, timeout=10.0)
