@tool
extends "res://addons/godot_ai/handlers/command_handler.gd"

const ErrorCodes := preload("res://addons/godot_ai/utils/error_codes.gd")

## Handles 2D/3D light nodes, shadows, decals, and reflection/GI probes.

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


func scaffold_light_3d(params: Dictionary) -> Dictionary:
	var scene_root := _get_scene_root()
	if scene_root == null:
		return {"error": "No edited scene root available", "code": ErrorCodes.NODE_NOT_FOUND}

	var parent_path: String = params.get("parent_path", "")
	var parent: Node = _resolve_node(scene_root, parent_path)
	if parent == null:
		return {"error": "Parent node not found: %s" % parent_path, "code": ErrorCodes.NODE_NOT_FOUND}

	var type_str: String = params.get("type", "DirectionalLight3D").to_lower()
	var node_name: String = params.get("name", "Light3D")
	var energy: float = float(params.get("energy", 1.0))
	var shadows: bool = bool(params.get("shadows", true))

	var light: Light3D = null
	match type_str:
		"omnilight3d", "omni":
			var omni := OmniLight3D.new()
			omni.omni_range = float(params.get("range", 5.0))
			omni.omni_attenuation = float(params.get("attenuation", 1.0))
			light = omni
		"spotlight3d", "spot":
			var spot := SpotLight3D.new()
			spot.spot_range = float(params.get("range", 5.0))
			spot.spot_angle = float(params.get("spot_angle", 45.0))
			light = spot
		_:
			light = DirectionalLight3D.new()

	light.name = node_name
	light.light_energy = energy
	light.shadow_enabled = shadows

	if params.has("color") and params["color"] is Array and params["color"].size() >= 3:
		var c: Array = params["color"]
		light.light_color = Color(float(c[0]), float(c[1]), float(c[2]))

	parent.add_child(light)
	light.owner = scene_root

	return {
		"success": true,
		"light_path": str(light.get_path()),
		"type": light.get_class()
	}


func scaffold_light_2d(params: Dictionary) -> Dictionary:
	var scene_root := _get_scene_root()
	if scene_root == null:
		return {"error": "No edited scene root available", "code": ErrorCodes.NODE_NOT_FOUND}

	var parent_path: String = params.get("parent_path", "")
	var parent: Node = _resolve_node(scene_root, parent_path)
	if parent == null:
		return {"error": "Parent node not found: %s" % parent_path, "code": ErrorCodes.NODE_NOT_FOUND}

	var type_str: String = params.get("type", "PointLight2D").to_lower()
	var node_name: String = params.get("name", "Light2D")
	var energy: float = float(params.get("energy", 1.0))
	var shadows: bool = bool(params.get("shadows", false))

	var light: Light2D = null
	if type_str == "directionallight2d" or type_str == "directional":
		light = DirectionalLight2D.new()
	else:
		light = PointLight2D.new()

	light.name = node_name
	light.energy = energy
	light.shadow_enabled = shadows

	if params.has("color") and params["color"] is Array and params["color"].size() >= 3:
		var c: Array = params["color"]
		light.color = Color(float(c[0]), float(c[1]), float(c[2]))

	parent.add_child(light)
	light.owner = scene_root

	return {
		"success": true,
		"light_path": str(light.get_path()),
		"type": light.get_class()
	}


func scaffold_decal(params: Dictionary) -> Dictionary:
	var scene_root := _get_scene_root()
	if scene_root == null:
		return {"error": "No edited scene root available", "code": ErrorCodes.NODE_NOT_FOUND}

	var parent_path: String = params.get("parent_path", "")
	var parent: Node = _resolve_node(scene_root, parent_path)
	if parent == null:
		return {"error": "Parent node not found: %s" % parent_path, "code": ErrorCodes.NODE_NOT_FOUND}

	var decal := Decal.new()
	decal.name = params.get("name", "Decal")
	if params.has("size") and params["size"] is Array and params["size"].size() >= 3:
		var s: Array = params["size"]
		decal.size = Vector3(float(s[0]), float(s[1]), float(s[2]))

	var albedo_path: String = params.get("texture_albedo", "")
	if not albedo_path.is_empty():
		if not albedo_path.begins_with("res://"):
			albedo_path = "res://" + albedo_path
		var tex := ResourceLoader.load(albedo_path)
		if tex is Texture2D:
			decal.texture_albedo = tex

	parent.add_child(decal)
	decal.owner = scene_root

	return {
		"success": true,
		"decal_path": str(decal.get_path())
	}


