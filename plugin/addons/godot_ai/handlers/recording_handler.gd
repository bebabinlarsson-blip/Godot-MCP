@tool
extends "res://addons/godot_ai/handlers/command_handler.gd"

const ErrorCodes := preload("res://addons/godot_ai/utils/error_codes.gd")

## Handles Viewport frame capture and MovieWriter configuration.

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


func capture_viewport(params: Dictionary) -> Dictionary:
	var target_path: String = params.get("target_path", "res://screenshot.png")
	if not target_path.begins_with("res://") and not target_path.begins_with("user://"):
		target_path = "res://" + target_path

	var vp_path: String = params.get("viewport_path", "")
	var target_vp: Viewport = null

	var tree := Engine.get_main_loop() as SceneTree
	var scene_root := _get_scene_root()

	if not vp_path.is_empty() and scene_root != null:
		var node := _resolve_node(scene_root, vp_path)
		if node is Viewport:
			target_vp = node

	if target_vp == null and tree != null and tree.root != null:
		target_vp = tree.root

	if target_vp == null:
		return {"error": "Could not find a valid Viewport to capture", "code": ErrorCodes.NODE_NOT_FOUND}

	var tex: ViewportTexture = target_vp.get_texture()
	if tex == null:
		return {"error": "Viewport has no valid texture", "code": ErrorCodes.INTERNAL_ERROR}

	var img: Image = tex.get_image()
	if img == null or img.is_empty():
		return {"error": "Failed to extract image from ViewportTexture", "code": ErrorCodes.INTERNAL_ERROR}

	var err := img.save_png(target_path)
	return {
		"success": (err == OK),
		"target_path": target_path,
		"width": img.get_width(),
		"height": img.get_height()
	}


func configure_movie_writer(params: Dictionary) -> Dictionary:
	var movie_file: String = params.get("movie_file", "res://movie.avi")
	var fps: int = int(params.get("fps", 60))
	var quality: float = float(params.get("quality", 0.8))

	ProjectSettings.set_setting("editor/movie_writer/movie_file", movie_file)
	ProjectSettings.set_setting("editor/movie_writer/fps", fps)
	ProjectSettings.set_setting("editor/movie_writer/mjpeg_quality", quality)
	ProjectSettings.save()

	return {
		"success": true,
		"movie_file": movie_file,
		"fps": fps,
		"quality": quality
	}


func get_writer_status(_params: Dictionary) -> Dictionary:
	var is_movie: bool = OS.has_feature("movie")
	var movie_file: String = ""
	if ProjectSettings.has_setting("editor/movie_writer/movie_file"):
		movie_file = ProjectSettings.get_setting("editor/movie_writer/movie_file")

	return {
		"success": true,
		"movie_mode_active": is_movie,
		"configured_movie_file": movie_file
	}
