"""Handler functions routing Viewport Capture and MovieWriter commands
to the connected Godot runtime.
"""

from __future__ import annotations

from typing import Any

from godot_ai.handlers._readiness import require_writable_async
from godot_ai.runtime.direct import DirectRuntime


async def recording_capture_viewport(
    runtime: DirectRuntime,
    target_path: str = "res://screenshot.png",
    viewport_path: str = "",
) -> dict[str, Any]:
    """Capture a viewport texture and save it to an image file."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "target_path": target_path,
        "viewport_path": viewport_path,
    }
    return await runtime.send_command("recording_capture_viewport", params, timeout=10.0)


async def recording_configure_movie_writer(
    runtime: DirectRuntime,
    movie_file: str = "res://movie.avi",
    fps: int = 60,
    quality: float = 0.8,
) -> dict[str, Any]:
    """Configure MovieWriter settings in ProjectSettings."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "movie_file": movie_file,
        "fps": fps,
        "quality": quality,
    }
    return await runtime.send_command(
        "recording_configure_movie_writer", params, timeout=10.0
    )


async def recording_get_writer_status(
    runtime: DirectRuntime,
) -> dict[str, Any]:
    """Check MovieWriter activation status and configured output file."""
    return await runtime.send_command("recording_get_writer_status", {}, timeout=10.0)
