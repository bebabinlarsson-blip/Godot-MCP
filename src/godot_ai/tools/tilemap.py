"""MCP tool for TileMap / TileMapLayer authoring."""

from __future__ import annotations

from fastmcp import FastMCP

from godot_ai.handlers import tilemap as tilemap_handlers
from godot_ai.tools._meta_tool import register_manage_tool

_DESCRIPTION = """\
TileMap / TileMapLayer authoring (set tiles, fill rects, clear, read cells, generate layouts).

CRITICAL DIRECTIVE: ALWAYS place tiles directly down into the TileMap or TileMapLayer
node in the active editor scene using this tool. NEVER generate maps by writing procedural
GDScript code in _ready() unless the user explicitly requested runtime procedural generation.
Direct tile placement enables visual editing, native Godot physics, and instant editor inspection.

All operations target TileMapLayer or TileMap nodes in the currently edited scene by
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
        Place a tile with exact rotation (0, 90, 180, 270) and flip flags.
        Returns: {map_x, map_y, source_id, atlas_col, atlas_row, alternative_tile, rotation_degrees, flip_h, flip_v}

  • tilemap_rotate_cell(path, map_x, map_y, degrees=90)
        Rotate an existing tile cell at (map_x, map_y) clockwise by degrees (90, 180, 270) with D4 symmetry.
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

  • tilemap_generate_layout(path, genre="platformer", rect_w=32, rect_h=18, rect_x=0, rect_y=0,
                            source_id=0, floor_col=0, floor_row=0, wall_col=1, wall_row=0, accent_col=2, accent_row=0, layer=0)
        Generate a complete layout placed directly into the editor. Supported genres: 'platformer', 'topdown', 'rpg', 'dungeon', 'arena'.
        Returns: {genre, cells_placed, rect, source_id, layer, undoable}
"""


def register_tilemap_tools(mcp: FastMCP) -> None:
    register_manage_tool(
        mcp,
        tool_name="tilemap_manage",
        description=_DESCRIPTION,
        ops={
            "tilemap_set_cell":        tilemap_handlers.tilemap_set_cell,
            "tilemap_set_cells_rect":  tilemap_handlers.tilemap_set_cells_rect,
            "tilemap_clear":           tilemap_handlers.tilemap_clear,
            "tilemap_get_cells":       tilemap_handlers.tilemap_get_cells,
            "tilemap_place_tile":      tilemap_handlers.tilemap_place_tile,
            "tilemap_rotate_cell":     tilemap_handlers.tilemap_rotate_cell,
            "tilemap_flip_cell":       tilemap_handlers.tilemap_flip_cell,
            "tilemap_erase_cell":      tilemap_handlers.tilemap_erase_cell,
            "tilemap_get_cell":        tilemap_handlers.tilemap_get_cell,
            "tilemap_generate_layout": tilemap_handlers.tilemap_generate_layout,
            "tilemap_paint_terrain":   tilemap_handlers.tilemap_paint_terrain,
            "tilemap_import_matrix":   tilemap_handlers.tilemap_import_matrix,
            "tilemap_scatter_props":   tilemap_handlers.tilemap_scatter_props,
            "generate_layout":         tilemap_handlers.tilemap_generate_layout,
            "paint_terrain":           tilemap_handlers.tilemap_paint_terrain,
            "import_matrix":           tilemap_handlers.tilemap_import_matrix,
            "scatter_props":           tilemap_handlers.tilemap_scatter_props,
            "place_tile":              tilemap_handlers.tilemap_place_tile,
            "rotate_cell":             tilemap_handlers.tilemap_rotate_cell,
            "flip_cell":               tilemap_handlers.tilemap_flip_cell,
            "erase_cell":              tilemap_handlers.tilemap_erase_cell,
            "get_cell":                tilemap_handlers.tilemap_get_cell,
            "set_cell":                tilemap_handlers.tilemap_set_cell,
            "set_cells_rect":          tilemap_handlers.tilemap_set_cells_rect,
            "clear":                   tilemap_handlers.tilemap_clear,
            "get_cells":               tilemap_handlers.tilemap_get_cells,
        },
        read_resource_forms={
            "tilemap_get_cells": None,
            "tilemap_get_cell": None,
            "get_cells": None,
            "get_cell": None,
        },
    )

