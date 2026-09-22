@tool
extends "res://addons/godot_ai/handlers/command_handler.gd"

const ErrorCodes := preload("res://addons/godot_ai/utils/error_codes.gd")

## Handles 2D and 3D physics joints scaffolding, configuration, and inspection.

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


func scaffold_joint_2d(params: Dictionary) -> Dictionary:
	var scene_root := _get_scene_root()
	if scene_root == null:
		return {"error": "No edited scene root available", "code": ErrorCodes.NODE_NOT_FOUND}

	var parent_path: String = params.get("parent_path", "")
	var parent: Node = _resolve_node(scene_root, parent_path)
	if parent == null:
		return {"error": "Parent node not found: %s" % parent_path, "code": ErrorCodes.NODE_NOT_FOUND}

	var joint_type: String = params.get("joint_type", "pin").to_lower()
	var joint: Joint2D
	if joint_type == "groove":
		joint = GrooveJoint2D.new()
	elif joint_type == "damped_spring" or joint_type == "spring":
		joint = DampedSpringJoint2D.new()
	else:
		joint = PinJoint2D.new()

	joint.name = params.get("node_name", "Joint2D")
	var node_a: String = params.get("node_a_path", "")
	var node_b: String = params.get("node_b_path", "")
	if not node_a.is_empty():
		joint.node_a = NodePath(node_a)
	if not node_b.is_empty():
		joint.node_b = NodePath(node_b)

	parent.add_child(joint)
	joint.owner = scene_root

	return {
		"success": true,
		"node_path": str(joint.get_path()),
		"joint_class": joint.get_class()
	}


func scaffold_joint_3d(params: Dictionary) -> Dictionary:
	var scene_root := _get_scene_root()
	if scene_root == null:
		return {"error": "No edited scene root available", "code": ErrorCodes.NODE_NOT_FOUND}

	var parent_path: String = params.get("parent_path", "")
	var parent: Node = _resolve_node(scene_root, parent_path)
	if parent == null:
		return {"error": "Parent node not found: %s" % parent_path, "code": ErrorCodes.NODE_NOT_FOUND}

	var joint_type: String = params.get("joint_type", "pin").to_lower()
	var joint: Joint3D
	if joint_type == "hinge":
		joint = HingeJoint3D.new()
	elif joint_type == "slider":
		joint = SliderJoint3D.new()
	elif joint_type == "cone_twist":
		joint = ConeTwistJoint3D.new()
	elif joint_type == "generic_6dof" or joint_type == "6dof":
		joint = Generic6DOFJoint3D.new()
	else:
		joint = PinJoint3D.new()

	joint.name = params.get("node_name", "Joint3D")
	var node_a: String = params.get("node_a_path", "")
	var node_b: String = params.get("node_b_path", "")
	if not node_a.is_empty():
		joint.node_a = NodePath(node_a)
	if not node_b.is_empty():
		joint.node_b = NodePath(node_b)

	parent.add_child(joint)
	joint.owner = scene_root

	return {
		"success": true,
		"node_path": str(joint.get_path()),
		"joint_class": joint.get_class()
	}


func configure_joint(params: Dictionary) -> Dictionary:
	var scene_root := _get_scene_root()
	if scene_root == null:
		return {"error": "No edited scene root available", "code": ErrorCodes.NODE_NOT_FOUND}

	var joint_path: String = params.get("joint_path", "")
	var joint: Node = _resolve_node(scene_root, joint_path)
	if joint == null:
		return {"error": "Joint node not found: %s" % joint_path, "code": ErrorCodes.NODE_NOT_FOUND}

	var properties: Dictionary = params.get("properties", {})
	for prop_name in properties:
		joint.set(str(prop_name), properties[prop_name])

	return {
		"success": true,
		"joint_path": joint_path,
		"configured_count": properties.size()
	}


func get_joint_info(params: Dictionary) -> Dictionary:
	var scene_root := _get_scene_root()
	if scene_root == null:
		return {"error": "No edited scene root available", "code": ErrorCodes.NODE_NOT_FOUND}

	var joint_path: String = params.get("joint_path", "")
	var joint: Node = _resolve_node(scene_root, joint_path)
	if joint == null:
		return {"error": "Joint node not found: %s" % joint_path, "code": ErrorCodes.NODE_NOT_FOUND}

	return {
		"success": true,
		"joint_path": joint_path,
		"class": joint.get_class(),
		"node_a": str(joint.get("node_a")),
		"node_b": str(joint.get("node_b"))
	}
