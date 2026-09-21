"""Shared handlers for scene tools and resources."""

from __future__ import annotations

from typing import Any

from godot_ai.handlers._readiness import require_writable_async
from godot_ai.runtime.direct import DirectRuntime


async def scene_get_hierarchy(
    runtime: DirectRuntime,
    depth: int = 10,
    offset: int = 0,
    limit: int = 100,
) -> dict:
    return await runtime.send_command(
        "get_scene_tree", {"depth": depth, "offset": offset, "limit": limit}
    )


async def scene_get_roots(runtime: DirectRuntime) -> dict:
    return await runtime.send_command("get_open_scenes")


async def scene_create(
    runtime: DirectRuntime,
    path: str,
    root_type: str = "Node3D",
    root_name: str = "",
) -> dict:
    await require_writable_async(runtime)
    params: dict = {"path": path, "root_type": root_type}
    if root_name:
        params["root_name"] = root_name
    return await runtime.send_command("create_scene", params)


async def scene_open(
    runtime: DirectRuntime,
    path: str,
    force_reload: bool = False,
) -> dict:
    await require_writable_async(runtime)
    params: dict = {"path": path}
    if force_reload:
        params["force_reload"] = True
    return await runtime.send_command("open_scene", params)


async def scene_save(runtime: DirectRuntime) -> dict:
    await require_writable_async(runtime)
    return await runtime.send_command("save_scene")


async def scene_save_as(runtime: DirectRuntime, path: str) -> dict:
    await require_writable_async(runtime)
    return await runtime.send_command("save_scene_as", {"path": path})


async def scene_instantiate_batch(
    runtime: DirectRuntime,
    instances: list[dict],
    parent_path: str = "",
) -> dict:
    """Instantiate multiple PackedScenes into the active scene in a single UndoRedo action.

    instances is a list of objects with scene_path (res:// path) and optional name, position,
    rotation, scale, and properties.
    """
    await require_writable_async(runtime)
    return await runtime.send_command(
        "instantiate_batch",
        {"instances": instances, "parent_path": parent_path},
    )


async def current_scene_resource_data(runtime: DirectRuntime) -> dict:
    state = await runtime.send_command("get_editor_state")
    return {
        "current_scene": state.get("current_scene", ""),
        "project_name": state.get("project_name", ""),
        "is_playing": state.get("is_playing", False),
    }


## The godot://scene/hierarchy resource takes no arguments and cannot paginate,
## so a full read of a large scene would dump an unbounded node list into the
## reader's context. Cap it at the same node budget the tool defaults to (100)
## and stamp a truncated read so the reader knows to reach for the
## scene_get_hierarchy tool (offset/limit, or a narrower depth) for the rest.
_RESOURCE_HIERARCHY_NODE_CAP = 100


async def scene_hierarchy_resource_data(runtime: DirectRuntime) -> dict:
    result = await scene_get_hierarchy(
        runtime, depth=10, offset=0, limit=_RESOURCE_HIERARCHY_NODE_CAP
    )
    if result.get("has_more"):
        total = result.get("total_count")
        result["resource_truncated"] = True
        result["hint"] = (
            f"Scene tree has {total} nodes; this resource returns the first "
            f"{_RESOURCE_HIERARCHY_NODE_CAP}. Use the scene_get_hierarchy tool with "
            "offset/limit to page the rest, or a smaller depth to scope it."
        )
    return result


async def scene_diagnose(
    runtime: DirectRuntime,
    root_path: str = "",
) -> dict:
    params: dict[str, Any] = {}
    if root_path:
        params["root_path"] = root_path
    return await runtime.send_command("scene_diagnose", params, timeout=30.0)

