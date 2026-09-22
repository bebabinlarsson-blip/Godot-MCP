@tool
extends "res://addons/godot_ai/handlers/command_handler.gd"

const ErrorCodes := preload("res://addons/godot_ai/utils/error_codes.gd")

## Handles OS introspection, Time APIs, Engine time scale, clipboard,
## and environment variables.

var _undo_redo: EditorUndoRedoManager
var _connection: McpConnection


func _init(undo_redo: EditorUndoRedoManager = null, connection: McpConnection = null) -> void:
	_undo_redo = undo_redo
	_connection = connection


func get_system_info(_params: Dictionary) -> Dictionary:
	var os_name := OS.get_name()
	var os_version := OS.get_version()
	var proc_count := OS.get_processor_count()
	var model := OS.get_model_name()
	var video_adapter := RenderingServer.get_video_adapter_name()
	var video_vendor := RenderingServer.get_video_adapter_vendor()

	return {
		"success": true,
		"os_name": os_name,
		"os_version": os_version,
		"processor_count": proc_count,
		"model_name": model,
		"video_adapter": video_adapter,
		"video_vendor": video_vendor,
		"locale": OS.get_locale(),
		"time_scale": Engine.time_scale
	}


func get_time(_params: Dictionary) -> Dictionary:
	var unix_time := Time.get_unix_time_from_system()
	var datetime_str := Time.get_datetime_string_from_system(false, true)
	var datetime_dict := Time.get_datetime_dict_from_system()
	var timezone := Time.get_time_zone_from_system()

	return {
		"success": true,
		"unix_time": unix_time,
		"datetime_string": datetime_str,
		"datetime": datetime_dict,
		"timezone": timezone
	}


func set_time_scale(params: Dictionary) -> Dictionary:
	var scale: float = float(params.get("time_scale", 1.0))
	if scale < 0.0:
		scale = 0.0
	if scale > 100.0:
		scale = 100.0

	Engine.time_scale = scale
	return {
		"success": true,
		"time_scale": Engine.time_scale
	}


func get_clipboard(_params: Dictionary) -> Dictionary:
	var text := DisplayServer.clipboard_get()
	return {
		"success": true,
		"text": text
	}


func set_clipboard(params: Dictionary) -> Dictionary:
	var text: String = params.get("text", "")
	DisplayServer.clipboard_set(text)
	return {
		"success": true,
		"length": text.length()
	}


func get_env(params: Dictionary) -> Dictionary:
	var var_name: String = params.get("var_name", "")
	if var_name.is_empty():
		return {"error": "var_name is required", "code": ErrorCodes.INVALID_PARAMS}

	var val := OS.get_environment(var_name)
	return {
		"success": true,
		"var_name": var_name,
		"value": val,
		"exists": OS.has_environment(var_name)
	}


func set_env(params: Dictionary) -> Dictionary:
	var var_name: String = params.get("var_name", "")
	var val: String = params.get("value", "")
	if var_name.is_empty():
		return {"error": "var_name is required", "code": ErrorCodes.INVALID_PARAMS}

	OS.set_environment(var_name, val)
	return {
		"success": true,
		"var_name": var_name,
		"value": val
	}
