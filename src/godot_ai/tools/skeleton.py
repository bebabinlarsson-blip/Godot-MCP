"""MCP tool for Godot Skeleton3D, bone poses, sockets, and ragdolls."""

from __future__ import annotations

from fastmcp import FastMCP

from godot_ai.handlers import skeleton as skeleton_handlers
from godot_ai.tools._meta_tool import register_manage_tool

_DESCRIPTION = """\
Skeleton3D Rigging, Bone Transform Inspection, BoneAttachment3D Sockets, and Ragdolls.

Ops:
  * get_skeleton_info(skeleton_path="")
        Inspect bone hierarchy, rest transforms, and pose transforms.

  * set_bone_pose(skeleton_path, bone_name, position=None, rotation=None, scale=None)
        Set position, rotation, or scale for a specific bone.

  * scaffold_bone_attachment(skeleton_path, bone_name, name="BoneAttachment3D")
        Scaffold a BoneAttachment3D node attached to a designated bone.

  * scaffold_ragdoll(skeleton_path, collision_layer=1, collision_mask=1, total_mass=70.0)
        Generate PhysicalBone3D nodes for all bones in a Skeleton3D.
"""


def register_skeleton_tools(mcp: FastMCP) -> None:
    register_manage_tool(
        mcp,
        tool_name="skeleton_manage",
        description=_DESCRIPTION,
        ops={
            "get_skeleton_info": skeleton_handlers.skeleton_get_skeleton_info,
            "set_bone_pose": skeleton_handlers.skeleton_set_bone_pose,
            "scaffold_bone_attachment": skeleton_handlers.skeleton_scaffold_bone_attachment,
            "scaffold_ragdoll": skeleton_handlers.skeleton_scaffold_ragdoll,
        },
        read_resource_forms={
            "get_skeleton_info": None,
        },
    )
