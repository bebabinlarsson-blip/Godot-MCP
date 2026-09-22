@tool
extends "res://addons/godot_ai/handlers/command_handler.gd"

const ErrorCodes := preload("res://addons/godot_ai/utils/error_codes.gd")

## Handles 2D and 3D occlusion culling setup and inspection.

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


func scaffold_occluder_3d(params: Dictionary) -> Dictionary:
	var scene_root := _get_scene_root()
	if scene_root == null:
		return {"error": "No edited scene root available", "code": ErrorCodes.NODE_NOT_FOUND}

	var parent_path: String = params.get("parent_path", "")
	var parent: Node = _resolve_node(scene_root, parent_path)
	if parent == null:
		return {"error": "Parent node not found: %s" % parent_path, "code": ErrorCodes.NODE_NOT_FOUND}

	var inst := OccluderInstance3D.new()
	inst.name = params.get("node_name", "OccluderInstance3D")

	var occ_type: String = params.get("occluder_type", "box").to_lower()
	var size_arr: Array = params.get("size", [1.0, 1.0, 1.0])
	var sz := Vector3(1.0, 1.0, 1.0)
	if size_arr.size() >= 3:
		sz = Vector3(float(size_arr[0]), float(size_arr[1]), float(size_arr[2]))

	if occ_type == "sphere":
		var sph := SphereOccluder3D.new()
		sph.radius = sz.x * 0.5
		inst.occluder = sph
	elif occ_type == "quad":
		var qd := QuadOccluder3D.new()
		qd.size = Vector2(sz.x, sz.y)
		inst.occluder = qd
	else:
		var bx := BoxOccluder3D.new()
		bx.size = sz
		inst.occluder = bx

	parent.add_child(inst)
	inst.owner = scene_root

	return {
		"success": true,
		"node_path": str(inst.get_path()),
		"occluder_class": inst.occluder.get_class()
	}


func scaffold_occluder_2d(params: Dictionary) -> Dictionary:
	var scene_root := _get_scene_root()
	if scene_root == null:
		return {"error": "No edited scene root available", "code": ErrorCodes.NODE_NOT_FOUND}

	var parent_path: String = params.get("parent_path", "")
	var parent: Node = _resolve_node(scene_root, parent_path)
	if parent == null:
		return {"error": "Parent node not found: %s" % parent_path, "code": ErrorCodes.NODE_NOT_FOUND}

	var occ := LightOccluder2D.new()
	occ.name = params.get("node_name", "LightOccluder2D")

	var poly := OccluderPolygon2D.new()
	poly.closed = bool(params.get("closed", true))
	var pts_arr: Array = params.get("polygon_points", [[-16, -16], [16, -16], [16, 16], [-16, 16]])
	var packed_pts := PackedVector2Array()
	for p in pts_arr:
		if p is Array and p.size() >= 2:
			packed_pts.append(Vector2(float(p[0]), float(p[1])))
	poly.polygon = packed_pts
	occ.occluder = poly

	parent.add_child(occ)
	occ.owner = scene_root

	return {
		"success": true,
		"node_path": str(occ.get_path()),
		"points_count": packed_pts.size(),
		"closed": poly.closed
	}


func get_occluder_info(params: Dictionary) -> Dictionary:
	var scene_root := _get_scene_root()
	if scene_root == null:
		return {"error": "No edited scene root available", "code": ErrorCodes.NODE_NOT_FOUND}

	var occluder_path: String = params.get("occluder_path", "")
	var node: Node = _resolve_node(scene_root, occluder_path)
	if node == null:
		return {"error": "Node not found: %s" % occluder_path, "code": ErrorCodes.NODE_NOT_FOUND}

	var occ_res: Resource = null
	if node is OccluderInstance3D:
		occ_res = (node as OccluderInstance3D).occluder
	elif node is LightOccluder2D:
		occ_res = (node as LightOccluder2D).occluder

	var res_class := ""
	if occ_res != null:
		res_class = occ_res.get_class()

	return {
		"success": true,
		"node_path": occluder_path,
		"node_class": node.get_class(),
		"occluder_resource_class": res_class
	}
