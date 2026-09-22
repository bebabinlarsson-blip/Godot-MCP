"""Handler functions routing font management commands to Godot runtime."""

from __future__ import annotations

from typing import Any

from godot_ai.handlers._readiness import require_writable_async
from godot_ai.runtime.direct import DirectRuntime


async def font_create_system_font(
    runtime: DirectRuntime,
    font_names: list[str] | None = None,
    italic: bool = False,
    weight: int = 400,
    save_path: str = "",
) -> dict[str, Any]:
    """Create a SystemFont resource and optionally save to disk."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "font_names": font_names or ["Sans-Serif"],
        "italic": italic,
        "weight": weight,
        "save_path": save_path,
    }
    return await runtime.send_command("font_create_system_font", params, timeout=10.0)


async def font_create_font_variation(
    runtime: DirectRuntime,
    base_font_path: str,
    variation_embolden: float = 0.0,
    save_path: str = "",
) -> dict[str, Any]:
    """Create a FontVariation resource derived from a base font."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "base_font_path": base_font_path,
        "variation_embolden": variation_embolden,
        "save_path": save_path,
    }
    return await runtime.send_command("font_create_font_variation", params, timeout=10.0)


async def font_create_label_settings(
    runtime: DirectRuntime,
    font_path: str = "",
    font_size: int = 16,
    font_color: str = "#ffffff",
    outline_size: int = 0,
    outline_color: str = "#000000",
    shadow_size: int = 0,
    shadow_color: str = "#000000",
    save_path: str = "",
) -> dict[str, Any]:
    """Create a LabelSettings resource with font styling options."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "font_path": font_path,
        "font_size": font_size,
        "font_color": font_color,
        "outline_size": outline_size,
        "outline_color": outline_color,
        "shadow_size": shadow_size,
        "shadow_color": shadow_color,
        "save_path": save_path,
    }
    return await runtime.send_command("font_create_label_settings", params, timeout=10.0)


async def font_get_font_info(
    runtime: DirectRuntime,
    font_path: str,
) -> dict[str, Any]:
    """Inspect metadata and properties of a font resource."""
    params: dict[str, Any] = {"font_path": font_path}
    return await runtime.send_command("font_get_font_info", params, timeout=10.0)
