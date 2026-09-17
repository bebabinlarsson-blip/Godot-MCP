@tool
extends "res://addons/godot_ai/handlers/command_handler.gd"

const ErrorCodes := preload("res://addons/godot_ai/utils/error_codes.gd")

## Godot Omni Master Handler:
## Gives AI agents unconstrained, omnipotent control over the Godot engine:
## - Arbitrary GDScript evaluation in Editor process context
## - Universal Object Reflection on any Node, Resource, Singleton, or RefCounted
## - Semantic UI Control tree inspection, clicking, typing, and shortcuts
## - Direct ClassDB instantiation and manipulation

var _undo_redo
var _connection


func _init(undo_redo = null, connection = null) -> void:
	_undo_redo = undo_redo
	_connection = connection


func omni_eval(params: Dictionary) -> Dictionary:
	var code: String = params.get("code", "").strip_edges()
	if code.is_empty():
		return ErrorCodes.make(ErrorCodes.MISSING_REQUIRED_PARAM, "code parameter is required")

	var mode: String = params.get("mode", "auto")
	var inputs: Dictionary = params.get("inputs", {})

	# If simple single-line expression without return or assignment
	if mode == "expression" or (mode == "auto" and not code.contains("\n") and not code.begins_with("var ") and not code.contains(";")):
		var expr := Expression.new()
		var input_names := PackedStringArray(inputs.keys())
		var input_values := inputs.values()

		var err := expr.parse(code, input_names)
		if err == OK:
			var base_context: Object = EditorInterface.get_base_control()
			var res: Variant = expr.execute(input_values, base_context)
			if not expr.has_execute_failed():
				return {
					"data": {
						"mode": "expression",
						"result": res,
						"type": type_string(typeof(res)),
					}
				}

	# Fallback or block mode: Ephemeral @tool GDScript execution
	var lines := code.split("\n")
	var indented_lines: Array[String] = []
	var has_return := false

	for line in lines:
		if line.strip_edges().begins_with("return "):
			has_return = true
		indented_lines.append("\t" + line)

	if not has_return and indented_lines.size() > 0:
		# If the last line is an expression, return it
		var last_idx := indented_lines.size() - 1
		var last_raw := lines[last_idx].strip_edges()
		if not last_raw.is_empty() and not last_raw.begins_with("var ") and not last_raw.ends_with(":"):
			indented_lines[last_idx] = "\treturn (" + last_raw + ")"

	var wrapper_code := (
		"@tool\n"
		+ "extends RefCounted\n\n"
		+ "func run(inputs: Dictionary = {}, editor_interface: EditorInterface = null) -> Variant:\n"
		+ "\n".join(indented_lines) + "\n"
	)

	var script := GDScript.new()
	script.source_code = wrapper_code
	var reload_err := script.reload()
	if reload_err != OK:
		return ErrorCodes.make(
			ErrorCodes.INVALID_PARAMS,
			"GDScript compilation failed (error %d). Source:\n%s" % [reload_err, wrapper_code]
		)

	var instance: Object = script.new()
	if instance == null:
		return ErrorCodes.make(ErrorCodes.INTERNAL_ERROR, "Failed to instantiate compiled GDScript.")

	var exec_res: Variant = null
	if instance.has_method("run"):
		exec_res = instance.call("run", inputs, EditorInterface)

	return {
		"data": {
			"mode": "block",
			"result": exec_res,
			"type": type_string(typeof(exec_res)),
		}
	}


func omni_execute_script(params: Dictionary) -> Dictionary:
	var path: String = params.get("path", "")
	var inputs: Dictionary = params.get("inputs", {})

	if not path.is_empty():
		if not ResourceLoader.exists(path):
			return ErrorCodes.make(ErrorCodes.RESOURCE_NOT_FOUND, "Script file not found: %s" % path)
		var script_res = load(path)
		if script_res is GDScript:
			var obj = script_res.new()
			var res: Variant = null
			if obj.has_method("run"):
				res = obj.call("run", inputs)
			elif obj.has_method("_run"):
				res = obj.call("_run")
			return {"data": {"result": res, "path": path}}

	return omni_eval(params)


func reflection_call(params: Dictionary) -> Dictionary:
	var target_ref: Variant = params.get("target")
	var method: StringName = StringName(params.get("method", ""))
	var args: Array = params.get("args", [])

	if str(method).is_empty():
		return ErrorCodes.make(ErrorCodes.MISSING_REQUIRED_PARAM, "method parameter is required")

	var obj := _resolve_object(target_ref)
	if obj == null or not is_instance_valid(obj):
		return ErrorCodes.make(ErrorCodes.INVALID_PARAMS, "OBJECT_FREED: Target object %s is null or freed." % str(target_ref))

	if not obj.has_method(method):
		return ErrorCodes.make(
			ErrorCodes.VALUE_OUT_OF_RANGE,
			"Method '%s' not found on class '%s'." % [method, obj.get_class()]
		)

	var res: Variant = obj.callv(method, args)
	return {
		"data": {
			"result": res,
			"type": type_string(typeof(res)),
			"target_class": obj.get_class(),
			"instance_id": obj.get_instance_id(),
		}
	}


