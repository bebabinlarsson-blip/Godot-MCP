@tool
extends "res://addons/godot_ai/handlers/command_handler.gd"

const ErrorCodes := preload("res://addons/godot_ai/utils/error_codes.gd")

## Handles VisualShader graph creation, node addition, connection, and inspection.

var _undo_redo: EditorUndoRedoManager
var _connection: McpConnection


func _init(undo_redo: EditorUndoRedoManager = null, connection: McpConnection = null) -> void:
	_undo_redo = undo_redo
	_connection = connection


func create_visual_shader(params: Dictionary) -> Dictionary:
	var shader_type: String = params.get("shader_type", "spatial").to_lower()
	var save_path: String = params.get("save_path", "")

	var vs := VisualShader.new()
	if shader_type == "canvas_item":
		vs.set_mode(Shader.MODE_CANVAS_ITEM)
	elif shader_type == "particles":
		vs.set_mode(Shader.MODE_PARTICLES)
	elif shader_type == "sky":
		vs.set_mode(Shader.MODE_SKY)
	elif shader_type == "fog":
		vs.set_mode(Shader.MODE_FOG)
	else:
		vs.set_mode(Shader.MODE_SPATIAL)

	if not save_path.is_empty():
		if not save_path.begins_with("res://"):
			save_path = "res://" + save_path
		var err := ResourceSaver.save(vs, save_path)
		if err != OK:
			return {"error": "Failed to save VisualShader to: %s" % save_path, "code": ErrorCodes.INTERNAL_ERROR}

	return {
		"success": true,
		"shader_type": shader_type,
		"save_path": save_path
	}


func add_node(params: Dictionary) -> Dictionary:
	var shader_path: String = params.get("shader_path", "")
	var node_type: String = params.get("node_type", "VisualShaderNodeColorConstant")
	var shader_type_enum: int = int(params.get("shader_type_enum", 0))
	var pos_array: Array = params.get("position", [0, 0])

	if shader_path.is_empty():
		return {"error": "shader_path is required", "code": ErrorCodes.INVALID_PARAMS}
	if not shader_path.begins_with("res://"):
		shader_path = "res://" + shader_path

	if not ResourceLoader.exists(shader_path):
		return {"error": "Shader file not found: %s" % shader_path, "code": ErrorCodes.RESOURCE_NOT_FOUND}

	var res = load(shader_path)
	if not res is VisualShader:
		return {"error": "Resource is not a VisualShader: %s" % shader_path, "code": ErrorCodes.WRONG_TYPE}

	var vs: VisualShader = res
	if not ClassDB.class_exists(node_type):
		return {"error": "Unknown VisualShaderNode type: %s" % node_type, "code": ErrorCodes.INVALID_PARAMS}

	var node_inst = ClassDB.instantiate(node_type)
	if not node_inst is VisualShaderNode:
		return {"error": "Class is not a VisualShaderNode: %s" % node_type, "code": ErrorCodes.WRONG_TYPE}

	var id: int = vs.get_valid_node_id(shader_type_enum)
	var pos := Vector2(0, 0)
	if pos_array.size() >= 2:
		pos = Vector2(float(pos_array[0]), float(pos_array[1]))

	vs.add_node(shader_type_enum, node_inst, pos, id)
	var err := ResourceSaver.save(vs, shader_path)
	if err != OK:
		return {"error": "Failed to save updated VisualShader", "code": ErrorCodes.INTERNAL_ERROR}

	return {
		"success": true,
		"shader_path": shader_path,
		"node_id": id,
		"node_type": node_type
	}


func connect_nodes(params: Dictionary) -> Dictionary:
	var shader_path: String = params.get("shader_path", "")
	var shader_type_enum: int = int(params.get("shader_type_enum", 0))
	var from_node: int = int(params.get("from_node", 0))
	var from_port: int = int(params.get("from_port", 0))
	var to_node: int = int(params.get("to_node", 0))
	var to_port: int = int(params.get("to_port", 0))

	if shader_path.is_empty():
		return {"error": "shader_path is required", "code": ErrorCodes.INVALID_PARAMS}
	if not shader_path.begins_with("res://"):
		shader_path = "res://" + shader_path

	if not ResourceLoader.exists(shader_path):
		return {"error": "Shader file not found: %s" % shader_path, "code": ErrorCodes.RESOURCE_NOT_FOUND}

	var res = load(shader_path)
	if not res is VisualShader:
		return {"error": "Resource is not a VisualShader: %s" % shader_path, "code": ErrorCodes.WRONG_TYPE}

	var vs: VisualShader = res
	var err := vs.connect_nodes(shader_type_enum, from_node, from_port, to_node, to_port)
	if err != OK:
		return {"error": "Failed to connect nodes in VisualShader (code %d)" % err, "code": ErrorCodes.INTERNAL_ERROR}

	var save_err := ResourceSaver.save(vs, shader_path)
	if save_err != OK:
		return {"error": "Failed to save connected VisualShader", "code": ErrorCodes.INTERNAL_ERROR}

	return {
		"success": true,
		"from_node": from_node,
		"from_port": from_port,
		"to_node": to_node,
		"to_port": to_port
	}


func get_graph(params: Dictionary) -> Dictionary:
	var shader_path: String = params.get("shader_path", "")
	var shader_type_enum: int = int(params.get("shader_type_enum", 0))

	if shader_path.is_empty():
		return {"error": "shader_path is required", "code": ErrorCodes.INVALID_PARAMS}
	if not shader_path.begins_with("res://"):
		shader_path = "res://" + shader_path

	if not ResourceLoader.exists(shader_path):
		return {"error": "Shader file not found: %s" % shader_path, "code": ErrorCodes.RESOURCE_NOT_FOUND}

	var res = load(shader_path)
	if not res is VisualShader:
		return {"error": "Resource is not a VisualShader: %s" % shader_path, "code": ErrorCodes.WRONG_TYPE}

	var vs: VisualShader = res
	var node_ids: PackedInt32Array = vs.get_node_list(shader_type_enum)
	var connections: Array = vs.get_node_connections(shader_type_enum)

	var nodes_summary: Array = []
	for id in node_ids:
		var n = vs.get_node(shader_type_enum, id)
		if n != null:
			nodes_summary.append({
				"id": id,
				"class": n.get_class(),
				"position": [vs.get_node_position(shader_type_enum, id).x, vs.get_node_position(shader_type_enum, id).y]
			})

	var conns_summary: Array = []
	for c in connections:
		conns_summary.append({
			"from_node": c.get("from_node", 0),
			"from_port": c.get("from_port", 0),
			"to_node": c.get("to_node", 0),
			"to_port": c.get("to_port", 0)
		})

	return {
		"success": true,
		"shader_path": shader_path,
		"shader_type_enum": shader_type_enum,
		"nodes": nodes_summary,
		"connections": conns_summary
	}
