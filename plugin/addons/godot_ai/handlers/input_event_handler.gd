@tool
extends "res://addons/godot_ai/handlers/command_handler.gd"

const ErrorCodes := preload("res://addons/godot_ai/utils/error_codes.gd")

## Handles input event simulation, virtual action triggering, and input replay.

var _undo_redo: EditorUndoRedoManager
var _connection: McpConnection


func _init(undo_redo: EditorUndoRedoManager = null, connection: McpConnection = null) -> void:
	_undo_redo = undo_redo
	_connection = connection


func simulate_action(params: Dictionary) -> Dictionary:
	var action: String = params.get("action", "")
	if action.is_empty():
		return {"error": "action name must not be empty."}

	var pressed: bool = params.get("pressed", true)
	var strength: float = float(params.get("strength", 1.0))

	if pressed:
		Input.action_press(action, strength)
	else:
		Input.action_release(action)

	return {
		"status": "ok",
		"action": action,
		"pressed": pressed,
		"strength": strength,
	}


func simulate_key(params: Dictionary) -> Dictionary:
	var key_val = params.get("key", "")
	var pressed: bool = params.get("pressed", true)
	var echo: bool = params.get("echo", false)
	var shift: bool = params.get("shift", false)
	var ctrl: bool = params.get("ctrl", false)
	var alt: bool = params.get("alt", false)

	var ev := InputEventKey.new()
	if key_val is int:
		ev.keycode = key_val
	elif key_val is String:
		var key_str: String = key_val
		if key_str.length() == 1:
			ev.keycode = OS.find_keycode_from_string(key_str)
		else:
			ev.keycode = OS.find_keycode_from_string(key_str)

	ev.pressed = pressed
	ev.echo = echo
	ev.shift_pressed = shift
	ev.ctrl_pressed = ctrl
	ev.alt_pressed = alt

	Input.parse_input_event(ev)
	return {
		"status": "ok",
		"key": str(key_val),
		"keycode": ev.keycode,
		"pressed": pressed,
	}


func simulate_mouse_button(params: Dictionary) -> Dictionary:
	var button_index: int = int(params.get("button_index", 1))
	var pressed: bool = params.get("pressed", true)
	var pos_arr: Array = params.get("position", [0.0, 0.0])

	var ev := InputEventMouseButton.new()
	ev.button_index = button_index as MouseButton
	ev.pressed = pressed
	if pos_arr.size() >= 2:
		ev.position = Vector2(float(pos_arr[0]), float(pos_arr[1]))
		ev.global_position = ev.position

	Input.parse_input_event(ev)
	return {
		"status": "ok",
		"button_index": button_index,
		"pressed": pressed,
		"position": [ev.position.x, ev.position.y],
	}


func simulate_mouse_motion(params: Dictionary) -> Dictionary:
	var pos_arr: Array = params.get("position", [0.0, 0.0])
	var rel_arr: Array = params.get("relative", [0.0, 0.0])
	var vel_arr: Array = params.get("velocity", [0.0, 0.0])

	var ev := InputEventMouseMotion.new()
	if pos_arr.size() >= 2:
		ev.position = Vector2(float(pos_arr[0]), float(pos_arr[1]))
		ev.global_position = ev.position
	if rel_arr.size() >= 2:
		ev.relative = Vector2(float(rel_arr[0]), float(rel_arr[1]))
	if vel_arr.size() >= 2:
		ev.velocity = Vector2(float(vel_arr[0]), float(vel_arr[1]))

	Input.parse_input_event(ev)
	return {
		"status": "ok",
		"position": [ev.position.x, ev.position.y],
		"relative": [ev.relative.x, ev.relative.y],
	}


func replay_macro(params: Dictionary) -> Dictionary:
	var events: Array = params.get("events", [])
	var processed_count: int = 0

	for ev_item in events:
		if not ev_item is Dictionary:
			continue
		var ev_type: String = ev_item.get("type", "action")
		if ev_type == "action":
			simulate_action(ev_item)
		elif ev_type == "key":
			simulate_key(ev_item)
		elif ev_type == "mouse_button":
			simulate_mouse_button(ev_item)
		elif ev_type == "mouse_motion":
			simulate_mouse_motion(ev_item)
		processed_count += 1

	return {"status": "ok", "dispatched_events": processed_count}


func get_input_state(params: Dictionary) -> Dictionary:
	var action: String = params.get("action", "")
	if action.is_empty():
		return {"error": "action name must not be empty."}

	var is_pressed: bool = Input.is_action_pressed(action)
	var strength: float = Input.get_action_strength(action)

	return {
		"status": "ok",
		"action": action,
		"is_pressed": is_pressed,
		"strength": strength,
	}
