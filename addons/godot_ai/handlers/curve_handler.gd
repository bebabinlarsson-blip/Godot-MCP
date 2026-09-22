@tool
extends "res://addons/godot_ai/handlers/command_handler.gd"

const ErrorCodes := preload("res://addons/godot_ai/utils/error_codes.gd")

## Handles Curves (1D, 2D, 3D), Gradients, and GradientTextures.

var _undo_redo: EditorUndoRedoManager
var _connection: McpConnection


func _init(undo_redo: EditorUndoRedoManager = null, connection: McpConnection = null) -> void:
	_undo_redo = undo_redo
	_connection = connection


func create_curve_1d(params: Dictionary) -> Dictionary:
	var curve := Curve.new()
	curve.min_value = float(params.get("min_value", 0.0))
	curve.max_value = float(params.get("max_value", 1.0))

	var points: Array = params.get("points", [[0.0, 0.0], [1.0, 1.0]])
	curve.clear_points()
	for pt in points:
		if pt is Array and pt.size() >= 2:
			var pos := Vector2(float(pt[0]), float(pt[1]))
			var left_tangent: float = float(pt[2]) if pt.size() > 2 else 0.0
			var right_tangent: float = float(pt[3]) if pt.size() > 3 else 0.0
			curve.add_point(pos, left_tangent, right_tangent)

	var save_path: String = params.get("save_path", "")
	if not save_path.is_empty():
		var err := ResourceSaver.save(curve, save_path)
		if err != OK:
			return {"error": "Failed to save Curve to %s (code %d)" % [save_path, err]}

	return {
		"status": "ok",
		"point_count": curve.point_count,
		"min_value": curve.min_value,
		"max_value": curve.max_value,
		"save_path": save_path,
	}


func create_curve_2d(params: Dictionary) -> Dictionary:
	var curve := Curve2D.new()
	var points: Array = params.get("points", [[0.0, 0.0], [100.0, 100.0]])
	var in_tangents: Array = params.get("in_tangents", [])
	var out_tangents: Array = params.get("out_tangents", [])

	for i in range(points.size()):
		var pt = points[i]
		if pt is Array and pt.size() >= 2:
			var pos := Vector2(float(pt[0]), float(pt[1]))
			var in_tan := Vector2.ZERO
			var out_tan := Vector2.ZERO
			if i < in_tangents.size() and in_tangents[i] is Array and in_tangents[i].size() >= 2:
				in_tan = Vector2(float(in_tangents[i][0]), float(in_tangents[i][1]))
			if i < out_tangents.size() and out_tangents[i] is Array and out_tangents[i].size() >= 2:
				out_tan = Vector2(float(out_tangents[i][0]), float(out_tangents[i][1]))
			curve.add_point(pos, in_tan, out_tan)

	var save_path: String = params.get("save_path", "")
	if not save_path.is_empty():
		var err := ResourceSaver.save(curve, save_path)
		if err != OK:
			return {"error": "Failed to save Curve2D to %s (code %d)" % [save_path, err]}

	return {
		"status": "ok",
		"point_count": curve.point_count,
		"save_path": save_path,
	}


func create_curve_3d(params: Dictionary) -> Dictionary:
	var curve := Curve3D.new()
	var points: Array = params.get("points", [[0.0, 0.0, 0.0], [0.0, 5.0, 10.0]])
	var in_tangents: Array = params.get("in_tangents", [])
	var out_tangents: Array = params.get("out_tangents", [])

	for i in range(points.size()):
		var pt = points[i]
		if pt is Array and pt.size() >= 3:
			var pos := Vector3(float(pt[0]), float(pt[1]), float(pt[2]))
			var in_tan := Vector3.ZERO
			var out_tan := Vector3.ZERO
			if i < in_tangents.size() and in_tangents[i] is Array and in_tangents[i].size() >= 3:
				in_tan = Vector3(float(in_tangents[i][0]), float(in_tangents[i][1]), float(in_tangents[i][2]))
			if i < out_tangents.size() and out_tangents[i] is Array and out_tangents[i].size() >= 3:
				out_tan = Vector3(float(out_tangents[i][0]), float(out_tangents[i][1]), float(out_tangents[i][2]))
			curve.add_point(pos, in_tan, out_tan)

	var save_path: String = params.get("save_path", "")
	if not save_path.is_empty():
		var err := ResourceSaver.save(curve, save_path)
		if err != OK:
			return {"error": "Failed to save Curve3D to %s (code %d)" % [save_path, err]}

	return {
		"status": "ok",
		"point_count": curve.point_count,
		"save_path": save_path,
	}


