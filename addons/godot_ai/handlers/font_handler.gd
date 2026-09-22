@tool
extends "res://addons/godot_ai/handlers/command_handler.gd"

const ErrorCodes := preload("res://addons/godot_ai/utils/error_codes.gd")

## Handles fonts, SystemFont, FontVariation, and LabelSettings.

var _undo_redo: EditorUndoRedoManager
var _connection: McpConnection


func _init(undo_redo: EditorUndoRedoManager = null, connection: McpConnection = null) -> void:
	_undo_redo = undo_redo
	_connection = connection


func create_system_font(params: Dictionary) -> Dictionary:
	var font_names: Array = params.get("font_names", ["Sans-Serif"])
	var italic: bool = params.get("italic", false)
	var weight: int = int(params.get("weight", 400))
	var save_path: String = params.get("save_path", "")

	var font := SystemFont.new()
	var names_packed := PackedStringArray()
	for n in font_names:
		names_packed.append(str(n))
	font.font_names = names_packed
	font.font_italic = italic
	font.font_weight = weight

	if not save_path.is_empty():
		if not save_path.begins_with("res://"):
			save_path = "res://" + save_path
		var err := ResourceSaver.save(font, save_path)
		if err != OK:
			return {"error": "Failed to save SystemFont to: %s" % save_path, "code": ErrorCodes.INTERNAL_ERROR}

	return {
		"success": true,
		"font_names": font_names,
		"italic": italic,
		"weight": weight,
		"save_path": save_path
	}


func create_font_variation(params: Dictionary) -> Dictionary:
	var base_font_path: String = params.get("base_font_path", "")
	var variation_embolden: float = float(params.get("variation_embolden", 0.0))
	var save_path: String = params.get("save_path", "")

	if base_font_path.is_empty():
		return {"error": "base_font_path is required", "code": ErrorCodes.INVALID_PARAMS}
	if not base_font_path.begins_with("res://"):
		base_font_path = "res://" + base_font_path

	if not ResourceLoader.exists(base_font_path):
		return {"error": "Base font file not found: %s" % base_font_path, "code": ErrorCodes.RESOURCE_NOT_FOUND}

	var base_font = load(base_font_path)
	if not base_font is Font:
		return {"error": "Resource is not a Font: %s" % base_font_path, "code": ErrorCodes.WRONG_TYPE}

	var variation := FontVariation.new()
	variation.base_font = base_font
	variation.variation_embolden = variation_embolden

	if not save_path.is_empty():
		if not save_path.begins_with("res://"):
			save_path = "res://" + save_path
		var err := ResourceSaver.save(variation, save_path)
		if err != OK:
			return {"error": "Failed to save FontVariation to: %s" % save_path, "code": ErrorCodes.INTERNAL_ERROR}

	return {
		"success": true,
		"base_font": base_font_path,
		"variation_embolden": variation_embolden,
		"save_path": save_path
	}


func create_label_settings(params: Dictionary) -> Dictionary:
	var font_path: String = params.get("font_path", "")
	var font_size: int = int(params.get("font_size", 16))
	var font_color_str: String = params.get("font_color", "#ffffff")
	var outline_size: int = int(params.get("outline_size", 0))
	var outline_color_str: String = params.get("outline_color", "#000000")
	var shadow_size: int = int(params.get("shadow_size", 0))
	var shadow_color_str: String = params.get("shadow_color", "#000000")
	var save_path: String = params.get("save_path", "")

	var settings := LabelSettings.new()
	settings.font_size = font_size
	settings.font_color = Color.from_string(font_color_str, Color.WHITE)
	settings.outline_size = outline_size
	settings.outline_color = Color.from_string(outline_color_str, Color.BLACK)
	settings.shadow_size = shadow_size
	settings.shadow_color = Color.from_string(shadow_color_str, Color.BLACK)

	if not font_path.is_empty():
		if not font_path.begins_with("res://"):
			font_path = "res://" + font_path
		if ResourceLoader.exists(font_path):
			var font_res = load(font_path)
			if font_res is Font:
				settings.font = font_res

	if not save_path.is_empty():
		if not save_path.begins_with("res://"):
			save_path = "res://" + save_path
		var err := ResourceSaver.save(settings, save_path)
		if err != OK:
			return {"error": "Failed to save LabelSettings to: %s" % save_path, "code": ErrorCodes.INTERNAL_ERROR}

	return {
		"success": true,
		"font_size": font_size,
		"save_path": save_path
	}


func get_font_info(params: Dictionary) -> Dictionary:
	var font_path: String = params.get("font_path", "")
	if font_path.is_empty():
		return {"error": "font_path is required", "code": ErrorCodes.INVALID_PARAMS}
	if not font_path.begins_with("res://"):
		font_path = "res://" + font_path

	if not ResourceLoader.exists(font_path):
		return {"error": "Font file not found: %s" % font_path, "code": ErrorCodes.RESOURCE_NOT_FOUND}

	var res = load(font_path)
	if not res is Font:
		return {"error": "Resource is not a Font: %s" % font_path, "code": ErrorCodes.WRONG_TYPE}

	var font: Font = res
	return {
		"success": true,
		"font_path": font_path,
		"class": font.get_class(),
		"is_system_font": font is SystemFont,
		"is_variation": font is FontVariation
	}
