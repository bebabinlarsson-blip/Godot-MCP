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
	elif target_ref is int or target_ref is float:
		return instance_from_id(int(target_ref))
	elif target_ref is String:
		var s := str(target_ref).strip_edges()
		if s == "EditorInterface":
			return EditorInterface
		if s.begins_with("obj://"):
			var parts := s.split("/")
			if parts.size() >= 4:
				return instance_from_id(int(parts[3]))
		elif s.begins_with("/root") or s.begins_with("."):
			var tree := Engine.get_main_loop() as SceneTree
			if tree and tree.root:
				return tree.root.get_node_or_null(NodePath(s))
		elif s.begins_with("res://"):
			if ResourceLoader.exists(s):
				return load(s)
		elif Engine.has_singleton(s):
			return Engine.get_singleton(s)
		elif s.is_valid_int():
			var id := s.to_int()
			if id > 0:
				var obj_by_id := instance_from_id(id)
				if obj_by_id:
					return obj_by_id

		var scene_root: Node = EditorInterface.get_edited_scene_root()
		if scene_root:
			if s == scene_root.name or s == "":
				return scene_root
			var n := scene_root.get_node_or_null(NodePath(s))
			if n:
				return n
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


func scene_instantiate_prefab(params: Dictionary) -> Dictionary:
	var scene_path: String = params.get("scene_path", "")
	if scene_path.is_empty():
		return ErrorCodes.make(ErrorCodes.MISSING_REQUIRED_PARAM, "scene_path is required")

	if not ResourceLoader.exists(scene_path):
		return ErrorCodes.make(ErrorCodes.RESOURCE_NOT_FOUND, "Scene file not found: %s" % scene_path)

	var packed := ResourceLoader.load(scene_path) as PackedScene
	if packed == null:
		return ErrorCodes.make(ErrorCodes.WRONG_TYPE, "Resource at %s is not a PackedScene" % scene_path)

	var scene_root: Node = EditorInterface.get_edited_scene_root()
	if scene_root == null:
		return ErrorCodes.make(ErrorCodes.EDITOR_NOT_READY, "No scene is currently open in the editor")

	var parent: Node = scene_root
	var parent_path: String = params.get("parent_path", "")
	if not parent_path.is_empty():
		parent = scene_root.get_node_or_null(parent_path)
		if parent == null:
			return ErrorCodes.make(ErrorCodes.NODE_NOT_FOUND, "Parent node not found at: %s" % parent_path)

	var inst := packed.instantiate(PackedScene.GEN_EDIT_STATE_INSTANCE)
	if inst == null:
		return ErrorCodes.make(ErrorCodes.INTERNAL_ERROR, "Failed to instantiate %s" % scene_path)

	var custom_name: String = params.get("node_name", "")
	if not custom_name.is_empty():
		inst.name = custom_name

	var pos_val = params.get("position", null)
	if pos_val != null and pos_val is Array:
		if inst is Node2D and pos_val.size() >= 2:
			(inst as Node2D).position = Vector2(float(pos_val[0]), float(pos_val[1]))
		elif inst is Node3D and pos_val.size() >= 3:
			(inst as Node3D).position = Vector3(float(pos_val[0]), float(pos_val[1]), float(pos_val[2]))

	if _undo_redo != null:
		_undo_redo.create_action("Instantiate Prefab: %s" % inst.name)
		_undo_redo.add_do_method(parent, "add_child", inst)
		_undo_redo.add_do_property(inst, "owner", scene_root)
		_undo_redo.add_do_reference(inst)
		_undo_redo.add_undo_method(parent, "remove_child", inst)
		_undo_redo.commit_action()
	else:
		parent.add_child(inst)
		inst.owner = scene_root

	return {
		"data": {
			"ok": true,
			"node_name": str(inst.name),
			"node_path": str(scene_root.get_path_to(inst)),
			"scene_path": scene_path
		}
	}


