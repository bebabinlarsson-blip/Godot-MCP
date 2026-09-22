@tool
extends "res://addons/godot_ai/handlers/command_handler.gd"

const ErrorCodes := preload("res://addons/godot_ai/utils/error_codes.gd")

var _undo_redo: EditorUndoRedoManager
var _connection: McpConnection


func _init(undo_redo: EditorUndoRedoManager, connection: McpConnection = null) -> void:
	_undo_redo = undo_redo
	_connection = connection


func raycast_2d(params: Dictionary) -> Dictionary:
	var scene_root := EditorInterface.get_edited_scene_root()
	if scene_root == null:
		return ErrorCodes.make(ErrorCodes.EDITOR_NOT_READY, "No active scene open")

	var world_2d := scene_root.get_viewport().find_world_2d() if scene_root.get_viewport() != null else null
	if world_2d == null:
		return ErrorCodes.make(ErrorCodes.INTERNAL_ERROR, "World2D not available for active scene")

	var direct_state := PhysicsServer2D.space_get_direct_state(world_2d.space)
	if direct_state == null:
		return ErrorCodes.make(ErrorCodes.INTERNAL_ERROR, "Direct space state 2D not available")

	var from_raw = params.get("from_pos", [0, 0])
	var to_raw = params.get("to_pos", [0, 100])
	var from_vec := Vector2(float(from_raw[0]), float(from_raw[1])) if from_raw is Array and from_raw.size() >= 2 else Vector2.ZERO
	var to_vec := Vector2(float(to_raw[0]), float(to_raw[1])) if to_raw is Array and to_raw.size() >= 2 else Vector2(0, 100)

	var query := PhysicsRayQueryParameters2D.create(from_vec, to_vec)
	query.collision_mask = int(params.get("collision_mask", 4294967295))
	query.collide_with_bodies = bool(params.get("collide_with_bodies", true))
	query.collide_with_areas = bool(params.get("collide_with_areas", false))
	query.hit_from_inside = bool(params.get("hit_from_inside", false))

	var result := direct_state.intersect_ray(query)
	if result.is_empty():
		return {
			"data": {
				"hit": false,
				"from": [from_vec.x, from_vec.y],
				"to": [to_vec.x, to_vec.y]
			}
		}

	var collider: Object = result.get("collider")
	var collider_node := collider as Node
	return {
		"data": {
			"hit": true,
			"position": [result.position.x, result.position.y],
			"normal": [result.normal.x, result.normal.y],
			"collider_id": result.collider_id,
			"collider_name": collider_node.name if collider_node != null else "",
			"collider_path": str(collider_node.get_path()) if collider_node != null else "",
			"shape": result.shape
		}
	}


func raycast_3d(params: Dictionary) -> Dictionary:
	var scene_root := EditorInterface.get_edited_scene_root()
	if scene_root == null:
		return ErrorCodes.make(ErrorCodes.EDITOR_NOT_READY, "No active scene open")

	var world_3d := scene_root.get_viewport().find_world_3d() if scene_root.get_viewport() != null else null
	if world_3d == null:
		return ErrorCodes.make(ErrorCodes.INTERNAL_ERROR, "World3D not available for active scene")

	var direct_state := PhysicsServer3D.space_get_direct_state(world_3d.space)
	if direct_state == null:
		return ErrorCodes.make(ErrorCodes.INTERNAL_ERROR, "Direct space state 3D not available")

	var from_raw = params.get("from_pos", [0, 10, 0])
	var to_raw = params.get("to_pos", [0, -10, 0])
	var from_vec := Vector3(float(from_raw[0]), float(from_raw[1]), float(from_raw[2])) if from_raw is Array and from_raw.size() >= 3 else Vector3(0, 10, 0)
	var to_vec := Vector3(float(to_raw[0]), float(to_raw[1]), float(to_raw[2])) if to_raw is Array and to_raw.size() >= 3 else Vector3(0, -10, 0)

	var query := PhysicsRayQueryParameters3D.create(from_vec, to_vec)
	query.collision_mask = int(params.get("collision_mask", 4294967295))
	query.collide_with_bodies = bool(params.get("collide_with_bodies", true))
	query.collide_with_areas = bool(params.get("collide_with_areas", false))
	query.hit_from_inside = bool(params.get("hit_from_inside", false))

	var result := direct_state.intersect_ray(query)
	if result.is_empty():
		return {
			"data": {
				"hit": false,
				"from": [from_vec.x, from_vec.y, from_vec.z],
				"to": [to_vec.x, to_vec.y, to_vec.z]
			}
		}

	var collider: Object = result.get("collider")
	var collider_node := collider as Node
	return {
		"data": {
			"hit": true,
			"position": [result.position.x, result.position.y, result.position.z],
			"normal": [result.normal.x, result.normal.y, result.normal.z],
			"collider_id": result.collider_id,
			"collider_name": collider_node.name if collider_node != null else "",
			"collider_path": str(collider_node.get_path()) if collider_node != null else "",
			"shape": result.shape
		}
	}


