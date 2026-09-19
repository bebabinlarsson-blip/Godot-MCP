"""Shared handlers for TileMap / TileMapLayer authoring tools."""

from __future__ import annotations

from godot_ai.handlers._readiness import require_writable_async
from godot_ai.runtime.direct import DirectRuntime


async def tilemap_set_cell(
    runtime: DirectRuntime,
    path: str,
    source_id: int,
    atlas_col: int,
    atlas_row: int,
    map_x: int,
    map_y: int,
) -> dict:
    """Set a single tile at (map_x, map_y) on a TileMapLayer node."""
    await require_writable_async(runtime)
    return await runtime.send_command(
        "tilemap_set_cell",
        {
            "path": path,
            "source_id": source_id,
            "atlas_col": atlas_col,
            "atlas_row": atlas_row,
            "map_x": map_x,
            "map_y": map_y,
        },
    )


async def tilemap_set_cells_rect(
    runtime: DirectRuntime,
    path: str,
    source_id: int,
    atlas_col: int,
    atlas_row: int,
    rect_x: int,
    rect_y: int,
    rect_w: int,
    rect_h: int,
) -> dict:
    """Fill a rect_w × rect_h region starting at (rect_x, rect_y) with one
    tile type in a single undo action.
    """
    await require_writable_async(runtime)
    return await runtime.send_command(
        "tilemap_set_cells_rect",
        {
            "path": path,
            "source_id": source_id,
            "atlas_col": atlas_col,
            "atlas_row": atlas_row,
            "rect_x": rect_x,
            "rect_y": rect_y,
            "rect_w": rect_w,
            "rect_h": rect_h,
        },
    )


async def tilemap_clear(
    runtime: DirectRuntime,
    path: str,
) -> dict:
    """Remove all tiles from a TileMapLayer node."""
    await require_writable_async(runtime)
    return await runtime.send_command("tilemap_clear", {"path": path})


async def tilemap_get_cells(
    runtime: DirectRuntime,
    path: str,
) -> dict:
    """Return all used cell coordinates of a TileMapLayer node.

    Returns ``{cells: [{x, y}, ...], count: int}``.
    """
    return await runtime.send_command("tilemap_get_cells", {"path": path})


async def tilemap_place_tile(
    runtime: DirectRuntime,
    path: str,
    source_id: int,
    atlas_col: int,
    atlas_row: int,
    map_x: int,
    map_y: int,
    rotation_degrees: int = 0,
    flip_h: bool = False,
    flip_v: bool = False,
    alternative_tile: int = -1,
) -> dict:
    """Place a tile with rotation and flip support."""
    await require_writable_async(runtime)
    return await runtime.send_command(
        "tilemap_place_tile",
        {
            "path": path,
            "source_id": source_id,
            "atlas_col": atlas_col,
            "atlas_row": atlas_row,
            "map_x": map_x,
            "map_y": map_y,
            "rotation_degrees": rotation_degrees,
            "flip_h": flip_h,
            "flip_v": flip_v,
            "alternative_tile": alternative_tile,
        },
    )


async def tilemap_rotate_cell(
    runtime: DirectRuntime,
    path: str,
    map_x: int,
    map_y: int,
    degrees: int = 90,
) -> dict:
    """Rotate an existing tile cell at (map_x, map_y)."""
    await require_writable_async(runtime)
    return await runtime.send_command(
        "tilemap_rotate_cell",
        {
            "path": path,
            "map_x": map_x,
            "map_y": map_y,
            "degrees": degrees,
        },
    )


async def tilemap_flip_cell(
    runtime: DirectRuntime,
    path: str,
    map_x: int,
    map_y: int,
    flip_h: bool = False,
    flip_v: bool = False,
) -> dict:
    """Flip an existing tile cell at (map_x, map_y)."""
    await require_writable_async(runtime)
    return await runtime.send_command(
        "tilemap_flip_cell",
        {
            "path": path,
            "map_x": map_x,
            "map_y": map_y,
            "flip_h": flip_h,
            "flip_v": flip_v,
        },
    )


async def tilemap_erase_cell(
    runtime: DirectRuntime,
    path: str,
    map_x: int,
    map_y: int,
) -> dict:
    """Erase a single tile at (map_x, map_y)."""
    await require_writable_async(runtime)
    return await runtime.send_command(
        "tilemap_erase_cell",
        {
            "path": path,
            "map_x": map_x,
            "map_y": map_y,
        },
    )


