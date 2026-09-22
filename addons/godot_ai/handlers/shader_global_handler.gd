@tool
extends "res://addons/godot_ai/handlers/command_handler.gd"

const ErrorCodes := preload("res://addons/godot_ai/utils/error_codes.gd")

## Handles Global Shader Parameters via RenderingServer and ProjectSettings.

var _undo_redo: EditorUndoRedoManager
var _connection: McpConnection


func _init(undo_redo: EditorUndoRedoManager = null, connection: McpConnection = null) -> void:
	_undo_redo = undo_redo
	_connection = connection


func list_globals(_params: Dictionary) -> Dictionary:
	var names: PackedStringArray = RenderingServer.global_shader_parameter_get_list()
	var globals: Array = []

	for g_name in names:
		var g_type := RenderingServer.global_shader_parameter_get_type(g_name)
		var g_val = RenderingServer.global_shader_parameter_get(g_name)
		globals.append({
			"name": g_name,
			"type": g_type,
			"value": str(g_val)
		})

	return {
		"success": true,
		"count": globals.size(),
		"parameters": globals
	}


func set_global(params: Dictionary) -> Dictionary:
	var g_name: String = params.get("name", "")
	if g_name.is_empty():
		return {"error": "name is required", "code": ErrorCodes.INVALID_PARAMS}

	var val = params.get("value")
	var g_type := RenderingServer.global_shader_parameter_get_type(g_name)
	var final_val = val

	# Convert arrays to appropriate Vector/Color types if needed
	if val is Array:
		if val.size() == 2:
			final_val = Vector2(float(val[0]), float(val[1]))
		elif val.size() == 3:
			final_val = Vector3(float(val[0]), float(val[1]), float(val[2]))
		elif val.size() == 4:
			final_val = Color(float(val[0]), float(val[1]), float(val[2]), float(val[3]))

	RenderingServer.global_shader_parameter_set(g_name, final_val)
	return {
		"success": true,
		"name": g_name,
		"type": g_type
	}


func add_global(params: Dictionary) -> Dictionary:
	var g_name: String = params.get("name", "")
	if g_name.is_empty():
		return {"error": "name is required", "code": ErrorCodes.INVALID_PARAMS}

	var type_str: String = params.get("type", "float").to_lower()
	var val = params.get("value")

	var param_type := RenderingServer.GLOBAL_VAR_TYPE_FLOAT
	var default_val: Variant = 0.0

	match type_str:
		"bool":
			param_type = RenderingServer.GLOBAL_VAR_TYPE_BOOL
			default_val = bool(val) if val != null else false
		"int":
			param_type = RenderingServer.GLOBAL_VAR_TYPE_INT
			default_val = int(val) if val != null else 0
		"color":
			param_type = RenderingServer.GLOBAL_VAR_TYPE_COLOR
			default_val = Color(1, 1, 1, 1)
			if val is Array and val.size() >= 3:
				default_val = Color(float(val[0]), float(val[1]), float(val[2]), float(val[3]) if val.size() >= 4 else 1.0)
		"vec2":
			param_type = RenderingServer.GLOBAL_VAR_TYPE_VEC2
			default_val = Vector2.ZERO
			if val is Array and val.size() >= 2:
				default_val = Vector2(float(val[0]), float(val[1]))
		"vec3":
			param_type = RenderingServer.GLOBAL_VAR_TYPE_VEC3
			default_val = Vector3.ZERO
			if val is Array and val.size() >= 3:
				default_val = Vector3(float(val[0]), float(val[1]), float(val[2]))
		"vec4":
			param_type = RenderingServer.GLOBAL_VAR_TYPE_VEC4
			default_val = Vector4.ZERO
			if val is Array and val.size() >= 4:
				default_val = Vector4(float(val[0]), float(val[1]), float(val[2]), float(val[3]))
		_:
			param_type = RenderingServer.GLOBAL_VAR_TYPE_FLOAT
			default_val = float(val) if val != null else 0.0

	RenderingServer.global_shader_parameter_add(g_name, param_type, default_val)

	# Store in ProjectSettings for persistence
	var setting_name := "shader_globals/" + g_name
	ProjectSettings.set_setting(setting_name, {
		"type": type_str,
		"value": default_val
	})
	ProjectSettings.save()

	return {
		"success": true,
		"name": g_name,
		"type": type_str,
		"value": str(default_val)
	}


func remove_global(params: Dictionary) -> Dictionary:
	var g_name: String = params.get("name", "")
	if g_name.is_empty():
		return {"error": "name is required", "code": ErrorCodes.INVALID_PARAMS}

	RenderingServer.global_shader_parameter_remove(g_name)

	var setting_name := "shader_globals/" + g_name
	if ProjectSettings.has_setting(setting_name):
		ProjectSettings.set_setting(setting_name, null)
		ProjectSettings.save()

	return {
		"success": true,
		"name": g_name
	}