func reflection_get(params: Dictionary) -> Dictionary:
	var target_ref: Variant = params.get("target")
	var prop: StringName = StringName(params.get("property", ""))

	if str(prop).is_empty():
		return ErrorCodes.make(ErrorCodes.MISSING_REQUIRED_PARAM, "property parameter is required")

	var obj := _resolve_object(target_ref)
	if obj == null or not is_instance_valid(obj):
		return ErrorCodes.make(ErrorCodes.INVALID_PARAMS, "OBJECT_FREED: Target object is null or freed.")

	var val: Variant = obj.get(prop)
	return {
		"data": {
			"property": str(prop),
			"value": val,
			"type": type_string(typeof(val)),
			"target_class": obj.get_class(),
		}
	}


func reflection_set(params: Dictionary) -> Dictionary:
	var target_ref: Variant = params.get("target")
	var prop: StringName = StringName(params.get("property", ""))
	var val: Variant = params.get("value")

	if str(prop).is_empty():
		return ErrorCodes.make(ErrorCodes.MISSING_REQUIRED_PARAM, "property parameter is required")

	var obj := _resolve_object(target_ref)
	if obj == null or not is_instance_valid(obj):
		return ErrorCodes.make(ErrorCodes.INVALID_PARAMS, "OBJECT_FREED: Target object is null or freed.")

	obj.set(prop, val)
	return {
		"data": {
			"property": str(prop),
			"value": obj.get(prop),
			"target_class": obj.get_class(),
		}
	}


func reflection_inspect(params: Dictionary) -> Dictionary:
	var target_ref: Variant = params.get("target")
	var obj := _resolve_object(target_ref)
	if obj == null or not is_instance_valid(obj):
		return ErrorCodes.make(ErrorCodes.INVALID_PARAMS, "OBJECT_FREED: Target object is null or freed.")

	var methods: Array = []
	for m in obj.get_method_list():
		methods.append({
			"name": m.name,
			"args": m.args.map(func(a): return {"name": a.name, "type": type_string(a.type)}),
			"return": type_string(m.return.type),
		})

	var properties: Array = []
	for p in obj.get_property_list():
		properties.append({
			"name": p.name,
			"type": type_string(p.type),
			"value": obj.get(p.name),
		})

	var signals: Array = []
	for sig in obj.get_signal_list():
		signals.append({
			"name": sig.name,
			"args": sig.args.map(func(a): return {"name": a.name, "type": type_string(a.type)}),
		})

	return {
		"data": {
			"instance_id": obj.get_instance_id(),
			"class": obj.get_class(),
			"is_node": obj is Node,
			"is_resource": obj is Resource,
			"node_path": str((obj as Node).get_path()) if obj is Node else "",
			"method_count": methods.size(),
			"methods": methods,
			"property_count": properties.size(),
			"properties": properties,
			"signal_count": signals.size(),
			"signals": signals,
		}
	}


func reflection_instantiate(params: Dictionary) -> Dictionary:
	var class_name_str: String = params.get("class_name", "")
	var script_path: String = params.get("script_path", "")

	var obj: Object = null
	if not script_path.is_empty():
		var script_res = load(script_path)
		if script_res is GDScript:
			obj = script_res.new()
	elif not class_name_str.is_empty():
		if ClassDB.can_instantiate(class_name_str):
			obj = ClassDB.instantiate(class_name_str)
		else:
			return ErrorCodes.make(ErrorCodes.VALUE_OUT_OF_RANGE, "Class '%s' cannot be instantiated." % class_name_str)

	if obj == null:
		return ErrorCodes.make(ErrorCodes.INTERNAL_ERROR, "Failed to instantiate requested object.")

	return {
		"data": {
			"instance_id": obj.get_instance_id(),
			"class": obj.get_class(),
			"handle": "obj://session/%d" % obj.get_instance_id(),
			"is_node": obj is Node,
			"is_resource": obj is Resource,
		}
	}


func ui_semantic_tree(params: Dictionary) -> Dictionary:
	var max_depth: int = int(params.get("max_depth", 8))
	var base := EditorInterface.get_base_control()
	if base == null:
		return ErrorCodes.make(ErrorCodes.INTERNAL_ERROR, "Editor base control is not available.")

	return {"data": _walk_ui(base, 0, max_depth)}


