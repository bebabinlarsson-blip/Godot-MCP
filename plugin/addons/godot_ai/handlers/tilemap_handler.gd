@tool
extends "res://addons/godot_ai/handlers/command_handler.gd"

## TileMap / TileMapLayer authoring — set, fill, clear, place, rotate, and generate
## level layouts directly in the editor scene with full undo/redo support.
##
## Compatible with both Godot 4.3+ TileMapLayer and Godot 4.0-4.2+ TileMap nodes.

const ErrorCodes := preload("res://addons/godot_ai/utils/error_codes.gd")
const MAX_RECT_FILL_CELLS := 4096

var _undo_redo: EditorUndoRedoManager


func _init(undo_redo: EditorUndoRedoManager) -> void:
	_undo_redo = undo_redo


## Set a single tile cell.
## params: {path, source_id, atlas_col, atlas_row, map_x, map_y, layer?}
func set_cell(params: Dictionary) -> Dictionary:
	var resolved := _resolve_layer(params)
	if resolved.has("error"): return resolved
	var node: Node = resolved.node
	var layer_idx: int = resolved.layer

	var pos := Vector2i(params.get("map_x", 0), params.get("map_y", 0))
	var src := int(params.get("source_id", 0))
	var atlas := Vector2i(params.get("atlas_col", 0), params.get("atlas_row", 0))
	var prev := _capture_cell_state(node, pos, layer_idx)

	_undo_redo.create_action("MCP: TileMap set_cell")
	_undo_redo.add_do_method(self, "_apply_cell", node, pos, src, atlas, 0, layer_idx)
	_undo_redo.add_undo_method(self, "_restore_cell_state", node, pos, prev)
	_undo_redo.commit_action()

	return {"data": {
		"map_x": pos.x,
		"map_y": pos.y,
		"source_id": src,
		"atlas_col": atlas.x,
		"atlas_row": atlas.y,
		"layer": layer_idx,
		"undoable": true
	}}


## Fill a rectangular region with one tile type in a single undo action.
## params: {path, source_id, atlas_col, atlas_row, rect_x, rect_y, rect_w, rect_h, layer?}
func set_cells_rect(params: Dictionary) -> Dictionary:
	var resolved := _resolve_layer(params)
	if resolved.has("error"): return resolved
	var node: Node = resolved.node
	var layer_idx: int = resolved.layer

	var src := int(params.get("source_id", 0))
	var atlas := Vector2i(params.get("atlas_col", 0), params.get("atlas_row", 0))
	var rx := int(params.get("rect_x", 0))
	var ry := int(params.get("rect_y", 0))
	var rw := int(params.get("rect_w", 1))
	var rh := int(params.get("rect_h", 1))

	if rw <= 0 or rh <= 0:
		return ErrorCodes.make(
			ErrorCodes.VALUE_OUT_OF_RANGE,
			"rect_w and rect_h must be > 0 (got %d x %d)" % [rw, rh]
		)
	var cell_count := rw * rh
	if cell_count > MAX_RECT_FILL_CELLS:
		return ErrorCodes.make(
			ErrorCodes.VALUE_OUT_OF_RANGE,
			"Rect too large: %d cells exceeds max %d" % [cell_count, MAX_RECT_FILL_CELLS]
		)

	var cells: Array[Vector2i] = []
	var snapshot: Array[Dictionary] = []
	for x in range(rx, rx + rw):
		for y in range(ry, ry + rh):
			var pos := Vector2i(x, y)
			cells.append(pos)
			snapshot.append({"pos": pos, "state": _capture_cell_state(node, pos, layer_idx)})

	_undo_redo.create_action("MCP: TileMap set_cells_rect %dx%d" % [rw, rh])
	for pos in cells:
		_undo_redo.add_do_method(self, "_apply_cell", node, pos, src, atlas, 0, layer_idx)
	_undo_redo.add_undo_method(self, "_restore_rect_snapshot", node, snapshot)
	_undo_redo.commit_action()

	return {"data": {
		"cells_filled": cells.size(),
		"rect": {"x": rx, "y": ry, "w": rw, "h": rh},
		"layer": layer_idx,
		"undoable": true
	}}


