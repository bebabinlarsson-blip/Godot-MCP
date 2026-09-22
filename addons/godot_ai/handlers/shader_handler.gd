@tool
extends "res://addons/godot_ai/handlers/command_handler.gd"

const ErrorCodes := preload("res://addons/godot_ai/utils/error_codes.gd")

var _undo_redo: EditorUndoRedoManager
var _connection: McpConnection

const PRESETS := {
	"outline_2d": """shader_type canvas_item;

uniform vec4 outline_color : source_color = vec4(1.0, 1.0, 1.0, 1.0);
uniform float outline_width : hint_range(0.0, 10.0, 0.5) = 1.0;

void fragment() {
	vec4 col = texture(TEXTURE, UV);
	if (col.a > 0.0) {
		COLOR = col;
	} else {
		vec2 size = TEXTURE_PIXEL_SIZE * outline_width;
		float a = texture(TEXTURE, UV + vec2(0.0, -size.y)).a +
				  texture(TEXTURE, UV + vec2(0.0, size.y)).a +
				  texture(TEXTURE, UV + vec2(-size.x, 0.0)).a +
				  texture(TEXTURE, UV + vec2(size.x, 0.0)).a;
		if (a > 0.0) {
			COLOR = outline_color;
		} else {
			COLOR = vec4(0.0);
		}
	}
}
""",
	"hit_flash": """shader_type canvas_item;

uniform vec4 flash_color : source_color = vec4(1.0, 1.0, 1.0, 1.0);
uniform float flash_modifier : hint_range(0.0, 1.0, 0.05) = 0.0;

void fragment() {
	vec4 col = texture(TEXTURE, UV);
	COLOR = mix(col, vec4(flash_color.rgb, col.a), flash_modifier);
}
""",
	"dissolve_2d": """shader_type canvas_item;

uniform float dissolve_amount : hint_range(0.0, 1.0, 0.01) = 0.0;
uniform vec4 burn_color : source_color = vec4(1.0, 0.4, 0.0, 1.0);
uniform float burn_size : hint_range(0.0, 0.2, 0.01) = 0.05;

float hash(vec2 p) {
	return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

void fragment() {
	vec4 col = texture(TEXTURE, UV);
	float noise = hash(floor(UV * 64.0));
	if (noise < dissolve_amount) {
		discard;
	} else if (noise < dissolve_amount + burn_size) {
		COLOR = burn_color;
	} else {
		COLOR = col;
	}
}
""",
	"water_2d": """shader_type canvas_item;

uniform vec4 water_tint : source_color = vec4(0.1, 0.4, 0.8, 0.8);
uniform float wave_speed : hint_range(0.1, 10.0) = 2.0;
uniform float wave_freq : hint_range(1.0, 50.0) = 10.0;
uniform float wave_amp : hint_range(0.0, 0.1) = 0.02;

void fragment() {
	vec2 uv = UV;
	uv.x += sin(uv.y * wave_freq + TIME * wave_speed) * wave_amp;
	uv.y += cos(uv.x * wave_freq + TIME * wave_speed) * wave_amp;
	vec4 col = texture(TEXTURE, uv);
	COLOR = mix(col, water_tint, 0.5);
}
""",
	"foliage_wind": """shader_type canvas_item;

uniform float wind_speed : hint_range(0.1, 10.0) = 3.0;
uniform float wind_strength : hint_range(0.0, 50.0) = 8.0;

void vertex() {
	if (VERTEX.y < 0.0) {
		VERTEX.x += sin(TIME * wind_speed + VERTEX.y * 0.1) * wind_strength;
	}
}
""",
	"crt_scanline": """shader_type canvas_item;

uniform float scanline_count : hint_range(50.0, 800.0) = 240.0;
uniform float scanline_intensity : hint_range(0.0, 1.0) = 0.25;
uniform float vignette_intensity : hint_range(0.0, 2.0) = 0.4;

void fragment() {
	vec4 col = texture(TEXTURE, UV);
	float sl = sin(UV.y * scanline_count * 3.14159) * 0.5 + 0.5;
	col.rgb -= sl * scanline_intensity;
	float vig = 1.0 - length(UV - vec2(0.5)) * vignette_intensity;
	col.rgb *= clamp(vig, 0.0, 1.0);
	COLOR = col;
}
""",
	"hologram_glitch": """shader_type canvas_item;

uniform vec4 holo_color : source_color = vec4(0.2, 0.8, 1.0, 0.8);
uniform float scanline_density : hint_range(10.0, 500.0) = 150.0;
uniform float glitch_speed : hint_range(0.1, 20.0) = 4.0;

void fragment() {
	vec2 uv = UV;
	float scan = sin(uv.y * scanline_density + TIME * glitch_speed) * 0.5 + 0.5;
	vec4 col = texture(TEXTURE, uv);
	col.rgb = holo_color.rgb * (0.6 + 0.4 * scan);
	col.a = col.a * holo_color.a * (0.5 + 0.5 * scan);
	COLOR = col;
}
"""
}


func _init(undo_redo: EditorUndoRedoManager, connection: McpConnection = null) -> void:
	_undo_redo = undo_redo
	_connection = connection


