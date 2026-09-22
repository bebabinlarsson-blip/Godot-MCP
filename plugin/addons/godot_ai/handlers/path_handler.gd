@tool
extends "res://addons/godot_ai/handlers/command_handler.gd"

const ErrorCodes := preload("res://addons/godot_ai/utils/error_codes.gd")

## Handles Curve2D, Curve3D, Path2D, Path3D, and procedural spline generation.

var _undo_redo: EditorUndoRedoManager
var _connection: McpConnection


func _init(undo_redo: EditorUndoRedoManager = null, connection: McpConnection = null) -> void:
	_undo_redo = undo_redo
	_connection = connection


func _get_scene_root() -> Node:
	if Engine.is_editor_hint():
		var tree := Engine.get_main_loop() as SceneTree
		if tree != null and Engine.has_singleton("EditorInterface"):
			var editor_interface := Engine.get_singleton("EditorInterface")
			if editor_interface.has_method("get_edited_scene_root"):
				var root: Node = editor_interface.get_edited_scene_root()
				if root != null:
					return root
		if tree != null and tree.edited_scene_root != null:
			return tree.edited_scene_root
		if tree != null and tree.current_scene != null:
			return tree.current_scene
		if tree != null and tree.root != null:
			return tree.root
	return null


func _resolve_node(scene_root: Node, node_path: String) -> Node:
	if node_path.is_empty():
		return scene_root
	return scene_root.get_node_or_null(NodePath(node_path))


func create_curve_2d(params: Dictionary) -> Dictionary:
	var curve := Curve2D.new()
	var raw_points: Array = params.get("points", [])
	var closed: bool = params.get("closed", false)
	var save_path: String = params.get("save_path", "")

	for p in raw_points:
		var pos := Vector2.ZERO
		var in_h := Vector2.ZERO
		var out_h := Vector2.ZERO
		if p is Dictionary:
			var pos_arr: Array = p.get("position", [0.0, 0.0])
			if pos_arr.size() >= 2:
				pos = Vector2(float(pos_arr[0]), float(pos_arr[1]))
			var in_arr: Array = p.get("in", [0.0, 0.0])
			if in_arr.size() >= 2:
				in_h = Vector2(float(in_arr[0]), float(in_arr[1]))
			var out_arr: Array = p.get("out", [0.0, 0.0])
			if out_arr.size() >= 2:
				out_h = Vector2(float(out_arr[0]), float(out_arr[1]))
		elif p is Array and p.size() >= 2:
			pos = Vector2(float(p[0]), float(p[1]))
		curve.add_point(pos, in_h, out_h)

	if closed and curve.point_count > 2:
		var first_pos := curve.get_point_position(0)
		curve.add_point(first_pos)

	var saved := false
	if not save_path.is_empty():
		if not save_path.begins_with("res://"):
			save_path = "res://" + save_path
		var err := ResourceSaver.save(curve, save_path)
		if err == OK:
			saved = true

	return {
		"success": true,
		"point_count": curve.point_count,
		"baked_length": curve.get_baked_length(),
		"saved": saved,
		"save_path": save_path if saved else ""
	}


func create_curve_3d(params: Dictionary) -> Dictionary:
	var curve := Curve3D.new()
	var raw_points: Array = params.get("points", [])
	var closed: bool = params.get("closed", false)
	var save_path: String = params.get("save_path", "")

	for p in raw_points:
		var pos := Vector3.ZERO
		var in_h := Vector3.ZERO
		var out_h := Vector3.ZERO
		if p is Dictionary:
			var pos_arr: Array = p.get("position", [0.0, 0.0, 0.0])
			if pos_arr.size() >= 3:
				pos = Vector3(float(pos_arr[0]), float(pos_arr[1]), float(pos_arr[2]))
			var in_arr: Array = p.get("in", [0.0, 0.0, 0.0])
			if in_arr.size() >= 3:
				in_h = Vector3(float(in_arr[0]), float(in_arr[1]), float(in_arr[2]))
			var out_arr: Array = p.get("out", [0.0, 0.0, 0.0])
			if out_arr.size() >= 3:
				out_h = Vector3(float(out_arr[0]), float(out_arr[1]), float(out_arr[2]))
		elif p is Array and p.size() >= 3:
			pos = Vector3(float(p[0]), float(p[1]), float(p[2]))
		curve.add_point(pos, in_h, out_h)

	if closed and curve.point_count > 2:
		var first_pos := curve.get_point_position(0)
		curve.add_point(first_pos)

	var saved := false
	if not save_path.is_empty():
		if not save_path.begins_with("res://"):
			save_path = "res://" + save_path
		var err := ResourceSaver.save(curve, save_path)
		if err == OK:
			saved = true

	return {
		"success": true,
		"point_count": curve.point_count,
		"baked_length": curve.get_baked_length(),
		"saved": saved,
		"save_path": save_path if saved else ""
	}