## Place a tile with rotation and flip support.
## params: {path, source_id, atlas_col, atlas_row, map_x, map_y, rotation_degrees?, flip_h?, flip_v?, alternative_tile?, layer?}
func place_tile(params: Dictionary) -> Dictionary:
	var resolved := _resolve_layer(params)
	if resolved.has("error"): return resolved
	var node: Node = resolved.node
	var layer_idx: int = resolved.layer

	var pos := Vector2i(params.get("map_x", 0), params.get("map_y", 0))
	var src := int(params.get("source_id", 0))
	var atlas := Vector2i(params.get("atlas_col", 0), params.get("atlas_row", 0))
	var alt := int(params.get("alternative_tile", -1))
	var rot := int(params.get("rotation_degrees", 0)) % 360
	if rot < 0: rot += 360
	var flip_h := bool(params.get("flip_h", false))
	var flip_v := bool(params.get("flip_v", false))

	if alt < 0:
		alt = 0
		if rot == 90:
			alt = 16384 | 4096
		elif rot == 180:
			alt = 4096 | 8192
		elif rot == 270:
			alt = 16384 | 8192

		if flip_h:
			alt ^= 4096
		if flip_v:
			alt ^= 8192

	var prev := _capture_cell_state(node, pos, layer_idx)
	_undo_redo.create_action("MCP: TileMap place_tile")
	_undo_redo.add_do_method(self, "_apply_cell", node, pos, src, atlas, alt, layer_idx)
	_undo_redo.add_undo_method(self, "_restore_cell_state", node, pos, prev)
	_undo_redo.commit_action()

	return {"data": {
		"map_x": pos.x,
		"map_y": pos.y,
		"source_id": src,
		"atlas_col": atlas.x,
		"atlas_row": atlas.y,
		"alternative_tile": alt,
		"rotation_degrees": rot,
		"flip_h": flip_h,
		"flip_v": flip_v,
		"layer": layer_idx,
		"undoable": true
	}}


## Rotate an existing cell by degrees clockwise (90, 180, 270).
## params: {path, map_x, map_y, degrees?, layer?}
func rotate_cell(params: Dictionary) -> Dictionary:
	var resolved := _resolve_layer(params)
	if resolved.has("error"): return resolved
	var node: Node = resolved.node
	var layer_idx: int = resolved.layer

	var pos := Vector2i(params.get("map_x", 0), params.get("map_y", 0))
	var prev := _capture_cell_state(node, pos, layer_idx)
	if not prev.get("has_tile", false):
		return ErrorCodes.make(ErrorCodes.RESOURCE_NOT_FOUND, "No tile found at (%d, %d)" % [pos.x, pos.y])

	var degrees := int(params.get("degrees", 90)) % 360
	if degrees < 0: degrees += 360
	var old_alt: int = prev.get("alternative", 0)
	var base_id: int = old_alt & ~(4096 | 8192 | 16384)
	var current_flags: int = old_alt & (4096 | 8192 | 16384)

	var steps := int(round(degrees / 90.0)) % 4
	for _i in range(steps):
		match current_flags:
			0: current_flags = 20480
			20480: current_flags = 12288
			12288: current_flags = 24576
			24576: current_flags = 0
			4096: current_flags = 28672
			28672: current_flags = 8192
			8192: current_flags = 16384
			16384: current_flags = 4096
			_: current_flags = 20480

	var new_alt: int = base_id | current_flags

	_undo_redo.create_action("MCP: TileMap rotate_cell (%d, %d)" % [pos.x, pos.y])
	_undo_redo.add_do_method(self, "_apply_cell", node, pos, prev.source_id, Vector2i(prev.atlas_col, prev.atlas_row), new_alt, layer_idx)
	_undo_redo.add_undo_method(self, "_restore_cell_state", node, pos, prev)
	_undo_redo.commit_action()

	return {"data": {
		"map_x": pos.x,
		"map_y": pos.y,
		"degrees": degrees,
		"old_alternative": old_alt,
		"new_alternative": new_alt,
		"undoable": true
	}}


