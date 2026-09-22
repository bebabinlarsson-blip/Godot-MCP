"""MCP tool for Godot 2D and 3D physics joints."""

from __future__ import annotations

from fastmcp import FastMCP

from godot_ai.handlers import joint as joint_handlers
from godot_ai.tools._meta_tool import register_manage_tool

_DESCRIPTION = """\
Physics Joints Management (2D and 3D).

Ops:
  * scaffold_joint_2d(parent_path="", joint_type="pin", node_a_path="", node_b_path="",
                      node_name="Joint2D")
        Scaffold a 2D physics joint (pin, groove, damped_spring).

  * scaffold_joint_3d(parent_path="", joint_type="pin", node_a_path="", node_b_path="",
                      node_name="Joint3D")
        Scaffold a 3D physics joint (pin, hinge, slider, cone_twist, generic_6dof).

  * configure_joint(joint_path, properties={})
        Configure properties and parameters of a physics joint node.

  * get_joint_info(joint_path)
        Inspect connected nodes and properties of a physics joint node.
"""


def register_joint_tools(mcp: FastMCP) -> None:
    register_manage_tool(
        mcp,
        tool_name="joint_manage",
        description=_DESCRIPTION,
        ops={
            "scaffold_joint_2d": joint_handlers.joint_scaffold_joint_2d,
            "scaffold_joint_3d": joint_handlers.joint_scaffold_joint_3d,
            "configure_joint": joint_handlers.joint_configure_joint,
            "get_joint_info": joint_handlers.joint_get_joint_info,
        },
        read_resource_forms={
            "get_joint_info": None,
        },
    )