func ui_click_control(params: Dictionary) -> Dictionary:
	var text_query: String = params.get("text", "")
	var path: String = params.get("path", "")
	var base := EditorInterface.get_base_control()

	var target_ctrl: Control = null
	if not path.is_empty():
		target_ctrl = base.get_node_or_null(NodePath(path)) as Control
	elif not text_query.is_empty():
		target_ctrl = _find_ctrl_by_text(base, text_query)

	if target_ctrl == null or not is_instance_valid(target_ctrl):
		return ErrorCodes.make(ErrorCodes.NODE_NOT_FOUND, "Target UI Control not found.")

	var center := target_ctrl.global_position + target_ctrl.size * 0.5
	var ev_press := InputEventMouseButton.new()
	ev_press.button_index = MOUSE_BUTTON_LEFT
	ev_press.pressed = true
	ev_press.position = center
	ev_press.global_position = center
	Input.parse_input_event(ev_press)

	var ev_release := InputEventMouseButton.new()
	ev_release.button_index = MOUSE_BUTTON_LEFT
	ev_release.pressed = false
	ev_release.position = center
	ev_release.global_position = center
	Input.parse_input_event(ev_release)

	return {
		"data": {
			"clicked": true,
			"control_name": target_ctrl.name,
			"control_class": target_ctrl.get_class(),
			"position": {"x": center.x, "y": center.y},
		}
	}


func ui_type_text(params: Dictionary) -> Dictionary:
	var text: String = params.get("text", "")
	var target_query: String = params.get("target", "")
	var base := EditorInterface.get_base_control()

	var target_ctrl: Control = null
	if not target_query.is_empty():
		target_ctrl = _find_ctrl_by_text(base, target_query)
	if target_ctrl == null:
		# Use current focused control
		target_ctrl = base.get_viewport().gui_get_focus_owner()

	if target_ctrl is LineEdit:
		var le := target_ctrl as LineEdit
		le.text = text
		le.text_submitted.emit(text)
		return {"data": {"success": true, "type": "LineEdit", "text": text}}
	elif target_ctrl is TextEdit:
		var te := target_ctrl as TextEdit
		te.text = text
		te.text_changed.emit()
		return {"data": {"success": true, "type": "TextEdit", "text": text}}

	return ErrorCodes.make(ErrorCodes.INVALID_PARAMS, "No focused or matching editable text control found.")


func _resolve_object(target_ref: Variant) -> Object:
	if target_ref is Object:
		return target_ref if is_instance_valid(target_ref) else null
	elif target_ref is int:
		return instance_from_id(int(target_ref))
	elif target_ref is float:
		return instance_from_id(int(target_ref))
	elif target_ref is String:
		var s := str(target_ref).strip_edges()
		if s.begins_with("obj://"):
			var parts := s.split("/")
			if parts.size() >= 4:
				return instance_from_id(int(parts[3]))
		elif s.begins_with("/root") or s.begins_with("."):
			var tree := Engine.get_main_loop() as SceneTree
			if tree and tree.root:
				return tree.root.get_node_or_null(NodePath(s))
		elif Engine.has_singleton(s):
			return Engine.get_singleton(s)
	return null


func _walk_ui(node: Node, depth: int, max_depth: int) -> Dictionary:
	var info: Dictionary = {
		"name": node.name,
		"class": node.get_class(),
	}
	if node is Control:
		var ctrl := node as Control
		info["visible"] = ctrl.is_visible_in_tree()
		info["rect"] = [ctrl.global_position.x, ctrl.global_position.y, ctrl.size.x, ctrl.size.y]
		if not ctrl.tooltip_text.is_empty():
			info["tooltip"] = ctrl.tooltip_text
		if ctrl is Button:
			info["text"] = (ctrl as Button).text
		elif ctrl is LineEdit:
			info["text"] = (ctrl as LineEdit).text
		elif ctrl is Label:
			info["text"] = (ctrl as Label).text

	if depth < max_depth:
		var children: Array = []
		for child in node.get_children():
			if child is Control and not (child as Control).is_visible():
				continue
			children.append(_walk_ui(child, depth + 1, max_depth))
		if not children.is_empty():
			info["children"] = children

	return info


func _find_ctrl_by_text(root: Node, query: String) -> Control:
	var q := query.to_lower()
	var stack: Array[Node] = [root]
	while not stack.is_empty():
		var curr = stack.pop_back()
		if curr is Control and (curr as Control).is_visible_in_tree():
			if curr is Button and (curr as Button).text.to_lower().contains(q):
				return curr as Control
			if curr.tooltip_text.to_lower().contains(q):
				return curr as Control
		for ch in curr.get_children():
			stack.push_back(ch)
	return null
