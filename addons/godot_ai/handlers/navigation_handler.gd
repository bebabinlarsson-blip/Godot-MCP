@tool
extends "res://addons/godot_ai/handlers/command_handler.gd"

const ErrorCodes := preload("res://addons/godot_ai/utils/error_codes.gd")

var _undo_redo: EditorUndoRedoManager
var _connection


func _init(undo_redo: EditorUndoRedoManager, connection = null) -> void:
	_undo_redo = undo_redo
	_connection = connection


func setup_region_2d(params: Dictionary) -> Dictionary:
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

	var region_name: String = params.get("name", "NavigationRegion2D")
	var cell_size: float = float(params.get("cell_size", 1.0))
	var agent_radius: float = float(params.get("agent_radius", 10.0))
	var parsed_geom_str: String = str(params.get("parsed_geometry_type", "mesh_instances_and_colliders")).to_lower()

	var region := NavigationRegion2D.new()
	region.name = region_name

	var nav_poly := NavigationPolygon.new()
	nav_poly.cell_size = cell_size
	nav_poly.agent_radius = agent_radius

	match parsed_geom_str:
		"static_colliders":
			nav_poly.parsed_geometry_type = NavigationPolygon.PARSED_GEOMETRY_STATIC_COLLIDERS
		"both":
			nav_poly.parsed_geometry_type = NavigationPolygon.PARSED_GEOMETRY_BOTH
		_:
			nav_poly.parsed_geometry_type = NavigationPolygon.PARSED_GEOMETRY_BOTH

	var points_param = params.get("polygon", null)
	var outline := PackedVector2Array()
	if points_param is Array and not points_param.is_empty():
		for pt in points_param:
			if pt is Array and pt.size() >= 2:
				outline.append(Vector2(float(pt[0]), float(pt[1])))
			elif pt is Vector2:
				outline.append(pt)
	else:
		outline.append(Vector2(-500, -500))
		outline.append(Vector2(500, -500))
		outline.append(Vector2(500, 500))
		outline.append(Vector2(-500, 500))

	if outline.size() >= 3:
		nav_poly.add_outline(outline)
		nav_poly.make_polygons_from_outlines()

	region.navigation_polygon = nav_poly

	_undo_redo.create_action("Setup NavigationRegion2D: %s" % region_name)
	_undo_redo.add_do_method(parent, "add_child", region)
	_undo_redo.add_do_reference(region)
	_undo_redo.add_undo_method(parent, "remove_child", region)
	_undo_redo.commit_action()

	region.owner = scene_root

	return {
		"region_path": McpScenePath.from_node(region, scene_root),
		"name": region.name,
		"cell_size": cell_size,
		"agent_radius": agent_radius,
		"polygon_vertices": outline.size(),
		"parsed_geometry_type": parsed_geom_str,
	}


