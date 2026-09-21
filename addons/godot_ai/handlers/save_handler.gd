@tool
extends "res://addons/godot_ai/handlers/command_handler.gd"

const ErrorCodes := preload("res://addons/godot_ai/utils/error_codes.gd")

var _undo_redo: EditorUndoRedoManager
var _connection


func _init(undo_redo: EditorUndoRedoManager, connection = null) -> void:
	_undo_redo = undo_redo
	_connection = connection


func scaffold_save_system(params: Dictionary) -> Dictionary:
	var name: String = params.get("name", "SaveManager")
	var script_path: String = params.get("script_path", "res://scripts/save_manager.gd")
	var save_directory: String = params.get("save_directory", "user://saves/")
	var register_autoload: bool = bool(params.get("register_autoload", true))
	var enable_encryption: bool = bool(params.get("enable_encryption", false))
	var encryption_password: String = params.get("encryption_password", "")

	var script_err = McpPathValidator.path_error(script_path, "script_path")
	if script_err != null:
		return script_err

	var script_dir := script_path.get_base_dir()
	if not DirAccess.dir_exists_absolute(script_dir):
		DirAccess.make_dir_recursive_absolute(script_dir)

	var save_code := """extends Node

signal game_saved(slot_name: String)
signal game_loaded(slot_name: String)
signal save_failed(slot_name: String, error_msg: String)
signal load_failed(slot_name: String, error_msg: String)

var save_dir: String = "%s"
var current_slot: String = ""
var enable_encryption: bool = %s
var encryption_password: String = "%s"

func _ready() -> void:
	ensure_save_dir()

func ensure_save_dir() -> void:
	if not DirAccess.dir_exists_absolute(save_dir):
		DirAccess.make_dir_recursive_absolute(save_dir)

func get_slot_path(slot_name: String) -> String:
	return save_dir.path_join(slot_name + ".save")

func has_save(slot_name: String) -> bool:
	return FileAccess.file_exists(get_slot_path(slot_name))

func save_game(slot_name: String, extra_data: Dictionary = {}) -> bool:
	ensure_save_dir()
	current_slot = slot_name

	var saveables = get_tree().get_nodes_in_group("saveable")
	var nodes_data: Array[Dictionary] = []
	var root_node := get_tree().root

	for node in saveables:
		if node.has_method("save_state"):
			var npath: String = str(root_node.get_path_to(node))
			nodes_data.append({
				"path": npath,
				"data": node.call("save_state")
			})

	var payload: Dictionary = {
		"slot_name": slot_name,
		"timestamp": Time.get_datetime_string_from_system(),
		"unix_time": Time.get_unix_time_from_system(),
		"nodes": nodes_data,
		"extra": extra_data
	}

	var json_str := JSON.stringify(payload, "\\t")
	var final_path := get_slot_path(slot_name)
	var temp_path := final_path + ".tmp"

	var file: FileAccess
	if enable_encryption and not encryption_password.is_empty():
		file = FileAccess.open_encrypted_with_pass(temp_path, FileAccess.WRITE, encryption_password)
	else:
		file = FileAccess.open(temp_path, FileAccess.WRITE)

	if file == null:
		var err := FileAccess.get_open_error()
		save_failed.emit(slot_name, "Failed to open file for writing: " + str(err))
		return false

	file.store_string(json_str)
	file.flush()
	file.close()

	# Atomic file replacement
	if FileAccess.file_exists(final_path):
		DirAccess.remove_absolute(final_path)
	var ren_err := DirAccess.rename_absolute(temp_path, final_path)
	if ren_err != OK:
		save_failed.emit(slot_name, "Failed to rename temp save file: " + str(ren_err))
		return false

	game_saved.emit(slot_name)
	return true

func load_game(slot_name: String) -> Dictionary:
	var path := get_slot_path(slot_name)
	if not FileAccess.file_exists(path):
		load_failed.emit(slot_name, "Save file does not exist: " + path)
		return {}

	var file: FileAccess
	if enable_encryption and not encryption_password.is_empty():
		file = FileAccess.open_encrypted_with_pass(path, FileAccess.READ, encryption_password)
	else:
		file = FileAccess.open(path, FileAccess.READ)

	if file == null:
		var err := FileAccess.get_open_error()
		load_failed.emit(slot_name, "Failed to open save file for reading: " + str(err))
		return {}

	var text := file.get_as_text()
	file.close()

	var json := JSON.new()
	var parse_err := json.parse(text)
	if parse_err != OK or not (json.data is Dictionary):
		load_failed.emit(slot_name, "Corrupted save file format.")
		return {}

	var payload: Dictionary = json.data
	current_slot = slot_name

	# Restore saveable nodes
	var root_node := get_tree().root
	var nodes_data: Array = payload.get("nodes", [])
	for entry in nodes_data:
		if entry is Dictionary and entry.has("path") and entry.has("data"):
			var target_node = root_node.get_node_or_null(NodePath(entry["path"]))
			if target_node and target_node.has_method("load_state"):
				target_node.call("load_state", entry["data"])

	game_loaded.emit(slot_name)
	return payload

func list_saves() -> Array[Dictionary]:
	ensure_save_dir()
	var results: Array[Dictionary] = []
	var dir := DirAccess.open(save_dir)
	if dir:
		dir.list_dir_begin()
		var fname := dir.get_next()
		while fname != "":
			if not dir.current_is_dir() and fname.ends_with(".save"):
				var slot := fname.trim_suffix(".save")
				results.append({
					"slot_name": slot,
					"file_name": fname,
					"path": save_dir.path_join(fname)
				})
			fname = dir.get_next()
		dir.list_dir_end()
	return results

func delete_save(slot_name: String) -> bool:
	var path := get_slot_path(slot_name)
	if FileAccess.file_exists(path):
		var err := DirAccess.remove_absolute(path)
		return err == OK
	return false
""" % [save_directory, ("true" if enable_encryption else "false"), encryption_password]

	var file := FileAccess.open(script_path, FileAccess.WRITE)
	if file == null:
		return ErrorCodes.make(ErrorCodes.INTERNAL_ERROR, "Failed to create save manager script at: %s" % script_path)
	file.store_string(save_code)
	file.close()

	var autoload_ok := false
	if register_autoload:
		var key := "autoload/%s" % name
		ProjectSettings.set_setting(key, "*" + script_path)
		ProjectSettings.set_initial_value(key, "")
		ProjectSettings.set_as_basic(key, true)
		var p_err := ProjectSettings.save()
		autoload_ok = (p_err == OK)

	var efs := EditorInterface.get_resource_filesystem()
	if efs != null:
		efs.update_file(script_path)

	return {
		"data": {
			"name": name,
			"script_path": script_path,
			"save_directory": save_directory,
			"register_autoload": register_autoload,
			"autoload_saved": autoload_ok,
			"enable_encryption": enable_encryption,
		}
	}


