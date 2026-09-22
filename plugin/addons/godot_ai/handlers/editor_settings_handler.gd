@tool
extends "res://addons/godot_ai/handlers/command_handler.gd"

const ErrorCodes := preload("res://addons/godot_ai/utils/error_codes.gd")

## Handles editor persistent configuration via EditorSettings and EditorPaths.

var _undo_redo: EditorUndoRedoManager
var _connection: McpConnection


func _init(undo_redo: EditorUndoRedoManager = null, connection: McpConnection = null) -> void:
	_undo_redo = undo_redo
	_connection = connection


func get_setting(params: Dictionary) -> Dictionary:
	var setting_name: String = params.get("setting_name", "")
	if setting_name.is_empty():
		return {"error": "setting_name is required", "code": ErrorCodes.INVALID_PARAMS}

	var settings := EditorInterface.get_editor_settings()
	if settings == null:
		return {"error": "EditorSettings not available", "code": ErrorCodes.RESOURCE_NOT_FOUND}

	if not settings.has_setting(setting_name):
		return {"error": "Setting not found: %s" % setting_name, "code": ErrorCodes.RESOURCE_NOT_FOUND}

	return {
		"success": true,
		"setting_name": setting_name,
		"value": settings.get_setting(setting_name)
	}


func set_setting(params: Dictionary) -> Dictionary:
	var setting_name: String = params.get("setting_name", "")
	if setting_name.is_empty() or not params.has("value"):
		return {"error": "setting_name and value are required", "code": ErrorCodes.INVALID_PARAMS}

	var settings := EditorInterface.get_editor_settings()
	if settings == null:
		return {"error": "EditorSettings not available", "code": ErrorCodes.RESOURCE_NOT_FOUND}

	settings.set_setting(setting_name, params["value"])
	return {
		"success": true,
		"setting_name": setting_name,
		"value": params["value"]
	}


func list_settings(params: Dictionary) -> Dictionary:
	var prefix: String = params.get("prefix", "")
	var settings := EditorInterface.get_editor_settings()
	if settings == null:
		return {"error": "EditorSettings not available", "code": ErrorCodes.RESOURCE_NOT_FOUND}

	var matching_keys: Array = []
	for p in settings.get_property_list():
		var pname: String = p.get("name", "")
		if prefix.is_empty() or pname.begins_with(prefix):
			matching_keys.append(pname)

	return {
		"success": true,
		"prefix": prefix,
		"settings_count": matching_keys.size(),
		"settings": matching_keys.slice(0, 100)
	}


func get_editor_paths(params: Dictionary) -> Dictionary:
	var paths := EditorInterface.get_editor_paths()
	if paths == null:
		return {"error": "EditorPaths not available", "code": ErrorCodes.RESOURCE_NOT_FOUND}

	return {
		"success": true,
		"config_dir": paths.get_config_dir(),
		"data_dir": paths.get_data_dir(),
		"cache_dir": paths.get_cache_dir(),
		"self_contained": paths.is_self_contained()
	}
