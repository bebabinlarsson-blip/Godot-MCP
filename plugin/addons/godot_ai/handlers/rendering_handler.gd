@tool
extends "res://addons/godot_ai/handlers/command_handler.gd"

const ErrorCodes := preload("res://addons/godot_ai/utils/error_codes.gd")

## Handles WorldEnvironment, post-processing effects, CameraAttributes,
## and lighting presets.

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


func _find_world_environment(scene_root: Node, path_hint: String = "") -> WorldEnvironment:
	if not path_hint.is_empty():
		var target := _resolve_node(scene_root, path_hint)
		if target is WorldEnvironment:
			return target

	# Find recursively in scene
	var stack: Array[Node] = [scene_root]
	while not stack.is_empty():
		var cur: Node = stack.pop_back()
		if cur is WorldEnvironment:
			return cur
		for c in cur.get_children():
			stack.append(c)
	return null


func scaffold_world_environment(params: Dictionary) -> Dictionary:
	var scene_root := _get_scene_root()
	if scene_root == null:
		return {"error": "No edited scene root available", "code": ErrorCodes.NODE_NOT_FOUND}

	var parent_path: String = params.get("parent_path", "")
	var parent: Node = _resolve_node(scene_root, parent_path)
	if parent == null:
		return {"error": "Parent node not found at: %s" % parent_path, "code": ErrorCodes.NODE_NOT_FOUND}

	var sky_mode: String = params.get("sky_mode", "procedural").to_lower()
	var tonemap_mode_str: String = params.get("tonemap_mode", "aces").to_lower()
	var node_name: String = params.get("name", "WorldEnvironment")

	var env_node := WorldEnvironment.new()
	env_node.name = node_name

	var env := Environment.new()
	match sky_mode:
		"procedural":
			var sky := Sky.new()
			sky.sky_material = ProceduralSkyMaterial.new()
			env.background_mode = Environment.BG_SKY
			env.sky = sky
		"physical":
			var sky := Sky.new()
			sky.sky_material = PhysicalSkyMaterial.new()
			env.background_mode = Environment.BG_SKY
			env.sky = sky
		"color":
			env.background_mode = Environment.BG_COLOR
			env.background_color = Color(0.1, 0.1, 0.15)
		_:
			env.background_mode = Environment.BG_CLEAR_COLOR

	match tonemap_mode_str:
		"reinhard":
			env.tonemap_mode = Environment.TONE_MAPPER_REINHARDT
		"filmic":
			env.tonemap_mode = Environment.TONE_MAPPER_FILMIC
		"linear":
			env.tonemap_mode = Environment.TONE_MAPPER_LINEAR
		_:
			env.tonemap_mode = Environment.TONE_MAPPER_ACES

	env_node.environment = env
	parent.add_child(env_node)
	env_node.owner = scene_root

	return {
		"success": true,
		"node_path": str(env_node.get_path()),
		"sky_mode": sky_mode,
		"tonemap_mode": tonemap_mode_str
	}


func set_environment_effects(params: Dictionary) -> Dictionary:
	var scene_root := _get_scene_root()
	if scene_root == null:
		return {"error": "No edited scene root available", "code": ErrorCodes.NODE_NOT_FOUND}

	var node_path: String = params.get("node_path", "")
	var env_node := _find_world_environment(scene_root, node_path)
	if env_node == null or env_node.environment == null:
		return {"error": "WorldEnvironment node or environment resource not found", "code": ErrorCodes.NODE_NOT_FOUND}

	var env: Environment = env_node.environment
	var applied: Array[String] = []

	if params.has("glow_enabled"):
		env.glow_enabled = bool(params["glow_enabled"])
		applied.append("glow_enabled")
	if params.has("glow_intensity"):
		env.glow_intensity = float(params["glow_intensity"])
		applied.append("glow_intensity")
	if params.has("ssr_enabled"):
		env.ssr_enabled = bool(params["ssr_enabled"])
		applied.append("ssr_enabled")
	if params.has("ssao_enabled"):
		env.ssao_enabled = bool(params["ssao_enabled"])
		applied.append("ssao_enabled")
	if params.has("ssil_enabled"):
		env.ssil_enabled = bool(params["ssil_enabled"])
		applied.append("ssil_enabled")
	if params.has("sdfgi_enabled"):
		env.sdfgi_enabled = bool(params["sdfgi_enabled"])
		applied.append("sdfgi_enabled")
	if params.has("volumetric_fog_enabled"):
		env.volumetric_fog_enabled = bool(params["volumetric_fog_enabled"])
		applied.append("volumetric_fog_enabled")
	if params.has("volumetric_fog_density"):
		env.volumetric_fog_density = float(params["volumetric_fog_density"])
		applied.append("volumetric_fog_density")

	return {
		"success": true,
		"applied_effects": applied
	}


