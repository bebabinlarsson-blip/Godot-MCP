"""Handler functions routing parallax and canvas layer commands to Godot runtime."""

from __future__ import annotations

from typing import Any

from godot_ai.handlers._readiness import require_writable_async
from godot_ai.runtime.direct import DirectRuntime


async def parallax_scaffold_parallax(
    runtime: DirectRuntime,
    parent_path: str = "",
    scroll_scale: list[float] | None = None,
    repeat_size: list[float] | None = None,
    node_name: str = "Parallax2D",
) -> dict[str, Any]:
    """Scaffold a Parallax2D node for background layer scrolling."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "parent_path": parent_path,
        "scroll_scale": scroll_scale or [1.0, 1.0],
        "repeat_size": repeat_size or [0.0, 0.0],
        "node_name": node_name,
    }
    return await runtime.send_command("parallax_scaffold_parallax", params, timeout=10.0)


async def parallax_scaffold_canvas_layer(
    runtime: DirectRuntime,
    parent_path: str = "",
    layer: int = 1,
    follow_viewport: bool = False,
    node_name: str = "CanvasLayer",
) -> dict[str, Any]:
    """Scaffold a CanvasLayer node in the scene tree."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "parent_path": parent_path,
        "layer": layer,
        "follow_viewport": follow_viewport,
        "node_name": node_name,
    }
    return await runtime.send_command("parallax_scaffold_canvas_layer", params, timeout=10.0)


async def parallax_scaffold_visibility_notifier(
    runtime: DirectRuntime,
    parent_path: str = "",
    is_2d: bool = True,
    rect_size: list[float] | None = None,
    node_name: str = "VisibilityNotifier",
) -> dict[str, Any]:
    """Scaffold a VisibleOnScreenNotifier2D or 3D node."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "parent_path": parent_path,
        "is_2d": is_2d,
        "rect_size": rect_size or [100.0, 100.0],
        "node_name": node_name,
    }
    return await runtime.send_command(
        "parallax_scaffold_visibility_notifier", params, timeout=10.0
    )


async def parallax_get_parallax_info(
    runtime: DirectRuntime,
    node_path: str,
) -> dict[str, Any]:
    """Inspect properties of a parallax or canvas layer node."""
    params: dict[str, Any] = {"node_path": node_path}
    return await runtime.send_command("parallax_get_parallax_info", params, timeout=10.0)