## Flip an existing tile cell horizontally and/or vertically.
## params: {path, map_x, map_y, flip_h?, flip_v?, layer?}
func flip_cell(params: Dictionary) -> Dictionary:
	var resolved := _resolve_layer(params)
	if resolved.has("error"): return resolved
	var node: Node = resolved.node
	var layer_idx: int = resolved.layer

	var pos := Vector2i(params.get("map_x", 0), params.get("map_y", 0))
	var prev := _capture_cell_state(node, pos, layer_idx)
	if not prev.get("has_tile", false):
		return ErrorCodes.make(ErrorCodes.RESOURCE_NOT_FOUND, "No tile found at (%d, %d)" % [pos.x, pos.y])

	var flip_h: bool = params.get("flip_h", false)
	var flip_v: bool = params.get("flip_v", false)
	var alt: int = prev.get("alternative", 0)
	if flip_h: alt ^= 4096
	if flip_v: alt ^= 8192

	_undo_redo.create_action("MCP: TileMap flip_cell (%d, %d)" % [pos.x, pos.y])
	_undo_redo.add_do_method(self, "_apply_cell", node, pos, prev.source_id, Vector2i(prev.atlas_col, prev.atlas_row), alt, layer_idx)
	_undo_redo.add_undo_method(self, "_restore_cell_state", node, pos, prev)
	_undo_redo.commit_action()

	return {"data": {
		"map_x": pos.x,
		"map_y": pos.y,
		"flip_h_applied": flip_h,
		"flip_v_applied": flip_v,
		"new_alternative": alt,
		"undoable": true
	}}


## Erase a single tile at (map_x, map_y).
## params: {path, map_x, map_y, layer?}
func erase_cell(params: Dictionary) -> Dictionary:
	var resolved := _resolve_layer(params)
	if resolved.has("error"): return resolved
	var node: Node = resolved.node
	var layer_idx: int = resolved.layer

	var pos := Vector2i(params.get("map_x", 0), params.get("map_y", 0))
	var prev := _capture_cell_state(node, pos, layer_idx)
	if not prev.get("has_tile", false):
		return {"data": {"map_x": pos.x, "map_y": pos.y, "erased": false, "was_empty": true}}

	_undo_redo.create_action("MCP: TileMap erase_cell (%d, %d)" % [pos.x, pos.y])
	_undo_redo.add_do_method(self, "_apply_erase", node, pos, layer_idx)
	_undo_redo.add_undo_method(self, "_restore_cell_state", node, pos, prev)
	_undo_redo.commit_action()

	return {"data": {"map_x": pos.x, "map_y": pos.y, "erased": true, "undoable": true}}


## Return all used cell coordinates.
## params: {path, layer?}
func get_used_cells(params: Dictionary) -> Dictionary:
	var resolved := _resolve_layer(params)
	if resolved.has("error"): return resolved
	var node: Node = resolved.node
	var layer_idx: int = resolved.layer

	var cells: Array = []
	if node is TileMapLayer:
		cells = node.get_used_cells()
	elif node.has_method("get_used_cells"):
		cells = node.call("get_used_cells", layer_idx)

	var result: Array = []
	for c in cells:
		result.append({"x": c.x, "y": c.y})
	return {"data": {"cells": result, "count": result.size(), "layer": layer_idx}}


## Remove all tiles from a TileMapLayer or TileMap.
## params: {path, layer?}
func clear_layer(params: Dictionary) -> Dictionary:
	var resolved := _resolve_layer(params)
	if resolved.has("error"): return resolved
	var node: Node = resolved.node
	var layer_idx: int = resolved.layer

	var snapshot := _capture_used_cells_snapshot(node, layer_idx)
	_undo_redo.create_action("MCP: TileMap clear")
	if node is TileMapLayer:
		_undo_redo.add_do_method(node, "clear")
	elif node.has_method("clear_layer"):
		_undo_redo.add_do_method(node, "clear_layer", layer_idx)
	elif node.has_method("clear"):
		_undo_redo.add_do_method(node, "clear")

	_undo_redo.add_undo_method(self, "_restore_rect_snapshot", node, snapshot)
	_undo_redo.commit_action()
	return {"data": {"cleared": true, "layer": layer_idx, "undoable": true}}


