@tool
extends "res://addons/godot_ai/handlers/command_handler.gd"

const ErrorCodes := preload("res://addons/godot_ai/utils/error_codes.gd")

## Handles AudioServer DSP effect additions, removals, configurations, and queries on buses.

var _undo_redo: EditorUndoRedoManager
var _connection: McpConnection


func _init(undo_redo: EditorUndoRedoManager = null, connection: McpConnection = null) -> void:
	_undo_redo = undo_redo
	_connection = connection


func _resolve_bus_index(bus_name_or_idx: Variant) -> int:
	if bus_name_or_idx is int:
		return bus_name_or_idx
	var name_str := str(bus_name_or_idx)
	if name_str.is_valid_int():
		return name_str.to_int()
	return AudioServer.get_bus_index(name_str)


func add_effect_to_bus(params: Dictionary) -> Dictionary:
	var bus_val = params.get("bus_name", "Master")
	var bus_idx := _resolve_bus_index(bus_val)
	if bus_idx < 0 or bus_idx >= AudioServer.bus_count:
		return {"error": "Audio bus not found: %s" % str(bus_val), "code": ErrorCodes.NODE_NOT_FOUND}

	var effect_class: String = params.get("effect_class", "AudioEffectReverb")
	if not effect_class.begins_with("AudioEffect"):
		effect_class = "AudioEffect" + effect_class

	if not ClassDB.class_exists(effect_class):
		return {
			"error": "Unknown AudioEffect class: %s" % effect_class,
			"code": ErrorCodes.INVALID_PARAMS
		}

	var effect_obj = ClassDB.instantiate(effect_class)
	if not (effect_obj is AudioEffect):
		return {
			"error": "Instantiated class is not an AudioEffect: %s" % effect_class,
			"code": ErrorCodes.INVALID_PARAMS
		}

	var at_pos: int = int(params.get("at_position", -1))
	AudioServer.add_bus_effect(bus_idx, effect_obj, at_pos)
	var effect_idx := AudioServer.get_bus_effect_count(bus_idx) - 1
	if at_pos >= 0 and at_pos < AudioServer.get_bus_effect_count(bus_idx):
		effect_idx = at_pos

	var properties: Dictionary = params.get("properties", {})
	for prop in properties:
		effect_obj.set(str(prop), properties[prop])

	return {
		"success": true,
		"bus_index": bus_idx,
		"bus_name": AudioServer.get_bus_name(bus_idx),
		"effect_index": effect_idx,
		"effect_class": effect_class
	}


func configure_effect(params: Dictionary) -> Dictionary:
	var bus_val = params.get("bus_name", "Master")
	var bus_idx := _resolve_bus_index(bus_val)
	if bus_idx < 0 or bus_idx >= AudioServer.bus_count:
		return {"error": "Audio bus not found: %s" % str(bus_val), "code": ErrorCodes.NODE_NOT_FOUND}

	var effect_idx: int = int(params.get("effect_index", 0))
	if effect_idx < 0 or effect_idx >= AudioServer.get_bus_effect_count(bus_idx):
		return {
			"error": "Effect index %d out of bounds on bus %d" % [effect_idx, bus_idx],
			"code": ErrorCodes.VALUE_OUT_OF_RANGE
		}

	var effect: AudioEffect = AudioServer.get_bus_effect(bus_idx, effect_idx)
	if effect == null:
		return {"error": "Effect at index %d is null" % effect_idx, "code": ErrorCodes.NODE_NOT_FOUND}

	var properties: Dictionary = params.get("properties", {})
	for prop in properties:
		effect.set(str(prop), properties[prop])

	if params.has("enabled"):
		AudioServer.set_bus_effect_enabled(bus_idx, effect_idx, bool(params["enabled"]))

	return {
		"success": true,
		"bus_index": bus_idx,
		"bus_name": AudioServer.get_bus_name(bus_idx),
		"effect_index": effect_idx,
		"effect_class": effect.get_class(),
		"configured_count": properties.size()
	}


func remove_effect(params: Dictionary) -> Dictionary:
	var bus_val = params.get("bus_name", "Master")
	var bus_idx := _resolve_bus_index(bus_val)
	if bus_idx < 0 or bus_idx >= AudioServer.bus_count:
		return {"error": "Audio bus not found: %s" % str(bus_val), "code": ErrorCodes.NODE_NOT_FOUND}

	var effect_idx: int = int(params.get("effect_index", 0))
	if effect_idx < 0 or effect_idx >= AudioServer.get_bus_effect_count(bus_idx):
		return {
			"error": "Effect index %d out of bounds on bus %d" % [effect_idx, bus_idx],
			"code": ErrorCodes.VALUE_OUT_OF_RANGE
		}

	AudioServer.remove_bus_effect(bus_idx, effect_idx)

	return {
		"success": true,
		"bus_index": bus_idx,
		"bus_name": AudioServer.get_bus_name(bus_idx),
		"removed_effect_index": effect_idx
	}


func list_bus_effects(params: Dictionary) -> Dictionary:
	var bus_val = params.get("bus_name", "Master")
	var bus_idx := _resolve_bus_index(bus_val)
	if bus_idx < 0 or bus_idx >= AudioServer.bus_count:
		return {"error": "Audio bus not found: %s" % str(bus_val), "code": ErrorCodes.NODE_NOT_FOUND}

	var count := AudioServer.get_bus_effect_count(bus_idx)
	var effects: Array = []
	for i in range(count):
		var eff: AudioEffect = AudioServer.get_bus_effect(bus_idx, i)
		if eff != null:
			effects.append({
				"index": i,
				"class": eff.get_class(),
				"enabled": AudioServer.is_bus_effect_enabled(bus_idx, i)
			})

	return {
		"success": true,
		"bus_index": bus_idx,
		"bus_name": AudioServer.get_bus_name(bus_idx),
		"effects": effects,
		"count": effects.size()
	}