func attach_agent_2d(params: Dictionary) -> Dictionary:
	var node_path: String = params.get("node_path", "")
	if node_path.is_empty():
		return ErrorCodes.make(ErrorCodes.MISSING_REQUIRED_PARAM, "node_path is required")

	var scene_check := McpNodeValidator.require_scene_or_error()
	if scene_check.has("error"):
		return scene_check
	var scene_root: Node = scene_check.scene_root

	var resolved := McpNodeValidator.resolve_or_error(node_path, "node_path")
	if resolved.has("error"):
		return resolved
	var target_node: Node = resolved.node

	var agent_name: String = params.get("agent_name", "NavigationAgent2D")
	var radius: float = float(params.get("radius", 16.0))
	var max_speed: float = float(params.get("max_speed", 150.0))
	var path_desired_distance: float = float(params.get("path_desired_distance", 20.0))
	var target_desired_distance: float = float(params.get("target_desired_distance", 20.0))
	var avoidance_enabled: bool = bool(params.get("avoidance_enabled", true))

	var existing = target_node.get_node_or_null(NodePath(agent_name))
	if existing != null and existing is NavigationAgent2D:
		var agent: NavigationAgent2D = existing
		agent.radius = radius
		agent.max_speed = max_speed
		agent.path_desired_distance = path_desired_distance
		agent.target_desired_distance = target_desired_distance
		agent.avoidance_enabled = avoidance_enabled
		return {
			"agent_path": McpScenePath.from_node(agent, scene_root),
			"target_node": McpScenePath.from_node(target_node, scene_root),
			"radius": radius,
			"max_speed": max_speed,
			"created": false,
		}

	var agent := NavigationAgent2D.new()
	agent.name = agent_name
	agent.radius = radius
	agent.max_speed = max_speed
	agent.path_desired_distance = path_desired_distance
	agent.target_desired_distance = target_desired_distance
	agent.avoidance_enabled = avoidance_enabled

	_undo_redo.create_action("Attach NavigationAgent2D to %s" % target_node.name)
	_undo_redo.add_do_method(target_node, "add_child", agent)
	_undo_redo.add_do_reference(agent)
	_undo_redo.add_undo_method(target_node, "remove_child", agent)
	_undo_redo.commit_action()

	agent.owner = scene_root

	return {
		"agent_path": McpScenePath.from_node(agent, scene_root),
		"target_node": McpScenePath.from_node(target_node, scene_root),
		"radius": radius,
		"max_speed": max_speed,
		"path_desired_distance": path_desired_distance,
		"target_desired_distance": target_desired_distance,
		"avoidance_enabled": avoidance_enabled,
		"created": true,
	}


func bake_2d(params: Dictionary) -> Dictionary:
	var region_path: String = params.get("region_path", "")
	if region_path.is_empty():
		return ErrorCodes.make(ErrorCodes.MISSING_REQUIRED_PARAM, "region_path is required")

	var scene_check := McpNodeValidator.require_scene_or_error()
	if scene_check.has("error"):
		return scene_check
	var scene_root: Node = scene_check.scene_root

	var resolved := McpNodeValidator.resolve_or_error(region_path, "region_path")
	if resolved.has("error"):
		return resolved
	var node: Node = resolved.node

	if not (node is NavigationRegion2D):
		return ErrorCodes.make(ErrorCodes.WRONG_TYPE, "Node '%s' is not a NavigationRegion2D" % region_path)

	var region: NavigationRegion2D = node
	var on_thread: bool = bool(params.get("on_thread", false))

	if region.has_method("bake_navigation_polygon"):
		region.call("bake_navigation_polygon", on_thread)

	return {
		"region_path": McpScenePath.from_node(region, scene_root),
		"baked": true,
	}


func setup_region_3d(params: Dictionary) -> Dictionary:
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

	var region_name: String = params.get("name", "NavigationRegion3D")
	var cell_size: float = float(params.get("cell_size", 0.25))
	var cell_height: float = float(params.get("cell_height", 0.25))
	var agent_radius: float = float(params.get("agent_radius", 0.5))
	var agent_height: float = float(params.get("agent_height", 1.8))

	var region := NavigationRegion3D.new()
	region.name = region_name

	var nav_mesh := NavigationMesh.new()
	nav_mesh.cell_size = cell_size
	nav_mesh.cell_height = cell_height
	nav_mesh.agent_radius = agent_radius
	nav_mesh.agent_height = agent_height
	region.navigation_mesh = nav_mesh

	_undo_redo.create_action("Setup NavigationRegion3D: %s" % region_name)
	_undo_redo.add_do_method(parent, "add_child", region)
	_undo_redo.add_do_reference(region)
	_undo_redo.add_undo_method(parent, "remove_child", region)
	_undo_redo.commit_action()

	region.owner = scene_root

	return {
		"region_path": McpScenePath.from_node(region, scene_root),
		"name": region.name,
		"cell_size": cell_size,
		"cell_height": cell_height,
		"agent_radius": agent_radius,
		"agent_height": agent_height,
	}