## Get detailed tile cell information.
## params: {path, map_x, map_y, layer?}
func get_cell(params: Dictionary) -> Dictionary:
	var resolved := _resolve_layer(params)
	if resolved.has("error"): return resolved
	var node: Node = resolved.node
	var layer_idx: int = resolved.layer

	var pos := Vector2i(params.get("map_x", 0), params.get("map_y", 0))
	var prev := _capture_cell_state(node, pos, layer_idx)
	if not prev.get("has_tile", false):
		return {"data": {"has_tile": false, "map_x": pos.x, "map_y": pos.y}}
	var alt: int = prev.get("alternative", 0)
	return {"data": {
		"has_tile": true,
		"map_x": pos.x,
		"map_y": pos.y,
		"source_id": prev.source_id,
		"atlas_col": prev.atlas_col,
		"atlas_row": prev.atlas_row,
		"alternative_tile": alt,
		"flip_h": (alt & 4096) != 0,
		"flip_v": (alt & 8192) != 0,
		"transpose": (alt & 16384) != 0,
		"layer": layer_idx,
	}}


## Automatically generate a complete level layout directly in the editor scene.
## params: {path, genre="platformer"|"topdown"|"dungeon"|"arena", rect_w=32, rect_h=18, rect_x=0, rect_y=0, source_id=0, floor_col=0, floor_row=0, wall_col=1, wall_row=0, accent_col=2, accent_row=0, layer=0}
func generate_layout(params: Dictionary) -> Dictionary:
	var resolved := _resolve_layer(params)
	if resolved.has("error"): return resolved
	var node: Node = resolved.node
	var layer_idx: int = resolved.layer

	var genre: String = str(params.get("genre", "platformer")).to_lower().strip_edges()
	var rx: int = int(params.get("rect_x", 0))
	var ry: int = int(params.get("rect_y", 0))
	var rw: int = int(params.get("rect_w", 32))
	var rh: int = int(params.get("rect_h", 18))
	var src: int = int(params.get("source_id", 0))

	var floor_atlas := Vector2i(int(params.get("floor_col", 0)), int(params.get("floor_row", 0)))
	var wall_atlas := Vector2i(int(params.get("wall_col", 1)), int(params.get("wall_row", 0)))
	var accent_atlas := Vector2i(int(params.get("accent_col", 2)), int(params.get("accent_row", 0)))

	var placements: Array[Dictionary] = []

	match genre:
		"platformer":
			# Solid ground across bottom 2 rows with jump gaps
			for x in range(rx, rx + rw):
				var is_gap := (x == rx + int(rw * 0.35) or x == rx + int(rw * 0.35) + 1 or x == rx + int(rw * 0.7) or x == rx + int(rw * 0.7) + 1)
				if not is_gap:
					placements.append({"pos": Vector2i(x, ry + rh - 1), "atlas": wall_atlas, "alt": 0})
					placements.append({"pos": Vector2i(x, ry + rh - 2), "atlas": floor_atlas, "alt": 0})

			# Boundary walls
			for y in range(ry, ry + rh):
				placements.append({"pos": Vector2i(rx, y), "atlas": wall_atlas, "alt": 0})
				placements.append({"pos": Vector2i(rx + rw - 1, y), "atlas": wall_atlas, "alt": 0})

			# Stepping platforms
			for x in range(rx + 4, rx + 10):
				placements.append({"pos": Vector2i(x, ry + rh - 5), "atlas": floor_atlas, "alt": 0})
			for x in range(rx + 13, rx + 19):
				placements.append({"pos": Vector2i(x, ry + rh - 8), "atlas": floor_atlas, "alt": 0})
			for x in range(rx + 22, rx + 28):
				placements.append({"pos": Vector2i(x, ry + rh - 5), "atlas": floor_atlas, "alt": 0})
			for x in range(rx + 10, rx + 16):
				placements.append({"pos": Vector2i(x, ry + rh - 12), "atlas": accent_atlas, "alt": 0})

		"topdown", "rpg":
			# Outer walls with doorway
			var mid_x := rx + int(rw / 2.0)
			for x in range(rx, rx + rw):
				for y in range(ry, ry + rh):
					var is_outer_x := (x == rx or x == rx + rw - 1)
					var is_outer_y := (y == ry or y == ry + rh - 1)
					var is_door := (x == mid_x and y == ry + rh - 1)
					if (is_outer_x or is_outer_y) and not is_door:
						placements.append({"pos": Vector2i(x, y), "atlas": wall_atlas, "alt": 0})
					else:
						placements.append({"pos": Vector2i(x, y), "atlas": floor_atlas, "alt": 0})
			# Corner accents
			placements.append({"pos": Vector2i(rx + 3, ry + 3), "atlas": accent_atlas, "alt": 0})
			placements.append({"pos": Vector2i(rx + rw - 4, ry + 3), "atlas": accent_atlas, "alt": 0})
			placements.append({"pos": Vector2i(rx + 3, ry + rh - 4), "atlas": accent_atlas, "alt": 0})
			placements.append({"pos": Vector2i(rx + rw - 4, ry + rh - 4), "atlas": accent_atlas, "alt": 0})

		"dungeon":
			# Thick perimeter walls with corridor openings
			var mid_x := rx + int(rw / 2.0)
			for x in range(rx, rx + rw):
				for y in range(ry, ry + rh):
					var is_wall := (x <= rx + 1 or x >= rx + rw - 2 or y <= ry + 1 or y >= ry + rh - 2)
					if (x == mid_x or x == mid_x + 1) and (y <= ry + 1 or y >= ry + rh - 2):
						is_wall = false
					if is_wall:
						placements.append({"pos": Vector2i(x, y), "atlas": wall_atlas, "alt": 0})
					else:
						placements.append({"pos": Vector2i(x, y), "atlas": floor_atlas, "alt": 0})
			# Central columns
			for cx in [rx + 6, rx + rw - 8]:
				for cy in [ry + 5, ry + rh - 7]:
					placements.append({"pos": Vector2i(cx, cy), "atlas": accent_atlas, "alt": 0})
					placements.append({"pos": Vector2i(cx + 1, cy), "atlas": accent_atlas, "alt": 0})

		"arena":
			# Outer boundary
			for x in range(rx, rx + rw):
				for y in range(ry, ry + rh):
					if x == rx or x == rx + rw - 1 or y == ry or y == ry + rh - 1:
						placements.append({"pos": Vector2i(x, y), "atlas": wall_atlas, "alt": 0})
					else:
						placements.append({"pos": Vector2i(x, y), "atlas": floor_atlas, "alt": 0})
			# Symmetrical barriers
			var cx := rx + int(rw / 2.0)
			var cy := ry + int(rh / 2.0)
			placements.append({"pos": Vector2i(cx - 2, cy), "atlas": accent_atlas, "alt": 0})
			placements.append({"pos": Vector2i(cx, cy), "atlas": accent_atlas, "alt": 0})
			placements.append({"pos": Vector2i(cx + 2, cy), "atlas": accent_atlas, "alt": 0})

		_:
			# Default: fill floor
			for x in range(rx, rx + rw):
				for y in range(ry, ry + rh):
					placements.append({"pos": Vector2i(x, y), "atlas": floor_atlas, "alt": 0})

	var snapshot: Array[Dictionary] = []
	for p in placements:
		snapshot.append({"pos": p.pos, "state": _capture_cell_state(node, p.pos, layer_idx)})

	_undo_redo.create_action("MCP: TileMap generate_layout %s (%dx%d)" % [genre, rw, rh])
	for p in placements:
		_undo_redo.add_do_method(self, "_apply_cell", node, p.pos, src, p.atlas, p.alt, layer_idx)
	_undo_redo.add_undo_method(self, "_restore_rect_snapshot", node, snapshot)
	_undo_redo.commit_action()

	return {
		"data": {
			"genre": genre,
			"cells_placed": placements.size(),
			"rect": {"x": rx, "y": ry, "w": rw, "h": rh},
			"source_id": src,
			"layer": layer_idx,
			"undoable": true
		}
	}


