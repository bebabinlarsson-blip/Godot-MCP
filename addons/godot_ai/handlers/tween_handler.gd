@tool
extends "res://addons/godot_ai/handlers/command_handler.gd"

const ErrorCodes := preload("res://addons/godot_ai/utils/error_codes.gd")

## Handles Godot Tween creation, procedural motion presets (juice/game feel),
## and procedural tween code generation.

var _undo_redo: EditorUndoRedoManager
var _connection: McpConnection


func _init(undo_redo: EditorUndoRedoManager, connection: McpConnection = null) -> void:
	_undo_redo = undo_redo
	_connection = connection


func _get_scene_root() -> Node:
	if Engine.is_editor_hint():
		var tree := Engine.get_main_loop() as SceneTree
		if tree != null and Engine.has_singleton("EditorInterface"):
			var editor_interface := Engine.get_singleton("EditorInterface")
			if editor_interface.has_method("get_edited_scene_root"):
				var root: Node = editor_interface.get_edited_scene_root()
				if root != null:
					return root
		if tree != null and tree.edited_scene_root != null:
			return tree.edited_scene_root
		if tree != null and tree.current_scene != null:
			return tree.current_scene
		if tree != null and tree.root != null:
			return tree.root
	return null


func _resolve_node(scene_root: Node, node_path: String) -> Node:
	if node_path.is_empty():
		return scene_root
	return scene_root.get_node_or_null(NodePath(node_path))


func _parse_trans_type(trans_str: String) -> Tween.TransitionType:
	match trans_str.to_lower():
		"sine": return Tween.TRANS_SINE
		"quint": return Tween.TRANS_QUINT
		"quart": return Tween.TRANS_QUART
		"quad": return Tween.TRANS_QUAD
		"expo": return Tween.TRANS_EXPO
		"elastic": return Tween.TRANS_ELASTIC
		"cubic": return Tween.TRANS_CUBIC
		"circ": return Tween.TRANS_CIRC
		"bounce": return Tween.TRANS_BOUNCE
		"back": return Tween.TRANS_BACK
		"spring": return Tween.TRANS_SPRING
		_: return Tween.TRANS_LINEAR


func _parse_ease_type(ease_str: String) -> Tween.EaseType:
	match ease_str.to_lower():
		"in": return Tween.EASE_IN
		"out": return Tween.EASE_OUT
		"in_out": return Tween.EASE_IN_OUT
		"out_in": return Tween.EASE_OUT_IN
		_: return Tween.EASE_IN_OUT


func _parse_variant(val: Variant, current_val: Variant) -> Variant:
	if val is Array:
		var arr := val as Array
		if current_val is Vector2 or current_val is Vector2i:
			if arr.size() >= 2:
				return Vector2(float(arr[0]), float(arr[1]))
		elif current_val is Vector3 or current_val is Vector3i:
			if arr.size() >= 3:
				return Vector3(float(arr[0]), float(arr[1]), float(arr[2]))
		elif current_val is Color:
			if arr.size() >= 4:
				return Color(float(arr[0]), float(arr[1]), float(arr[2]), float(arr[3]))
			elif arr.size() >= 3:
				return Color(float(arr[0]), float(arr[1]), float(arr[2]))
	return val


