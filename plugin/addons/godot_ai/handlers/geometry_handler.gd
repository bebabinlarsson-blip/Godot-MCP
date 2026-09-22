@tool
extends "res://addons/godot_ai/handlers/command_handler.gd"

const ErrorCodes := preload("res://addons/godot_ai/utils/error_codes.gd")

## Handles 2D constructive solid geometry (Geometry2D boolean operations,
## offset, triangulation, convex hull) and procedural 3D mesh synthesis via SurfaceTool.

var _undo_redo: EditorUndoRedoManager
var _connection: McpConnection


func _init(undo_redo: EditorUndoRedoManager, connection: McpConnection = null) -> void:
	_undo_redo = undo_redo
	_connection = connection


func _to_vector2_array(raw_points: Array) -> PackedVector2Array:
	var result := PackedVector2Array()
	for pt in raw_points:
		if pt is Array and pt.size() >= 2:
			result.append(Vector2(float(pt[0]), float(pt[1])))
	return result


func _from_vector2_array(points: PackedVector2Array) -> Array:
	var result: Array = []
	for p in points:
		result.append([p.x, p.y])
	return result


func _from_polygons(polys: Array[PackedVector2Array]) -> Array:
	var result: Array = []
	for poly in polys:
		result.append(_from_vector2_array(poly))
	return result


func polygon_boolean(params: Dictionary) -> Dictionary:
	var op: String = params.get("operation", "merge").to_lower()
	var raw_a: Array = params.get("poly_a", [])
	var raw_b: Array = params.get("poly_b", [])

	var poly_a := _to_vector2_array(raw_a)
	var poly_b := _to_vector2_array(raw_b)

	if poly_a.size() < 3:
		return ErrorCodes.make(ErrorCodes.VALUE_OUT_OF_RANGE, "poly_a must contain at least 3 points")
	if poly_b.size() < 3:
		return ErrorCodes.make(ErrorCodes.VALUE_OUT_OF_RANGE, "poly_b must contain at least 3 points")

	var output_polys: Array[PackedVector2Array] = []
	match op:
		"merge":
			output_polys = Geometry2D.merge_polygons(poly_a, poly_b)
		"clip":
			output_polys = Geometry2D.clip_polygons(poly_a, poly_b)
		"intersect":
			output_polys = Geometry2D.intersect_polygons(poly_a, poly_b)
		"exclude":
			output_polys = Geometry2D.exclude_polygons(poly_a, poly_b)
		_:
			return ErrorCodes.make(ErrorCodes.VALUE_OUT_OF_RANGE,
				"Unknown operation '%s'. Valid: merge, clip, intersect, exclude" % op)

	return {
		"data": {
			"operation": op,
			"result_count": output_polys.size(),
			"polygons": _from_polygons(output_polys)
		}
	}


func polygon_offset(params: Dictionary) -> Dictionary:
	var raw_poly: Array = params.get("polygon", [])
	var delta: float = float(params.get("delta", 5.0))
	var join_str: String = params.get("join_type", "square").to_lower()

	var poly := _to_vector2_array(raw_poly)
	if poly.size() < 3:
		return ErrorCodes.make(ErrorCodes.VALUE_OUT_OF_RANGE, "polygon must contain at least 3 points")

	var join_type := Geometry2D.JOIN_SQUARE
	match join_str:
		"square":
			join_type = Geometry2D.JOIN_SQUARE
		"round":
			join_type = Geometry2D.JOIN_ROUND
		"miter":
			join_type = Geometry2D.JOIN_MITER
		_:
			return ErrorCodes.make(ErrorCodes.VALUE_OUT_OF_RANGE,
				"Unknown join_type '%s'. Valid: square, round, miter" % join_str)

	var output_polys := Geometry2D.offset_polygon(poly, delta, join_type)
	return {
		"data": {
			"delta": delta,
			"join_type": join_str,
			"result_count": output_polys.size(),
			"polygons": _from_polygons(output_polys)
		}
	}


func triangulate(params: Dictionary) -> Dictionary:
	var raw_poly: Array = params.get("polygon", [])
	var poly := _to_vector2_array(raw_poly)
	if poly.size() < 3:
		return ErrorCodes.make(ErrorCodes.VALUE_OUT_OF_RANGE, "polygon must contain at least 3 points")

	var indices: PackedInt32Array = Geometry2D.triangulate_polygon(poly)
	var triangles: Array = []
	for i in range(0, indices.size(), 3):
		if i + 2 < indices.size():
			triangles.append([indices[i], indices[i + 1], indices[i + 2]])

	return {
		"data": {
			"point_count": poly.size(),
			"triangle_count": triangles.size(),
			"indices": Array(indices),
			"triangles": triangles
		}
	}


