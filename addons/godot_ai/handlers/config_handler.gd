@tool
extends "res://addons/godot_ai/handlers/command_handler.gd"

const ErrorCodes := preload("res://addons/godot_ai/utils/error_codes.gd")

## Handles ConfigFile INI reading/writing, JSON parsing/generation, and Expression evaluation.

var _undo_redo: EditorUndoRedoManager
var _connection: McpConnection


func _init(undo_redo: EditorUndoRedoManager = null, connection: McpConnection = null) -> void:
	_undo_redo = undo_redo
	_connection = connection


func config_read(params: Dictionary) -> Dictionary:
	var file_path: String = params.get("file_path", "")
	if file_path.is_empty():
		return {"error": "file_path is required", "code": ErrorCodes.INVALID_PARAMS}
	if not file_path.begins_with("res://") and not file_path.begins_with("user://"):
		file_path = "res://" + file_path

	var cfg := ConfigFile.new()
	var err := cfg.load(file_path)
	if err != OK:
		return {"error": "Failed to load ConfigFile: %s (code %d)" % [file_path, err], "code": ErrorCodes.INTERNAL_ERROR}

	var section: String = params.get("section", "")
	var key: String = params.get("key", "")

	if not section.is_empty() and not key.is_empty():
		return {
			"success": true,
			"section": section,
			"key": key,
			"value": cfg.get_value(section, key, null)
		}

	var result: Dictionary = {}
	for s in cfg.get_sections():
		result[s] = {}
		for k in cfg.get_section_keys(s):
			result[s][k] = cfg.get_value(s, k)

	return {
		"success": true,
		"file_path": file_path,
		"data": result
	}


func config_write(params: Dictionary) -> Dictionary:
	var file_path: String = params.get("file_path", "")
	var section: String = params.get("section", "")
	var key: String = params.get("key", "")

	if file_path.is_empty() or section.is_empty() or key.is_empty() or not params.has("value"):
		return {"error": "file_path, section, key, and value are required", "code": ErrorCodes.INVALID_PARAMS}

	if not file_path.begins_with("res://") and not file_path.begins_with("user://"):
		file_path = "res://" + file_path

	var cfg := ConfigFile.new()
	if FileAccess.file_exists(file_path):
		var _load_err := cfg.load(file_path)

	cfg.set_value(section, key, params["value"])
	var err := cfg.save(file_path)
	if err != OK:
		return {"error": "Failed to save ConfigFile: %s (code %d)" % [file_path, err], "code": ErrorCodes.INTERNAL_ERROR}

	return {
		"success": true,
		"file_path": file_path,
		"section": section,
		"key": key
	}


func json_parse(params: Dictionary) -> Dictionary:
	var json_string: String = params.get("json_string", "")
	var parsed = JSON.parse_string(json_string)
	if parsed == null and not json_string.strip_edges() == "null":
		return {"error": "Failed to parse JSON string", "code": ErrorCodes.INVALID_PARAMS}

	return {
		"success": true,
		"data": parsed
	}


func json_generate(params: Dictionary) -> Dictionary:
	if not params.has("data"):
		return {"error": "data parameter is required", "code": ErrorCodes.INVALID_PARAMS}

	var indent: String = params.get("indent", "")
	var json_str := JSON.stringify(params["data"], indent)

	return {
		"success": true,
		"json_string": json_str
	}


func expression_eval(params: Dictionary) -> Dictionary:
	var expr_str: String = params.get("expression_string", "")
	if expr_str.is_empty():
		return {"error": "expression_string is required", "code": ErrorCodes.INVALID_PARAMS}

	var expr := Expression.new()
	var input_names: Array = params.get("input_names", [])
	var input_values: Array = params.get("input_values", [])

	var names_packed := PackedStringArray()
	for n in input_names:
		names_packed.append(str(n))

	var err := expr.parse(expr_str, names_packed)
	if err != OK:
		return {"error": "Failed to parse expression: %s (code %d)" % [expr.get_error_text_or_empty() if expr.has_method("get_error_text_or_empty") else str(err), err], "code": ErrorCodes.INVALID_PARAMS}

	var result = expr.execute(input_values, null, true)
	if expr.has_execute_failed():
		return {"error": "Expression execution failed", "code": ErrorCodes.INTERNAL_ERROR}

	return {
		"success": true,
		"expression": expr_str,
		"result": result
	}