func create_shader(params: Dictionary) -> Dictionary:
	var path: String = params.get("path", "")
	var shader_type: String = params.get("shader_type", "canvas_item")
	var code: String = params.get("code", "")
	var overwrite: bool = params.get("overwrite", false)

	if path.is_empty():
		return ErrorCodes.make(ErrorCodes.MISSING_REQUIRED_PARAM, "path is required")

	if not path.begins_with("res://"):
		path = "res://" + path.trim_prefix("/")
	if not path.ends_with(".gdshader"):
		path += ".gdshader"

	var dir_path := path.get_base_dir()
	if not DirAccess.dir_exists_absolute(dir_path):
		DirAccess.make_dir_recursive_absolute(dir_path)

	if FileAccess.file_exists(path) and not overwrite:
		return ErrorCodes.make(ErrorCodes.INVALID_PARAMS, "Shader file already exists at %s" % path)

	if code.strip_edges().is_empty():
		code = "shader_type %s;\n\nvoid fragment() {\n\t// Place fragment shader code here.\n}\n" % shader_type

	var file := FileAccess.open(path, FileAccess.WRITE)
	if file == null:
		return ErrorCodes.make(ErrorCodes.RESOURCE_NOT_FOUND, "Failed to write shader file: %s" % error_string(FileAccess.get_open_error()))
	file.store_string(code)
	file.close()

	EditorInterface.get_resource_filesystem().reimport_files(PackedStringArray([path]))

	return {
		"data": {
			"path": path,
			"shader_type": shader_type,
			"code_length": code.length()
		}
	}


func apply_preset(params: Dictionary) -> Dictionary:
	var preset: String = params.get("preset", "")
	var target_node_path: String = params.get("target_node_path", "")
	var shader_path: String = params.get("shader_path", "")
	var uniform_params: Dictionary = params.get("params", {})

	if not PRESETS.has(preset):
		var valid_presets: Array = PRESETS.keys()
		return ErrorCodes.make(
			ErrorCodes.INVALID_PARAMS,
			"Unknown shader preset '%s'. Available presets: %s" % [preset, ", ".join(valid_presets)]
		)

	if shader_path.is_empty():
		shader_path = "res://shaders/%s.gdshader" % preset
	elif not shader_path.begins_with("res://"):
		shader_path = "res://" + shader_path.trim_prefix("/")
	if not shader_path.ends_with(".gdshader"):
		shader_path += ".gdshader"

	var dir_path := shader_path.get_base_dir()
	if not DirAccess.dir_exists_absolute(dir_path):
		DirAccess.make_dir_recursive_absolute(dir_path)

	var code: String = PRESETS[preset]
	var file := FileAccess.open(shader_path, FileAccess.WRITE)
	if file != null:
		file.store_string(code)
		file.close()
		EditorInterface.get_resource_filesystem().reimport_files(PackedStringArray([shader_path]))

	var shader := Shader.new()
	shader.code = code

	var mat := ShaderMaterial.new()
	mat.shader = shader

	for k in uniform_params.keys():
		mat.set_shader_parameter(StringName(k), uniform_params[k])

	var target_node: Node = null
	if not target_node_path.is_empty():
		var scene_root := EditorInterface.get_edited_scene_root()
		if scene_root != null:
			target_node = scene_root.get_node_or_null(NodePath(target_node_path))
			if target_node == null and (target_node_path == scene_root.name or target_node_path == "."):
				target_node = scene_root
			if target_node != null:
				if _undo_redo != null:
					_undo_redo.create_action("Apply Shader Preset " + preset)
					_undo_redo.add_do_property(target_node, "material", mat)
					_undo_redo.add_undo_property(target_node, "material", target_node.get("material"))
					_undo_redo.commit_action()
				else:
					target_node.set("material", mat)

	return {
		"data": {
			"preset": preset,
			"shader_path": shader_path,
			"target_node": target_node.name if target_node != null else "",
			"applied_to_node": target_node != null,
			"uniforms_set": uniform_params.keys()
		}
	}


func set_param(params: Dictionary) -> Dictionary:
	var param_name: String = params.get("param", "")
	var value: Variant = params.get("value")
	var target_node_path: String = params.get("target_node_path", "")
	var material_path: String = params.get("material_path", "")

	if param_name.is_empty():
		return ErrorCodes.make(ErrorCodes.MISSING_REQUIRED_PARAM, "param is required")

	var mat: ShaderMaterial = null
	if not material_path.is_empty():
		var res := ResourceLoader.load(material_path)
		if res is ShaderMaterial:
			mat = res as ShaderMaterial
	elif not target_node_path.is_empty():
		var scene_root := EditorInterface.get_edited_scene_root()
		if scene_root != null:
			var node := scene_root.get_node_or_null(NodePath(target_node_path))
			if node != null and node.get("material") is ShaderMaterial:
				mat = node.get("material") as ShaderMaterial

	if mat == null:
		return ErrorCodes.make(ErrorCodes.RESOURCE_NOT_FOUND, "No ShaderMaterial found on target or material path")

	mat.set_shader_parameter(StringName(param_name), value)
	return {
		"data": {
			"param": param_name,
			"value": value,
			"success": true
		}
	}


func get_params(params: Dictionary) -> Dictionary:
	var target_node_path: String = params.get("target_node_path", "")
	var material_path: String = params.get("material_path", "")

	var mat: ShaderMaterial = null
	if not material_path.is_empty():
		var res := ResourceLoader.load(material_path)
		if res is ShaderMaterial:
			mat = res as ShaderMaterial
	elif not target_node_path.is_empty():
		var scene_root := EditorInterface.get_edited_scene_root()
		if scene_root != null:
			var node := scene_root.get_node_or_null(NodePath(target_node_path))
			if node != null and node.get("material") is ShaderMaterial:
				mat = node.get("material") as ShaderMaterial

	if mat == null:
		return ErrorCodes.make(ErrorCodes.RESOURCE_NOT_FOUND, "No ShaderMaterial found on target or material path")

	var shader := mat.shader
	var code := shader.code if shader != null else ""
	return {
		"data": {
			"has_shader": shader != null,
			"code_length": code.length()
		}
	}