func shader_create(params: Dictionary) -> Dictionary:
	var shader_path: String = params.get("shader_path", "")
	if shader_path.is_empty():
		return ErrorCodes.make(ErrorCodes.MISSING_REQUIRED_PARAM, "shader_path is required (e.g. res://glow.gdshader)")

	var shader_type: String = params.get("shader_type", "canvas_item")
	var code: String = params.get("code", "")
	if code.is_empty():
		code = "shader_type %s;\n\nvoid fragment() {\n\t// COLOR = vec4(1.0, 1.0, 1.0, 1.0);\n}\n" % shader_type

	var file := FileAccess.open(shader_path, FileAccess.WRITE)
	if file == null:
		return ErrorCodes.make(ErrorCodes.INTERNAL_ERROR, "Cannot write to shader file: %s" % shader_path)
	file.store_string(code)
	file.close()

	EditorInterface.get_resource_filesystem().scan()

	var shader := Shader.new()
	shader.code = code
	ResourceSaver.save(shader, shader_path)

	var target_node_path: String = params.get("target_node_path", "")
	if not target_node_path.is_empty():
		var scene_root: Node = EditorInterface.get_edited_scene_root()
		if scene_root != null:
			var target = scene_root.get_node_or_null(target_node_path)
			if target != null:
				var mat := ShaderMaterial.new()
				mat.shader = shader
				if target is CanvasItem:
					(target as CanvasItem).material = mat
				elif target.has_method("set_material_override"):
					target.call("set_material_override", mat)

	return {
		"data": {
			"ok": true,
			"shader_path": shader_path,
			"shader_type": shader_type
		}
	}


func mesh_create_primitive(params: Dictionary) -> Dictionary:
	var scene_root: Node = EditorInterface.get_edited_scene_root()
	if scene_root == null:
		return ErrorCodes.make(ErrorCodes.EDITOR_NOT_READY, "No scene is currently open in editor")

	var ptype: String = str(params.get("primitive_type", "box")).to_lower()
	var mesh_inst := MeshInstance3D.new()
	var prim_mesh: PrimitiveMesh = null

	match ptype:
		"box", "cube":
			var bm := BoxMesh.new()
			var sz = params.get("size", [1.0, 1.0, 1.0])
			if sz is Array and sz.size() >= 3:
				bm.size = Vector3(float(sz[0]), float(sz[1]), float(sz[2]))
			prim_mesh = bm
		"sphere":
			var sm := SphereMesh.new()
			var radius = float(params.get("radius", 0.5))
			sm.radius = radius
			sm.height = radius * 2.0
			prim_mesh = sm
		"cylinder":
			var cm := CylinderMesh.new()
			cm.top_radius = float(params.get("top_radius", 0.5))
			cm.bottom_radius = float(params.get("bottom_radius", 0.5))
			cm.height = float(params.get("height", 2.0))
			prim_mesh = cm
		"plane":
			var pm := PlaneMesh.new()
			var sz = params.get("size", [2.0, 2.0])
			if sz is Array and sz.size() >= 2:
				pm.size = Vector2(float(sz[0]), float(sz[1]))
			prim_mesh = pm
		"capsule":
			var cap := CapsuleMesh.new()
			cap.radius = float(params.get("radius", 0.5))
			cap.height = float(params.get("height", 2.0))
			prim_mesh = cap
		"prism":
			var prm := PrismMesh.new()
			var sz = params.get("size", [1.0, 1.0, 1.0])
			if sz is Array and sz.size() >= 3:
				prm.size = Vector3(float(sz[0]), float(sz[1]), float(sz[2]))
			prim_mesh = prm
		_:
			return ErrorCodes.make(ErrorCodes.INVALID_PARAMS, "Unsupported primitive_type: %s" % ptype)

	mesh_inst.mesh = prim_mesh

	var color_arr = params.get("albedo_color", null)
	if color_arr != null and color_arr is Array and color_arr.size() >= 3:
		var mat := StandardMaterial3D.new()
		var a := 1.0
		if color_arr.size() >= 4:
			a = float(color_arr[3])
		mat.albedo_color = Color(float(color_arr[0]), float(color_arr[1]), float(color_arr[2]), a)
		mesh_inst.material_override = mat

	var node_name: String = params.get("node_name", ptype.capitalize() + "Mesh")
	mesh_inst.name = node_name

	var pos = params.get("position", [0.0, 0.0, 0.0])
	if pos is Array and pos.size() >= 3:
		mesh_inst.position = Vector3(float(pos[0]), float(pos[1]), float(pos[2]))

	var parent: Node = scene_root
	var parent_path: String = params.get("parent_path", "")
	if not parent_path.is_empty():
		parent = scene_root.get_node_or_null(parent_path)
		if parent == null:
			parent = scene_root

	if _undo_redo != null:
		_undo_redo.create_action("Create Primitive Mesh: %s" % mesh_inst.name)
		_undo_redo.add_do_method(parent, "add_child", mesh_inst)
		_undo_redo.add_do_property(mesh_inst, "owner", scene_root)
		_undo_redo.add_do_reference(mesh_inst)
		_undo_redo.add_undo_method(parent, "remove_child", mesh_inst)
		_undo_redo.commit_action()
	else:
		parent.add_child(mesh_inst)
		mesh_inst.owner = scene_root

	return {
		"data": {
			"ok": true,
			"node_name": str(mesh_inst.name),
			"node_path": str(scene_root.get_path_to(mesh_inst)),
			"primitive": ptype
		}
	}


