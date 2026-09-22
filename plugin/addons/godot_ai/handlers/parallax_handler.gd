@tool
extends "res://addons/godot_ai/handlers/command_handler.gd"

const ErrorCodes := preload("res://addons/godot_ai/utils/error_codes.gd")

## Handles Parallax2D, CanvasLayer, and VisibleOnScreenNotifier scaffolding.

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


func scaffold_parallax(params: Dictionary) -> Dictionary:
	var scene_root := _get_scene_root()
	if scene_root == null:
		return {"error": "No edited scene root available", "code": ErrorCodes.NODE_NOT_FOUND}

	var parent_path: String = params.get("parent_path", "")
	var parent: Node = _resolve_node(scene_root, parent_path)
	if parent == null:
		return {"error": "Parent node not found: %s" % parent_path, "code": ErrorCodes.NODE_NOT_FOUND}

	var node: Node = null
	if ClassDB.class_exists("Parallax2D"):
		node = ClassDB.instantiate("Parallax2D")
		var scroll_scale: Array = params.get("scroll_scale", [1.0, 1.0])
		if scroll_scale.size() >= 2:
			node.set("scroll_scale", Vector2(float(scroll_scale[0]), float(scroll_scale[1])))
		var repeat_size: Array = params.get("repeat_size", [0.0, 0.0])
		if repeat_size.size() >= 2:
			node.set("repeat_size", Vector2(float(repeat_size[0]), float(repeat_size[1])))
	else:
		node = ParallaxBackground.new()

	node.name = params.get("node_name", "Parallax2D")
	parent.add_child(node)
	node.owner = scene_root

	return {
		"success": true,
		"node_path": str(node.get_path()),
		"node_class": node.get_class()
	}


func scaffold_canvas_layer(params: Dictionary) -> Dictionary:
	var scene_root := _get_scene_root()
	if scene_root == null:
		return {"error": "No edited scene root available", "code": ErrorCodes.NODE_NOT_FOUND}

	var parent_path: String = params.get("parent_path", "")
	var parent: Node = _resolve_node(scene_root, parent_path)
	if parent == null:
		return {"error": "Parent node not found: %s" % parent_path, "code": ErrorCodes.NODE_NOT_FOUND}

	var layer := CanvasLayer.new()
	layer.name = params.get("node_name", "CanvasLayer")
	layer.layer = int(params.get("layer", 1))
	layer.follow_viewport_enabled = bool(params.get("follow_viewport", false))

	parent.add_child(layer)
	layer.owner = scene_root

	return {
		"success": true,
		"node_path": str(layer.get_path()),
		"layer": layer.layer
	}


func scaffold_visibility_notifier(params: Dictionary) -> Dictionary:
	var scene_root := _get_scene_root()
	if scene_root == null:
		return {"error": "No edited scene root available", "code": ErrorCodes.NODE_NOT_FOUND}

	var parent_path: String = params.get("parent_path", "")
	var parent: Node = _resolve_node(scene_root, parent_path)
	if parent == null:
		return {"error": "Parent node not found: %s" % parent_path, "code": ErrorCodes.NODE_NOT_FOUND}

	var is_2d: bool = params.get("is_2d", true)
	var node: Node
	if is_2d:
		var n2 := VisibleOnScreenNotifier2D.new()
		var sz_arr: Array = params.get("rect_size", [100.0, 100.0])
		if sz_arr.size() >= 2:
			n2.rect = Rect2(-float(sz_arr[0]) * 0.5, -float(sz_arr[1]) * 0.5, float(sz_arr[0]), float(sz_arr[1]))
		node = n2
	else:
		var n3 := VisibleOnScreenNotifier3D.new()
		node = n3

	node.name = params.get("node_name", "VisibilityNotifier")
	parent.add_child(node)
	node.owner = scene_root

	return {
		"success": true,
		"node_path": str(node.get_path()),
		"is_2d": is_2d
	}


func get_parallax_info(params: Dictionary) -> Dictionary:
	var scene_root := _get_scene_root()
	if scene_root == null:
		return {"error": "No edited scene root available", "code": ErrorCodes.NODE_NOT_FOUND}

	var node_path: String = params.get("node_path", "")
	var node: Node = _resolve_node(scene_root, node_path)
	if node == null:
		return {"error": "Node not found: %s" % node_path, "code": ErrorCodes.NODE_NOT_FOUND}

	return {
		"success": true,
		"node_path": node_path,
		"class": node.get_class()
	}
