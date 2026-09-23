"""Shared handlers for the batch_execute tool."""

from __future__ import annotations

from godot_ai.handlers._readiness import require_writable_async
from godot_ai.runtime.direct import DirectRuntime


async def batch_execute(
    runtime: DirectRuntime,
    commands: list[dict],
    undo: bool = True,
) -> dict:
    await require_writable_async(runtime)
    if not isinstance(commands, list) or not commands:
        return {
            "succeeded": 0,
            "stopped_at": None,
            "results": [],
            "undo": undo,
            "rolled_back": False,
            "undoable": False,
            "error": {
                "code": "INVALID_PARAMS",
                "message": "commands must be a non-empty list",
            },
        }
    return await runtime.send_command(
        "batch_execute",
        {"commands": commands, "undo": undo},
        timeout=30.0,
    )


async def preview_scene_changes(runtime: DirectRuntime, commands: list[dict]) -> dict:
    """Preview structure edits and undo every recorded scene action."""
    await require_writable_async(runtime)
    return await runtime.send_command(
        "preview_scene_changes", {"commands": commands}, timeout=30.0,
    )
