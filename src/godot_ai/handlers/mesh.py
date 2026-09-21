"""Handler functions routing Mesh generation and manipulation commands
to the connected Godot runtime.
"""

from __future__ import annotations

from typing import Any

from godot_ai.handlers._readiness import require_writable_async
from godot_ai.runtime.direct import DirectRuntime


async def mesh_generate_surface_mesh(
    runtime: DirectRuntime,
    primitive_type: str = "TRIANGLES",
    vertices: list[Any] | None = None,
    normals: list[Any] | None = None,
    uvs: list[Any] | None = None,
    colors: list[Any] | None = None,
    indices: list[int] | None = None,
    generate_normals: bool = False,
    generate_tangents: bool = False,
    save_path: str = "",
    attach_to: str = "",
) -> dict[str, Any]:
    """Generate custom ArrayMesh geometry via SurfaceTool."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "primitive_type": primitive_type,
        "vertices": vertices or [],
        "normals": normals or [],
        "uvs": uvs or [],
        "colors": colors or [],
        "indices": indices or [],
        "generate_normals": generate_normals,
        "generate_tangents": generate_tangents,
        "save_path": save_path,
        "attach_to": attach_to,
    }
    return await runtime.send_command("mesh_generate_surface_mesh", params, timeout=10.0)


async def mesh_deform_mesh(
    runtime: DirectRuntime,
    mesh_path: str,
    mode: str = "displace",
    axis: str = "y",
    factor: float = 1.0,
    save_path: str = "",
) -> dict[str, Any]:
    """Inspect and deform an existing mesh via MeshDataTool."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "mesh_path": mesh_path,
        "mode": mode,
        "axis": axis,
        "factor": factor,
        "save_path": save_path,
    }
    return await runtime.send_command("mesh_deform_mesh", params, timeout=10.0)


async def mesh_create_primitive(
    runtime: DirectRuntime,
    primitive: str = "BoxMesh",
    properties: dict[str, Any] | None = None,
    save_path: str = "",
    attach_to: str = "",
) -> dict[str, Any]:
    """Create a configured PrimitiveMesh resource."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "primitive": primitive,
        "properties": properties or {},
        "save_path": save_path,
        "attach_to": attach_to,
    }
    return await runtime.send_command("mesh_create_primitive", params, timeout=10.0)


async def mesh_get_mesh_info(
    runtime: DirectRuntime,
    mesh_path: str = "",
    node_path: str = "",
) -> dict[str, Any]:
    """Read mesh class, surface count, and AABB dimensions."""
    params: dict[str, Any] = {
        "mesh_path": mesh_path,
        "node_path": node_path,
    }
    return await runtime.send_command("mesh_get_mesh_info", params, timeout=10.0)