func query_point_2d(params: Dictionary) -> Dictionary:
	var scene_root := EditorInterface.get_edited_scene_root()
	if scene_root == null:
		return ErrorCodes.make(ErrorCodes.EDITOR_NOT_READY, "No active scene open")

	var world_2d := scene_root.get_viewport().find_world_2d() if scene_root.get_viewport() != null else null
	if world_2d == null:
		return ErrorCodes.make(ErrorCodes.INTERNAL_ERROR, "World2D not available for active scene")

	var direct_state := PhysicsServer2D.space_get_direct_state(world_2d.space)
	if direct_state == null:
		return ErrorCodes.make(ErrorCodes.INTERNAL_ERROR, "Direct space state 2D not available")

	var pt_raw = params.get("point", [0, 0])
	var pt_vec := Vector2(float(pt_raw[0]), float(pt_raw[1])) if pt_raw is Array and pt_raw.size() >= 2 else Vector2.ZERO

	var query := PhysicsPointQueryParameters2D.new()
	query.position = pt_vec
	query.collision_mask = int(params.get("collision_mask", 4294967295))
	query.collide_with_bodies = bool(params.get("collide_with_bodies", true))
	query.collide_with_areas = bool(params.get("collide_with_areas", false))

	var max_results: int = int(params.get("max_results", 32))
	var results := direct_state.intersect_point(query, max_results)

	var items: Array = []
	for res in results:
		var collider: Object = res.get("collider")
		var node := collider as Node
		items.append({
			"collider_id": res.collider_id,
			"collider_name": node.name if node != null else "",
			"collider_path": str(node.get_path()) if node != null else "",
			"shape": res.shape
		})

	return {
		"data": {
			"point": [pt_vec.x, pt_vec.y],
			"count": items.size(),
			"results": items
		}
	}


func scaffold_sensor(params: Dictionary) -> Dictionary:
	var scene_root := EditorInterface.get_edited_scene_root()
	if scene_root == null:
		return ErrorCodes.make(ErrorCodes.EDITOR_NOT_READY, "No active scene open")

	var parent_path: String = params.get("parent_path", "")
	var parent: Node = scene_root
	if not parent_path.is_empty():
		parent = scene_root.get_node_or_null(NodePath(parent_path))
		if parent == null:
			return ErrorCodes.make(ErrorCodes.NODE_NOT_FOUND, "Parent node not found at %s" % parent_path)

	var is_2d: bool = bool(params.get("is_2d", true))
	var sensor_name: String = params.get("sensor_name", "RaySensor")
	var target_pos = params.get("target_position", [0, 50] if is_2d else [0, -2, 0])
	var mask: int = int(params.get("collision_mask", 1))
	var enabled: bool = bool(params.get("enabled", true))

	var sensor_node: Node = null
	if is_2d:
		var ray2d := RayCast2D.new()
		ray2d.name = sensor_name
		ray2d.target_position = Vector2(float(target_pos[0]), float(target_pos[1])) if target_pos is Array and target_pos.size() >= 2 else Vector2(0, 50)
		ray2d.collision_mask = mask
		ray2d.enabled = enabled
		sensor_node = ray2d
	else:
		var ray3d := RayCast3D.new()
		ray3d.name = sensor_name
		ray3d.target_position = Vector3(float(target_pos[0]), float(target_pos[1]), float(target_pos[2])) if target_pos is Array and target_pos.size() >= 3 else Vector3(0, -2, 0)
		ray3d.collision_mask = mask
		ray3d.enabled = enabled
		sensor_node = ray3d

	if _undo_redo != null:
		_undo_redo.create_action("Scaffold RayCast Sensor " + sensor_name)
		_undo_redo.add_do_method(parent, "add_child", sensor_node)
		_undo_redo.add_do_property(sensor_node, "owner", scene_root)
		_undo_redo.add_undo_method(parent, "remove_child", sensor_node)
		_undo_redo.commit_action()
	else:
		parent.add_child(sensor_node)
		sensor_node.owner = scene_root

	return {
		"data": {
			"node_name": str(sensor_node.name),
			"node_path": str(sensor_node.get_path()),
			"is_2d": is_2d,
			"target_position": target_pos,
			"collision_mask": mask
		}
	}


