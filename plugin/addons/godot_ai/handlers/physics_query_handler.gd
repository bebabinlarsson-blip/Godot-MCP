@tool
extends "res://addons/godot_ai/handlers/command_handler.gd"

const ErrorCodes := preload("res://addons/godot_ai/utils/error_codes.gd")

## Handles direct 2D and 3D physics space state raycasts and shape queries.

var _undo_redo: EditorUndoRedoManager
var _connection: McpConnection


func _init(undo_redo: EditorUndoRedoManager = null, connection: McpConnection = null) -> void:
	_undo_redo = undo_redo
	_connection = connection


func _get_world_3d() -> World3D:
	if Engine.is_editor_hint():
		var tree := Engine.get_main_loop() as SceneTree
		if tree != null and tree.root != null:
			var viewport: Viewport = tree.root
			if Engine.has_singleton("EditorInterface"):
				var editor_interface := Engine.get_singleton("EditorInterface")
				if editor_interface.has_method("get_editor_viewport_3d"):
					var vp = editor_interface.get_editor_viewport_3d(0)
					if vp != null and vp.find_world_3d() != null:
						return vp.find_world_3d()
			return viewport.find_world_3d()
	return null


func _get_world_2d() -> World2D:
	if Engine.is_editor_hint():
		var tree := Engine.get_main_loop() as SceneTree
		if tree != null and tree.root != null:
			var viewport: Viewport = tree.root
			if Engine.has_singleton("EditorInterface"):
				var editor_interface := Engine.get_singleton("EditorInterface")
				if editor_interface.has_method("get_editor_viewport_2d"):
					var vp = editor_interface.get_editor_viewport_2d()
					if vp != null and vp.find_world_2d() != null:
						return vp.find_world_2d()
			return viewport.find_world_2d()
	return null


func intersect_ray_3d(params: Dictionary) -> Dictionary:
	var world := _get_world_3d()
	if world == null or world.direct_space_state == null:
		return {"error": "No 3D physics space state available."}

	var from_arr: Array = params.get("from_pos", [0.0, 0.0, 0.0])
	var to_arr: Array = params.get("to_pos", [0.0, -10.0, 0.0])
	var mask: int = int(params.get("collision_mask", 0xFFFFFFFF))
	var collide_with_bodies: bool = params.get("collide_with_bodies", true)
	var collide_with_areas: bool = params.get("collide_with_areas", false)

	var from_vec := Vector3(float(from_arr[0]), float(from_arr[1]), float(from_arr[2]))
	var to_vec := Vector3(float(to_arr[0]), float(to_arr[1]), float(to_arr[2]))

	var query := PhysicsRayQueryParameters3D.create(from_vec, to_vec, mask)
	query.collide_with_bodies = collide_with_bodies
	query.collide_with_areas = collide_with_areas

	var hit: Dictionary = world.direct_space_state.intersect_ray(query)
	if hit.is_empty():
		return {"status": "ok", "hit": false}

	var collider = hit.get("collider")
	var collider_path: String = ""
	if collider is Node:
		collider_path = str(collider.get_path())

	var pos: Vector3 = hit.get("position", Vector3.ZERO)
	var norm: Vector3 = hit.get("normal", Vector3.UP)

	return {
		"status": "ok",
		"hit": true,
		"position": [pos.x, pos.y, pos.z],
		"normal": [norm.x, norm.y, norm.z],
		"collider_path": collider_path,
		"collider_id": hit.get("collider_id", 0),
		"shape": hit.get("shape", 0),
	}


func intersect_ray_2d(params: Dictionary) -> Dictionary:
	var world := _get_world_2d()
	if world == null or world.direct_space_state == null:
		return {"error": "No 2D physics space state available."}

	var from_arr: Array = params.get("from_pos", [0.0, 0.0])
	var to_arr: Array = params.get("to_pos", [0.0, 100.0])
	var mask: int = int(params.get("collision_mask", 0xFFFFFFFF))
	var collide_with_bodies: bool = params.get("collide_with_bodies", true)
	var collide_with_areas: bool = params.get("collide_with_areas", false)

	var from_vec := Vector2(float(from_arr[0]), float(from_arr[1]))
	var to_vec := Vector2(float(to_arr[0]), float(to_arr[1]))

	var query := PhysicsRayQueryParameters2D.create(from_vec, to_vec, mask)
	query.collide_with_bodies = collide_with_bodies
	query.collide_with_areas = collide_with_areas

	var hit: Dictionary = world.direct_space_state.intersect_ray(query)
	if hit.is_empty():
		return {"status": "ok", "hit": false}

	var collider = hit.get("collider")
	var collider_path: String = ""
	if collider is Node:
		collider_path = str(collider.get_path())

	var pos: Vector2 = hit.get("position", Vector2.ZERO)
	var norm: Vector2 = hit.get("normal", Vector2.UP)

	return {
		"status": "ok",
		"hit": true,
		"position": [pos.x, pos.y],
		"normal": [norm.x, norm.y],
		"collider_path": collider_path,
		"collider_id": hit.get("collider_id", 0),
		"shape": hit.get("shape", 0),
	}


