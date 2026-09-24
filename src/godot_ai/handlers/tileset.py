"""Shared handlers for TileSet management tools."""

from __future__ import annotations

from godot_ai.handlers._readiness import require_writable_async
from godot_ai.runtime.direct import DirectRuntime


async def tileset_diagnose(
    runtime: DirectRuntime,
    tileset_path: str,
    check_collision: bool = False,
    physics_layer: int = 0,
    max_findings: int = 80,
) -> dict:
    """Return bounded, read-only atlas and optional collision findings."""
    return await runtime.send_command("tileset_diagnose", {
        "tileset_path": tileset_path,
        "check_collision": check_collision,
        "physics_layer": physics_layer,
        "max_findings": max_findings,
    })


async def tileset_get_atlas_tiles(
    runtime: DirectRuntime,
    tileset_path: str,
    source_id: int,
) -> dict:
    """Return all occupied atlas positions for one source in a TileSet.

    Calls the GDScript ``get_atlas_tiles`` handler (read-only) and returns
    its result unchanged.

    Args:
        runtime:       In-process runtime adapter.
        tileset_path:  ``res://`` path to the ``.tres`` TileSet resource.
        source_id:     Integer index of the ``TileSetAtlasSource`` to query.

    Returns:
        ``{"data": {"tiles": [{"col": int, "row": int}, ...], "count": int}}`` on
        success, or an error dict from the GDScript handler.
    """
    return await runtime.send_command(
        "tileset_get_atlas_tiles",
        {
            "tileset_path": tileset_path,
            "source_id": source_id,
        },
    )


async def tileset_get_atlas_image(
    runtime: DirectRuntime,
    tileset_path: str,
    source_id: int,
    max_size: int = 0,
) -> dict:
    """Return the atlas texture of a TileSetAtlasSource as a Base64-encoded PNG.

    Reads the ``TileSetAtlasSource.texture`` directly from the resource —
    no UI interaction required.  The image can optionally be downscaled for
    faster transfer.

    Args:
        runtime:       In-process runtime adapter.
        tileset_path:  ``res://`` path to the ``.tres`` TileSet resource.
        source_id:     Integer index of the ``TileSetAtlasSource`` to query.
        max_size:      If > 0, scale the image so its longest edge is at most
                       this many pixels.  0 (default) = full resolution.

    Returns:
          ``{"data": {"image_base64": str, "width": int, "height": int,
              "original_width": int, "original_height": int, "format": "png"}}``
        on success, or an error dict from the GDScript handler.
    """
    return await runtime.send_command(
        "tileset_get_atlas_image",
        {
            "tileset_path": tileset_path,
            "source_id": source_id,
            "max_size": max_size,
        },
    )


async def tileset_create_from_texture(
    runtime: DirectRuntime,
    texture_path: str,
    save_path: str,
    tile_width: int = 16,
    tile_height: int = 16,
    separation_x: int = 0,
    separation_y: int = 0,
    margin_x: int = 0,
    margin_y: int = 0,
) -> dict:
    """Generate an atlas TileSet resource (.tres) sliced from a texture."""
    await require_writable_async(runtime)
    return await runtime.send_command(
        "tileset_create_from_texture",
        {
            "texture_path": texture_path,
            "save_path": save_path,
            "tile_width": tile_width,
            "tile_height": tile_height,
            "separation_x": separation_x,
            "separation_y": separation_y,
            "margin_x": margin_x,
            "margin_y": margin_y,
        },
    )


async def tileset_create_collision_polygon(
    runtime: DirectRuntime,
    tileset_path: str,
    source_id: int = 0,
    atlas_col: int = 0,
    atlas_row: int = 0,
    shape_type: str = "box",
    points: list[dict | list] | None = None,
    physics_layer: int = 0,
) -> dict:
    """Add a box or custom collision polygon to a tile in a TileSet resource."""
    await require_writable_async(runtime)
    params: dict = {
        "tileset_path": tileset_path,
        "source_id": source_id,
        "atlas_col": atlas_col,
        "atlas_row": atlas_row,
        "shape_type": shape_type,
        "physics_layer": physics_layer,
    }
    if points is not None:
        params["points"] = points
    return await runtime.send_command("tileset_create_collision_polygon", params)


async def tileset_scaffold_terrain_bitmasks(
    runtime: DirectRuntime,
    tileset_path: str,
    source_id: int = 0,
    terrain_set: int = 0,
    terrain_id: int = 0,
    template: str = "simple_box",
    atlas_offset_col: int = 0,
    atlas_offset_row: int = 0,
    tiles: list[dict] | None = None,
) -> dict:
    """Scaffold terrain autotile peering bitmasks across an atlas region."""
    await require_writable_async(runtime)
    params: dict = {
        "tileset_path": tileset_path,
        "source_id": source_id,
        "terrain_set": terrain_set,
        "terrain_id": terrain_id,
        "template": template,
        "atlas_offset_col": atlas_offset_col,
        "atlas_offset_row": atlas_offset_row,
    }
    if tiles is not None:
        params["tiles"] = tiles
    return await runtime.send_command("tileset_scaffold_terrain_bitmasks", params)