## Internal helper functions
func _resolve_layer(params: Dictionary) -> Dictionary:
	var path: String = params.get("path", "")
	var scene_file: String = params.get("scene_file", "")
	var resolved := McpNodeValidator.resolve_or_error(path, "path", scene_file)
	if resolved.has("error"):
		return resolved
	var node: Node = resolved.node
	var layer_idx: int = int(params.get("layer", 0))
	if node is TileMapLayer:
		return {"node": node, "layer": 0}
	elif node.get_class() == "TileMap" or node.has_method("set_cell"):
		return {"node": node, "layer": layer_idx}
	return ErrorCodes.make(ErrorCodes.WRONG_TYPE,
		"Node is not a TileMapLayer or TileMap: %s (class: %s)" % [path, node.get_class()])


func _apply_cell(node: Node, pos: Vector2i, src: int, atlas: Vector2i, alt: int = 0, layer_idx: int = 0) -> void:
	if node is TileMapLayer:
		node.set_cell(pos, src, atlas, alt)
	elif node.has_method("set_cell"):
		node.call("set_cell", layer_idx, pos, src, atlas, alt)


func _apply_erase(node: Node, pos: Vector2i, layer_idx: int = 0) -> void:
	if node is TileMapLayer:
		node.erase_cell(pos)
	elif node.has_method("erase_cell"):
		node.call("erase_cell", layer_idx, pos)