func create_tween(params: Dictionary) -> Dictionary:
	var scene_root := _get_scene_root()
	if scene_root == null:
		return ErrorCodes.make(ErrorCodes.EDITOR_NOT_READY, "No active scene to create tween in")

	var node_path: String = params.get("node_path", "")
	if node_path.is_empty():
		return ErrorCodes.make(ErrorCodes.INVALID_PARAMS, "node_path must be specified")

	var target_node := _resolve_node(scene_root, node_path)
	if target_node == null:
		return ErrorCodes.make(ErrorCodes.NODE_NOT_FOUND, "Target node not found at %s" % node_path)

	var prop: String = params.get("property", "")
	if prop.is_empty():
		return ErrorCodes.make(ErrorCodes.INVALID_PARAMS, "property must be specified")

	var current_val = target_node.get_indexed(NodePath(prop))
	var raw_target = params.get("target_value")
	var final_val = _parse_variant(raw_target, current_val)
	var duration: float = float(params.get("duration", 0.5))
	var trans_str: String = params.get("trans_type", "linear")
	var ease_str: String = params.get("ease_type", "in_out")
	var delay: float = float(params.get("delay", 0.0))
	var relative: bool = bool(params.get("relative", false))

	var trans := _parse_trans_type(trans_str)
	var ease_mode := _parse_ease_type(ease_str)

	var tween := target_node.create_tween()
	tween.set_trans(trans).set_ease(ease_mode)

	var prop_tweener = tween.tween_property(target_node, NodePath(prop), final_val, duration)
	if delay > 0.0:
		prop_tweener.set_delay(delay)
	if relative:
		prop_tweener.as_relative()

	return {
		"data": {
			"node_path": str(target_node.get_path()),
			"property": prop,
			"initial_value": current_val,
			"target_value": final_val,
			"duration": duration,
			"trans_type": trans_str,
			"ease_type": ease_str,
			"delay": delay,
			"relative": relative,
			"tween_started": true,
		}
	}