func set_camera_attributes(params: Dictionary) -> Dictionary:
	var scene_root := _get_scene_root()
	if scene_root == null:
		return {"error": "No edited scene root available", "code": ErrorCodes.NODE_NOT_FOUND}

	var camera_path: String = params.get("camera_path", "")
	var node := _resolve_node(scene_root, camera_path)
	if not (node is Camera3D):
		return {"error": "Camera3D not found at: %s" % camera_path, "code": ErrorCodes.NODE_NOT_FOUND}

	var cam: Camera3D = node
	var attr_type: String = params.get("attributes_type", "practical").to_lower()
	var attrs: CameraAttributes = null

	if attr_type == "physical":
		attrs = CameraAttributesPhysical.new()
	else:
		var prac := CameraAttributesPractical.new()
		if params.has("dof_blur_far_enabled"):
			prac.dof_blur_far_enabled = bool(params["dof_blur_far_enabled"])
		if params.has("dof_blur_far_distance"):
			prac.dof_blur_far_distance = float(params["dof_blur_far_distance"])
		attrs = prac

	if params.has("auto_exposure_enabled"):
		attrs.auto_exposure_enabled = bool(params["auto_exposure_enabled"])

	cam.attributes = attrs
	return {
		"success": true,
		"camera_path": str(cam.get_path()),
		"attributes_type": attr_type
	}


func apply_lighting_preset(params: Dictionary) -> Dictionary:
	var scene_root := _get_scene_root()
	if scene_root == null:
		return {"error": "No edited scene root available", "code": ErrorCodes.NODE_NOT_FOUND}

	var node_path: String = params.get("node_path", "")
	var env_node := _find_world_environment(scene_root, node_path)
	if env_node == null:
		var res := scaffold_world_environment({"parent_path": "", "sky_mode": "procedural"})
		if not res.get("success", false):
			return res
		env_node = _find_world_environment(scene_root)

	var env: Environment = env_node.environment
	var preset: String = params.get("preset", "outdoor_sunny").to_lower()

	match preset:
		"outdoor_sunny":
			env.background_mode = Environment.BG_SKY
			var sky := Sky.new()
			sky.sky_material = ProceduralSkyMaterial.new()
			env.sky = sky
			env.tonemap_mode = Environment.TONE_MAPPER_ACES
			env.glow_enabled = true
			env.glow_intensity = 0.4
			env.ssao_enabled = true
			env.volumetric_fog_enabled = false
		"dungeon_dark":
			env.background_mode = Environment.BG_COLOR
			env.background_color = Color(0.01, 0.01, 0.02)
			env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
			env.ambient_light_color = Color(0.05, 0.05, 0.08)
			env.tonemap_mode = Environment.TONE_MAPPER_FILMIC
			env.glow_enabled = true
			env.glow_intensity = 0.8
			env.ssao_enabled = true
			env.volumetric_fog_enabled = true
			env.volumetric_fog_density = 0.05
		"scifi_cyberpunk":
			env.background_mode = Environment.BG_COLOR
			env.background_color = Color(0.02, 0.01, 0.05)
			env.tonemap_mode = Environment.TONE_MAPPER_ACES
			env.glow_enabled = true
			env.glow_intensity = 1.2
			env.glow_bloom = 0.2
			env.ssr_enabled = true
			env.ssao_enabled = true
			env.volumetric_fog_enabled = true
			env.volumetric_fog_density = 0.02
		"retro_pixel":
			env.background_mode = Environment.BG_COLOR
			env.background_color = Color(0.1, 0.1, 0.1)
			env.tonemap_mode = Environment.TONE_MAPPER_LINEAR
			env.glow_enabled = false
			env.ssr_enabled = false
			env.ssao_enabled = false
			env.volumetric_fog_enabled = false
		_:
			# cinematic_moody
			env.background_mode = Environment.BG_SKY
			var sky := Sky.new()
			var psm := ProceduralSkyMaterial.new()
			psm.sky_energy_multiplier = 0.8
			sky.sky_material = psm
			env.sky = sky
			env.tonemap_mode = Environment.TONE_MAPPER_ACES
			env.glow_enabled = true
			env.glow_intensity = 0.5
			env.ssao_enabled = true
			env.ssil_enabled = true
			env.volumetric_fog_enabled = true
			env.volumetric_fog_density = 0.01

	return {
		"success": true,
		"preset": preset,
		"node_path": str(env_node.get_path())
	}


func get_environment_info(params: Dictionary) -> Dictionary:
	var scene_root := _get_scene_root()
	if scene_root == null:
		return {"error": "No edited scene root available", "code": ErrorCodes.NODE_NOT_FOUND}

	var node_path: String = params.get("node_path", "")
	var env_node := _find_world_environment(scene_root, node_path)
	if env_node == null or env_node.environment == null:
		return {"error": "WorldEnvironment node or environment resource not found", "code": ErrorCodes.NODE_NOT_FOUND}

	var env: Environment = env_node.environment
	return {
		"success": true,
		"node_path": str(env_node.get_path()),
		"background_mode": env.background_mode,
		"tonemap_mode": env.tonemap_mode,
		"glow_enabled": env.glow_enabled,
		"ssr_enabled": env.ssr_enabled,
		"ssao_enabled": env.ssao_enabled,
		"ssil_enabled": env.ssil_enabled,
		"sdfgi_enabled": env.sdfgi_enabled,
		"volumetric_fog_enabled": env.volumetric_fog_enabled
	}