async def tilemap_get_cell(
    runtime: DirectRuntime,
    path: str,
    map_x: int,
    map_y: int,
) -> dict:
    """Get detailed tile cell information at (map_x, map_y)."""
    return await runtime.send_command(
        "tilemap_get_cell",
        {
            "path": path,
            "map_x": map_x,
            "map_y": map_y,
        },
    )


async def tilemap_generate_layout(
    runtime: DirectRuntime,
    path: str,
    genre: str = "platformer",
    rect_w: int = 32,
    rect_h: int = 18,
    rect_x: int = 0,
    rect_y: int = 0,
    source_id: int = 0,
    floor_col: int = 0,
    floor_row: int = 0,
    wall_col: int = 1,
    wall_row: int = 0,
    accent_col: int = 2,
    accent_row: int = 0,
    layer: int = 0,
) -> dict:
    """Generate a cohesive level layout placed directly into the editor TileMap/TileMapLayer.

    Supported genres: 'platformer', 'topdown', 'rpg', 'dungeon', 'arena'.
    Places all tiles directly down into the active editor scene with full Undo/Redo.
    """
    await require_writable_async(runtime)
    return await runtime.send_command(
        "tilemap_generate_layout",
        {
            "path": path,
            "genre": genre,
            "rect_w": rect_w,
            "rect_h": rect_h,
            "rect_x": rect_x,
            "rect_y": rect_y,
            "source_id": source_id,
            "floor_col": floor_col,
            "floor_row": floor_row,
            "wall_col": wall_col,
            "wall_row": wall_row,
            "accent_col": accent_col,
            "accent_row": accent_row,
            "layer": layer,
        },
    )


async def tilemap_paint_terrain(
    runtime: DirectRuntime,
    path: str,
    terrain_id: int,
    cells: list[dict | list | tuple],
    terrain_set: int = 0,
    layer: int = 0,
) -> dict:
    """Paint autotiling terrain using TileMapLayer.set_cells_terrain_connect().

    Connects corner/edge transition tiles automatically.
    cells is a list of coordinates, e.g. [{"x": 0, "y": 0}, {"x": 1, "y": 0}] or [[0, 0], [1, 0]].
    """
    await require_writable_async(runtime)
    return await runtime.send_command(
        "tilemap_paint_terrain",
        {
            "path": path,
            "terrain_set": terrain_set,
            "terrain_id": terrain_id,
            "cells": cells,
            "layer": layer,
        },
    )


async def tilemap_import_matrix(
    runtime: DirectRuntime,
    path: str,
    map_array: list[str] | list[list],
    legend: dict,
    origin_x: int = 0,
    origin_y: int = 0,
    layer: int = 0,
) -> dict:
    """Stamp an ASCII or 2D matrix layout directly into the editor TileMap/TileMapLayer.

    map_array is a list of strings (e.g. ["####", "#..#", "####"]) or a 2D array.
    legend maps characters or values to tile specs, e.g.
    {"#": {"source_id": 0, "atlas_col": 1, "atlas_row": 0}, ".": {"source_id": 0, "atlas_col": 0, "atlas_row": 0}}.
    """
    await require_writable_async(runtime)
    return await runtime.send_command(
        "tilemap_import_matrix",
        {
            "path": path,
            "map_array": map_array,
            "legend": legend,
            "origin_x": origin_x,
            "origin_y": origin_y,
            "layer": layer,
        },
    )


async def tilemap_scatter_props(
    runtime: DirectRuntime,
    parent_path: str,
    prop_scenes: list[str],
    region_rect: dict,
    count: int = 0,
    density: float = 0.05,
    seed: int = 0,
) -> dict:
    """Procedurally scatter scene instances (trees, rocks, chests) in a region.

    region_rect is {x, y, w, h}.
    prop_scenes is a list of res:// scene paths (e.g. ["res://tree.tscn"]).
    All instances are added in a single undo action.
    """
    await require_writable_async(runtime)
    return await runtime.send_command(
        "tilemap_scatter_props",
        {
            "parent_path": parent_path,
            "prop_scenes": prop_scenes,
            "region_rect": region_rect,
            "count": count,
            "density": density,
            "seed": seed,
        },
    )



