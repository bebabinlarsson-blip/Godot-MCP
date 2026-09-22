"""Handler functions routing AnimationTree commands to Godot runtime."""

from __future__ import annotations

from typing import Any

from godot_ai.handlers._readiness import require_writable_async
from godot_ai.runtime.direct import DirectRuntime


async def animation_tree_scaffold_state_machine(
    runtime: DirectRuntime,
    parent_path: str = "",
    anim_player_path: str = "",
    node_name: str = "AnimationTree",
) -> dict[str, Any]:
    """Scaffold an AnimationTree with an AnimationNodeStateMachine root."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "parent_path": parent_path,
        "anim_player_path": anim_player_path,
        "node_name": node_name,
    }
    return await runtime.send_command(
        "animation_tree_scaffold_state_machine", params, timeout=10.0
    )


async def animation_tree_add_state(
    runtime: DirectRuntime,
    tree_path: str,
    state_name: str,
    animation_name: str = "",
    position: list[float] | None = None,
) -> dict[str, Any]:
    """Add an animation state node into an AnimationNodeStateMachine."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "tree_path": tree_path,
        "state_name": state_name,
        "animation_name": animation_name,
        "position": position or [0, 0],
    }
    return await runtime.send_command("animation_tree_add_state", params, timeout=10.0)


async def animation_tree_add_transition(
    runtime: DirectRuntime,
    tree_path: str,
    from_state: str,
    to_state: str,
    auto_advance: bool = False,
) -> dict[str, Any]:
    """Add a transition between two states in an AnimationNodeStateMachine."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "tree_path": tree_path,
        "from_state": from_state,
        "to_state": to_state,
        "auto_advance": auto_advance,
    }
    return await runtime.send_command("animation_tree_add_transition", params, timeout=10.0)


async def animation_tree_scaffold_blend_tree(
    runtime: DirectRuntime,
    parent_path: str = "",
    anim_player_path: str = "",
    node_name: str = "AnimationTreeBlend",
) -> dict[str, Any]:
    """Scaffold an AnimationTree with an AnimationNodeBlendTree root."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "parent_path": parent_path,
        "anim_player_path": anim_player_path,
        "node_name": node_name,
    }
    return await runtime.send_command(
        "animation_tree_scaffold_blend_tree", params, timeout=10.0
    )


async def animation_tree_get_tree_info(
    runtime: DirectRuntime,
    tree_path: str,
) -> dict[str, Any]:
    """Inspect root node configuration and status of an AnimationTree."""
    params: dict[str, Any] = {"tree_path": tree_path}
    return await runtime.send_command("animation_tree_get_tree_info", params, timeout=10.0)