func preset_animation(params: Dictionary) -> Dictionary:
	var scene_root := _get_scene_root()
	if scene_root == null:
		return ErrorCodes.make(ErrorCodes.EDITOR_NOT_READY, "No active scene to execute preset animation in")

	var node_path: String = params.get("node_path", "")
	var target_node := _resolve_node(scene_root, node_path)
	if target_node == null:
		return ErrorCodes.make(ErrorCodes.NODE_NOT_FOUND, "Target node not found at %s" % node_path)

	var preset: String = params.get("preset", "punch_scale").to_lower()
	var duration: float = float(params.get("duration", 0.3))

	var tween := target_node.create_tween()
	var details: Dictionary = {}

	match preset:
		"punch_scale":
			var punch_factor: float = float(params.get("punch_factor", 1.25))
			var orig_scale: Vector2 = target_node.get("scale") if target_node.get("scale") != null else Vector2.ONE
			var peaked_scale := orig_scale * punch_factor
			tween.set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
			tween.tween_property(target_node, "scale", peaked_scale, duration * 0.4)
			tween.tween_property(target_node, "scale", orig_scale, duration * 0.6)
			details = {"preset": "punch_scale", "punch_factor": punch_factor, "orig_scale": [orig_scale.x, orig_scale.y]}

		"shake_2d":
			var amplitude: float = float(params.get("amplitude", 8.0))
			var orig_pos: Vector2 = target_node.get("position") if target_node.get("position") != null else Vector2.ZERO
			var step_time := duration / 6.0
			tween.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
			tween.tween_property(target_node, "position", orig_pos + Vector2(amplitude, -amplitude * 0.5), step_time)
			tween.tween_property(target_node, "position", orig_pos + Vector2(-amplitude * 0.8, amplitude * 0.6), step_time)
			tween.tween_property(target_node, "position", orig_pos + Vector2(amplitude * 0.5, -amplitude * 0.3), step_time)
			tween.tween_property(target_node, "position", orig_pos + Vector2(-amplitude * 0.3, amplitude * 0.2), step_time)
			tween.tween_property(target_node, "position", orig_pos, step_time * 2.0)
			details = {"preset": "shake_2d", "amplitude": amplitude, "orig_position": [orig_pos.x, orig_pos.y]}

		"float_bob":
			var bob_distance: float = float(params.get("bob_distance", 10.0))
			var loops: int = int(params.get("loops", 0))
			var orig_pos: Vector2 = target_node.get("position") if target_node.get("position") != null else Vector2.ZERO
			tween.set_loops(loops)
			tween.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
			tween.tween_property(target_node, "position:y", orig_pos.y - bob_distance, duration * 0.5)
			tween.tween_property(target_node, "position:y", orig_pos.y, duration * 0.5)
			details = {"preset": "float_bob", "bob_distance": bob_distance, "loops": loops}

		"fade":
			var target_alpha: float = float(params.get("target_alpha", 0.0))
			tween.set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
			tween.tween_property(target_node, "modulate:a", target_alpha, duration)
			details = {"preset": "fade", "target_alpha": target_alpha}

		"flash_color":
			var orig_mod: Color = target_node.get("modulate") if target_node.get("modulate") != null else Color.WHITE
			var flash_col: Color = Color.WHITE
			var raw_col = params.get("flash_color", [1.0, 1.0, 1.0, 1.0])
			if raw_col is Array and raw_col.size() >= 3:
				flash_col = Color(float(raw_col[0]), float(raw_col[1]), float(raw_col[2]), float(raw_col[3]) if raw_col.size() >= 4 else 1.0)
			tween.tween_property(target_node, "modulate", flash_col, duration * 0.2)
			tween.tween_property(target_node, "modulate", orig_mod, duration * 0.8)
			details = {"preset": "flash_color", "orig_modulate": [orig_mod.r, orig_mod.g, orig_mod.b, orig_mod.a]}

		"progress_fill":
			var target_val: float = float(params.get("target_value", 100.0))
			tween.set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_OUT)
			tween.tween_property(target_node, "value", target_val, duration)
			details = {"preset": "progress_fill", "target_value": target_val}

		"bounce_in":
			var drop_offset: float = float(params.get("drop_offset", 100.0))
			var orig_pos: Vector2 = target_node.get("position") if target_node.get("position") != null else Vector2.ZERO
			target_node.set("position", orig_pos + Vector2(0, -drop_offset))
			tween.set_trans(Tween.TRANS_BOUNCE).set_ease(Tween.EASE_OUT)
			tween.tween_property(target_node, "position", orig_pos, duration)
			details = {"preset": "bounce_in", "drop_offset": drop_offset}

		"spin":
			var revolutions: float = float(params.get("revolutions", 1.0))
			var orig_rot: float = float(target_node.get("rotation")) if target_node.get("rotation") != null else 0.0
			tween.set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
			tween.tween_property(target_node, "rotation", orig_rot + revolutions * TAU, duration)
			details = {"preset": "spin", "revolutions": revolutions}

		_:
			return ErrorCodes.make(ErrorCodes.INVALID_PARAMS, "Unknown preset: %s" % preset)

	return {
		"data": {
			"node_path": str(target_node.get_path()),
			"preset": preset,
			"duration": duration,
			"details": details,
			"tween_started": true,
		}
	}


func generate_code(params: Dictionary) -> Dictionary:
	var target_var: String = params.get("target_var", "self")
	var property: String = params.get("property", "position")
	var target_value_str: String = str(params.get("target_value", "Vector2(100, 100)"))
	var duration: float = float(params.get("duration", 0.5))
	var trans_type: String = params.get("trans_type", "linear").to_upper()
	var ease_type: String = params.get("ease_type", "in_out").to_upper()
	var delay: float = float(params.get("delay", 0.0))
	var is_relative: bool = bool(params.get("relative", false))

	var code := ""
	code += "var tween := create_tween()\n"
	code += "tween.set_trans(Tween.TRANS_%s).set_ease(Tween.EASE_%s)\n" % [trans_type, ease_type]
	var call_line := "var tweener = tween.tween_property(%s, \"%s\", %s, %.2f)" % [target_var, property, target_value_str, duration]
	if delay > 0.0:
		call_line += ".set_delay(%.2f)" % delay
	if is_relative:
		call_line += ".as_relative()"
	code += call_line + "\n"

	return {
		"data": {
			"code": code,
			"property": property,
			"duration": duration,
		}
	}
