@tool
extends "res://addons/godot_ai/handlers/command_handler.gd"

const ErrorCodes := preload("res://addons/godot_ai/utils/error_codes.gd")

## Handles headless execution, CLI commands, scripts, scenes, and engine introspection.

var _undo_redo: EditorUndoRedoManager
var _connection: McpConnection


func _init(undo_redo: EditorUndoRedoManager = null, connection: McpConnection = null) -> void:
	_undo_redo = undo_redo
	_connection = connection


func get_engine_info(params: Dictionary = {}) -> Dictionary:
	var v_info := Engine.get_version_info()
	return {
		"success": true,
		"version": Engine.get_version_info(),
		"version_string": "%d.%d.%d.%s" % [v_info.major, v_info.minor, v_info.patch, v_info.status],
		"executable_path": OS.get_executable_path(),
		"cmdline_args": OS.get_cmdline_args(),
		"is_editor": Engine.is_editor_hint(),
		"platform": OS.get_name(),
		"headless_supported": true
	}


func run_script(params: Dictionary) -> Dictionary:
	var script_path: String = params.get("script_path", "")
	var inline_code: String = params.get("inline_code", "")

	if script_path.is_empty() and inline_code.is_empty():
		return {"error": "Must provide either script_path or inline_code", "code": ErrorCodes.INVALID_PARAMS}

	if not script_path.is_empty():
		var godot_bin := OS.get_executable_path()
		var args := PackedStringArray(["--headless", "-s", script_path])
		var output: Array = []
		var exit_code := OS.execute(godot_bin, args, output, true)
		return {
			"success": exit_code == 0,
			"exit_code": exit_code,
			"output": "".join(output),
			"script_path": script_path
		}

	# Run inline code dynamically
	var script := GDScript.new()
	script.source_code = (
		"@tool\nextends RefCounted\nfunc run() -> Variant:\n"
		+ "\t" + inline_code.replace("\n", "\n\t") + "\n"
	)
	var err := script.reload()
	if err != OK:
		return {"error": "Failed to compile inline script: %d" % err, "code": ErrorCodes.INVALID_PARAMS}

	var instance = script.new()
	var result = null
	if instance.has_method("run"):
		result = instance.run()

	return {
		"success": true,
		"result": result
	}


func run_headless_scene(params: Dictionary) -> Dictionary:
	var scene_path: String = params.get("scene_path", "")
	if scene_path.is_empty():
		return {"error": "scene_path is required", "code": ErrorCodes.INVALID_PARAMS}

	var godot_bin := OS.get_executable_path()
	var args := PackedStringArray(["--headless", scene_path, "--quit-after", str(params.get("quit_after_frames", 60))])
	var output: Array = []
	var exit_code := OS.execute(godot_bin, args, output, true)

	return {
		"success": exit_code == 0,
		"exit_code": exit_code,
		"output": "".join(output),
		"scene_path": scene_path
	}


func export_project_cli(params: Dictionary) -> Dictionary:
	var preset: String = params.get("preset", "")
	var output_path: String = params.get("output_path", "")
	if preset.is_empty() or output_path.is_empty():
		return {"error": "preset and output_path are required", "code": ErrorCodes.INVALID_PARAMS}

	var is_debug: bool = params.get("is_debug", false)
	var godot_bin := OS.get_executable_path()
	var flag := "--export-debug" if is_debug else "--export-release"
	var args := PackedStringArray(["--headless", flag, preset, output_path])
	var output: Array = []
	var exit_code := OS.execute(godot_bin, args, output, true)

	return {
		"success": exit_code == 0,
		"exit_code": exit_code,
		"output": "".join(output),
		"preset": preset,
		"output_path": output_path
	}


func reimport_assets_cli(params: Dictionary = {}) -> Dictionary:
	var godot_bin := OS.get_executable_path()
	var args := PackedStringArray(["--editor", "--headless", "--quit"])
	var output: Array = []
	var exit_code := OS.execute(godot_bin, args, output, true)

	return {
		"success": exit_code == 0,
		"exit_code": exit_code,
		"output": "".join(output)
	}
