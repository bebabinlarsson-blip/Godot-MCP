@tool
extends "res://addons/godot_ai/handlers/command_handler.gd"

const ErrorCodes := preload("res://addons/godot_ai/utils/error_codes.gd")

## Handles Skeleton3D bone inspection, bone pose modification, BoneAttachment3D sockets,
## and PhysicalBone3D ragdoll generation.

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


func _find_skeleton(scene_root: Node, path_hint: String = "") -> Skeleton3D:
	if not path_hint.is_empty():
		var target := _resolve_node(scene_root, path_hint)
		if target is Skeleton3D:
			return target

	var stack: Array[Node] = [scene_root]
	while not stack.is_empty():
		var cur: Node = stack.pop_back()
		if cur is Skeleton3D:
			return cur
		for c in cur.get_children():
			stack.append(c)
	return null


func get_skeleton_info(params: Dictionary) -> Dictionary:
	var scene_root := _get_scene_root()
	if scene_root == null:
		return {"error": "No edited scene root available", "code": ErrorCodes.NODE_NOT_FOUND}

	var skel_path: String = params.get("skeleton_path", "")
	var skel := _find_skeleton(scene_root, skel_path)
	if skel == null:
		return {"error": "Skeleton3D not found at: %s" % skel_path, "code": ErrorCodes.NODE_NOT_FOUND}

	var count := skel.get_bone_count()
	var bones: Array = []
	for i in range(count):
		var b_name := skel.get_bone_name(i)
		var parent_idx := skel.get_bone_parent(i)
		var rest := skel.get_bone_rest(i)
		var pose_pos := skel.get_bone_pose_position(i)
		var pose_rot := skel.get_bone_pose_rotation(i)
		var pose_scale := skel.get_bone_pose_scale(i)
		bones.append({
			"index": i,
			"name": b_name,
			"parent_index": parent_idx,
			"rest_position": [rest.origin.x, rest.origin.y, rest.origin.z],
			"pose_position": [pose_pos.x, pose_pos.y, pose_pos.z],
			"pose_rotation": [pose_rot.x, pose_rot.y, pose_rot.z, pose_rot.w],
			"pose_scale": [pose_scale.x, pose_scale.y, pose_scale.z]
		})

	return {
		"success": true,
		"skeleton_path": str(skel.get_path()),
		"bone_count": count,
		"bones": bones
	}


func set_bone_pose(params: Dictionary) -> Dictionary:
	var scene_root := _get_scene_root()
	if scene_root == null:
		return {"error": "No edited scene root available", "code": ErrorCodes.NODE_NOT_FOUND}

	var skel_path: String = params.get("skeleton_path", "")
	var skel := _find_skeleton(scene_root, skel_path)
	if skel == null:
		return {"error": "Skeleton3D not found at: %s" % skel_path, "code": ErrorCodes.NODE_NOT_FOUND}

	var bone_name: String = params.get("bone_name", "")
	var bone_idx := skel.find_bone(bone_name)
	if bone_idx < 0:
		return {"error": "Bone not found: %s" % bone_name, "code": ErrorCodes.NODE_NOT_FOUND}

	if params.has("position") and params["position"] is Array and params["position"].size() >= 3:
		var p: Array = params["position"]
		skel.set_bone_pose_position(bone_idx, Vector3(float(p[0]), float(p[1]), float(p[2])))

	if params.has("rotation") and params["rotation"] is Array:
		var r: Array = params["rotation"]
		if r.size() == 4:
			skel.set_bone_pose_rotation(bone_idx, Quaternion(float(r[0]), float(r[1]), float(r[2]), float(r[3])))
		elif r.size() == 3:
			var euler := Vector3(float(r[0]), float(r[1]), float(r[2]))
			skel.set_bone_pose_rotation(bone_idx, Quaternion.from_euler(euler))

	if params.has("scale") and params["scale"] is Array and params["scale"].size() >= 3:
		var s: Array = params["scale"]
		skel.set_bone_pose_scale(bone_idx, Vector3(float(s[0]), float(s[1]), float(s[2])))

	return {
		"success": true,
		"bone_name": bone_name,
		"bone_index": bone_idx
	}


func scaffold_bone_attachment(params: Dictionary) -> Dictionary:
	var scene_root := _get_scene_root()
	if scene_root == null:
		return {"error": "No edited scene root available", "code": ErrorCodes.NODE_NOT_FOUND}

	var skel_path: String = params.get("skeleton_path", "")
	var skel := _find_skeleton(scene_root, skel_path)
	if skel == null:
		return {"error": "Skeleton3D not found at: %s" % skel_path, "code": ErrorCodes.NODE_NOT_FOUND}

	var bone_name: String = params.get("bone_name", "")
	var bone_idx := skel.find_bone(bone_name)
	if bone_idx < 0:
		return {"error": "Bone not found: %s" % bone_name, "code": ErrorCodes.NODE_NOT_FOUND}

	var node_name: String = params.get("name", "BoneAttachment3D")
	var attachment := BoneAttachment3D.new()
	attachment.name = node_name
	attachment.bone_name = bone_name

	skel.add_child(attachment)
	attachment.owner = scene_root

	return {
		"success": true,
		"attachment_path": str(attachment.get_path()),
		"bone_name": bone_name
	}


func scaffold_ragdoll(params: Dictionary) -> Dictionary:
	var scene_root := _get_scene_root()
	if scene_root == null:
		return {"error": "No edited scene root available", "code": ErrorCodes.NODE_NOT_FOUND}

	var skel_path: String = params.get("skeleton_path", "")
	var skel := _find_skeleton(scene_root, skel_path)
	if skel == null:
		return {"error": "Skeleton3D not found at: %s" % skel_path, "code": ErrorCodes.NODE_NOT_FOUND}

	var bone_count := skel.get_bone_count()
	if bone_count == 0:
		return {"error": "Skeleton3D has no bones", "code": ErrorCodes.INVALID_PARAMS}

	var col_layer: int = int(params.get("collision_layer", 1))
	var col_mask: int = int(params.get("collision_mask", 1))
	var mass_per_bone: float = float(params.get("total_mass", 70.0)) / float(max(1, bone_count))

	var created_count := 0
	for i in range(bone_count):
		var b_name := skel.get_bone_name(i)
		var pb := PhysicalBone3D.new()
		pb.name = "PhysicalBone_%s" % b_name
		pb.bone_name = b_name
		pb.collision_layer = col_layer
		pb.collision_mask = col_mask
		pb.mass = mass_per_bone

		var col_shape := CollisionShape3D.new()
		col_shape.name = "CollisionShape3D"
		var cap := CapsuleShape3D.new()
		cap.radius = 0.1
		cap.height = 0.4
		col_shape.shape = cap

		pb.add_child(col_shape)
		skel.add_child(pb)
		pb.owner = scene_root
		col_shape.owner = scene_root
		created_count += 1

	return {
		"success": true,
		"skeleton_path": str(skel.get_path()),
		"physical_bones_created": created_count
	}
