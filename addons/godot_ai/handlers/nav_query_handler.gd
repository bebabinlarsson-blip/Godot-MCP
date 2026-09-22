@tool
extends "res://addons/godot_ai/handlers/command_handler.gd"

const ErrorCodes := preload("res://addons/godot_ai/utils/error_codes.gd")

## Handles NavigationServer path queries, navigation links, and obstacle scaffolding.

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


func query_path_2d(params: Dictionary) -> Dictionary:
	var start_arr = params.get("start", [0.0, 0.0])
	var end_arr = params.get("end", [0.0, 0.0])
	var start := Vector2(float(start_arr[0]), float(start_arr[1]))
	var end := Vector2(float(end_arr[0]), float(end_arr[1]))
	var optimize: bool = params.get("optimize", true)

	var map_rid: RID
	var scene_root := _get_scene_root()
	if scene_root != null and scene_root.get_world_2d() != null:
		map_rid = scene_root.get_world_2d().get_navigation_map()
	else:
		var maps := NavigationServer2D.get_maps()
		if maps.size() > 0:
			map_rid = maps[0]

	if not map_rid.is_valid():
		return {"error": "No valid Navigation2D map found", "code": ErrorCodes.NODE_NOT_FOUND}

	var path_points: PackedVector2Array = NavigationServer2D.map_get_path(
		map_rid, start, end, optimize
	)
	var serialized_points: Array = []
	for pt in path_points:
		serialized_points.append([pt.x, pt.y])

	return {
		"success": true,
		"point_count": path_points.size(),
		"path": serialized_points
	}


func query_path_3d(params: Dictionary) -> Dictionary:
	var start_arr = params.get("start", [0.0, 0.0, 0.0])
	var end_arr = params.get("end", [0.0, 0.0, 0.0])
	var start := Vector3(float(start_arr[0]), float(start_arr[1]), float(start_arr[2]))
	var end := Vector3(float(end_arr[0]), float(end_arr[1]), float(end_arr[2]))
	var optimize: bool = params.get("optimize", true)

	var map_rid: RID
	var scene_root := _get_scene_root()
	if scene_root != null and scene_root.get_world_3d() != null:
		map_rid = scene_root.get_world_3d().get_navigation_map()
	else:
		var maps := NavigationServer3D.get_maps()
		if maps.size() > 0:
			map_rid = maps[0]

	if not map_rid.is_valid():
		return {"error": "No valid Navigation3D map found", "code": ErrorCodes.NODE_NOT_FOUND}

	var path_points: PackedVector3Array = NavigationServer3D.map_get_path(
		map_rid, start, end, optimize
	)
	var serialized_points: Array = []
	for pt in path_points:
		serialized_points.append([pt.x, pt.y, pt.z])

	return {
		"success": true,
		"point_count": path_points.size(),
		"path": serialized_points
	}


func scaffold_nav_link(params: Dictionary) -> Dictionary:
	var scene_root := _get_scene_root()
	if scene_root == null:
		return {"error": "No edited scene root available", "code": ErrorCodes.NODE_NOT_FOUND}

	var parent_path: String = params.get("parent_path", "")
	var parent: Node = _resolve_node(scene_root, parent_path)
	if parent == null:
		return {"error": "Parent node not found: %s" % parent_path, "code": ErrorCodes.NODE_NOT_FOUND}

	var is_3d: bool = params.get("is_3d", false)
	var link_name: String = params.get("node_name", "NavLink")

	var link_node: Node
	if is_3d:
		var link_3d := NavigationLink3D.new()
		var start_arr = params.get("start_position", [0.0, 0.0, 0.0])
		var end_arr = params.get("end_position", [1.0, 0.0, 0.0])
		link_3d.start_position = Vector3(float(start_arr[0]), float(start_arr[1]), float(start_arr[2]))
		link_3d.end_position = Vector3(float(end_arr[0]), float(end_arr[1]), float(end_arr[2]))
		link_3d.bidirectional = params.get("bidirectional", true)
		link_node = link_3d
	else:
		var link_2d := NavigationLink2D.new()
		var start_arr = params.get("start_position", [0.0, 0.0])
		var end_arr = params.get("end_position", [100.0, 0.0])
		link_2d.start_position = Vector2(float(start_arr[0]), float(start_arr[1]))
		link_2d.end_position = Vector2(float(end_arr[0]), float(end_arr[1]))
		link_2d.bidirectional = params.get("bidirectional", true)
		link_node = link_2d

	link_node.name = link_name
	parent.add_child(link_node)
	link_node.owner = scene_root

	return {
		"success": true,
		"node_path": str(link_node.get_path()),
		"is_3d": is_3d
	}


func scaffold_nav_obstacle(params: Dictionary) -> Dictionary:
	var scene_root := _get_scene_root()
	if scene_root == null:
		return {"error": "No edited scene root available", "code": ErrorCodes.NODE_NOT_FOUND}

	var parent_path: String = params.get("parent_path", "")
	var parent: Node = _resolve_node(scene_root, parent_path)
	if parent == null:
		return {"error": "Parent node not found: %s" % parent_path, "code": ErrorCodes.NODE_NOT_FOUND}

	var is_3d: bool = params.get("is_3d", false)
	var obs_name: String = params.get("node_name", "NavObstacle")

	var obs_node: Node
	if is_3d:
		var obs_3d := NavigationObstacle3D.new()
		obs_3d.radius = float(params.get("radius", 1.0))
		obs_node = obs_3d
	else:
		var obs_2d := NavigationObstacle2D.new()
		obs_2d.radius = float(params.get("radius", 32.0))
		obs_node = obs_2d

	obs_node.name = obs_name
	parent.add_child(obs_node)
	obs_node.owner = scene_root

	return {
		"success": true,
		"node_path": str(obs_node.get_path()),
		"radius": obs_node.get("radius"),
		"is_3d": is_3d
	}


func get_nav_map_info(params: Dictionary) -> Dictionary:
	var is_3d: bool = params.get("is_3d", false)
	var info: Dictionary = {"success": true, "is_3d": is_3d}

	if is_3d:
		var maps_3d := NavigationServer3D.get_maps()
		info["map_count"] = maps_3d.size()
		if maps_3d.size() > 0:
			var m = maps_3d[0]
			info["cell_size"] = NavigationServer3D.map_get_cell_size(m)
			info["cell_height"] = NavigationServer3D.map_get_cell_height(m)
			info["edge_connection_margin"] = NavigationServer3D.map_get_edge_connection_margin(m)
	else:
		var maps_2d := NavigationServer2D.get_maps()
		info["map_count"] = maps_2d.size()
		if maps_2d.size() > 0:
			var m = maps_2d[0]
			info["cell_size"] = NavigationServer2D.map_get_cell_size(m)
			info["edge_connection_margin"] = NavigationServer2D.map_get_edge_connection_margin(m)

	return info
