"""MCP tool for Godot Viewport, SubViewport, and splitscreen management."""

from __future__ import annotations

from fastmcp import FastMCP

from godot_ai.handlers import viewport as vp_handlers
from godot_ai.tools._meta_tool import register_manage_tool

_DESCRIPTION = """\
Godot Viewport and SubViewport Lifecycle, Splitscreen, and Render Texture Routing.

Ops:
  * create_subviewport(parent_path="", name="SubViewport", size=[512, 512],
                       render_target_update_mode=3, transparent_bg=false,
                       own_world_3d=false, as_container=false)
        Create a SubViewport or SubViewportContainer in the active scene.

  * scaffold_splitscreen(layout="2p_horizontal", is_3d=false, parent_path="")
        Scaffold a multi-player splitscreen layout (2p_horizontal, 2p_vertical, 4p_quad)
        with SubViewports, SubViewportContainers, and independent cameras.

  * wire_render_texture(viewport_path, target_node_path, target_property="")
        Route a SubViewport's ViewportTexture into a Sprite2D, TextureRect, or
        MeshInstance3D material albedo.

  * get_viewport_tree()
        Inspect all Viewports in the active scene, their sizes, update modes,
        and active cameras.

  * set_properties(viewport_path, size=..., transparent_bg=..., render_target_update_mode=...,
                   own_world_3d=..., msaa_2d=..., msaa_3d=..., screen_space_aa=..., use_hdr_2d=...)
        Configure rendering fidelity and options for an existing Viewport.
"""


def register_viewport_tools(mcp: FastMCP) -> None:
    register_manage_tool(
        mcp,
        tool_name="viewport_manage",
        description=_DESCRIPTION,
        ops={
            "create_subviewport": vp_handlers.viewport_create_subviewport,
            "scaffold_splitscreen": vp_handlers.viewport_scaffold_splitscreen,
            "wire_render_texture": vp_handlers.viewport_wire_render_texture,
            "get_viewport_tree": vp_handlers.viewport_get_viewport_tree,
            "set_properties": vp_handlers.viewport_set_properties,
        },
        read_resource_forms={
            "get_viewport_tree": None,
        },
    )
