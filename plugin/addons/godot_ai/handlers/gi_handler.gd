@tool
extends "res://addons/godot_ai/handlers/command_handler.gd"

const ErrorCodes := preload("res://addons/godot_ai/utils/error_codes.gd")

## Handles Global Illumination, Decals, ReflectionProbes, VoxelGI, and LightmapGI.

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


func create_decal(params: Dictionary) -> Dictionary:
	var scene_root := _get_scene_root()
	if scene_root == null:
		return {"error": "No active scene root available."}

	var parent_path: String = params.get("parent_path", "")
	var parent_node := _resolve_node(scene_root, parent_path)
	if parent_node == null:
		return {"error": "Parent node not found at: %s" % parent_path}

	var name_str: String = params.get("name", "Decal")
	var size_arr: Array = params.get("size", [2.0, 2.0, 2.0])
	var texture_albedo_path: String = params.get("texture_albedo", "")

	var decal := Decal.new()
	decal.name = name_str
	if size_arr.size() >= 3:
		decal.size = Vector3(float(size_arr[0]), float(size_arr[1]), float(size_arr[2]))

	if not texture_albedo_path.is_empty() and ResourceLoader.exists(texture_albedo_path):
		var tex: Texture2D = load(texture_albedo_path)
		if tex != null:
			decal.texture_albedo = tex

	if _undo_redo != null:
		_undo_redo.create_action("Create Decal")
		_undo_redo.add_do_method(parent_node, "add_child", decal)
		_undo_redo.add_do_method(decal, "set_owner", scene_root)
		_undo_redo.add_do_reference(decal)
		_undo_redo.add_undo_method(parent_node, "remove_child", decal)
		_undo_redo.commit_action()
	else:
		parent_node.add_child(decal)
		decal.owner = scene_root

	return {
		"status": "ok",
		"node_path": str(scene_root.get_path_to(decal)),
		"size": [decal.size.x, decal.size.y, decal.size.z],
	}


func configure_decal(params: Dictionary) -> Dictionary:
	var scene_root := _get_scene_root()
	if scene_root == null:
		return {"error": "No active scene root available."}

	var node_path: String = params.get("node_path", "")
	var decal: Decal = _resolve_node(scene_root, node_path) as Decal
	if decal == null:
		return {"error": "Decal node not found at: %s" % node_path}

	if params.has("size") and params["size"] is Array and params["size"].size() >= 3:
		decal.size = Vector3(float(params["size"][0]), float(params["size"][1]), float(params["size"][2]))

	if params.has("texture_albedo") and not str(params["texture_albedo"]).is_empty():
		if ResourceLoader.exists(params["texture_albedo"]):
			decal.texture_albedo = load(params["texture_albedo"])

	if params.has("texture_normal") and not str(params["texture_normal"]).is_empty():
		if ResourceLoader.exists(params["texture_normal"]):
			decal.texture_normal = load(params["texture_normal"])

	if params.has("texture_orm") and not str(params["texture_orm"]).is_empty():
		if ResourceLoader.exists(params["texture_orm"]):
			decal.texture_orm = load(params["texture_orm"])

	if params.has("emission_energy"):
		decal.emission_energy = float(params["emission_energy"])
	if params.has("upper_fade"):
		decal.upper_fade = float(params["upper_fade"])
	if params.has("lower_fade"):
		decal.lower_fade = float(params["lower_fade"])

	return {
		"status": "ok",
		"node_path": str(scene_root.get_path_to(decal)),
		"size": [decal.size.x, decal.size.y, decal.size.z],
	}


func create_reflection_probe(params: Dictionary) -> Dictionary:
	var scene_root := _get_scene_root()
	if scene_root == null:
		return {"error": "No active scene root available."}

	var parent_path: String = params.get("parent_path", "")
	var parent_node := _resolve_node(scene_root, parent_path)
	if parent_node == null:
		return {"error": "Parent node not found at: %s" % parent_path}

	var name_str: String = params.get("name", "ReflectionProbe")
	var size_arr: Array = params.get("size", [20.0, 20.0, 20.0])
	var update_mode_str: String = params.get("update_mode", "once")

	var probe := ReflectionProbe.new()
	probe.name = name_str
	if size_arr.size() >= 3:
		probe.size = Vector3(float(size_arr[0]), float(size_arr[1]), float(size_arr[2]))

	if update_mode_str == "always":
		probe.update_mode = ReflectionProbe.UPDATE_ALWAYS
	else:
		probe.update_mode = ReflectionProbe.UPDATE_ONCE

	if _undo_redo != null:
		_undo_redo.create_action("Create ReflectionProbe")
		_undo_redo.add_do_method(parent_node, "add_child", probe)
		_undo_redo.add_do_method(probe, "set_owner", scene_root)
		_undo_redo.add_do_reference(probe)
		_undo_redo.add_undo_method(parent_node, "remove_child", probe)
		_undo_redo.commit_action()
	else:
		parent_node.add_child(probe)
		probe.owner = scene_root

	return {
		"status": "ok",
		"node_path": str(scene_root.get_path_to(probe)),
		"size": [probe.size.x, probe.size.y, probe.size.z],
	}