func intersect_point_3d(params: Dictionary) -> Dictionary:
	var world := _get_world_3d()
	if world == null or world.direct_space_state == null:
		return {"error": "No 3D physics space state available."}

	var pos_arr: Array = params.get("position", [0.0, 0.0, 0.0])
	var max_results: int = int(params.get("max_results", 32))
	var mask: int = int(params.get("collision_mask", 0xFFFFFFFF))

	var query := PhysicsPointQueryParameters3D.new()
	query.position = Vector3(float(pos_arr[0]), float(pos_arr[1]), float(pos_arr[2]))
	query.collision_mask = mask

	var hits: Array[Dictionary] = world.direct_space_state.intersect_point(query, max_results)
	var results: Array = []
	for h in hits:
		var c = h.get("collider")
		results.append({
			"collider_path": str(c.get_path()) if c is Node else "",
			"collider_id": h.get("collider_id", 0),
			"shape": h.get("shape", 0),
		})

	return {"status": "ok", "count": results.size(), "results": results}


func intersect_point_2d(params: Dictionary) -> Dictionary:
	var world := _get_world_2d()
	if world == null or world.direct_space_state == null:
		return {"error": "No 2D physics space state available."}

	var pos_arr: Array = params.get("position", [0.0, 0.0])
	var max_results: int = int(params.get("max_results", 32))
	var mask: int = int(params.get("collision_mask", 0xFFFFFFFF))

	var query := PhysicsPointQueryParameters2D.new()
	query.position = Vector2(float(pos_arr[0]), float(pos_arr[1]))
	query.collision_mask = mask

	var hits: Array[Dictionary] = world.direct_space_state.intersect_point(query, max_results)
	var results: Array = []
	for h in hits:
		var c = h.get("collider")
		results.append({
			"collider_path": str(c.get_path()) if c is Node else "",
			"collider_id": h.get("collider_id", 0),
			"shape": h.get("shape", 0),
		})

	return {"status": "ok", "count": results.size(), "results": results}


func intersect_shape_3d(params: Dictionary) -> Dictionary:
	var world := _get_world_3d()
	if world == null or world.direct_space_state == null:
		return {"error": "No 3D physics space state available."}

	var shape_type: String = params.get("shape_type", "sphere")
	var radius: float = float(params.get("radius", 1.0))
	var max_results: int = int(params.get("max_results", 32))

	var shape: Shape3D = null
	if shape_type == "box":
		var b := BoxShape3D.new()
		b.size = Vector3(radius, radius, radius)
		shape = b
	else:
		var s := SphereShape3D.new()
		s.radius = radius
		shape = s

	var query := PhysicsShapeQueryParameters3D.new()
	query.shape = shape
	query.transform = Transform3D.IDENTITY

	var hits: Array[Dictionary] = world.direct_space_state.intersect_shape(query, max_results)
	return {"status": "ok", "count": hits.size()}


func cast_motion_3d(params: Dictionary) -> Dictionary:
	var world := _get_world_3d()
	if world == null or world.direct_space_state == null:
		return {"error": "No 3D physics space state available."}

	var shape_type: String = params.get("shape_type", "sphere")
	var radius: float = float(params.get("radius", 1.0))
	var motion_arr: Array = params.get("motion", [0.0, -1.0, 0.0])

	var shape: Shape3D = SphereShape3D.new()
	if shape_type == "box":
		var b := BoxShape3D.new()
		b.size = Vector3(radius, radius, radius)
		shape = b
	else:
		(shape as SphereShape3D).radius = radius

	var query := PhysicsShapeQueryParameters3D.new()
	query.shape = shape
	query.motion = Vector3(float(motion_arr[0]), float(motion_arr[1]), float(motion_arr[2]))

	var safe_unsafe: PackedFloat32Array = world.direct_space_state.cast_motion(query)
	var safe: float = safe_unsafe[0] if safe_unsafe.size() > 0 else 1.0
	var unsafe: float = safe_unsafe[1] if safe_unsafe.size() > 1 else 1.0

	return {"status": "ok", "safe_fraction": safe, "unsafe_fraction": unsafe}
