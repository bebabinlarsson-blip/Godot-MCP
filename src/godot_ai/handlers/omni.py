"""Handler functions routing Omni commands to the connected Godot runtime."""

from __future__ import annotations

from typing import Any

from godot_ai.runtime.direct import DirectRuntime


async def omni_eval(
    runtime: DirectRuntime,
    code: str,
    mode: str = "auto",
    inputs: dict[str, Any] | None = None,
) -> dict:
    """Execute arbitrary GDScript code in the Godot editor process."""
    return await runtime.send_command(
        "omni_eval",
        {
            "code": code,
            "mode": mode,
            "inputs": inputs or {},
        },
        timeout=30.0,
    )


async def omni_execute_script(
    runtime: DirectRuntime,
    code: str = "",
    path: str = "",
    inputs: dict[str, Any] | None = None,
) -> dict:
    """Execute a script file or inline GDScript code."""
    return await runtime.send_command(
        "omni_execute_script",
        {
            "code": code,
            "path": path,
            "inputs": inputs or {},
        },
        timeout=30.0,
    )


async def reflection_call(
    runtime: DirectRuntime,
    target: Any,
    method: str,
    args: list[Any] | None = None,
) -> dict:
    """Call any method on any Godot Object (Node, Resource, Singleton, RefCounted)."""
    return await runtime.send_command(
        "reflection_call",
        {
            "target": target,
            "method": method,
            "args": args or [],
        },
        timeout=15.0,
    )


async def reflection_get(
    runtime: DirectRuntime,
    target: Any,
    property: str,
) -> dict:
    """Read any property on any Godot Object."""
    return await runtime.send_command(
        "reflection_get",
        {
            "target": target,
            "property": property,
        },
        timeout=10.0,
    )


async def reflection_set(
    runtime: DirectRuntime,
    target: Any,
    property: str,
    value: Any,
) -> dict:
    """Write any property on any Godot Object."""
    return await runtime.send_command(
        "reflection_set",
        {
            "target": target,
            "property": property,
            "value": value,
        },
        timeout=10.0,
    )


async def reflection_inspect(
    runtime: DirectRuntime,
    target: Any,
) -> dict:
    """Inspect full methods, properties, and signals of any Godot Object."""
    return await runtime.send_command(
        "reflection_inspect",
        {
            "target": target,
        },
        timeout=10.0,
    )


async def reflection_instantiate(
    runtime: DirectRuntime,
    class_name: str = "",
    script_path: str = "",
) -> dict:
    """Instantiate any Godot engine ClassDB class or custom script."""
    return await runtime.send_command(
        "reflection_instantiate",
        {
            "class_name": class_name,
            "script_path": script_path,
        },
        timeout=10.0,
    )


async def ui_semantic_tree(
    runtime: DirectRuntime,
    max_depth: int = 8,
) -> dict:
    """Extract full hierarchical semantic UI Control tree from the Godot Editor."""
    return await runtime.send_command(
        "ui_semantic_tree",
        {
            "max_depth": max_depth,
        },
        timeout=15.0,
    )


async def ui_click_control(
    runtime: DirectRuntime,
    text: str = "",
    path: str = "",
) -> dict:
    """Simulate mouse click on any editor button, tab, checkbox, or menu."""
    return await runtime.send_command(
        "ui_click_control",
        {
            "text": text,
            "path": path,
        },
        timeout=10.0,
    )


async def ui_type_text(
    runtime: DirectRuntime,
    text: str,
    target: str = "",
) -> dict:
    """Type text into any editor LineEdit or TextEdit."""
    return await runtime.send_command(
        "ui_type_text",
        {
            "text": text,
            "target": target,
        },
        timeout=10.0,
    )