func collision_shape_create(params: Dictionary) -> Dictionary:
	var scene_root: Node = EditorInterface.get_edited_scene_root()
	if scene_root == null:
		return ErrorCodes.make(ErrorCodes.EDITOR_NOT_READY, "No scene is currently open in editor")

	var parent: Node = scene_root
	var parent_path: String = params.get("parent_path", "")
	if not parent_path.is_empty():
		parent = scene_root.get_node_or_null(parent_path)
		if parent == null:
			return ErrorCodes.make(ErrorCodes.NODE_NOT_FOUND, "Parent node not found at: %s" % parent_path)

	var shape_type: String = str(params.get("shape_type", "box")).to_lower()
	var is_2d: bool = params.get("is_2d", parent is Node2D)

	var col_node: Node
	var shape_res: Resource

	if is_2d:
		var c2d := CollisionShape2D.new()
		match shape_type:
			"box", "rectangle":
				var rect := RectangleShape2D.new()
				var sz = params.get("size", [32.0, 32.0])
				if sz is Array and sz.size() >= 2:
					rect.size = Vector2(float(sz[0]), float(sz[1]))
				shape_res = rect
			"circle", "sphere":
				var circ := CircleShape2D.new()
				circ.radius = float(params.get("radius", 16.0))
				shape_res = circ
			"capsule":
				var cap := CapsuleShape2D.new()
				cap.radius = float(params.get("radius", 12.0))
				cap.height = float(params.get("height", 32.0))
				shape_res = cap
			_:
				return ErrorCodes.make(ErrorCodes.INVALID_PARAMS, "Unsupported 2D shape: %s" % shape_type)
		c2d.shape = shape_res
		col_node = c2d
	else:
		var c3d := CollisionShape3D.new()
		match shape_type:
			"box", "cube":
				var b3 := BoxShape3D.new()
				var sz = params.get("size", [1.0, 1.0, 1.0])
				if sz is Array and sz.size() >= 3:
					b3.size = Vector3(float(sz[0]), float(sz[1]), float(sz[2]))
				shape_res = b3
			"sphere", "circle":
				var s3 := SphereShape3D.new()
				s3.radius = float(params.get("radius", 0.5))
				shape_res = s3
			"capsule":
				var cap3 := CapsuleShape3D.new()
				cap3.radius = float(params.get("radius", 0.5))
				cap3.height = float(params.get("height", 2.0))
				shape_res = cap3
			_:
				return ErrorCodes.make(ErrorCodes.INVALID_PARAMS, "Unsupported 3D shape: %s" % shape_type)
		c3d.shape = shape_res
		col_node = c3d

	var node_name: String = params.get("node_name", "CollisionShape")
	col_node.name = node_name

	if _undo_redo != null:
		_undo_redo.create_action("Create Collision Shape: %s" % col_node.name)
		_undo_redo.add_do_method(parent, "add_child", col_node)
		_undo_redo.add_do_property(col_node, "owner", scene_root)
		_undo_redo.add_do_reference(col_node)
		_undo_redo.add_undo_method(parent, "remove_child", col_node)
		_undo_redo.commit_action()
	else:
		parent.add_child(col_node)
		col_node.owner = scene_root

	return {
		"data": {
			"ok": true,
			"node_name": str(col_node.name),
			"node_path": str(scene_root.get_path_to(col_node)),
			"is_2d": is_2d,
			"shape": shape_type
		}
	}


