"""MCP tool for Godot procedural mesh generation and manipulation."""

from __future__ import annotations

from fastmcp import FastMCP

from godot_ai.handlers import mesh as mesh_handlers
from godot_ai.tools._meta_tool import register_manage_tool

_DESCRIPTION = """\
Procedural 3D Mesh Synthesis, MeshDataTool Deformation, and Primitive Generation.

Ops:
  * generate_surface_mesh(primitive_type="TRIANGLES", vertices=None, normals=None,
                          uvs=None, colors=None, indices=None, generate_normals=false,
                          generate_tangents=false, save_path="", attach_to="")
        Generate custom ArrayMesh geometry via SurfaceTool.

  * deform_mesh(mesh_path, mode="displace", axis="y", factor=1.0, save_path="")
        Inspect and deform an existing mesh via MeshDataTool.

  * create_primitive(primitive="BoxMesh", properties=None, save_path="", attach_to="")
        Create a configured PrimitiveMesh resource.

  * get_mesh_info(mesh_path="", node_path="")
        Read mesh class, surface count, and AABB dimensions.
"""


def register_mesh_tools(mcp: FastMCP) -> None:
    register_manage_tool(
        mcp,
        tool_name="mesh_manage",
        description=_DESCRIPTION,
        ops={
            "generate_surface_mesh": mesh_handlers.mesh_generate_surface_mesh,
            "deform_mesh": mesh_handlers.mesh_deform_mesh,
            "create_primitive": mesh_handlers.mesh_create_primitive,
            "get_mesh_info": mesh_handlers.mesh_get_mesh_info,
        },
        read_resource_forms={
            "get_mesh_info": None,
        },
    )