func query_point_3d(params: Dictionary) -> Dictionary:
	var scene_root := EditorInterface.get_edited_scene_root()
	if scene_root == null:
		return ErrorCodes.make(ErrorCodes.EDITOR_NOT_READY, "No active scene open")

	var world_3d := scene_root.get_viewport().find_world_3d() if scene_root.get_viewport() != null else null
	if world_3d == null:
		return ErrorCodes.make(ErrorCodes.INTERNAL_ERROR, "World3D not available for active scene")

	var direct_state := PhysicsServer3D.space_get_direct_state(world_3d.space)
	if direct_state == null:
		return ErrorCodes.make(ErrorCodes.INTERNAL_ERROR, "Direct space state 3D not available")

	var pt_raw = params.get("point", [0, 0, 0])
	var pt_vec := Vector3(float(pt_raw[0]), float(pt_raw[1]), float(pt_raw[2])) if pt_raw is Array and pt_raw.size() >= 3 else Vector3.ZERO

	var query := PhysicsPointQueryParameters3D.new()
	query.position = pt_vec
	query.collision_mask = int(params.get("collision_mask", 4294967295))
	query.collide_with_bodies = bool(params.get("collide_with_bodies", true))
	query.collide_with_areas = bool(params.get("collide_with_areas", false))

	var max_results: int = int(params.get("max_results", 32))
	var results := direct_state.intersect_point(query, max_results)

	var items: Array = []
	for res in results:
		var collider: Object = res.get("collider")
		var node := collider as Node
		items.append({
			"collider_id": res.collider_id,
			"collider_name": node.name if node != null else "",
			"collider_path": str(node.get_path()) if node != null else "",
			"shape": res.shape
		})

	return {
		"data": {
			"point": [pt_vec.x, pt_vec.y, pt_vec.z],
			"count": items.size(),
			"results": items
		}
	}