func convex_hull(params: Dictionary) -> Dictionary:
	var raw_points: Array = params.get("points", [])
	var points := _to_vector2_array(raw_points)
	if points.size() < 3:
		return ErrorCodes.make(ErrorCodes.VALUE_OUT_OF_RANGE, "points must contain at least 3 items")

	var hull: PackedVector2Array = Geometry2D.convex_hull(points)
	return {
		"data": {
			"input_count": points.size(),
			"hull_count": hull.size(),
			"polygon": _from_vector2_array(hull)
		}
	}


func scaffold_polygon_2d(params: Dictionary) -> Dictionary:
	var scene_root := EditorInterface.get_edited_scene_root()
	if scene_root == null:
		return ErrorCodes.make(ErrorCodes.EDITOR_NOT_READY, "No active scene open")

	var parent_path: String = params.get("parent_path", "")
	var parent: Node = scene_root
	if not parent_path.is_empty():
		parent = scene_root.get_node_or_null(NodePath(parent_path))
		if parent == null:
			return ErrorCodes.make(ErrorCodes.NODE_NOT_FOUND, "Parent node not found at %s" % parent_path)

	var is_collision: bool = bool(params.get("is_collision", false))
	var poly_name: String = params.get("polygon_name", "CustomCollisionPolygon" if is_collision else "CustomPolygon")
	var raw_points: Array = params.get("points", [[-50, -50], [50, -50], [50, 50], [-50, 50]])
	var points := _to_vector2_array(raw_points)
	if points.size() < 3:
		return ErrorCodes.make(ErrorCodes.VALUE_OUT_OF_RANGE, "points must contain at least 3 vertices")

	var node: Node = null
	if is_collision:
		var cpoly := CollisionPolygon2D.new()
		cpoly.name = poly_name
		cpoly.polygon = points
		node = cpoly
	else:
		var p2d := Polygon2D.new()
		p2d.name = poly_name
		p2d.polygon = points
		var raw_color = params.get("color", [1.0, 1.0, 1.0, 1.0])
		if raw_color is Array and raw_color.size() >= 4:
			p2d.color = Color(float(raw_color[0]), float(raw_color[1]), float(raw_color[2]), float(raw_color[3]))
		node = p2d

	if _undo_redo != null:
		_undo_redo.create_action("Scaffold Polygon " + poly_name)
		_undo_redo.add_do_method(parent, "add_child", node)
		_undo_redo.add_do_property(node, "owner", scene_root)
		_undo_redo.add_undo_method(parent, "remove_child", node)
		_undo_redo.commit_action()
	else:
		parent.add_child(node)
		node.owner = scene_root

	return {
		"data": {
			"node_name": str(node.name),
			"node_path": str(node.get_path()),
			"is_collision": is_collision,
			"vertex_count": points.size()
		}
	}


