"""Handler functions routing curve and gradient commands to Godot."""

from __future__ import annotations

from typing import Any

from godot_ai.handlers._readiness import require_writable_async
from godot_ai.handlers._target import target_params
from godot_ai.runtime.direct import DirectRuntime


async def curve_set_points(
    runtime: DirectRuntime,
    points: list,
    path: str = "",
    property: str = "",
    resource_path: str = "",
) -> dict:
    """Legacy handler for setting points on an existing Curve resource."""
    await require_writable_async(runtime)
    params: dict = {"points": points}
    params.update(target_params(path, property, resource_path, False))
    return await runtime.send_command("curve_set_points", params)


async def curve_create_curve_1d(
    runtime: DirectRuntime,
    points: list[list[float]] | None = None,
    min_value: float = 0.0,
    max_value: float = 1.0,
    save_path: str = "",
) -> dict[str, Any]:
    """Create a 1D interpolation/easing Curve resource."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "points": points or [[0.0, 0.0], [1.0, 1.0]],
        "min_value": min_value,
        "max_value": max_value,
        "save_path": save_path,
    }
    return await runtime.send_command("curve_create_curve_1d", params, timeout=10.0)


async def curve_create_curve_2d(
    runtime: DirectRuntime,
    points: list[list[float]] | None = None,
    in_tangents: list[list[float]] | None = None,
    out_tangents: list[list[float]] | None = None,
    save_path: str = "",
) -> dict[str, Any]:
    """Create a 2D bezier spline Curve2D resource."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "points": points or [[0.0, 0.0], [100.0, 100.0]],
        "in_tangents": in_tangents or [],
        "out_tangents": out_tangents or [],
        "save_path": save_path,
    }
    return await runtime.send_command("curve_create_curve_2d", params, timeout=10.0)


async def curve_create_curve_3d(
    runtime: DirectRuntime,
    points: list[list[float]] | None = None,
    in_tangents: list[list[float]] | None = None,
    out_tangents: list[list[float]] | None = None,
    save_path: str = "",
) -> dict[str, Any]:
    """Create a 3D bezier spline Curve3D resource."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "points": points or [[0.0, 0.0, 0.0], [0.0, 5.0, 10.0]],
        "in_tangents": in_tangents or [],
        "out_tangents": out_tangents or [],
        "save_path": save_path,
    }
    return await runtime.send_command("curve_create_curve_3d", params, timeout=10.0)


async def curve_create_gradient(
    runtime: DirectRuntime,
    offsets: list[float] | None = None,
    colors: list[str] | None = None,
    save_path: str = "",
) -> dict[str, Any]:
    """Create a color ramp Gradient resource."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "offsets": offsets or [0.0, 1.0],
        "colors": colors or ["#000000", "#ffffff"],
        "save_path": save_path,
    }
    return await runtime.send_command("curve_create_gradient", params, timeout=10.0)


async def curve_create_gradient_texture(
    runtime: DirectRuntime,
    gradient_path: str = "",
    width: int = 256,
    is_2d: bool = False,
    height: int = 256,
    save_path: str = "",
) -> dict[str, Any]:
    """Create a GradientTexture1D or GradientTexture2D resource."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "gradient_path": gradient_path,
        "width": width,
        "is_2d": is_2d,
        "height": height,
        "save_path": save_path,
    }
    return await runtime.send_command("curve_create_gradient_texture", params, timeout=10.0)


async def curve_sample_curve(
    runtime: DirectRuntime,
    curve_path: str,
    offset: float = 0.5,
) -> dict[str, Any]:
    """Sample value or baked position on a Curve resource."""
    params: dict[str, Any] = {
        "curve_path": curve_path,
        "offset": offset,
    }
    return await runtime.send_command("curve_sample_curve", params, timeout=5.0)


async def curve_sample_gradient(
    runtime: DirectRuntime,
    gradient_path: str,
    offset: float = 0.5,
) -> dict[str, Any]:
    """Sample RGBA color on a Gradient resource."""
    params: dict[str, Any] = {
        "gradient_path": gradient_path,
        "offset": offset,
    }
    return await runtime.send_command("curve_sample_gradient", params, timeout=5.0)
