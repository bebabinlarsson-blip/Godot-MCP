@tool
extends "res://addons/godot_ai/handlers/command_handler.gd"

const ErrorCodes := preload("res://addons/godot_ai/utils/error_codes.gd")

## Handles WorldEnvironment, Sky materials, Volumetric Fog, and CameraAttributes.

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


func _get_or_create_environment(scene_root: Node, world_env_path: String) -> Dictionary:
	var world_node: Node = null
	if not world_env_path.is_empty():
		world_node = _resolve_node(scene_root, world_env_path)
	else:
		# Search for existing WorldEnvironment
		for child in scene_root.find_children("*", "WorldEnvironment", true, false):
			world_node = child
			break

	if world_node == null:
		world_node = WorldEnvironment.new()
		world_node.name = "WorldEnvironment"
		scene_root.add_child(world_node)
		world_node.owner = scene_root

	var env: Environment = world_node.get("environment")
	if env == null:
		env = Environment.new()
		world_node.set("environment", env)

	return {"node": world_node, "env": env}


func configure_world_environment(params: Dictionary) -> Dictionary:
	var scene_root := _get_scene_root()
	if scene_root == null:
		return {"error": "No edited scene root available", "code": ErrorCodes.NODE_NOT_FOUND}

	var world_env_path: String = params.get("node_path", "")
	var env_data := _get_or_create_environment(scene_root, world_env_path)
	var env: Environment = env_data["env"]
	var node: Node = env_data["node"]

	var properties: Dictionary = params.get("properties", {})
	for prop in properties:
		var val = properties[prop]
		if str(prop).ends_with("_color") and val is String:
			val = Color.from_string(val, Color.WHITE)
		env.set(str(prop), val)

	return {
		"success": true,
		"node_path": str(node.get_path()),
		"configured_count": properties.size()
	}


func create_sky_material(params: Dictionary) -> Dictionary:
	var scene_root := _get_scene_root()
	if scene_root == null:
		return {"error": "No edited scene root available", "code": ErrorCodes.NODE_NOT_FOUND}

	var world_env_path: String = params.get("node_path", "")
	var env_data := _get_or_create_environment(scene_root, world_env_path)
	var env: Environment = env_data["env"]
	var node: Node = env_data["node"]

	var sky_type: String = params.get("sky_type", "procedural").to_lower()
	var sky := Sky.new()

	if sky_type == "panorama":
		var pano_mat := PanoramaSkyMaterial.new()
		var texture_path: String = params.get("texture_path", "")
		if not texture_path.is_empty() and ResourceLoader.exists(texture_path):
			pano_mat.panorama = load(texture_path)
		sky.sky_material = pano_mat
	else:
		var proc_mat := ProceduralSkyMaterial.new()
		var sky_top_color: String = params.get("sky_top_color", "")
		if not sky_top_color.is_empty():
			proc_mat.sky_top_color = Color.from_string(sky_top_color, proc_mat.sky_top_color)
		var ground_bottom_color: String = params.get("ground_bottom_color", "")
		if not ground_bottom_color.is_empty():
			proc_mat.ground_bottom_color = Color.from_string(
				ground_bottom_color, proc_mat.ground_bottom_color
			)
		sky.sky_material = proc_mat

	env.background_mode = Environment.BG_SKY
	env.sky = sky

	return {
		"success": true,
		"node_path": str(node.get_path()),
		"sky_type": sky_type
	}


func set_volumetric_fog(params: Dictionary) -> Dictionary:
	var scene_root := _get_scene_root()
	if scene_root == null:
		return {"error": "No edited scene root available", "code": ErrorCodes.NODE_NOT_FOUND}

	var world_env_path: String = params.get("node_path", "")
	var env_data := _get_or_create_environment(scene_root, world_env_path)
	var env: Environment = env_data["env"]
	var node: Node = env_data["node"]

	var enabled: bool = params.get("enabled", true)
	env.volumetric_fog_enabled = enabled

	if params.has("density"):
		env.volumetric_fog_density = float(params["density"])
	if params.has("albedo"):
		env.volumetric_fog_albedo = Color.from_string(str(params["albedo"]), Color.WHITE)
	if params.has("emission"):
		env.volumetric_fog_emission = Color.from_string(str(params["emission"]), Color.BLACK)
	if params.has("anisotropy"):
		env.volumetric_fog_anisotropy = float(params["anisotropy"])
	if params.has("length"):
		env.volumetric_fog_length = float(params["length"])

	return {
		"success": true,
		"node_path": str(node.get_path()),
		"volumetric_fog_enabled": env.volumetric_fog_enabled,
		"density": env.volumetric_fog_density
	}


func configure_camera_attributes(params: Dictionary) -> Dictionary:
	var scene_root := _get_scene_root()
	if scene_root == null:
		return {"error": "No edited scene root available", "code": ErrorCodes.NODE_NOT_FOUND}

	var node_path: String = params.get("node_path", "")
	var target_node: Node = _resolve_node(scene_root, node_path)
	if target_node == null:
		var env_data := _get_or_create_environment(scene_root, "")
		target_node = env_data["node"]

	var attr_type: String = params.get("attribute_type", "practical").to_lower()
	var attrs: CameraAttributes
	if attr_type == "physical":
		attrs = CameraAttributesPhysical.new()
	else:
		attrs = CameraAttributesPractical.new()

	var properties: Dictionary = params.get("properties", {})
	for prop in properties:
		attrs.set(str(prop), properties[prop])

	target_node.set("camera_attributes", attrs)

	return {
		"success": true,
		"node_path": str(target_node.get_path()),
		"attribute_type": attr_type
	}


func get_world_info(params: Dictionary) -> Dictionary:
	var scene_root := _get_scene_root()
	if scene_root == null:
		return {"error": "No edited scene root available", "code": ErrorCodes.NODE_NOT_FOUND}

	var world_env_path: String = params.get("node_path", "")
	var world_node: Node = null
	if not world_env_path.is_empty():
		world_node = _resolve_node(scene_root, world_env_path)
	else:
		for child in scene_root.find_children("*", "WorldEnvironment", true, false):
			world_node = child
			break

	if world_node == null:
		return {
			"success": true,
			"has_world_environment": false
		}

	var env: Environment = world_node.get("environment")
	var info: Dictionary = {
		"success": true,
		"has_world_environment": true,
		"node_path": str(world_node.get_path()),
		"background_mode": env.background_mode if env != null else -1,
		"volumetric_fog_enabled": env.volumetric_fog_enabled if env != null else false,
		"glow_enabled": env.glow_enabled if env != null else false,
		"ssr_enabled": env.ssr_enabled if env != null else false,
		"ssao_enabled": env.ssao_enabled if env != null else false,
		"sdfgi_enabled": env.sdfgi_enabled if env != null else false,
	}
	return info
