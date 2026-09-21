"""Handler functions routing Omni commands to the connected Godot runtime."""

from __future__ import annotations

from typing import Any

from godot_ai.handlers._readiness import require_writable_async
from godot_ai.runtime.direct import DirectRuntime


async def omni_eval(
    runtime: DirectRuntime,
    code: str,
    mode: str = "auto",
    inputs: dict[str, Any] | None = None,
) -> dict:
    """Execute arbitrary GDScript code in the Godot editor process."""
    await require_writable_async(runtime)
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
    await require_writable_async(runtime)
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
    await require_writable_async(runtime)
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
    await require_writable_async(runtime)
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
    await require_writable_async(runtime)
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
    await require_writable_async(runtime)
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
    await require_writable_async(runtime)
    return await runtime.send_command(
        "ui_type_text",
        {
            "text": text,
            "target": target,
        },
        timeout=10.0,
    )


async def scene_instantiate_prefab(
    runtime: DirectRuntime,
    scene_path: str,
    parent_path: str = "",
    node_name: str = "",
    position: list[float] | None = None,
) -> dict:
    """Instantiate a .tscn scene file into the current active scene hierarchy."""
    await require_writable_async(runtime)
    return await runtime.send_command(
        "scene_instantiate_prefab",
        {
            "scene_path": scene_path,
            "parent_path": parent_path,
            "node_name": node_name,
            "position": position,
        },
        timeout=15.0,
    )


async def shader_create(
    runtime: DirectRuntime,
    shader_path: str,
    shader_type: str = "canvas_item",
    code: str = "",
    target_node_path: str = "",
) -> dict:
    """Create a new Shader (.gdshader) and optionally assign it as a ShaderMaterial to a node."""
    await require_writable_async(runtime)
    return await runtime.send_command(
        "shader_create",
        {
            "shader_path": shader_path,
            "shader_type": shader_type,
            "code": code,
            "target_node_path": target_node_path,
        },
        timeout=15.0,
    )


async def mesh_create_primitive(
    runtime: DirectRuntime,
    primitive_type: str = "box",
    node_name: str = "",
    parent_path: str = "",
    size: list[float] | None = None,
    albedo_color: list[float] | None = None,
    position: list[float] | None = None,
) -> dict:
    """Create a 3D PrimitiveMesh (box, sphere, cylinder, plane, capsule, prism)."""
    await require_writable_async(runtime)
    return await runtime.send_command(
        "mesh_create_primitive",
        {
            "primitive_type": primitive_type,
            "node_name": node_name,
            "parent_path": parent_path,
            "size": size,
            "albedo_color": albedo_color,
            "position": position,
        },
        timeout=15.0,
    )


async def collision_shape_create(
    runtime: DirectRuntime,
    parent_path: str,
    shape_type: str = "box",
    is_2d: bool = True,
    size: list[float] | None = None,
    radius: float = 16.0,
    height: float = 32.0,
    node_name: str = "CollisionShape",
) -> dict:
    """Create and attach a 2D or 3D CollisionShape with predefined geometry to a physics body."""
    await require_writable_async(runtime)
    return await runtime.send_command(
        "collision_shape_create",
        {
            "parent_path": parent_path,
            "shape_type": shape_type,
            "is_2d": is_2d,
            "size": size,
            "radius": radius,
            "height": height,
            "node_name": node_name,
        },
        timeout=15.0,
    )


async def animation_preset_motion(
    runtime: DirectRuntime,
    preset: str = "pulse",
    target_node_path: str = "",
    animation_player_path: str = "",
    anim_name: str = "",
    duration: float = 1.0,
    loop: bool = True,
) -> dict:
    """Generate procedural motion presets (pulse, fade_in, fade_out, slide_in)."""
    await require_writable_async(runtime)
    return await runtime.send_command(
        "animation_preset_motion",
        {
            "preset": preset,
            "target_node_path": target_node_path,
            "animation_player_path": animation_player_path,
            "anim_name": anim_name or preset,
            "duration": duration,
            "loop": loop,
        },
        timeout=15.0,
    )



async def mcp_ping(
    runtime: DirectRuntime,
) -> dict:
    """Quick diagnostic ping returning engine version, process frames, and memory metrics."""
    return await runtime.send_command(
        "mcp_ping",
        {},
        timeout=5.0,
    )
