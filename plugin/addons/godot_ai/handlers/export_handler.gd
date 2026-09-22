@tool
extends "res://addons/godot_ai/handlers/command_handler.gd"

const ErrorCodes := preload("res://addons/godot_ai/utils/error_codes.gd")

## Handles project export presets inspection, build target validation,
## and headless export execution.

var _undo_redo: EditorUndoRedoManager
var _connection: McpConnection


func _init(undo_redo: EditorUndoRedoManager = null, connection: McpConnection = null) -> void:
	_undo_redo = undo_redo
	_connection = connection


func list_presets(_params: Dictionary) -> Dictionary:
	var cfg_path := "res://export_presets.cfg"
	if not FileAccess.file_exists(cfg_path):
		return {
			"data": {
				"presets": [],
				"presets_count": 0,
				"config_file_exists": false,
			}
		}

	var config := ConfigFile.new()
	var err := config.load(cfg_path)
	if err != OK:
		return ErrorCodes.make(ErrorCodes.RESOURCE_NOT_FOUND, "Failed to load export_presets.cfg: %d" % err)

	var presets: Array = []
	for section in config.get_sections():
		if section.ends_with(".options"):
			continue
		var name: String = config.get_value(section, "name", "")
		var platform: String = config.get_value(section, "platform", "")
		var export_path: String = config.get_value(section, "export_path", "")
		var runnable: bool = bool(config.get_value(section, "runnable", false))
		presets.append({
			"id": section,
			"name": name,
			"platform": platform,
			"export_path": export_path,
			"runnable": runnable,
		})

	return {
		"data": {
			"presets": presets,
			"presets_count": presets.size(),
			"config_file_exists": true,
		}
	}


func get_preset_info(params: Dictionary) -> Dictionary:
	var preset_name: String = params.get("preset_name", "")
	if preset_name.is_empty():
		return ErrorCodes.make(ErrorCodes.INVALID_PARAMS, "preset_name must be specified")

	var cfg_path := "res://export_presets.cfg"
	if not FileAccess.file_exists(cfg_path):
		return ErrorCodes.make(ErrorCodes.RESOURCE_NOT_FOUND, "export_presets.cfg does not exist")

	var config := ConfigFile.new()
	var err := config.load(cfg_path)
	if err != OK:
		return ErrorCodes.make(ErrorCodes.RESOURCE_NOT_FOUND, "Failed to parse export_presets.cfg: %d" % err)

	var target_section := ""
	for section in config.get_sections():
		if section.ends_with(".options"):
			continue
		if config.get_value(section, "name", "") == preset_name:
			target_section = section
			break

	if target_section.is_empty():
		return ErrorCodes.make(ErrorCodes.NODE_NOT_FOUND, "Preset not found: %s" % preset_name)

	var details: Dictionary = {}
	for key in config.get_section_keys(target_section):
		details[key] = config.get_value(target_section, key)

	var opt_section := target_section + ".options"
	var options: Dictionary = {}
	if config.has_section(opt_section):
		for key in config.get_section_keys(opt_section):
			options[key] = config.get_value(opt_section, key)

	return {
		"data": {
			"name": preset_name,
			"preset_id": target_section,
			"details": details,
			"options": options,
		}
	}


func run_export(params: Dictionary) -> Dictionary:
	var preset_name: String = params.get("preset_name", "")
	if preset_name.is_empty():
		return ErrorCodes.make(ErrorCodes.INVALID_PARAMS, "preset_name must be specified")

	var output_path: String = params.get("output_path", "")
	var is_debug: bool = bool(params.get("debug", false))

	var export_mode := "--export-debug" if is_debug else "--export-release"
	var godot_bin := OS.get_executable_path()

	var args := ["--headless", export_mode, preset_name]
	if not output_path.is_empty():
		args.append(output_path)

	var output_lines: Array = []
	var exit_code := OS.execute(godot_bin, args, output_lines, true)

	return {
		"data": {
			"preset_name": preset_name,
			"output_path": output_path,
			"is_debug": is_debug,
			"exit_code": exit_code,
			"output": "".join(output_lines),
			"command": "%s %s" % [godot_bin, " ".join(args)],
		}
	}
