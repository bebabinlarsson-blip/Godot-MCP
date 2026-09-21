@tool
extends "res://addons/godot_ai/handlers/command_handler.gd"

const ErrorCodes := preload("res://addons/godot_ai/utils/error_codes.gd")

## Creates an Environment (+ optional Sky + ProceduralSkyMaterial) chain and
## either assigns it to a WorldEnvironment node or saves it to a .tres file.
## Bundles sub-resource creation + assignment in a single undo action.

const ResourceHandler := preload("res://addons/godot_ai/handlers/resource_handler.gd")

var _undo_redo: EditorUndoRedoManager
var _connection: McpConnection


func _init(undo_redo: EditorUndoRedoManager, connection: McpConnection = null) -> void:
	_undo_redo = undo_redo
	_connection = connection


const _PRESETS := {
	"default": {"sky": true, "fog": false},
	"clear": {"sky": true, "fog": false},
	"sunset": {"sky": true, "fog": false},
	"night": {"sky": true, "fog": false},
	"fog": {"sky": true, "fog": true},
}


func create_environment(params: Dictionary) -> Dictionary:
	var node_path: String = params.get("path", "")
	var resource_path: String = params.get("resource_path", "")
	var overwrite: bool = params.get("overwrite", false)
	var preset: String = params.get("preset", "default")
	var properties: Dictionary = params.get("properties", {})
	var sky_param = params.get("sky", null)  # nullable — falls back to preset default

	# environment_create targets the whole WorldEnvironment node (no separate
	# `property` param) — pass require_property=false.
	var home_err := McpResourceIO.validate_home(params, false)
	if home_err != null:
		return home_err

	if not _PRESETS.has(preset):
		return ErrorCodes.make(
			ErrorCodes.VALUE_OUT_OF_RANGE,
			"Invalid preset '%s'. Valid: %s" % [preset, ", ".join(_PRESETS.keys())]
		)

	var preset_config: Dictionary = _PRESETS[preset]
	var want_sky: bool = preset_config.sky
	var sky_properties: Dictionary = {}
	if sky_param != null:
		if sky_param is bool:
			want_sky = sky_param
		elif sky_param is Dictionary:
			var sky_config: Dictionary = (sky_param as Dictionary).duplicate()
			var material_type: String = String(sky_config.get("sky_material", "procedural")).to_lower()
			if material_type != "procedural":
				return ErrorCodes.make(
					ErrorCodes.INVALID_PARAMS,
					"sky.sky_material must be 'procedural' when sky is a dictionary"
				)
			sky_config.erase("sky_material")
			sky_properties = sky_config
			want_sky = true
		else:
			return ErrorCodes.make(
				ErrorCodes.WRONG_TYPE,
				"sky must be a bool, null, or dictionary of ProceduralSkyMaterial properties"
			)

	var env := Environment.new()
	var sky: Sky = null
	var sky_material: ProceduralSkyMaterial = null
	if want_sky:
		sky_material = ProceduralSkyMaterial.new()
		sky = Sky.new()
		sky.sky_material = sky_material
		env.background_mode = Environment.BG_SKY
		env.sky = sky
	else:
		env.background_mode = Environment.BG_CLEAR_COLOR

	_apply_preset(env, sky_material, preset)
	if not sky_properties.is_empty():
		var sky_apply_err := ResourceHandler._apply_resource_properties(sky_material, sky_properties)
		if sky_apply_err != null:
			return sky_apply_err
	if preset_config.fog:
		env.volumetric_fog_enabled = true
		env.volumetric_fog_density = 0.03

	if not properties.is_empty():
		var apply_err := ResourceHandler._apply_resource_properties(env, properties)
		if apply_err != null:
			return apply_err

	if not resource_path.is_empty():
		return _save_environment(env, sky, sky_material, resource_path, overwrite, preset)
	return _assign_environment(env, sky, sky_material, node_path, preset)


