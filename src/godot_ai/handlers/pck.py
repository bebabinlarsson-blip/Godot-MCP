"""Handler functions routing PCK and asset bundle packaging commands
to the connected Godot runtime.
"""

from __future__ import annotations

from typing import Any

from godot_ai.handlers._readiness import require_writable_async
from godot_ai.runtime.direct import DirectRuntime


async def pck_create_pck(
    runtime: DirectRuntime,
    pck_path: str,
    files: list[str] | None = None,
    alignment: int = 32,
) -> dict[str, Any]:
    """Create a standalone PCK package file from project resources."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "pck_path": pck_path,
        "files": files or [],
        "alignment": alignment,
    }
    return await runtime.send_command("pck_create_pck", params, timeout=10.0)


async def pck_load_pck(
    runtime: DirectRuntime,
    pck_path: str,
    replace_files: bool = True,
) -> dict[str, Any]:
    """Dynamically mount a PCK resource pack into the virtual filesystem."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "pck_path": pck_path,
        "replace_files": replace_files,
    }
    return await runtime.send_command("pck_load_pck", params, timeout=10.0)


async def pck_inspect_pck(
    runtime: DirectRuntime,
    pck_path: str,
) -> dict[str, Any]:
    """Inspect and check existence and size of a PCK package."""
    params: dict[str, Any] = {"pck_path": pck_path}
    return await runtime.send_command("pck_inspect_pck", params, timeout=10.0)