func generate_mesh(params: Dictionary) -> Dictionary:
	var mesh_type: String = params.get("mesh_type", "cube").to_lower()
	var dest_path: String = params.get("dest_path", "")
	var parent_path: String = params.get("parent_path", "")
	var size_raw = params.get("size", [2.0, 2.0, 2.0])
	var sx: float = float(size_raw[0]) if size_raw is Array and size_raw.size() >= 1 else 2.0
	var sy: float = float(size_raw[1]) if size_raw is Array and size_raw.size() >= 2 else sx
	var sz: float = float(size_raw[2]) if size_raw is Array and size_raw.size() >= 3 else sx

	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)

	match mesh_type:
		"plane":
			var hx := sx * 0.5
			var hz := sz * 0.5
			st.set_normal(Vector3.UP)
			st.set_uv(Vector2(0, 0))
			st.add_vertex(Vector3(-hx, 0, -hz))
			st.set_uv(Vector2(1, 0))
			st.add_vertex(Vector3(hx, 0, -hz))
			st.set_uv(Vector2(1, 1))
			st.add_vertex(Vector3(hx, 0, hz))

			st.set_uv(Vector2(0, 0))
			st.add_vertex(Vector3(-hx, 0, -hz))
			st.set_uv(Vector2(1, 1))
			st.add_vertex(Vector3(hx, 0, hz))
			st.set_uv(Vector2(0, 1))
			st.add_vertex(Vector3(-hx, 0, hz))

		"cube":
			var hx := sx * 0.5
			var hy := sy * 0.5
			var hz := sz * 0.5
			var faces = [
				## Front (+Z)
				[Vector3.BACK, [Vector3(-hx, -hy, hz), Vector3(hx, -hy, hz), Vector3(hx, hy, hz), Vector3(-hx, hy, hz)]],
				## Back (-Z)
				[Vector3.FORWARD, [Vector3(hx, -hy, -hz), Vector3(-hx, -hy, -hz), Vector3(-hx, hy, -hz), Vector3(hx, hy, -hz)]],
				## Top (+Y)
				[Vector3.UP, [Vector3(-hx, hy, hz), Vector3(hx, hy, hz), Vector3(hx, hy, -hz), Vector3(-hx, hy, -hz)]],
				## Bottom (-Y)
				[Vector3.DOWN, [Vector3(-hx, -hy, -hz), Vector3(hx, -hy, -hz), Vector3(hx, -hy, hz), Vector3(-hx, -hy, hz)]],
				## Right (+X)
				[Vector3.RIGHT, [Vector3(hx, -hy, hz), Vector3(hx, -hy, -hz), Vector3(hx, hy, -hz), Vector3(hx, hy, hz)]],
				## Left (-X)
				[Vector3.LEFT, [Vector3(-hx, -hy, -hz), Vector3(-hx, -hy, hz), Vector3(-hx, hy, hz), Vector3(-hx, hy, -hz)]],
			]
			for f in faces:
				var n: Vector3 = f[0]
				var v: Array = f[1]
				st.set_normal(n)
				st.set_uv(Vector2(0, 1))
				st.add_vertex(v[0])
				st.set_uv(Vector2(1, 1))
				st.add_vertex(v[1])
				st.set_uv(Vector2(1, 0))
				st.add_vertex(v[2])

				st.set_uv(Vector2(0, 1))
				st.add_vertex(v[0])
				st.set_uv(Vector2(1, 0))
				st.add_vertex(v[2])
				st.set_uv(Vector2(0, 0))
				st.add_vertex(v[3])

		"pyramid":
			var hx := sx * 0.5
			var hz := sz * 0.5
			var apex := Vector3(0, sy, 0)
			var b0 := Vector3(-hx, 0, -hz)
			var b1 := Vector3(hx, 0, -hz)
			var b2 := Vector3(hx, 0, hz)
			var b3 := Vector3(-hx, 0, hz)
			## Base
			st.set_normal(Vector3.DOWN)
			st.add_vertex(b0); st.add_vertex(b1); st.add_vertex(b2)
			st.add_vertex(b0); st.add_vertex(b2); st.add_vertex(b3)
			## Sides
			st.set_normal((b0 + b1).normalized())
			st.add_vertex(b0); st.add_vertex(apex); st.add_vertex(b1)
			st.set_normal((b1 + b2).normalized())
			st.add_vertex(b1); st.add_vertex(apex); st.add_vertex(b2)
			st.set_normal((b2 + b3).normalized())
			st.add_vertex(b2); st.add_vertex(apex); st.add_vertex(b3)
			st.set_normal((b3 + b0).normalized())
			st.add_vertex(b3); st.add_vertex(apex); st.add_vertex(b0)
		_:
			return ErrorCodes.make(ErrorCodes.VALUE_OUT_OF_RANGE,
				"Unknown mesh_type '%s'. Valid: plane, cube, pyramid" % mesh_type)

	var array_mesh: ArrayMesh = st.commit()

	if not dest_path.is_empty():
		if not dest_path.begins_with("res://"):
			return ErrorCodes.make(ErrorCodes.INVALID_PARAMS, "dest_path must start with res://")
		var err := ResourceSaver.save(array_mesh, dest_path)
		if err != OK:
			return ErrorCodes.make(ErrorCodes.INTERNAL_ERROR, "Failed to save mesh to %s (error %d)" % [dest_path, err])

	var attached_node_path := ""
	var scene_root := EditorInterface.get_edited_scene_root()
	if scene_root != null:
		var parent: Node = scene_root
		if not parent_path.is_empty():
			parent = scene_root.get_node_or_null(NodePath(parent_path))
		if parent != null:
			var mi := MeshInstance3D.new()
			mi.name = mesh_type.capitalize() + "Mesh"
			mi.mesh = array_mesh
			if _undo_redo != null:
				_undo_redo.create_action("Scaffold MeshInstance3D " + mi.name)
				_undo_redo.add_do_method(parent, "add_child", mi)
				_undo_redo.add_do_property(mi, "owner", scene_root)
				_undo_redo.add_undo_method(parent, "remove_child", mi)
				_undo_redo.commit_action()
			else:
				parent.add_child(mi)
				mi.owner = scene_root
			attached_node_path = str(mi.get_path())

	return {
		"data": {
			"mesh_type": mesh_type,
			"surface_count": array_mesh.get_surface_count(),
			"dest_path": dest_path,
			"attached_node_path": attached_node_path
		}
	}
