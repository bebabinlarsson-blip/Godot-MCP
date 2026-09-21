"""Handler functions routing Editor Undo/Redo commands to Godot."""

from __future__ import annotations

from typing import Any

from godot_ai.handlers._readiness import require_writable_async
from godot_ai.runtime.direct import DirectRuntime


async def undo_redo_get_history(
    runtime: DirectRuntime,
) -> dict[str, Any]:
    """Inspect active EditorUndoRedoManager history and available actions."""
    return await runtime.send_command("undo_redo_get_history", {}, timeout=10.0)


async def undo_redo_undo(
    runtime: DirectRuntime,
) -> dict[str, Any]:
    """Execute undo in the active editor."""
    await require_writable_async(runtime)
    return await runtime.send_command("undo_redo_undo", {}, timeout=10.0)


async def undo_redo_redo(
    runtime: DirectRuntime,
) -> dict[str, Any]:
    """Execute redo in the active editor."""
    await require_writable_async(runtime)
    return await runtime.send_command("undo_redo_redo", {}, timeout=10.0)
