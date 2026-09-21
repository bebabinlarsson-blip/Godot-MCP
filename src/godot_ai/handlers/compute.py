"""Handler functions routing GPU Compute Shader commands to Godot."""

from __future__ import annotations

from typing import Any

from godot_ai.handlers._readiness import require_writable_async
from godot_ai.runtime.direct import DirectRuntime


async def compute_create_shader(
    runtime: DirectRuntime,
    shader_path: str = "res://shaders/compute_example.glsl",
    code: str = "",
) -> dict[str, Any]:
    """Create a GLSL compute shader template file."""
    await require_writable_async(runtime)
    return await runtime.send_command(
        "compute_create_shader",
        {"shader_path": shader_path, "code": code},
        timeout=15.0,
    )


async def compute_get_device_info(
    runtime: DirectRuntime,
) -> dict[str, Any]:
    """Query active RenderingDevice hardware properties, limits, and driver info."""
    return await runtime.send_command(
        "compute_get_device_info",
        {},
        timeout=10.0,
    )


async def compute_run_compute(
    runtime: DirectRuntime,
    shader_path: str,
    input_buffer: list[float] | None = None,
    x_groups: int = 1,
    y_groups: int = 1,
    z_groups: int = 1,
) -> dict[str, Any]:
    """Dispatch a compute shader pipeline on GPU and read back output buffer."""
    await require_writable_async(runtime)
    return await runtime.send_command(
        "compute_run_compute",
        {
            "shader_path": shader_path,
            "input_buffer": input_buffer or [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0],
            "x_groups": x_groups,
            "y_groups": y_groups,
            "z_groups": z_groups,
        },
        timeout=20.0,
    )
