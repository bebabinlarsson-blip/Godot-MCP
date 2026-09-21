@tool
extends "res://addons/godot_ai/handlers/command_handler.gd"

const ErrorCodes := preload("res://addons/godot_ai/utils/error_codes.gd")

## Handles autoload listing, adding, and removing via ProjectSettings.


func list_autoloads(_params: Dictionary) -> Dictionary:
	var autoloads: Array[Dictionary] = []
	for prop in ProjectSettings.get_property_list():
		var key: String = prop.get("name", "")
		if not key.begins_with("autoload/"):
			continue
		var name := key.substr("autoload/".length())
		var raw_value: String = ProjectSettings.get_setting(key, "")
		var is_singleton := raw_value.begins_with("*")
		var path := raw_value.substr(1) if is_singleton else raw_value
		autoloads.append({
			"name": name,
			"path": path,
			"singleton": is_singleton,
		})
	return {"data": {"autoloads": autoloads, "count": autoloads.size()}}


func add_autoload(params: Dictionary) -> Dictionary:
	var name: String = params.get("name", "")
	var path: String = params.get("path", "")
	var singleton: bool = params.get("singleton", true)

	if name.is_empty():
		return ErrorCodes.make(ErrorCodes.MISSING_REQUIRED_PARAM, "Missing required param: name")
	if path.is_empty():
		return ErrorCodes.make(ErrorCodes.MISSING_REQUIRED_PARAM, "Missing required param: path")
	var path_err = McpPathValidator.path_error(path, "path")
	if path_err != null:
		return path_err
	if not FileAccess.file_exists(path):
		return ErrorCodes.make(ErrorCodes.RESOURCE_NOT_FOUND, "File not found: %s" % path)

	var key := "autoload/%s" % name
	if ProjectSettings.has_setting(key):
		return ErrorCodes.make(ErrorCodes.INVALID_PARAMS, "Autoload '%s' already exists" % name)

	var value := ("*" if singleton else "") + path
	ProjectSettings.set_setting(key, value)
	ProjectSettings.set_initial_value(key, "")
	ProjectSettings.set_as_basic(key, true)
	var err := ProjectSettings.save()
	if err != OK:
		ProjectSettings.clear(key)
		return ErrorCodes.make(ErrorCodes.INTERNAL_ERROR,
			"Failed to save project settings while adding autoload '%s': %s (error %d)" % [name, error_string(err), err])

	return {
		"data": {
			"name": name,
			"path": path,
			"singleton": singleton,
			"undoable": false,
			"reason": "Autoload changes are saved to project.godot",
		}
	}


func remove_autoload(params: Dictionary) -> Dictionary:
	var name: String = params.get("name", "")
	if name.is_empty():
		return ErrorCodes.make(ErrorCodes.MISSING_REQUIRED_PARAM, "Missing required param: name")

	var key := "autoload/%s" % name
	if not ProjectSettings.has_setting(key):
		return ErrorCodes.make(ErrorCodes.NODE_NOT_FOUND, "Autoload '%s' not found" % name)

	var old_value: String = ProjectSettings.get_setting(key, "")
	ProjectSettings.clear(key)
	var err := ProjectSettings.save()
	if err != OK:
		ProjectSettings.set_setting(key, old_value)
		return ErrorCodes.make(ErrorCodes.INTERNAL_ERROR,
			"Failed to save project settings while removing autoload '%s': %s (error %d)" % [name, error_string(err), err])

	return {
		"data": {
			"name": name,
			"removed": true,
			"undoable": false,
			"reason": "Autoload changes are saved to project.godot",
		}
	}


func scaffold_game_manager(params: Dictionary) -> Dictionary:
	var name: String = params.get("name", "GameManager")
	var script_path: String = params.get("script_path", "res://scripts/game_manager.gd")
	var max_lives: int = int(params.get("max_lives", 3))

	var path_err = McpPathValidator.path_error(script_path, "script_path")
	if path_err != null:
		return path_err

	var base_dir := script_path.get_base_dir()
	if not DirAccess.dir_exists_absolute(base_dir):
		DirAccess.make_dir_recursive_absolute(base_dir)

	var code := """extends Node

signal score_changed(new_score: int)
signal lives_changed(new_lives: int)
signal game_over
signal level_completed

var score: int = 0
var lives: int = %d
var current_level: int = 1
var is_game_over: bool = false

func add_score(amount: int) -> void:
	if is_game_over:
		return
	score += amount
	score_changed.emit(score)

func reset_score() -> void:
	score = 0
	score_changed.emit(score)

func take_damage(amount: int = 1) -> void:
	if is_game_over:
		return
	lives = max(lives - amount, 0)
	lives_changed.emit(lives)
	if lives <= 0:
		trigger_game_over()

func add_lives(amount: int = 1) -> void:
	if is_game_over:
		return
	lives += amount
	lives_changed.emit(lives)

func trigger_game_over() -> void:
	is_game_over = true
	game_over.emit()

func trigger_level_complete() -> void:
	level_completed.emit()

func restart_game() -> void:
	score = 0
	lives = %d
	is_game_over = false
	score_changed.emit(score)
	lives_changed.emit(lives)
	get_tree().reload_current_scene()

func change_scene(scene_path: String) -> void:
	get_tree().change_scene_to_file(scene_path)
""" % [max_lives, max_lives]

	var file := FileAccess.open(script_path, FileAccess.WRITE)
	if file == null:
		return ErrorCodes.make(ErrorCodes.INTERNAL_ERROR, "Failed to create script file at %s" % script_path)
	file.store_string(code)
	file.close()

	EditorInterface.get_resource_filesystem().reindex_file(script_path)

	var key := "autoload/%s" % name
	var value := "*" + script_path
	ProjectSettings.set_setting(key, value)
	ProjectSettings.set_initial_value(key, "")
	ProjectSettings.set_as_basic(key, true)
	var err := ProjectSettings.save()
	if err != OK:
		return ErrorCodes.make(ErrorCodes.INTERNAL_ERROR,
			"Failed to save project settings while registering autoload '%s': %s (error %d)" % [name, error_string(err), err])

	return {
		"data": {
			"name": name,
			"path": script_path,
			"singleton": true,
			"max_lives": max_lives,
			"undoable": false,
			"reason": "Autoload changes are saved to project.godot",
		}
	}

