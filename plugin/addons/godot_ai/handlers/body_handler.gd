@tool
extends "res://addons/godot_ai/handlers/command_handler.gd"

const ErrorCodes := preload("res://addons/godot_ai/utils/error_codes.gd")

## Handles 2D and 3D physics body configuration, impulses, collision masks, and scaffolding.

var _undo_redo: EditorUndoRedoManager
var _connection: McpConnection


func _init(undo_redo: EditorUndoRedoManager = null, connection: McpConnection = null) -> void:
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


func configure_body(params: Dictionary) -> Dictionary:
	var scene_root := _get_scene_root()
	if scene_root == null:
		return {"error": "No edited scene root available", "code": ErrorCodes.NODE_NOT_FOUND}

	var node_path: String = params.get("node_path", "")
	var node: Node = _resolve_node(scene_root, node_path)
	if node == null:
		return {"error": "Node not found: %s" % node_path, "code": ErrorCodes.NODE_NOT_FOUND}

	var properties: Dictionary = params.get("properties", {})
	for prop in properties:
		node.set(str(prop), properties[prop])

	return {
		"success": true,
		"node_path": node_path,
		"configured_count": properties.size()
	}


func apply_impulse(params: Dictionary) -> Dictionary:
	var scene_root := _get_scene_root()
	if scene_root == null:
		return {"error": "No edited scene root available", "code": ErrorCodes.NODE_NOT_FOUND}

	var node_path: String = params.get("node_path", "")
	var node: Node = _resolve_node(scene_root, node_path)
	if node == null:
		return {"error": "Node not found: %s" % node_path, "code": ErrorCodes.NODE_NOT_FOUND}

	var impulse: Variant = params.get("impulse")
	var position: Variant = params.get("position")

	if node is RigidBody2D:
		var imp2: Vector2 = Vector2.ZERO
		if impulse is Array and impulse.size() >= 2:
			imp2 = Vector2(impulse[0], impulse[1])
		elif impulse is Vector2:
			imp2 = impulse
		if position != null:
			var pos2: Vector2 = Vector2.ZERO
			if position is Array and position.size() >= 2:
				pos2 = Vector2(position[0], position[1])
			elif position is Vector2:
				pos2 = position
			node.apply_impulse(imp2, pos2)
		else:
			node.apply_central_impulse(imp2)
	elif node is RigidBody3D:
		var imp3: Vector3 = Vector3.ZERO
		if impulse is Array and impulse.size() >= 3:
			imp3 = Vector3(impulse[0], impulse[1], impulse[2])
		elif impulse is Vector3:
			imp3 = impulse
		if position != null:
			var pos3: Vector3 = Vector3.ZERO
			if position is Array and position.size() >= 3:
				pos3 = Vector3(position[0], position[1], position[2])
			elif position is Vector3:
				pos3 = position
			node.apply_impulse(imp3, pos3)
		else:
			node.apply_central_impulse(imp3)
	else:
		return {
			"error": "Target node is not a RigidBody2D or RigidBody3D: %s" % node.get_class(),
			"code": ErrorCodes.INVALID_PARAMS
		}

	return {"success": true, "node_path": node_path, "class": node.get_class()}


func set_collision_layer_mask(params: Dictionary) -> Dictionary:
	var scene_root := _get_scene_root()
	if scene_root == null:
		return {"error": "No edited scene root available", "code": ErrorCodes.NODE_NOT_FOUND}

	var node_path: String = params.get("node_path", "")
	var node: Node = _resolve_node(scene_root, node_path)
	if node == null:
		return {"error": "Node not found: %s" % node_path, "code": ErrorCodes.NODE_NOT_FOUND}

	if not (node is CollisionObject2D or node is CollisionObject3D):
		return {
			"error": "Target node is not a CollisionObject2D or CollisionObject3D",
			"code": ErrorCodes.INVALID_PARAMS
		}

	if params.has("collision_layer"):
		node.set("collision_layer", int(params["collision_layer"]))
	if params.has("collision_mask"):
		node.set("collision_mask", int(params["collision_mask"]))
	if params.has("collision_priority"):
		node.set("collision_priority", float(params["collision_priority"]))

	return {
		"success": true,
		"node_path": node_path,
		"collision_layer": node.get("collision_layer"),
		"collision_mask": node.get("collision_mask")
	}


func scaffold_character_body(params: Dictionary) -> Dictionary:
	var scene_root := _get_scene_root()
	if scene_root == null:
		return {"error": "No edited scene root available", "code": ErrorCodes.NODE_NOT_FOUND}

	var parent_path: String = params.get("parent_path", "")
	var parent: Node = _resolve_node(scene_root, parent_path)
	if parent == null:
		return {"error": "Parent node not found: %s" % parent_path, "code": ErrorCodes.NODE_NOT_FOUND}

	var is_3d: bool = params.get("is_3d", false)
	var body_name: String = params.get("node_name", "Player")

	var body: Node
	var col_shape: Node

	if is_3d:
		body = CharacterBody3D.new()
		col_shape = CollisionShape3D.new()
		var capsule := CapsuleShape3D.new()
		col_shape.set("shape", capsule)
	else:
		body = CharacterBody2D.new()
		col_shape = CollisionShape2D.new()
		var capsule := CapsuleShape2D.new()
		col_shape.set("shape", capsule)

	body.name = body_name
	col_shape.name = "CollisionShape"

	parent.add_child(body)
	body.owner = scene_root

	body.add_child(col_shape)
	col_shape.owner = scene_root

	return {
		"success": true,
		"node_path": str(body.get_path()),
		"collision_shape_path": str(col_shape.get_path()),
		"is_3d": is_3d
	}


func get_body_info(params: Dictionary) -> Dictionary:
	var scene_root := _get_scene_root()
	if scene_root == null:
		return {"error": "No edited scene root available", "code": ErrorCodes.NODE_NOT_FOUND}

	var node_path: String = params.get("node_path", "")
	var node: Node = _resolve_node(scene_root, node_path)
	if node == null:
		return {"error": "Node not found: %s" % node_path, "code": ErrorCodes.NODE_NOT_FOUND}

	var info: Dictionary = {
		"success": true,
		"node_path": node_path,
		"class": node.get_class(),
	}

	if node is CollisionObject2D or node is CollisionObject3D:
		info["collision_layer"] = node.get("collision_layer")
		info["collision_mask"] = node.get("collision_mask")
		info["collision_priority"] = node.get("collision_priority")

	if node is RigidBody2D or node is RigidBody3D:
		info["mass"] = node.get("mass")
		info["gravity_scale"] = node.get("gravity_scale")
		info["linear_damp"] = node.get("linear_damp")
		info["angular_damp"] = node.get("angular_damp")
		info["freeze"] = node.get("freeze")

	return info
