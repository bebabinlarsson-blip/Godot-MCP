@tool
extends "res://addons/godot_ai/handlers/command_handler.gd"

const ErrorCodes := preload("res://addons/godot_ai/utils/error_codes.gd")

## Handles background asynchronous resource and scene loading via ResourceLoader,
## status polling, progress reporting, and loading screen scaffolding.

var _undo_redo: EditorUndoRedoManager
var _connection: McpConnection


func _init(undo_redo: EditorUndoRedoManager = null, connection: McpConnection = null) -> void:
	_undo_redo = undo_redo
	_connection = connection


func start_load(params: Dictionary) -> Dictionary:
	var path: String = params.get("path", "")
	if path.is_empty():
		return ErrorCodes.make(ErrorCodes.INVALID_PARAMS, "path must be specified")

	var type_hint: String = params.get("type_hint", "")
	var use_sub_threads: bool = bool(params.get("use_sub_threads", false))
	var cache_mode: int = int(params.get("cache_mode", ResourceLoader.CACHE_MODE_REUSE))

	var err := ResourceLoader.load_threaded_request(path, type_hint, use_sub_threads, cache_mode)
	if err != OK:
		return ErrorCodes.make(ErrorCodes.RESOURCE_NOT_FOUND, "Failed to start threaded load for %s: %d" % [path, err])

	return {
		"data": {
			"path": path,
			"started": true,
			"use_sub_threads": use_sub_threads,
		}
	}


func get_status(params: Dictionary) -> Dictionary:
	var path: String = params.get("path", "")
	if path.is_empty():
		return ErrorCodes.make(ErrorCodes.INVALID_PARAMS, "path must be specified")

	var progress: Array = []
	var status_code := ResourceLoader.load_threaded_get_status(path, progress)

	var status_str := "invalid_resource"
	match status_code:
		ResourceLoader.THREAD_LOAD_IN_PROGRESS:
			status_str = "in_progress"
		ResourceLoader.THREAD_LOAD_FAILED:
			status_str = "failed"
		ResourceLoader.THREAD_LOAD_LOADED:
			status_str = "loaded"
		_:
			status_str = "invalid_resource"

	var progress_val: float = float(progress[0]) if progress.size() > 0 else 0.0

	return {
		"data": {
			"path": path,
			"status": status_str,
			"progress": progress_val,
		}
	}


func get_resource(params: Dictionary) -> Dictionary:
	var path: String = params.get("path", "")
	if path.is_empty():
		return ErrorCodes.make(ErrorCodes.INVALID_PARAMS, "path must be specified")

	var res := ResourceLoader.load_threaded_get(path)
	if res == null:
		return ErrorCodes.make(ErrorCodes.RESOURCE_NOT_FOUND, "Resource not loaded or failed: %s" % path)

	return {
		"data": {
			"path": path,
			"resource_class": res.get_class(),
			"loaded": true,
		}
	}


func scaffold_loading_screen(params: Dictionary) -> Dictionary:
	var save_path: String = params.get("save_path", "res://scripts/loading_screen.gd")

	var script_content := """extends Control

@export_file("*.tscn") var target_scene_path: String = ""
@export var progress_bar: ProgressBar
@export var status_label: Label

var _loading := false


func _ready() -> void:
	if not target_scene_path.is_empty():
		start_loading(target_scene_path)


func start_loading(scene_path: String) -> void:
	target_scene_path = scene_path
	_loading = true
	ResourceLoader.load_threaded_request(target_scene_path, "", false, ResourceLoader.CACHE_MODE_REUSE)
	if status_label:
		status_label.text = "Loading..."


func _process(_delta: float) -> void:
	if not _loading:
		return

	var progress: Array = []
	var status := ResourceLoader.load_threaded_get_status(target_scene_path, progress)

	if progress.size() > 0 and progress_bar:
		progress_bar.value = progress[0] * 100.0

	match status:
		ResourceLoader.THREAD_LOAD_LOADED:
			_loading = false
			var packed_scene: PackedScene = ResourceLoader.load_threaded_get(target_scene_path)
			if packed_scene:
				get_tree().change_scene_to_packed(packed_scene)
		ResourceLoader.THREAD_LOAD_FAILED:
			_loading = false
			if status_label:
				status_label.text = "Failed to load scene."
"""

	var global_path := ProjectSettings.globalize_path(save_path)
	var dir_path := global_path.get_base_dir()
	if not DirAccess.dir_exists_absolute(dir_path):
		DirAccess.make_dir_recursive_absolute(dir_path)

	var file := FileAccess.open(save_path, FileAccess.WRITE)
	if file == null:
		return ErrorCodes.make(ErrorCodes.RESOURCE_NOT_FOUND, "Failed to write %s: %d" % [save_path, FileAccess.get_open_error()])

	file.store_string(script_content)
	file.close()

	if Engine.has_singleton("EditorInterface"):
		var editor_interface := Engine.get_singleton("EditorInterface")
		var fs = editor_interface.get_resource_filesystem()
		if fs != null:
			fs.update_file(save_path)

	return {
		"data": {
			"save_path": save_path,
			"scaffolded": true,
		}
	}