func scaffold_path(params: Dictionary) -> Dictionary:
	var scene_root := _get_scene_root()
	if scene_root == null:
		return {"error": "No edited scene root available", "code": ErrorCodes.NODE_NOT_FOUND}

	var parent_path: String = params.get("parent_path", "")
	var parent: Node = _resolve_node(scene_root, parent_path)
	if parent == null:
		return {"error": "Parent node not found at: %s" % parent_path, "code": ErrorCodes.NODE_NOT_FOUND}

	var type_str: String = params.get("type", "Path3D")
	var node_name: String = params.get("name", "Path")
	var with_follow: bool = params.get("with_follow", true)
	var loop: bool = params.get("loop", true)

	var path_node: Node = null
	var follow_node: Node = null

	if type_str.to_lower() == "path2d":
		var p2 := Path2D.new()
		p2.name = node_name
		p2.curve = Curve2D.new()
		path_node = p2
		if with_follow:
			var pf2 := PathFollow2D.new()
			pf2.name = "PathFollow2D"
			pf2.loop = loop
			follow_node = pf2
	else:
		var p3 := Path3D.new()
		p3.name = node_name
		p3.curve = Curve3D.new()
		path_node = p3
		if with_follow:
			var pf3 := PathFollow3D.new()
			pf3.name = "PathFollow3D"
			pf3.loop = loop
			follow_node = pf3

	parent.add_child(path_node)
	path_node.owner = scene_root
	if follow_node != null:
		path_node.add_child(follow_node)
		follow_node.owner = scene_root

	return {
		"success": true,
		"path_node": str(path_node.get_path()),
		"follow_node": str(follow_node.get_path()) if follow_node != null else "",
		"type": type_str
	}


func sample_baked_points(params: Dictionary) -> Dictionary:
	var scene_root := _get_scene_root()
	var path_node_path: String = params.get("path_node_path", "")
	var interval: float = float(params.get("interval", 1.0))
	if interval <= 0.01:
		interval = 0.01

	if scene_root == null:
		return {"error": "No edited scene root available", "code": ErrorCodes.NODE_NOT_FOUND}

	var node := _resolve_node(scene_root, path_node_path)
	if node == null:
		return {"error": "Path node not found at: %s" % path_node_path, "code": ErrorCodes.NODE_NOT_FOUND}

	var sampled_points: Array = []
	var total_length := 0.0

	if node is Path3D and node.curve != null:
		var curve: Curve3D = node.curve
		total_length = curve.get_baked_length()
		var dist := 0.0
		while dist <= total_length:
			var pos := curve.sample_baked(dist)
			sampled_points.append([pos.x, pos.y, pos.z])
			dist += interval
	elif node is Path2D and node.curve != null:
		var curve: Curve2D = node.curve
		total_length = curve.get_baked_length()
		var dist := 0.0
		while dist <= total_length:
			var pos := curve.sample_baked(dist)
			sampled_points.append([pos.x, pos.y])
			dist += interval
	else:
		return {"error": "Node is not a Path2D or Path3D with a valid curve", "code": ErrorCodes.INVALID_PARAMS}

	return {
		"success": true,
		"total_length": total_length,
		"sample_count": sampled_points.size(),
		"points": sampled_points
	}


func generate_spline(params: Dictionary) -> Dictionary:
	var shape: String = params.get("shape", "circle").to_lower()
	var is_3d: bool = params.get("is_3d", true)
	var radius: float = float(params.get("radius", 5.0))
	var count: int = int(params.get("points_count", 16))
	var save_path: String = params.get("save_path", "")

	if count < 3:
		count = 3

	var points: Array = []
	match shape:
		"circle":
			for i in range(count):
				var angle := (float(i) / float(count)) * TAU
				if is_3d:
					points.append([cos(angle) * radius, 0.0, sin(angle) * radius])
				else:
					points.append([cos(angle) * radius, sin(angle) * radius])
		"sine":
			var width := radius * 2.0
			for i in range(count):
				var t := float(i) / float(count - 1)
				var x := (t - 0.5) * width
				var y := sin(t * TAU * 2.0) * (radius * 0.5)
				if is_3d:
					points.append([x, y, 0.0])
				else:
					points.append([x, y])
		"spiral":
			for i in range(count):
				var t := float(i) / float(count)
				var angle := t * TAU * 3.0
				var r := radius * t
				if is_3d:
					points.append([cos(angle) * r, t * radius, sin(angle) * r])
				else:
					points.append([cos(angle) * r, sin(angle) * r])
		"rect":
			var half := radius * 0.5
			if is_3d:
				points = [
					[-half, 0.0, -half],
					[half, 0.0, -half],
					[half, 0.0, half],
					[-half, 0.0, half]
				]
			else:
				points = [
					[-half, -half],
					[half, -half],
					[half, half],
					[-half, half]
				]
		_:
			# S-curve
			for i in range(count):
				var t := float(i) / float(count - 1)
				var x := (t - 0.5) * radius * 2.0
				var z := sin(t * PI) * radius
				if is_3d:
					points.append([x, 0.0, z])
				else:
					points.append([x, z])

	if is_3d:
		return create_curve_3d({"points": points, "closed": (shape == "circle" or shape == "rect"), "save_path": save_path})
	else:
		return create_curve_2d({"points": points, "closed": (shape == "circle" or shape == "rect"), "save_path": save_path})