static func _apply_preset(env: Environment, sky_material: ProceduralSkyMaterial, preset: String) -> void:
	match preset:
		"default", "clear":
			if sky_material != null:
				sky_material.sky_top_color = Color(0.38, 0.45, 0.55)
				sky_material.sky_horizon_color = Color(0.65, 0.67, 0.7)
				sky_material.ground_horizon_color = Color(0.65, 0.67, 0.7)
				sky_material.ground_bottom_color = Color(0.2, 0.17, 0.13)
				sky_material.sun_angle_max = 30.0
			env.ambient_light_source = Environment.AMBIENT_SOURCE_SKY
			env.ambient_light_energy = 1.0
		"sunset":
			if sky_material != null:
				sky_material.sky_top_color = Color(0.25, 0.3, 0.55)
				sky_material.sky_horizon_color = Color(1.0, 0.55, 0.3)
				sky_material.ground_horizon_color = Color(0.85, 0.4, 0.25)
				sky_material.ground_bottom_color = Color(0.2, 0.12, 0.1)
			env.ambient_light_source = Environment.AMBIENT_SOURCE_SKY
			env.ambient_light_color = Color(1.0, 0.75, 0.55)
			env.ambient_light_energy = 0.8
		"night":
			if sky_material != null:
				sky_material.sky_top_color = Color(0.02, 0.02, 0.07)
				sky_material.sky_horizon_color = Color(0.05, 0.07, 0.15)
				sky_material.ground_horizon_color = Color(0.04, 0.05, 0.1)
				sky_material.ground_bottom_color = Color(0.0, 0.0, 0.02)
			env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
			env.ambient_light_color = Color(0.2, 0.22, 0.35)
			env.ambient_light_energy = 0.4
		"fog":
			if sky_material != null:
				sky_material.sky_top_color = Color(0.65, 0.65, 0.7)
				sky_material.sky_horizon_color = Color(0.8, 0.8, 0.82)
				sky_material.ground_horizon_color = Color(0.7, 0.7, 0.72)
				sky_material.ground_bottom_color = Color(0.3, 0.3, 0.32)
			env.ambient_light_source = Environment.AMBIENT_SOURCE_SKY
			env.ambient_light_energy = 0.7


func _assign_environment(env: Environment, sky: Sky, sky_material: ProceduralSkyMaterial, node_path: String, preset: String) -> Dictionary:
	var _resolved := McpNodeValidator.resolve_or_error(node_path, "node_path")
	if _resolved.has("error"):
		return _resolved
	var node: Node = _resolved.node
	var _scene_root: Node = _resolved.scene_root
	if not (node is WorldEnvironment):
		return ErrorCodes.make(
			ErrorCodes.WRONG_TYPE,
			"Node at %s is %s — must be WorldEnvironment" % [node_path, node.get_class()]
		)

	var old_env = (node as WorldEnvironment).environment

	_undo_redo.create_action("MCP: Create Environment (%s) for %s" % [preset, node.name])
	_undo_redo.add_do_property(node, "environment", env)
	_undo_redo.add_undo_property(node, "environment", old_env)
	_undo_redo.add_do_reference(env)
	if sky != null:
		_undo_redo.add_do_reference(sky)
	if sky_material != null:
		_undo_redo.add_do_reference(sky_material)
	_undo_redo.commit_action()

	return {
		"data": {
			"path": node_path,
			"preset": preset,
			"sky_created": sky != null,
			"sky_material_class": sky_material.get_class() if sky_material != null else "",
			"undoable": true,
		}
	}


func _save_environment(env: Environment, _sky: Sky, _sky_material: ProceduralSkyMaterial, resource_path: String, overwrite: bool, preset: String) -> Dictionary:
	return McpResourceIO.save_to_disk(env, resource_path, overwrite, "Environment", {
		"preset": preset,
	}, _connection)


