"""MCP tool for TileMap / TileMapLayer authoring."""

from __future__ import annotations

from fastmcp import FastMCP

from godot_ai.handlers import tilemap as tilemap_handlers
from godot_ai.tools._meta_tool import register_manage_tool

_DESCRIPTION = """\
TileMap / TileMapLayer authoring (set tiles, fill rects, clear, read cells).

All operations target TileMapLayer nodes in the currently edited scene by
scene-relative path (e.g. "/LavaLake20x20/Ground"). All write ops are
undoable via EditorUndoRedoManager.

source_id is the TileSet source index. atlas_col/atlas_row are the
atlas coordinates of the tile within that source. For full-tile animated
sources (lava, water, sewage) use atlas_col=0, atlas_row=0.

IMPORTANT — Source-ID remapping in specialized .tres files:
When a layer uses a specialized .tres (e.g. volcano_animated.tres),
Source-IDs are re-numbered from 0. Example: volcano lava is Source 8 in
the main volcano.tres but Source 0 in volcano_animated.tres.
Always use the remapped ID when the TileMapLayer references a specialized
.tres, not the original ID from the main .tres.

Ops:
  • tilemap_set_cell(path, source_id, atlas_col, atlas_row, map_x, map_y)
        Set a single tile at (map_x, map_y).
        Returns: {map_x, map_y, source_id, atlas_col, atlas_row}

  • tilemap_set_cells_rect(path, source_id, atlas_col, atlas_row,
                            rect_x, rect_y, rect_w, rect_h)
        Fill a rect_w × rect_h region starting at (rect_x, rect_y) with
        one tile type in a single undo action.
        Returns: {cells_filled, rect: {x, y, w, h}}

  • tilemap_clear(path)
        Remove all tiles from the layer.
        Returns: {cleared: true}

  • tilemap_get_cells(path)
        Return all used cell coordinates.
        Returns: {cells: [{x, y}, ...], count: int}

  • tilemap_place_tile(path, source_id, atlas_col, atlas_row, map_x, map_y,
                       rotation_degrees=0, flip_h=false, flip_v=false, alternative_tile=-1)
        Place a tile with rotation and flip flags.
        Returns: {map_x, map_y, source_id, atlas_col, atlas_row, alternative_tile, rotation_degrees, flip_h, flip_v}

  • tilemap_rotate_cell(path, map_x, map_y, degrees=90)
        Rotate an existing tile cell at (map_x, map_y) clockwise by degrees (90, 180, 270).
        Returns: {map_x, map_y, degrees, old_alternative, new_alternative}

  • tilemap_flip_cell(path, map_x, map_y, flip_h=false, flip_v=false)
        Flip an existing tile cell at (map_x, map_y) horizontally and/or vertically.
        Returns: {map_x, map_y, flip_h_applied, flip_v_applied, new_alternative}

  • tilemap_erase_cell(path, map_x, map_y)
        Erase a single tile cell at (map_x, map_y).
        Returns: {map_x, map_y, erased}

  • tilemap_get_cell(path, map_x, map_y)
        Get detailed information of a tile cell.
        Returns: {has_tile, map_x, map_y, source_id, atlas_col, atlas_row, alternative_tile, flip_h, flip_v, transpose}
"""


def register_tilemap_tools(mcp: FastMCP) -> None:
    register_manage_tool(
        mcp,
        tool_name="tilemap_manage",
        description=_DESCRIPTION,
        ops={
            "tilemap_set_cell":       tilemap_handlers.tilemap_set_cell,
            "tilemap_set_cells_rect": tilemap_handlers.tilemap_set_cells_rect,
            "tilemap_clear":          tilemap_handlers.tilemap_clear,
            "tilemap_get_cells":      tilemap_handlers.tilemap_get_cells,
            "tilemap_place_tile":     tilemap_handlers.tilemap_place_tile,
            "tilemap_rotate_cell":    tilemap_handlers.tilemap_rotate_cell,
            "tilemap_flip_cell":      tilemap_handlers.tilemap_flip_cell,
            "tilemap_erase_cell":     tilemap_handlers.tilemap_erase_cell,
            "tilemap_get_cell":       tilemap_handlers.tilemap_get_cell,
        },
        read_resource_forms={
            "tilemap_get_cells": None,
            "tilemap_get_cell": None,
        },
    )