func create_gradient(params: Dictionary) -> Dictionary:
	var gradient := Gradient.new()
	var offsets: Array = params.get("offsets", [0.0, 1.0])
	var colors: Array = params.get("colors", ["#000000", "#ffffff"])

	var count: int = mini(offsets.size(), colors.size())
	if count > 0:
		var packed_offsets := PackedFloat32Array()
		var packed_colors := PackedColorArray()
		for i in range(count):
			packed_offsets.append(float(offsets[i]))
			packed_colors.append(Color.from_string(str(colors[i]), Color.WHITE))
		gradient.offsets = packed_offsets
		gradient.colors = packed_colors

	var save_path: String = params.get("save_path", "")
	if not save_path.is_empty():
		var err := ResourceSaver.save(gradient, save_path)
		if err != OK:
			return {"error": "Failed to save Gradient to %s (code %d)" % [save_path, err]}

	return {
		"status": "ok",
		"point_count": gradient.get_point_count(),
		"save_path": save_path,
	}


func create_gradient_texture(params: Dictionary) -> Dictionary:
	var gradient: Gradient = null
	var gradient_path: String = params.get("gradient_path", "")
	if not gradient_path.is_empty() and ResourceLoader.exists(gradient_path):
		gradient = load(gradient_path) as Gradient

	if gradient == null:
		gradient = Gradient.new()

	var is_2d: bool = params.get("is_2d", false)
	var width_val: int = int(params.get("width", 256))
	var height_val: int = int(params.get("height", 256))

	var tex: Resource
	if is_2d:
		var tex2d := GradientTexture2D.new()
		tex2d.gradient = gradient
		tex2d.width = width_val
		tex2d.height = height_val
		tex = tex2d
	else:
		var tex1d := GradientTexture1D.new()
		tex1d.gradient = gradient
		tex1d.width = width_val
		tex = tex1d

	var save_path: String = params.get("save_path", "")
	if not save_path.is_empty():
		var err := ResourceSaver.save(tex, save_path)
		if err != OK:
			return {"error": "Failed to save GradientTexture to %s (code %d)" % [save_path, err]}

	return {
		"status": "ok",
		"type": "GradientTexture2D" if is_2d else "GradientTexture1D",
		"width": width_val,
		"save_path": save_path,
	}


func sample_curve(params: Dictionary) -> Dictionary:
	var curve_path: String = params.get("curve_path", "")
	var offset: float = float(params.get("offset", 0.5))

	if curve_path.is_empty() or not ResourceLoader.exists(curve_path):
		return {"error": "Curve resource not found at: %s" % curve_path}

	var res := load(curve_path)
	if res is Curve:
		return {"status": "ok", "value": res.sample(offset)}
	elif res is Curve2D:
		var p: Vector2 = res.sample_baked(offset * res.get_baked_length())
		return {"status": "ok", "position": [p.x, p.y]}
	elif res is Curve3D:
		var p: Vector3 = res.sample_baked(offset * res.get_baked_length())
		return {"status": "ok", "position": [p.x, p.y, p.z]}

	return {"error": "Resource is not a recognized Curve type."}


func sample_gradient(params: Dictionary) -> Dictionary:
	var gradient_path: String = params.get("gradient_path", "")
	var offset: float = float(params.get("offset", 0.5))

	if gradient_path.is_empty() or not ResourceLoader.exists(gradient_path):
		return {"error": "Gradient resource not found at: %s" % gradient_path}

	var res := load(gradient_path)
	if res is Gradient:
		var col: Color = res.sample(offset)
		return {"status": "ok", "color": [col.r, col.g, col.b, col.a]}

	return {"error": "Resource is not a Gradient."}
