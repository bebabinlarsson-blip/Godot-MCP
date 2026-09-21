"""Shared handlers for finite state machine scaffolding tools."""

from __future__ import annotations

from typing import Any

from godot_ai.handlers._readiness import require_writable_async
from godot_ai.runtime.direct import DirectRuntime


async def fsm_scaffold_fsm(
    runtime: DirectRuntime,
    target_node_path: str = "",
    name: str = "StateMachine",
    script_dir: str = "res://scripts/fsm/",
    preset: str = "enemy_ai",
    custom_states: list[str] | None = None,
    initial_state: str = "",
) -> dict:
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "target_node_path": target_node_path,
        "name": name,
        "script_dir": script_dir,
        "preset": preset,
        "custom_states": custom_states or [],
        "initial_state": initial_state,
    }
    return await runtime.send_command("fsm_scaffold_fsm", params)
