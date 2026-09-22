"""MCP tool for Godot VisualShader graph construction and inspection."""

from __future__ import annotations

from fastmcp import FastMCP

from godot_ai.handlers import visual_shader as visual_shader_handlers
from godot_ai.tools._meta_tool import register_manage_tool

_DESCRIPTION = """\
VisualShader Graph Management.

Ops:
  * create_visual_shader(shader_type="spatial", save_path="")
        Create a new VisualShader resource for spatial, canvas_item, particles, etc.

  * add_node(shader_path, node_type="VisualShaderNodeColorConstant",
             shader_type_enum=0, position=[0,0])
        Add a VisualShaderNode into the visual shader graph.

  * connect_nodes(shader_path, shader_type_enum=0, from_node=0, from_port=0,
                  to_node=0, to_port=0)
        Connect two node ports in a VisualShader graph.

  * get_graph(shader_path, shader_type_enum=0)
        Inspect all nodes and connections in a VisualShader graph.
"""


def register_visual_shader_tools(mcp: FastMCP) -> None:
    register_manage_tool(
        mcp,
        tool_name="visual_shader_manage",
        description=_DESCRIPTION,
        ops={
            "create_visual_shader": (
                visual_shader_handlers.visual_shader_create_visual_shader
            ),
            "add_node": visual_shader_handlers.visual_shader_add_node,
            "connect_nodes": visual_shader_handlers.visual_shader_connect_nodes,
            "get_graph": visual_shader_handlers.visual_shader_get_graph,
        },
        read_resource_forms={
            "get_graph": None,
        },
    )