func setup_environment_3d(params: Dictionary) -> Dictionary:
	var scene_check := McpNodeValidator.require_scene_or_error()
	if scene_check.has("error"):
		return scene_check
	var scene_root: Node = scene_check.scene_root

	var parent_path: String = params.get("parent_path", "")
	var parent: Node = scene_root
	if not parent_path.is_empty():
		var resolved := McpNodeValidator.resolve_or_error(parent_path, "parent_path")
		if resolved.has("error"):
			return resolved
		parent = resolved.node

	var preset: String = params.get("preset", "daylight").to_lower()
	var create_sun: bool = bool(params.get("create_sun", true))
	var volumetric_fog: bool = bool(params.get("volumetric_fog", false))
	var glow: bool = bool(params.get("glow", false))

	var world_env: WorldEnvironment = null
	for child in parent.get_children():
		if child is WorldEnvironment:
			world_env = child
			break

	var created_env_node := false
	if world_env == null:
		world_env = WorldEnvironment.new()
		world_env.name = "WorldEnvironment"
		created_env_node = true

	var env := Environment.new()
	var sky := Sky.new()
	var sky_mat := ProceduralSkyMaterial.new()
	sky.sky_material = sky_mat

	var sun_color := Color(1.0, 0.98, 0.92)
	var sun_energy := 1.0
	var sun_rotation := Vector3(-0.785398, 0.523599, 0.0)
	var sun_shadows := true

	match preset:
		"daylight":
			env.background_mode = Environment.BG_SKY
			env.sky = sky
			sky_mat.sky_top_color = Color(0.38, 0.45, 0.55)
			sky_mat.sky_horizon_color = Color(0.65, 0.67, 0.7)
			sky_mat.ground_bottom_color = Color(0.2, 0.17, 0.13)
			env.ambient_light_source = Environment.AMBIENT_SOURCE_SKY
			env.ambient_light_energy = 1.0
			env.tonemap_mode = Environment.TONE_MAPPER_FILMIC
			sun_color = Color(1.0, 0.96, 0.9)
			sun_energy = 1.2
			sun_rotation = Vector3(-0.785398, 0.523599, 0.0)
		"sunset":
			env.background_mode = Environment.BG_SKY
			env.sky = sky
			sky_mat.sky_top_color = Color(0.25, 0.3, 0.55)
			sky_mat.sky_horizon_color = Color(1.0, 0.55, 0.3)
			sky_mat.ground_horizon_color = Color(0.85, 0.4, 0.25)
			sky_mat.ground_bottom_color = Color(0.2, 0.12, 0.1)
			env.ambient_light_source = Environment.AMBIENT_SOURCE_SKY
			env.ambient_light_color = Color(1.0, 0.75, 0.55)
			env.ambient_light_energy = 0.8
			env.tonemap_mode = Environment.TONE_MAPPER_FILMIC
			sun_color = Color(1.0, 0.65, 0.35)
			sun_energy = 1.5
			sun_rotation = Vector3(-0.261799, -1.0472, 0.0)
			volumetric_fog = true
		"dark_dungeon":
			env.background_mode = Environment.BG_CLEAR_COLOR
			env.background_color = Color(0.015, 0.015, 0.02)
			env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
			env.ambient_light_color = Color(0.08, 0.08, 0.12)
			env.ambient_light_energy = 0.3
			env.tonemap_mode = Environment.TONE_MAPPER_ACES
			sun_color = Color(0.4, 0.45, 0.6)
			sun_energy = 0.2
			sun_rotation = Vector3(-1.0, 0.0, 0.0)
			volumetric_fog = true
		"neon_night":
			env.background_mode = Environment.BG_CLEAR_COLOR
			env.background_color = Color(0.02, 0.01, 0.04)
			env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
			env.ambient_light_color = Color(0.15, 0.08, 0.25)
			env.ambient_light_energy = 0.5
			env.glow_enabled = true
			env.glow_bloom = 0.25
			env.glow_intensity = 0.8
			env.tonemap_mode = Environment.TONE_MAPPER_ACES
			sun_color = Color(0.3, 0.2, 0.5)
			sun_energy = 0.3
			sun_rotation = Vector3(-1.2, 0.4, 0.0)
			glow = true
		_:
			env.background_mode = Environment.BG_SKY
			env.sky = sky
			env.ambient_light_source = Environment.AMBIENT_SOURCE_SKY
			env.ambient_light_energy = 1.0

	if volumetric_fog:
		env.volumetric_fog_enabled = true
		env.volumetric_fog_density = 0.02

	if glow:
		env.glow_enabled = true

	world_env.environment = env

	var dir_light: DirectionalLight3D = null
	if create_sun:
		for child in parent.get_children():
			if child is DirectionalLight3D:
				dir_light = child
				break
		if dir_light == null:
			dir_light = DirectionalLight3D.new()
			dir_light.name = "SunLight"

		dir_light.light_color = sun_color
		dir_light.light_energy = sun_energy
		dir_light.rotation = sun_rotation
		dir_light.shadow_enabled = sun_shadows

	_undo_redo.create_action("Setup 3D Environment: %s" % preset)
	if created_env_node:
		_undo_redo.add_do_method(parent, "add_child", world_env)
		_undo_redo.add_do_reference(world_env)
		_undo_redo.add_undo_method(parent, "remove_child", world_env)
	else:
		_undo_redo.add_do_property(world_env, "environment", env)
		_undo_redo.add_do_reference(env)

	if create_sun and dir_light != null and dir_light.get_parent() == null:
		_undo_redo.add_do_method(parent, "add_child", dir_light)
		_undo_redo.add_do_reference(dir_light)
		_undo_redo.add_undo_method(parent, "remove_child", dir_light)

	_undo_redo.commit_action()

	if created_env_node:
		world_env.owner = scene_root
	if create_sun and dir_light != null and dir_light.owner == null:
		dir_light.owner = scene_root

	return {
		"world_environment": McpScenePath.from_node(world_env, scene_root),
		"directional_light": McpScenePath.from_node(dir_light, scene_root) if dir_light != null else "",
		"preset": preset,
		"shadows_enabled": sun_shadows,
		"volumetric_fog": volumetric_fog,
		"glow": glow,
	}


