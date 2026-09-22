"""Handler functions routing ConfigFile, JSON, and Expression commands."""

from __future__ import annotations

from typing import Any

from godot_ai.handlers._readiness import require_writable_async
from godot_ai.runtime.direct import DirectRuntime


async def config_config_read(
    runtime: DirectRuntime,
    file_path: str,
    section: str = "",
    key: str = "",
) -> dict[str, Any]:
    """Read values or entire sections from an INI ConfigFile."""
    params: dict[str, Any] = {
        "file_path": file_path,
        "section": section,
        "key": key,
    }
    return await runtime.send_command("config_config_read", params, timeout=10.0)


async def config_config_write(
    runtime: DirectRuntime,
    file_path: str,
    section: str,
    key: str,
    value: Any,
) -> dict[str, Any]:
    """Write a section and key value into an INI ConfigFile."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "file_path": file_path,
        "section": section,
        "key": key,
        "value": value,
    }
    return await runtime.send_command("config_config_write", params, timeout=10.0)


async def config_json_parse(
    runtime: DirectRuntime,
    json_string: str,
) -> dict[str, Any]:
    """Parse a JSON string into Godot Variant data structure."""
    params: dict[str, Any] = {"json_string": json_string}
    return await runtime.send_command("config_json_parse", params, timeout=10.0)


async def config_json_generate(
    runtime: DirectRuntime,
    data: Any,
    indent: str = "",
) -> dict[str, Any]:
    """Serialize data into a formatted JSON string."""
    params: dict[str, Any] = {"data": data, "indent": indent}
    return await runtime.send_command("config_json_generate", params, timeout=10.0)


async def config_expression_eval(
    runtime: DirectRuntime,
    expression_string: str,
    input_names: list[str] | None = None,
    input_values: list[Any] | None = None,
) -> dict[str, Any]:
    """Evaluate a mathematical or logic expression via Godot Expression."""
    params: dict[str, Any] = {
        "expression_string": expression_string,
        "input_names": input_names or [],
        "input_values": input_values or [],
    }
    return await runtime.send_command("config_expression_eval", params, timeout=10.0)