func attach_agent_3d(params: Dictionary) -> Dictionary:
	var node_path: String = params.get("node_path", "")
	if node_path.is_empty():
		return ErrorCodes.make(ErrorCodes.MISSING_REQUIRED_PARAM, "node_path is required")

	var scene_check := McpNodeValidator.require_scene_or_error()
	if scene_check.has("error"):
		return scene_check
	var scene_root: Node = scene_check.scene_root

	var resolved := McpNodeValidator.resolve_or_error(node_path, "node_path")
	if resolved.has("error"):
		return resolved
	var target_node: Node = resolved.node

	var agent_name: String = params.get("agent_name", "NavigationAgent3D")
	var radius: float = float(params.get("radius", 0.5))
	var height: float = float(params.get("height", 1.8))
	var max_speed: float = float(params.get("max_speed", 5.0))
	var path_desired_distance: float = float(params.get("path_desired_distance", 1.0))
	var target_desired_distance: float = float(params.get("target_desired_distance", 1.0))
	var avoidance_enabled: bool = bool(params.get("avoidance_enabled", true))

	var existing = target_node.get_node_or_null(NodePath(agent_name))
	if existing != null and existing is NavigationAgent3D:
		var agent: NavigationAgent3D = existing
		agent.radius = radius
		agent.height = height
		agent.max_speed = max_speed
		agent.path_desired_distance = path_desired_distance
		agent.target_desired_distance = target_desired_distance
		agent.avoidance_enabled = avoidance_enabled
		return {
			"agent_path": McpScenePath.from_node(agent, scene_root),
			"target_node": McpScenePath.from_node(target_node, scene_root),
			"radius": radius,
			"max_speed": max_speed,
			"created": false,
		}

	var agent := NavigationAgent3D.new()
	agent.name = agent_name
	agent.radius = radius
	agent.height = height
	agent.max_speed = max_speed
	agent.path_desired_distance = path_desired_distance
	agent.target_desired_distance = target_desired_distance
	agent.avoidance_enabled = avoidance_enabled

	_undo_redo.create_action("Attach NavigationAgent3D to %s" % target_node.name)
	_undo_redo.add_do_method(target_node, "add_child", agent)
	_undo_redo.add_do_reference(agent)
	_undo_redo.add_undo_method(target_node, "remove_child", agent)
	_undo_redo.commit_action()

	agent.owner = scene_root

	return {
		"agent_path": McpScenePath.from_node(agent, scene_root),
		"target_node": McpScenePath.from_node(target_node, scene_root),
		"radius": radius,
		"height": height,
		"max_speed": max_speed,
		"path_desired_distance": path_desired_distance,
		"target_desired_distance": target_desired_distance,
		"avoidance_enabled": avoidance_enabled,
		"created": true,
	}


func bake_3d(params: Dictionary) -> Dictionary:
	var region_path: String = params.get("region_path", "")
	if region_path.is_empty():
		return ErrorCodes.make(ErrorCodes.MISSING_REQUIRED_PARAM, "region_path is required")

	var scene_check := McpNodeValidator.require_scene_or_error()
	if scene_check.has("error"):
		return scene_check
	var scene_root: Node = scene_check.scene_root

	var resolved := McpNodeValidator.resolve_or_error(region_path, "region_path")
	if resolved.has("error"):
		return resolved
	var node: Node = resolved.node

	if not (node is NavigationRegion3D):
		return ErrorCodes.make(ErrorCodes.WRONG_TYPE, "Node '%s' is not a NavigationRegion3D" % region_path)

	var region: NavigationRegion3D = node
	var on_thread: bool = bool(params.get("on_thread", false))

	if region.has_method("bake_navigation_mesh"):
		region.call("bake_navigation_mesh", on_thread)

	return {
		"region_path": McpScenePath.from_node(region, scene_root),
		"baked": true,
	}
