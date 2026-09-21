"""MCP tool for Godot 4 GPU Compute Shaders and RenderingDevice execution."""

from __future__ import annotations

from fastmcp import FastMCP

from godot_ai.handlers import compute as compute_handlers
from godot_ai.tools._meta_tool import register_manage_tool

_DESCRIPTION = """\
GPU Compute Shaders, RenderingDevice Uniform Buffers, and GPU Pipeline Execution.

Ops:
  * create_shader(shader_path="res://shaders/compute_example.glsl", code="")
        Create a GLSL compute shader template file.

  * get_device_info()
        Inspect RenderingDevice capabilities, workgroup limits, and driver version.

  * run_compute(shader_path, input_buffer=[...], x_groups=1, y_groups=1, z_groups=1)
        Compile and dispatch a compute pipeline on the GPU and read back output data.
"""


def register_compute_tools(mcp: FastMCP) -> None:
    register_manage_tool(
        mcp,
        tool_name="compute_manage",
        description=_DESCRIPTION,
        ops={
            "create_shader": compute_handlers.compute_create_shader,
            "get_device_info": compute_handlers.compute_get_device_info,
            "run_compute": compute_handlers.compute_run_compute,
        },
        read_resource_forms={
            "get_device_info": None,
        },
    )