func setup_environment_2d(params: Dictionary) -> Dictionary:
	var scene_check := McpNodeValidator.require_scene_or_error()
	if scene_check.has("error"):
		return scene_check
	var scene_root: Node = scene_check.scene_root

	var parent_path: String = params.get("parent_path", "")
	var parent: Node = scene_root
	if not parent_path.is_empty():
		var resolved := McpNodeValidator.resolve_or_error(parent_path, "parent_path")
		if resolved.has("error"):
			return resolved
		parent = resolved.node

	var preset: String = params.get("preset", "dungeon").to_lower()
	var add_torch_to: String = params.get("add_torch_to", "")
	var torch_energy: float = float(params.get("torch_energy", 1.2))
	var torch_radius: float = float(params.get("torch_radius", 2.0))
	var shadows: bool = bool(params.get("shadows", true))

	var ambient_color := Color(0.12, 0.12, 0.18, 1.0)
	var torch_color := Color(1.0, 0.8, 0.5, 1.0)

	match preset:
		"dungeon":
			ambient_color = Color(0.12, 0.12, 0.18, 1.0)
			torch_color = Color(1.0, 0.75, 0.45, 1.0)
		"midnight":
			ambient_color = Color(0.04, 0.04, 0.1, 1.0)
			torch_color = Color(0.8, 0.85, 1.0, 1.0)
		"sunset":
			ambient_color = Color(0.8, 0.45, 0.35, 1.0)
			torch_color = Color(1.0, 0.9, 0.6, 1.0)
		"spooky":
			ambient_color = Color(0.08, 0.16, 0.1, 1.0)
			torch_color = Color(0.5, 1.0, 0.5, 1.0)
		"foggy":
			ambient_color = Color(0.4, 0.42, 0.45, 1.0)
			torch_color = Color(1.0, 1.0, 0.9, 1.0)
		_:
			return ErrorCodes.make(ErrorCodes.VALUE_OUT_OF_RANGE,
				"Unknown preset '%s'. Supported presets: 'dungeon', 'midnight', 'sunset', 'spooky', 'foggy'." % preset)

	var canvas_mod: CanvasModulate = null
	for child in parent.get_children():
		if child is CanvasModulate:
			canvas_mod = child
			break

	var created_mod := false
	if canvas_mod == null:
		canvas_mod = CanvasModulate.new()
		canvas_mod.name = "CanvasModulate"
		canvas_mod.color = ambient_color
		created_mod = true

	var torch_node: PointLight2D = null
	var torch_parent: Node = null
	if not add_torch_to.is_empty():
		var t_resolved := McpNodeValidator.resolve_or_error(add_torch_to, "add_torch_to")
		if t_resolved.has("error"):
			return t_resolved
		torch_parent = t_resolved.node

		torch_node = PointLight2D.new()
		torch_node.name = "TorchLight2D"
		torch_node.color = torch_color
		torch_node.energy = torch_energy
		torch_node.texture_scale = torch_radius
		torch_node.shadow_enabled = shadows

		var grad_tex := GradientTexture2D.new()
		grad_tex.fill = GradientTexture2D.FILL_RADIAL
		grad_tex.fill_from = Vector2(0.5, 0.5)
		grad_tex.fill_to = Vector2(0.5, 0.0)
		var grad := Gradient.new()
		grad.set_color(0, Color(1.0, 1.0, 1.0, 1.0))
		grad.set_color(1, Color(1.0, 1.0, 1.0, 0.0))
		grad_tex.gradient = grad
		grad_tex.width = 256
		grad_tex.height = 256
		torch_node.texture = grad_tex

	_undo_redo.create_action("Setup 2D Environment: %s" % preset)
	if created_mod:
		_undo_redo.add_do_method(parent, "add_child", canvas_mod)
		_undo_redo.add_do_reference(canvas_mod)
		_undo_redo.add_undo_method(parent, "remove_child", canvas_mod)
	else:
		_undo_redo.add_do_property(canvas_mod, "color", ambient_color)

	if torch_node != null and torch_parent != null:
		_undo_redo.add_do_method(torch_parent, "add_child", torch_node)
		_undo_redo.add_do_reference(torch_node)
		_undo_redo.add_undo_method(torch_parent, "remove_child", torch_node)

	_undo_redo.commit_action()

	if created_mod:
		canvas_mod.owner = scene_root
	if torch_node != null:
		torch_node.owner = scene_root

	return {
		"data": {
			"canvas_modulate": McpScenePath.from_node(canvas_mod, scene_root),
			"ambient_color": ambient_color.to_html(true),
			"preset": preset,
			"torch_light": McpScenePath.from_node(torch_node, scene_root) if torch_node != null else "",
			"undoable": true,
		}
	}