func save_slot(params: Dictionary) -> Dictionary:
	var slot_name: String = params.get("slot_name", "slot_1")
	var data: Dictionary = params.get("data", {})
	var directory: String = params.get("directory", "user://saves/")

	if not DirAccess.dir_exists_absolute(directory):
		DirAccess.make_dir_recursive_absolute(directory)

	var final_path := directory.path_join(slot_name + ".save")
	var temp_path := final_path + ".tmp"

	var payload := {
		"slot_name": slot_name,
		"timestamp": Time.get_datetime_string_from_system(),
		"unix_time": Time.get_unix_time_from_system(),
		"data": data,
	}

	var json_str := JSON.stringify(payload, "\t")
	var file := FileAccess.open(temp_path, FileAccess.WRITE)
	if file == null:
		return ErrorCodes.make(ErrorCodes.INTERNAL_ERROR, "Failed to write temp save file: %s" % temp_path)
	file.store_string(json_str)
	file.flush()
	file.close()

	if FileAccess.file_exists(final_path):
		DirAccess.remove_absolute(final_path)
	var ren_err := DirAccess.rename_absolute(temp_path, final_path)
	if ren_err != OK:
		return ErrorCodes.make(ErrorCodes.INTERNAL_ERROR, "Failed to atomically rename save file: %s" % final_path)

	return {
		"data": {
			"slot_name": slot_name,
			"path": final_path,
			"timestamp": payload["timestamp"],
			"success": true,
		}
	}


func load_slot(params: Dictionary) -> Dictionary:
	var slot_name: String = params.get("slot_name", "slot_1")
	var directory: String = params.get("directory", "user://saves/")
	var path := directory.path_join(slot_name + ".save")

	if not FileAccess.file_exists(path):
		return ErrorCodes.make(ErrorCodes.RESOURCE_NOT_FOUND, "Save slot not found: %s" % path)

	var file := FileAccess.open(path, FileAccess.READ)
	if file == null:
		return ErrorCodes.make(ErrorCodes.INTERNAL_ERROR, "Failed to read save slot: %s" % path)
	var text := file.get_as_text()
	file.close()

	var json := JSON.new()
	if json.parse(text) != OK or not (json.data is Dictionary):
		return ErrorCodes.make(ErrorCodes.INTERNAL_ERROR, "Corrupted save slot format.")

	return {
		"data": json.data
	}


func list_slots(params: Dictionary) -> Dictionary:
	var directory: String = params.get("directory", "user://saves/")
	var slots: Array[Dictionary] = []

	if DirAccess.dir_exists_absolute(directory):
		var dir := DirAccess.open(directory)
		if dir:
			dir.list_dir_begin()
			var fname := dir.get_next()
			while fname != "":
				if not dir.current_is_dir() and fname.ends_with(".save"):
					var slot_name := fname.trim_suffix(".save")
					var full_path := directory.path_join(fname)
					var file := FileAccess.open(full_path, FileAccess.READ)
					var meta := {}
					if file:
						var json := JSON.new()
						if json.parse(file.get_as_text()) == OK and json.data is Dictionary:
							meta = json.data
						file.close()
					slots.append({
						"slot_name": slot_name,
						"path": full_path,
						"timestamp": meta.get("timestamp", ""),
						"has_data": not meta.is_empty(),
					})
				fname = dir.get_next()
			dir.list_dir_end()

	return {
		"data": {
			"directory": directory,
			"count": slots.size(),
			"slots": slots,
		}
	}


func delete_slot(params: Dictionary) -> Dictionary:
	var slot_name: String = params.get("slot_name", "")
	var directory: String = params.get("directory", "user://saves/")
	if slot_name.is_empty():
		return ErrorCodes.make(ErrorCodes.MISSING_REQUIRED_PARAM, "Missing required param: slot_name")

	var path := directory.path_join(slot_name + ".save")
	if not FileAccess.file_exists(path):
		return ErrorCodes.make(ErrorCodes.RESOURCE_NOT_FOUND, "Save slot not found: %s" % path)

	var err := DirAccess.remove_absolute(path)
	if err != OK:
		return ErrorCodes.make(ErrorCodes.INTERNAL_ERROR, "Failed to delete save slot: %s" % path)

	return {
		"data": {
			"slot_name": slot_name,
			"deleted": true,
		}
	}