func _capture_cell_state(node: Node, pos: Vector2i, layer_idx: int = 0) -> Dictionary:
	var source_id := -1
	var atlas := Vector2i(-1, -1)
	var alternative := 0
	if node is TileMapLayer:
		source_id = node.get_cell_source_id(pos)
		if source_id != -1:
			atlas = node.get_cell_atlas_coords(pos)
			alternative = node.get_cell_alternative_tile(pos)
	elif node.has_method("get_cell_source_id"):
		source_id = int(node.call("get_cell_source_id", layer_idx, pos))
		if source_id != -1:
			var res_atlas = node.call("get_cell_atlas_coords", layer_idx, pos)
			if res_atlas is Vector2i:
				atlas = res_atlas
			alternative = int(node.call("get_cell_alternative_tile", layer_idx, pos))

	if source_id == -1:
		return {"has_tile": false, "layer": layer_idx}
	return {
		"has_tile": true,
		"source_id": source_id,
		"atlas_col": atlas.x,
		"atlas_row": atlas.y,
		"alternative": alternative,
		"layer": layer_idx,
	}


func _capture_used_cells_snapshot(node: Node, layer_idx: int = 0) -> Array[Dictionary]:
	var snapshot: Array[Dictionary] = []
	var cells: Array = []
	if node is TileMapLayer:
		cells = node.get_used_cells()
	elif node.has_method("get_used_cells"):
		cells = node.call("get_used_cells", layer_idx)
	for pos in cells:
		snapshot.append({"pos": pos, "state": _capture_cell_state(node, pos, layer_idx)})
	return snapshot


func _restore_rect_snapshot(node: Node, snapshot: Array[Dictionary]) -> void:
	for entry in snapshot:
		_restore_cell_state(node, entry.pos, entry.state)


func _restore_cell_state(node: Node, pos: Vector2i, state: Dictionary) -> void:
	var layer_idx: int = int(state.get("layer", 0))
	if not state.get("has_tile", false):
		_apply_erase(node, pos, layer_idx)
		return
	_apply_cell(
		node,
		pos,
		int(state.get("source_id", -1)),
		Vector2i(int(state.get("atlas_col", -1)), int(state.get("atlas_row", -1))),
		int(state.get("alternative", 0)),
		layer_idx
	)