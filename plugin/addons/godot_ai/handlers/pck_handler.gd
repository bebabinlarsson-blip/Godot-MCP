@tool
extends "res://addons/godot_ai/handlers/command_handler.gd"

const ErrorCodes := preload("res://addons/godot_ai/utils/error_codes.gd")

## Handles PCK package creation and dynamic mounting via ProjectSettings.

var _undo_redo: EditorUndoRedoManager
var _connection: McpConnection


func _init(undo_redo: EditorUndoRedoManager = null, connection: McpConnection = null) -> void:
	_undo_redo = undo_redo
	_connection = connection


func create_pck(params: Dictionary) -> Dictionary:
	var pck_path: String = params.get("pck_path", "")
	var files: Array = params.get("files", [])
	var alignment: int = int(params.get("alignment", 32))

	if pck_path.is_empty():
		return {"error": "pck_path is required", "code": ErrorCodes.INVALID_PARAMS}

	if not pck_path.begins_with("res://") and not pck_path.begins_with("user://"):
		pck_path = "res://" + pck_path

	var packer := PCKPacker.new()
	var err := packer.pck_start(pck_path, alignment)
	if err != OK:
		return {"error": "Failed to start PCKPacker for: %s (code %d)" % [pck_path, err], "code": ErrorCodes.INTERNAL_ERROR}

	var packed_count := 0
	for f in files:
		var file_str: String = str(f)
		if not file_str.begins_with("res://"):
			file_str = "res://" + file_str
		if FileAccess.file_exists(file_str):
			var add_err: int = packer.pck_add_file(file_str, file_str)
			if add_err == OK:
				packed_count += 1

	var flush_err: int = packer.flush(true)
	if flush_err != OK:
		return {"error": "Failed to flush PCKPacker", "code": ErrorCodes.INTERNAL_ERROR}

	return {
		"success": true,
		"pck_path": pck_path,
		"packed_files": packed_count
	}


func load_pck(params: Dictionary) -> Dictionary:
	var pck_path: String = params.get("pck_path", "")
	var replace_files: bool = params.get("replace_files", true)

	if pck_path.is_empty():
		return {"error": "pck_path is required", "code": ErrorCodes.INVALID_PARAMS}

	if not pck_path.begins_with("res://") and not pck_path.begins_with("user://"):
		pck_path = "res://" + pck_path

	var loaded := ProjectSettings.load_resource_pack(pck_path, replace_files)
	return {
		"success": loaded,
		"pck_path": pck_path,
		"replace_files": replace_files
	}


func inspect_pck(params: Dictionary) -> Dictionary:
	var pck_path: String = params.get("pck_path", "")

	if pck_path.is_empty():
		return {"error": "pck_path is required", "code": ErrorCodes.INVALID_PARAMS}

	if not pck_path.begins_with("res://") and not pck_path.begins_with("user://"):
		pck_path = "res://" + pck_path

	var exists := FileAccess.file_exists(pck_path)
	var file_size := 0
	if exists:
		var f := FileAccess.open(pck_path, FileAccess.READ)
		if f != null:
			file_size = f.get_length()
			f.close()

	return {
		"success": exists,
		"pck_path": pck_path,
		"exists": exists,
		"size_bytes": file_size
	}