func shapecast_scaffold(params: Dictionary) -> Dictionary:
	var scene_root := EditorInterface.get_edited_scene_root()
	if scene_root == null:
		return ErrorCodes.make(ErrorCodes.EDITOR_NOT_READY, "No active scene open")

	var parent_path: String = params.get("parent_path", "")
	var parent: Node = scene_root
	if not parent_path.is_empty():
		parent = scene_root.get_node_or_null(NodePath(parent_path))
		if parent == null:
			return ErrorCodes.make(ErrorCodes.NODE_NOT_FOUND, "Parent node not found at %s" % parent_path)

	var is_2d: bool = bool(params.get("is_2d", true))
	var sensor_name: String = params.get("sensor_name", "ShapeCastSensor")
	var target_pos = params.get("target_position", [0, 50] if is_2d else [0, -2, 0])
	var mask: int = int(params.get("collision_mask", 1))
	var shape_type: String = params.get("shape_type", "circle" if is_2d else "sphere").to_lower()

	var sensor_node: Node = null
	if is_2d:
		var sc2d := ShapeCast2D.new()
		sc2d.name = sensor_name
		sc2d.target_position = Vector2(float(target_pos[0]), float(target_pos[1])) if target_pos is Array and target_pos.size() >= 2 else Vector2(0, 50)
		sc2d.collision_mask = mask
		if shape_type == "rectangle" or shape_type == "box":
			var rect := RectangleShape2D.new()
			rect.size = Vector2(32, 32)
			sc2d.shape = rect
		else:
			var circle := CircleShape2D.new()
			circle.radius = 16.0
			sc2d.shape = circle
		sensor_node = sc2d
	else:
		var sc3d := ShapeCast3D.new()
		sc3d.name = sensor_name
		sc3d.target_position = Vector3(float(target_pos[0]), float(target_pos[1]), float(target_pos[2])) if target_pos is Array and target_pos.size() >= 3 else Vector3(0, -2, 0)
		sc3d.collision_mask = mask
		if shape_type == "box":
			var box := BoxShape3D.new()
			box.size = Vector3(1, 1, 1)
			sc3d.shape = box
		elif shape_type == "cylinder":
			var cyl := CylinderShape3D.new()
			cyl.radius = 0.5
			cyl.height = 1.0
			sc3d.shape = cyl
		else:
			var sphere := SphereShape3D.new()
			sphere.radius = 0.5
			sc3d.shape = sphere
		sensor_node = sc3d

	if _undo_redo != null:
		_undo_redo.create_action("Scaffold ShapeCast Sensor " + sensor_name)
		_undo_redo.add_do_method(parent, "add_child", sensor_node)
		_undo_redo.add_do_property(sensor_node, "owner", scene_root)
		_undo_redo.add_undo_method(parent, "remove_child", sensor_node)
		_undo_redo.commit_action()
	else:
		parent.add_child(sensor_node)
		sensor_node.owner = scene_root

	return {
		"data": {
			"node_name": str(sensor_node.name),
			"node_path": str(sensor_node.get_path()),
			"is_2d": is_2d,
			"shape_type": shape_type,
			"target_position": target_pos,
			"collision_mask": mask
		}
	}


func set_layer_names(params: Dictionary) -> Dictionary:
	var layer_type: String = params.get("layer_type", "2d_physics").to_lower()
	var prefix := ""
	match layer_type:
		"2d_physics":
			prefix = "layer_names/2d_physics/layer_"
		"3d_physics":
			prefix = "layer_names/3d_physics/layer_"
		"2d_render":
			prefix = "layer_names/2d_render/layer_"
		"3d_render":
			prefix = "layer_names/3d_render/layer_"
		_:
			return ErrorCodes.make(ErrorCodes.VALUE_OUT_OF_RANGE,
				"Unknown layer_type '%s'. Valid: 2d_physics, 3d_physics, 2d_render, 3d_render" % layer_type)

	var layers: Dictionary = params.get("layers", {})
	var applied: Dictionary = {}
	for raw_idx in layers.keys():
		var idx := int(raw_idx)
		if idx >= 1 and idx <= 32:
			var key := prefix + str(idx)
			var val := str(layers[raw_idx])
			ProjectSettings.set_setting(key, val)
			applied[str(idx)] = val

	var err := ProjectSettings.save()
	if err != OK:
		return ErrorCodes.make(ErrorCodes.INTERNAL_ERROR, "Failed to save ProjectSettings (error %d)" % err)

	return {
		"data": {
			"layer_type": layer_type,
			"applied_layers": applied,
			"saved": true
		}
	}


func get_layer_names(params: Dictionary = {}) -> Dictionary:
	var layer_type: String = params.get("layer_type", "all").to_lower()
	var types := ["2d_physics", "3d_physics", "2d_render", "3d_render"]
	if layer_type != "all" and types.has(layer_type):
		types = [layer_type]

	var result: Dictionary = {}
	for t in types:
		result[t] = {}
		var prefix := "layer_names/%s/layer_" % t
		for i in range(1, 33):
			var key := prefix + str(i)
			if ProjectSettings.has_setting(key):
				var val = ProjectSettings.get_setting(key)
				if val != null and not str(val).is_empty():
					result[t][str(i)] = str(val)

	return {
		"data": result
	}