func create_voxel_gi(params: Dictionary) -> Dictionary:
	var scene_root := _get_scene_root()
	if scene_root == null:
		return {"error": "No active scene root available."}

	var parent_path: String = params.get("parent_path", "")
	var parent_node := _resolve_node(scene_root, parent_path)
	if parent_node == null:
		return {"error": "Parent node not found at: %s" % parent_path}

	var name_str: String = params.get("name", "VoxelGI")
	var size_arr: Array = params.get("size", [20.0, 20.0, 20.0])
	var subdivide_val: int = int(params.get("subdivide", 1))

	var voxel_gi := VoxelGI.new()
	voxel_gi.name = name_str
	if size_arr.size() >= 3:
		voxel_gi.size = Vector3(float(size_arr[0]), float(size_arr[1]), float(size_arr[2]))
	voxel_gi.subdiv = subdivide_val

	if _undo_redo != null:
		_undo_redo.create_action("Create VoxelGI")
		_undo_redo.add_do_method(parent_node, "add_child", voxel_gi)
		_undo_redo.add_do_method(voxel_gi, "set_owner", scene_root)
		_undo_redo.add_do_reference(voxel_gi)
		_undo_redo.add_undo_method(parent_node, "remove_child", voxel_gi)
		_undo_redo.commit_action()
	else:
		parent_node.add_child(voxel_gi)
		voxel_gi.owner = scene_root

	return {
		"status": "ok",
		"node_path": str(scene_root.get_path_to(voxel_gi)),
		"size": [voxel_gi.size.x, voxel_gi.size.y, voxel_gi.size.z],
	}


func create_lightmap_gi(params: Dictionary) -> Dictionary:
	var scene_root := _get_scene_root()
	if scene_root == null:
		return {"error": "No active scene root available."}

	var parent_path: String = params.get("parent_path", "")
	var parent_node := _resolve_node(scene_root, parent_path)
	if parent_node == null:
		return {"error": "Parent node not found at: %s" % parent_path}

	var name_str: String = params.get("name", "LightmapGI")
	var bounces_val: int = int(params.get("bounces", 3))

	var lightmap := LightmapGI.new()
	lightmap.name = name_str
	lightmap.bounces = bounces_val

	if _undo_redo != null:
		_undo_redo.create_action("Create LightmapGI")
		_undo_redo.add_do_method(parent_node, "add_child", lightmap)
		_undo_redo.add_do_method(lightmap, "set_owner", scene_root)
		_undo_redo.add_do_reference(lightmap)
		_undo_redo.add_undo_method(parent_node, "remove_child", lightmap)
		_undo_redo.commit_action()
	else:
		parent_node.add_child(lightmap)
		lightmap.owner = scene_root

	return {
		"status": "ok",
		"node_path": str(scene_root.get_path_to(lightmap)),
		"bounces": lightmap.bounces,
	}


func get_gi_info(params: Dictionary) -> Dictionary:
	var scene_root := _get_scene_root()
	if scene_root == null:
		return {"error": "No active scene root available."}

	var node_path: String = params.get("node_path", "")
	var node := _resolve_node(scene_root, node_path)
	if node == null:
		return {"error": "Node not found at: %s" % node_path}

	var info: Dictionary = {
		"class": node.get_class(),
		"name": node.name,
		"path": str(scene_root.get_path_to(node)),
	}

	if node is Decal:
		var d: Decal = node as Decal
		info["size"] = [d.size.x, d.size.y, d.size.z]
		info["emission_energy"] = d.emission_energy
		info["upper_fade"] = d.upper_fade
		info["lower_fade"] = d.lower_fade
	elif node is ReflectionProbe:
		var rp: ReflectionProbe = node as ReflectionProbe
		info["size"] = [rp.size.x, rp.size.y, rp.size.z]
		info["update_mode"] = rp.update_mode
	elif node is VoxelGI:
		var v: VoxelGI = node as VoxelGI
		info["size"] = [v.size.x, v.size.y, v.size.z]
		info["subdivide"] = v.subdiv
	elif node is LightmapGI:
		var lm: LightmapGI = node as LightmapGI
		info["bounces"] = lm.bounces
		info["quality"] = lm.quality

	return {"status": "ok", "info": info}