func scaffold_probe(params: Dictionary) -> Dictionary:
	var scene_root := _get_scene_root()
	if scene_root == null:
		return {"error": "No edited scene root available", "code": ErrorCodes.NODE_NOT_FOUND}

	var parent_path: String = params.get("parent_path", "")
	var parent: Node = _resolve_node(scene_root, parent_path)
	if parent == null:
		return {"error": "Parent node not found: %s" % parent_path, "code": ErrorCodes.NODE_NOT_FOUND}

	var type_str: String = params.get("type", "ReflectionProbe").to_lower()
	var node_name: String = params.get("name", "Probe")
	var probe_node: Node = null

	match type_str:
		"lightmapgi", "lightmap":
			probe_node = LightmapGI.new()
		"voxelgi", "voxel":
			probe_node = VoxelGI.new()
		_:
			var rp := ReflectionProbe.new()
			if params.has("size") and params["size"] is Array and params["size"].size() >= 3:
				var s: Array = params["size"]
				rp.size = Vector3(float(s[0]), float(s[1]), float(s[2]))
			probe_node = rp

	probe_node.name = node_name
	parent.add_child(probe_node)
	probe_node.owner = scene_root

	return {
		"success": true,
		"probe_path": str(probe_node.get_path()),
		"type": probe_node.get_class()
	}


func set_light_properties(params: Dictionary) -> Dictionary:
	var scene_root := _get_scene_root()
	if scene_root == null:
		return {"error": "No edited scene root available", "code": ErrorCodes.NODE_NOT_FOUND}

	var light_path: String = params.get("light_path", "")
	var node := _resolve_node(scene_root, light_path)
	if node == null:
		return {"error": "Light node not found: %s" % light_path, "code": ErrorCodes.NODE_NOT_FOUND}

	if node is Light3D:
		if params.has("energy"): node.light_energy = float(params["energy"])
		if params.has("shadows"): node.shadow_enabled = bool(params["shadows"])
		if params.has("volumetric_fog_energy"): node.light_volumetric_fog_energy = float(params["volumetric_fog_energy"])
		if params.has("color") and params["color"] is Array and params["color"].size() >= 3:
			var c: Array = params["color"]
			node.light_color = Color(float(c[0]), float(c[1]), float(c[2]))
	elif node is Light2D:
		if params.has("energy"): node.energy = float(params["energy"])
		if params.has("shadows"): node.shadow_enabled = bool(params["shadows"])
		if params.has("color") and params["color"] is Array and params["color"].size() >= 3:
			var c: Array = params["color"]
			node.color = Color(float(c[0]), float(c[1]), float(c[2]))

	return {
		"success": true,
		"light_path": str(node.get_path())
	}


func get_light_info(params: Dictionary) -> Dictionary:
	var scene_root := _get_scene_root()
	if scene_root == null:
		return {"error": "No edited scene root available", "code": ErrorCodes.NODE_NOT_FOUND}

	var light_path: String = params.get("light_path", "")
	var node := _resolve_node(scene_root, light_path)
	if node == null:
		return {"error": "Light node not found: %s" % light_path, "code": ErrorCodes.NODE_NOT_FOUND}

	if node is Light3D:
		return {
			"success": true,
			"type": node.get_class(),
			"energy": node.light_energy,
			"shadow_enabled": node.shadow_enabled,
			"color": [node.light_color.r, node.light_color.g, node.light_color.b],
			"volumetric_fog_energy": node.light_volumetric_fog_energy
		}
	elif node is Light2D:
		return {
			"success": true,
			"type": node.get_class(),
			"energy": node.energy,
			"shadow_enabled": node.shadow_enabled,
			"color": [node.color.r, node.color.g, node.color.b]
		}

	return {"error": "Node is not a Light2D or Light3D", "code": ErrorCodes.INVALID_PARAMS}
