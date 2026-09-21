"""Handler functions routing Display and Window commands to the connected Godot runtime."""

from __future__ import annotations

from typing import Any

from godot_ai.handlers._readiness import require_writable_async
from godot_ai.runtime.direct import DirectRuntime


async def display_set_mode(
    runtime: DirectRuntime,
    mode: str = "windowed",
    borderless: bool | None = None,
    always_on_top: bool | None = None,
) -> dict[str, Any]:
    """Set window mode (windowed, fullscreen, exclusive_fullscreen, maximized, minimized)."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {"mode": mode}
    if borderless is not None:
        params["borderless"] = borderless
    if always_on_top is not None:
        params["always_on_top"] = always_on_top
    return await runtime.send_command("display_set_mode", params, timeout=10.0)


async def display_get_display_info(
    runtime: DirectRuntime,
) -> dict[str, Any]:
    """Get active screen resolutions, window geometry, VSync, and mouse mode."""
    return await runtime.send_command("display_get_display_info", {}, timeout=10.0)


async def display_set_window_rect(
    runtime: DirectRuntime,
    size: list[int] | None = None,
    position: list[int] | None = None,
) -> dict[str, Any]:
    """Resize and reposition the active window."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {}
    if size is not None:
        params["size"] = size
    if position is not None:
        params["position"] = position
    return await runtime.send_command("display_set_window_rect", params, timeout=10.0)


async def display_set_vsync(
    runtime: DirectRuntime,
    vsync_mode: str = "enabled",
) -> dict[str, Any]:
    """Configure VSync mode (disabled, enabled, adaptive, mailbox)."""
    await require_writable_async(runtime)
    return await runtime.send_command(
        "display_set_vsync", {"vsync_mode": vsync_mode}, timeout=10.0
    )


async def display_set_mouse_mode(
    runtime: DirectRuntime,
    mouse_mode: str = "visible",
) -> dict[str, Any]:
    """Configure mouse capture mode (visible, hidden, captured, confined)."""
    await require_writable_async(runtime)
    return await runtime.send_command(
        "display_set_mouse_mode", {"mouse_mode": mouse_mode}, timeout=10.0
    )


async def display_scaffold_subwindow(
    runtime: DirectRuntime,
    parent_path: str = "",
    window_type: str = "Window",
    name: str = "SubWindow",
    title: str = "Window",
    size: list[int] | None = None,
    transient: bool = True,
    exclusive: bool = False,
    dialog_text: str = "",
) -> dict[str, Any]:
    """Scaffold a Window or Dialog node in the active scene."""
    await require_writable_async(runtime)
    return await runtime.send_command(
        "display_scaffold_subwindow",
        {
            "parent_path": parent_path,
            "window_type": window_type,
            "name": name,
            "title": title,
            "size": size or [400, 300],
            "transient": transient,
            "exclusive": exclusive,
            "dialog_text": dialog_text,
        },
        timeout=15.0,
    )