func animation_preset_motion(params: Dictionary) -> Dictionary:
	var anim_player_path: String = params.get("animation_player_path", "")
	var scene_root: Node = EditorInterface.get_edited_scene_root()
	if scene_root == null:
		return ErrorCodes.make(ErrorCodes.EDITOR_NOT_READY, "No scene is currently open in editor")

	var player: AnimationPlayer = null
	if not anim_player_path.is_empty():
		player = scene_root.get_node_or_null(anim_player_path) as AnimationPlayer
	else:
		var stack: Array[Node] = [scene_root]
		while not stack.is_empty():
			var n = stack.pop_back()
			if n is AnimationPlayer:
				player = n as AnimationPlayer
				break
			for ch in n.get_children():
				stack.push_back(ch)

	if player == null:
		return ErrorCodes.make(ErrorCodes.NODE_NOT_FOUND, "No AnimationPlayer found in scene")

	var target_node_path: String = params.get("target_node_path", "")
	var target: Node = scene_root.get_node_or_null(target_node_path)
	if target == null:
		target = scene_root

	var preset: String = str(params.get("preset", "pulse")).to_lower()
	var duration: float = float(params.get("duration", 1.0))
	var anim_name: String = params.get("anim_name", preset)

	var anim := Animation.new()
	anim.length = duration
	anim.loop_mode = Animation.LOOP_LINEAR if params.get("loop", true) else Animation.LOOP_NONE

	var rel_path := str(player.get_path_to(target))

	match preset:
		"pulse":
			var track_idx := anim.add_track(Animation.TYPE_VALUE)
			anim.track_set_path(track_idx, NodePath(rel_path + ":scale"))
			var base_scale = target.get("scale") if target.get("scale") != null else Vector2(1, 1)
			var peak_scale = base_scale * float(params.get("scale_multiplier", 1.25))
			anim.track_insert_key(track_idx, 0.0, base_scale)
			anim.track_insert_key(track_idx, duration * 0.5, peak_scale)
			anim.track_insert_key(track_idx, duration, base_scale)
		"fade_in":
			var track_idx := anim.add_track(Animation.TYPE_VALUE)
			anim.track_set_path(track_idx, NodePath(rel_path + ":modulate:a"))
			anim.track_insert_key(track_idx, 0.0, 0.0)
			anim.track_insert_key(track_idx, duration, 1.0)
		"fade_out":
			var track_idx := anim.add_track(Animation.TYPE_VALUE)
			anim.track_set_path(track_idx, NodePath(rel_path + ":modulate:a"))
			anim.track_insert_key(track_idx, 0.0, 1.0)
			anim.track_insert_key(track_idx, duration, 0.0)
		"slide_in":
			var track_idx := anim.add_track(Animation.TYPE_VALUE)
			anim.track_set_path(track_idx, NodePath(rel_path + ":position"))
			var final_pos = target.get("position") if target.get("position") != null else Vector2.ZERO
			var offset = Vector2(float(params.get("offset_x", -100)), float(params.get("offset_y", 0)))
			anim.track_insert_key(track_idx, 0.0, final_pos + offset)
			anim.track_insert_key(track_idx, duration, final_pos)
		_:
			return ErrorCodes.make(ErrorCodes.INVALID_PARAMS, "Unsupported motion preset: %s" % preset)

	var lib: AnimationLibrary
	if player.has_animation_library(""):
		lib = player.get_animation_library("")
	else:
		lib = AnimationLibrary.new()
		player.add_animation_library("", lib)

	lib.add_animation(anim_name, anim)

	return {
		"data": {
			"ok": true,
			"animation_player": str(player.name),
			"anim_name": anim_name,
			"preset": preset,
			"duration": duration
		}
	}


func mcp_ping(params: Dictionary) -> Dictionary:
	var vinfo: Dictionary = Engine.get_version_info()
	var edited_root: Node = EditorInterface.get_edited_scene_root()
	var root_name: String = edited_root.name if edited_root != null else "None"

	return {
		"data": {
			"ok": true,
			"ping": "pong",
			"godot_version": str(vinfo.get("string", "4.x")),
			"engine_major": int(vinfo.get("major", 4)),
			"engine_minor": int(vinfo.get("minor", 0)),
			"process_frames": Engine.get_process_frames(),
			"edited_scene_root": root_name,
			"static_memory_bytes": OS.get_static_memory_usage(),
			"canonical_operations": 1820
		}
	}
