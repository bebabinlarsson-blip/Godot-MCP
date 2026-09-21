"""Handler functions routing Viewport commands to the connected Godot runtime."""

from __future__ import annotations

from typing import Any

from godot_ai.handlers._readiness import require_writable_async
from godot_ai.runtime.direct import DirectRuntime


async def viewport_create_subviewport(
    runtime: DirectRuntime,
    parent_path: str = "",
    name: str = "SubViewport",
    size: list[int] | None = None,
    render_target_update_mode: int = 3,
    transparent_bg: bool = False,
    own_world_3d: bool = False,
    as_container: bool = False,
) -> dict[str, Any]:
    """Create a SubViewport or SubViewportContainer in the active scene."""
    await require_writable_async(runtime)
    return await runtime.send_command(
        "viewport_create_subviewport",
        {
            "parent_path": parent_path,
            "name": name,
            "size": size or [512, 512],
            "render_target_update_mode": render_target_update_mode,
            "transparent_bg": transparent_bg,
            "own_world_3d": own_world_3d,
            "as_container": as_container,
        },
        timeout=15.0,
    )


async def viewport_scaffold_splitscreen(
    runtime: DirectRuntime,
    layout: str = "2p_horizontal",
    is_3d: bool = False,
    parent_path: str = "",
) -> dict[str, Any]:
    """Scaffold a splitscreen layout with independent SubViewports and cameras."""
    await require_writable_async(runtime)
    return await runtime.send_command(
        "viewport_scaffold_splitscreen",
        {
            "layout": layout,
            "is_3d": is_3d,
            "parent_path": parent_path,
        },
        timeout=15.0,
    )


async def viewport_wire_render_texture(
    runtime: DirectRuntime,
    viewport_path: str = "",
    target_node_path: str = "",
    target_property: str = "",
) -> dict[str, Any]:
    """Wire a SubViewport texture to a target node property or material."""
    await require_writable_async(runtime)
    return await runtime.send_command(
        "viewport_wire_render_texture",
        {
            "viewport_path": viewport_path,
            "target_node_path": target_node_path,
            "target_property": target_property,
        },
        timeout=15.0,
    )


async def viewport_get_viewport_tree(
    runtime: DirectRuntime,
) -> dict[str, Any]:
    """Inspect all Viewports in the active scene tree."""
    return await runtime.send_command(
        "viewport_get_viewport_tree",
        {},
        timeout=10.0,
    )


async def viewport_set_properties(
    runtime: DirectRuntime,
    viewport_path: str = "",
    size: list[int] | None = None,
    transparent_bg: bool | None = None,
    render_target_update_mode: int | None = None,
    own_world_3d: bool | None = None,
    msaa_2d: int | None = None,
    msaa_3d: int | None = None,
    screen_space_aa: int | None = None,
    use_hdr_2d: bool | None = None,
) -> dict[str, Any]:
    """Configure rendering and sizing properties of a Viewport."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {"viewport_path": viewport_path}
    if size is not None:
        params["size"] = size
    if transparent_bg is not None:
        params["transparent_bg"] = transparent_bg
    if render_target_update_mode is not None:
        params["render_target_update_mode"] = render_target_update_mode
    if own_world_3d is not None:
        params["own_world_3d"] = own_world_3d
    if msaa_2d is not None:
        params["msaa_2d"] = msaa_2d
    if msaa_3d is not None:
        params["msaa_3d"] = msaa_3d
    if screen_space_aa is not None:
        params["screen_space_aa"] = screen_space_aa
    if use_hdr_2d is not None:
        params["use_hdr_2d"] = use_hdr_2d
    return await runtime.send_command(
        "viewport_set_properties",
        params,
        timeout=15.0,
    )
