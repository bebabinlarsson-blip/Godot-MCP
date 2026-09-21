@tool
extends "res://addons/godot_ai/handlers/command_handler.gd"

const ErrorCodes := preload("res://addons/godot_ai/utils/error_codes.gd")

## Handles scene tree reading and node search.

var _connection: McpConnection
var _undo_redo: EditorUndoRedoManager
var _save_scene_callable: Callable = Callable()
var _save_scene_as_callable: Callable = Callable()


func _init(connection: McpConnection = null, undo_redo: EditorUndoRedoManager = null) -> void:
	_connection = connection
	_undo_redo = undo_redo


func _get_undo_redo() -> EditorUndoRedoManager:
	if _undo_redo != null:
		return _undo_redo
	return EditorInterface.get_editor_undo_redo()


func get_scene_tree(params: Dictionary) -> Dictionary:
	var max_depth: int = params.get("depth", 10)
	var offset: int = maxi(0, int(params.get("offset", 0)))
	# limit <= 0 means "no limit" (the hierarchy resource reads the whole tree);
	# the scene_get_hierarchy tool passes an explicit positive limit. Paginating
	# here — rather than walking + serializing the full tree and slicing on the
	# Python side — means only the requested window builds node dicts and clean
	# scene paths, and only the window crosses the WebSocket.
	var limit: int = int(params.get("limit", 0))
	var scene_root := EditorInterface.get_edited_scene_root()
	if scene_root == null:
		return {"data": {
			"nodes": [],
			"total_count": 0,
			"offset": offset,
			"limit": limit,
			"has_more": false,
			"message": "No scene open",
		}}

	var nodes: Array[Dictionary] = []
	# index_ref[0] is the running DFS index shared across the recursion (Arrays
	# pass by reference in GDScript). The walk still visits every node to get an
	# accurate total_count, but only materializes those inside the window.
	var index_ref: Array[int] = [0]
	# _walk_tree self-seeds the root's path for full reads; pass "" explicitly.
	_walk_tree(scene_root, nodes, 0, max_depth, scene_root, offset, limit, index_ref, "")
	var total: int = index_ref[0]
	return {"data": {
		"nodes": nodes,
		"total_count": total,
		"offset": offset,
		"limit": limit,
		"has_more": limit > 0 and offset + limit < total,
	}}


func get_open_scenes(_params: Dictionary) -> Dictionary:
	var scene_paths := EditorInterface.get_open_scenes()
	var scene_root := EditorInterface.get_edited_scene_root()
	var current := scene_root.scene_file_path if scene_root else ""
	return {
		"data": {
			"scenes": scene_paths,
			"current_scene": current,
			"count": scene_paths.size(),
		}
	}


func find_nodes(params: Dictionary) -> Dictionary:
	var name_filter: String = params.get("name", "")
	var type_filter: String = params.get("type", "")
	var group_filter: String = params.get("group", "")

	if name_filter.is_empty() and type_filter.is_empty() and group_filter.is_empty():
		return ErrorCodes.make(ErrorCodes.MISSING_REQUIRED_PARAM, "At least one filter (name, type, group) is required")

	var _scene_check := McpNodeValidator.require_scene_or_error()
	if _scene_check.has("error"):
		return _scene_check
	var scene_root: Node = _scene_check.scene_root

	var results: Array[Dictionary] = []
	_find_recursive(scene_root, scene_root, name_filter, type_filter, group_filter, results)
	return {"data": {"nodes": results, "count": results.size()}}


func _find_recursive(node: Node, scene_root: Node, name_filter: String, type_filter: String, group_filter: String, out: Array[Dictionary]) -> void:
	var matches := true

	if not name_filter.is_empty():
		if node.name.to_lower().find(name_filter.to_lower()) == -1:
			matches = false

	if matches and not type_filter.is_empty():
		if node.get_class() != type_filter:
			matches = false

	if matches and not group_filter.is_empty():
		if not node.is_in_group(group_filter):
			matches = false

	if matches:
		out.append({
			"name": node.name,
			"type": node.get_class(),
			"path": McpScenePath.from_node(node, scene_root),
		})

	for child in node.get_children():
		_find_recursive(child, scene_root, name_filter, type_filter, group_filter, out)


## Create a new scene with the given root node type, save to disk, and open it.
func create_scene(params: Dictionary) -> Dictionary:
	var root_type: String = params.get("root_type", "Node3D")
	var path: String = params.get("path", "")

	if path.is_empty():
		return ErrorCodes.make(ErrorCodes.MISSING_REQUIRED_PARAM, "Missing required param: path")

	var path_err = McpPathValidator.path_error(path, "path", true)
	if path_err != null:
		return path_err

	if not path.ends_with(".tscn") and not path.ends_with(".scn"):
		path += ".tscn"

	if not ClassDB.class_exists(root_type):
		return ErrorCodes.make(ErrorCodes.VALUE_OUT_OF_RANGE, "Unknown node type: %s" % root_type)
	if not ClassDB.is_parent_class(root_type, "Node"):
		return ErrorCodes.make(ErrorCodes.WRONG_TYPE, "%s is not a Node type" % root_type)

	# Ensure parent directory exists
	var dir_path := path.get_base_dir()
	if not DirAccess.dir_exists_absolute(dir_path):
		var err := DirAccess.make_dir_recursive_absolute(dir_path)
		if err != OK:
			return ErrorCodes.make(ErrorCodes.INTERNAL_ERROR, "Failed to create directory: %s" % dir_path)

	var root: Node = ClassDB.instantiate(root_type)
	if root == null:
		return ErrorCodes.make(ErrorCodes.INTERNAL_ERROR, "Failed to instantiate %s" % root_type)

	var root_name: String = params.get("root_name", "")
	if root_name.is_empty():
		root_name = path.get_file().get_basename()
	root.name = root_name

	if _connection:
		_connection.pause_processing = true
	var err := _pack_and_save_with_uid(root, path)
	if err == OK:
		EditorInterface.open_scene_from_path(path)
	if _connection:
		_connection.pause_processing = false

	if err != OK:
		return ErrorCodes.make(ErrorCodes.INTERNAL_ERROR, "Failed to save scene: %s" % error_string(err))

	return {
		"data": {
			"path": path,
			"root_type": root_type,
			"root_name": root_name,
			"undoable": false,
			"reason": "Scene creation involves file system operations",
		}
	}


## Pack `root` and save it to `path`, embedding a fresh uid or preserving the
## one `path` already had — the exact save sequence `create_scene` runs,
## minus the `pause_processing` guard (the caller owns that, since it also
## needs to bracket `open_scene_from_path`) and minus opening the scene
## (switching the editor's active scene isn't safe inside the shared test
## runner, so tests call this directly instead of going through
## `create_scene` end-to-end). Frees `root`. Returns `OK`, or the first
## `Error` encountered.
func _pack_and_save_with_uid(root: Node, path: String) -> Error:
	var packed := PackedScene.new()
	packed.pack(root)
	root.free()

	# Captured BEFORE the save below overwrites the file — see
	# McpResourceIO.ensure_uid's doc comment.
	var prior_uid := ResourceLoader.get_resource_uid(path) if FileAccess.file_exists(path) else ResourceUID.INVALID_ID

	var err := ResourceSaver.save(packed, path)
	if err == OK:
		err = McpResourceIO.ensure_uid(path, prior_uid)
	return err


## How long open_scene waits for the editor to actually switch to the
## requested scene before replying switched=false. Tab switches normally land
## within a few frames; keep this under the dispatcher's 4500 ms deferred
## default so the coroutine always answers before DEFERRED_TIMEOUT fires.
const _OPEN_SETTLE_MAX_MSEC := 3000


## Open an existing scene by file path.
func open_scene(params: Dictionary) -> Dictionary:
	var path: String = params.get("path", "")
	var force_reload: bool = params.get("force_reload", false)
	if path.is_empty():
		return ErrorCodes.make(ErrorCodes.MISSING_REQUIRED_PARAM, "Missing required param: path")

	var path_err = McpPathValidator.loadable_error(path, "path")
	if path_err != null:
		return path_err

	if not ResourceLoader.exists(path):
		return ErrorCodes.make(ErrorCodes.RESOURCE_NOT_FOUND, "Scene not found: %s" % path)

	var scene_root := EditorInterface.get_edited_scene_root()
	var current_path := scene_root.scene_file_path if scene_root else ""
	## Instance id of the root at call time. A completed open OR reload always
	## replaces the edited-scene root with a NEW instance, so this is the
	## reliable completion signal — unlike scene_file_path, which is unchanged
	## across a force_reload of the already-open scene (#633 review).
	var prev_root_id := scene_root.get_instance_id() if scene_root else 0
	var payload := {
		"path": path,
		"force_reload": force_reload,
		"reloaded_from_disk": false,
		"previous_scene_path": current_path,
		"undoable": false,
		"reason": "Scene navigation cannot be undone via editor undo",
	}

	if current_path == path and not force_reload:
		## Already the edited scene — nothing switches, reply immediately.
		payload["switched"] = true
		payload["settle"] = "already_current"
		return {"data": payload}

	if force_reload and current_path == path:
		EditorInterface.reload_scene_from_path(path)
		payload["reloaded_from_disk"] = true
	else:
		EditorInterface.open_scene_from_path(path)

	## The tab switch completes asynchronously; replying now lets an immediate
	## follow-up write land on the PREVIOUS scene (#633 — a scene_save issued
	## right after open_scene saved the old scene). Defer the reply until the
	## edited scene actually is `path` AND its root is a fresh instance, so
	## success means "the editor is now editing the (re)loaded scene".
	var request_id: String = params.get("_request_id", "")
	if _connection != null and not request_id.is_empty():
		_finish_open_scene_deferred(_connection, request_id, path, prev_root_id, payload)
		return McpDispatcher.DEFERRED_RESPONSE

	## Synchronous fallback (batch_execute and unit-test contexts can't await):
	## preserve the old reply-immediately behavior, flagged as not waited on.
	payload["switched"] = false
	payload["settle"] = "not_waited"
	return {"data": payload}


## `static` is load-bearing (same reason as FilesystemHandler's deferred scan
## finish): the coroutine must outlive this RefCounted handler, which can be
## freed mid-await by an editor_reload_plugin. Parameterise everything;
## reference no instance state.
static func _finish_open_scene_deferred(
	connection: McpConnection,
	request_id: String,
	path: String,
	prev_root_id: int,
	payload: Dictionary,
) -> void:
	var work := ScriptWork.begin("open_scene")
	await _settle_open_scene(connection, request_id, path, prev_root_id, payload)
	ScriptWork.finish(work)


static func _settle_open_scene(
	connection: McpConnection, request_id: String, path: String,
	prev_root_id: int, payload: Dictionary,
) -> void:
	if not is_instance_valid(connection):
		return
	var tree := connection.get_tree()
	if tree == null:
		return
	# Hand back a frame so _dispatch() registers this request as deferred
	# before the coroutine can push a reply.
	await tree.process_frame
	var deadline_ms := Time.get_ticks_msec() + _OPEN_SETTLE_MAX_MSEC
	while Time.get_ticks_msec() < deadline_ms:
		var root := EditorInterface.get_edited_scene_root()
		# Require BOTH the target path AND a fresh root instance: a
		# force_reload keeps scene_file_path == path across the reload, so the
		# instance swap is what proves the (re)load actually completed rather
		# than the coroutine settling on the stale pre-reload root.
		if root != null and root.scene_file_path == path and root.get_instance_id() != prev_root_id:
			if not is_instance_valid(connection):
				return
			payload["switched"] = true
			payload["settle"] = "settled"
			connection.send_deferred_response(request_id, {"data": payload})
			return
		await tree.process_frame
	if not is_instance_valid(connection):
		return
	payload["switched"] = false
	payload["settle"] = "timeout"
	connection.send_deferred_response(request_id, {"data": payload})


## Save the currently edited scene.
## Pauses WebSocket processing during save to prevent re-entrant _process()
## calls during EditorNode::_save_scene_with_preview's thumbnail render.
func save_scene(_params: Dictionary) -> Dictionary:
	var _scene_check := McpNodeValidator.require_scene_or_error()
	if _scene_check.has("error"):
		return _scene_check
	var scene_root: Node = _scene_check.scene_root

	var path := scene_root.scene_file_path
	if path.is_empty():
		return ErrorCodes.make(
			ErrorCodes.INVALID_PARAMS,
			"Current scene has never been saved; call scene_manage(op='save_as') with a res://... path ending in .tscn or .scn."
		)

	if _connection:
		_connection.pause_processing = true
	var err := _save_current_scene()
	if _connection:
		_connection.pause_processing = false

	if err != OK:
		return ErrorCodes.make(ErrorCodes.INTERNAL_ERROR, "Failed to save scene: %s" % error_string(err))

	return {
		"data": {
			"path": path,
			"undoable": false,
			"reason": "File save cannot be undone via editor undo",
		}
	}


## Save the currently edited scene to a new file path.
func save_scene_as(params: Dictionary) -> Dictionary:
	var path: String = params.get("path", "")
	if path.is_empty():
		return ErrorCodes.make(ErrorCodes.MISSING_REQUIRED_PARAM, "Missing required param: path")

	var path_err = McpPathValidator.path_error(path, "path", true)
	if path_err != null:
		return path_err

	if not path.ends_with(".tscn") and not path.ends_with(".scn"):
		path += ".tscn"

	var _scene_check := McpNodeValidator.require_scene_or_error()
	if _scene_check.has("error"):
		return _scene_check
	var scene_root: Node = _scene_check.scene_root

	# Ensure parent directory exists
	var dir_path := path.get_base_dir()
	if not DirAccess.dir_exists_absolute(dir_path):
		var err := DirAccess.make_dir_recursive_absolute(dir_path)
		if err != OK:
			return ErrorCodes.make(ErrorCodes.INTERNAL_ERROR, "Failed to create directory: %s" % dir_path)

	if _connection:
		_connection.pause_processing = true
	_save_current_scene_as(path)
	if _connection:
		_connection.pause_processing = false

	return {
		"data": {
			"path": path,
			"undoable": false,
			"reason": "File save cannot be undone via editor undo",
		}
	}


func _save_current_scene() -> int:
	if _save_scene_callable.is_valid():
		return int(_save_scene_callable.call())
	return EditorInterface.save_scene()


func _save_current_scene_as(path: String) -> void:
	if _save_scene_as_callable.is_valid():
		_save_scene_as_callable.call(path)
		return
	EditorInterface.save_scene_as(path)


func _walk_tree(node: Node, out: Array[Dictionary], depth: int, max_depth: int, scene_root: Node, offset: int, limit: int, index_ref: Array[int], node_path: String) -> void:
	if depth > max_depth:
		return
	var idx: int = index_ref[0]
	index_ref[0] = idx + 1
	# Materialize only nodes inside the [offset, offset+limit) window. Outside
	# it we still recurse (to count total_count) but skip the per-node dict.
	#
	# Path build strategy depends on the read shape (identical output either way):
	#   * A whole-tree read (offset == 0 and limit <= 0 — the resource-style read
	#     backing godot://scene/hierarchy) threads the parent's clean path down the
	#     DFS: each node's path is one O(1) concat reusing the descent, instead of
	#     McpScenePath.from_node's two native walks back up (is_ancestor_of +
	#     get_path_to). Benchmarked ~1.8x faster on a ~1.5k-node tree, up to ~5x on
	#     deep chains.
	#   * Any windowed read (limit > 0, or an offset > 0 skip) keeps from_node for
	#     just the emitted nodes: threading would concatenate a path for every node
	#     visited for total_count, which benchmarks ~20% slower for a small window.
	#
	# `node_path` is self-seeded at the scene root below, so a caller cannot leave
	# a full read unseeded (it has no default — pass "" for windowed reads).
	var incremental := limit <= 0 and offset == 0
	if incremental and node == scene_root:
		node_path = "/" + String(scene_root.name)
	var in_window := idx >= offset and (limit <= 0 or idx < offset + limit)
	if in_window:
		out.append({
			"name": node.name,
			"type": node.get_class(),
			"path": node_path if incremental else McpScenePath.from_node(node, scene_root),
			"children_count": node.get_child_count(),
		})
	for child in node.get_children():
		var child_path := (node_path + "/" + String(child.name)) if incremental else ""
		_walk_tree(child, out, depth + 1, max_depth, scene_root, offset, limit, index_ref, child_path)


func _apply_transform_properties(node: Node, inst_data: Dictionary) -> void:
	# Position
	if inst_data.has("position"):
		var p_val = inst_data.get("position")
		if p_val is Dictionary:
			if node is Node2D:
				node.position = Vector2(float(p_val.get("x", 0.0)), float(p_val.get("y", 0.0)))
			elif node is Node3D:
				node.position = Vector3(float(p_val.get("x", 0.0)), float(p_val.get("y", 0.0)), float(p_val.get("z", 0.0)))
		elif p_val is Array:
			if node is Node2D and p_val.size() >= 2:
				node.position = Vector2(float(p_val[0]), float(p_val[1]))
			elif node is Node3D and p_val.size() >= 3:
				node.position = Vector3(float(p_val[0]), float(p_val[1]), float(p_val[2]))
		elif p_val is Vector2 or p_val is Vector3:
			node.set("position", p_val)

	# Rotation
	if inst_data.has("rotation_degrees"):
		var rd = inst_data.get("rotation_degrees")
		if node is Node2D:
			node.rotation_degrees = float(rd)
		elif node is Node3D:
			if rd is Dictionary:
				node.rotation_degrees = Vector3(float(rd.get("x", 0.0)), float(rd.get("y", 0.0)), float(rd.get("z", 0.0)))
			elif rd is Vector3:
				node.rotation_degrees = rd
			elif rd is float or rd is int:
				node.rotation_degrees = Vector3(0.0, float(rd), 0.0)
	elif inst_data.has("rotation"):
		var rot = inst_data.get("rotation")
		if node is Node2D:
			node.rotation = float(rot)
		elif node is Node3D:
			if rot is Dictionary:
				node.rotation = Vector3(float(rot.get("x", 0.0)), float(rot.get("y", 0.0)), float(rot.get("z", 0.0)))
			elif rot is Vector3:
				node.rotation = rot
			elif rot is float or rot is int:
				node.rotation = Vector3(0.0, float(rot), 0.0)

	# Scale
	if inst_data.has("scale"):
		var s_val = inst_data.get("scale")
		if s_val is Dictionary:
			if node is Node2D:
				node.scale = Vector2(float(s_val.get("x", 1.0)), float(s_val.get("y", 1.0)))
			elif node is Node3D:
				node.scale = Vector3(float(s_val.get("x", 1.0)), float(s_val.get("y", 1.0)), float(s_val.get("z", 1.0)))
		elif s_val is Array:
			if node is Node2D and s_val.size() >= 2:
				node.scale = Vector2(float(s_val[0]), float(s_val[1]))
			elif node is Node3D and s_val.size() >= 3:
				node.scale = Vector3(float(s_val[0]), float(s_val[1]), float(s_val[2]))
		elif s_val is float or s_val is int:
			var s_num := float(s_val)
			if node is Node2D:
				node.scale = Vector2(s_num, s_num)
			elif node is Node3D:
				node.scale = Vector3(s_num, s_num, s_num)
		elif s_val is Vector2 or s_val is Vector3:
			node.set("scale", s_val)

	# Extra properties
	if inst_data.has("properties") and inst_data.get("properties") is Dictionary:
		var props: Dictionary = inst_data.get("properties")
		for k in props.keys():
			node.set(str(k), props[k])


## Batch-instantiate multiple PackedScenes into the active scene under parent_path in a single UndoRedo action.
## params: {
##   parent_path: String (optional, defaults to scene root or opened scene),
##   instances: Array [ { scene_path: String, name?: String, position?: ..., rotation?: ..., scale?: ..., properties?: ... } ]
## }
func instantiate_batch(params: Dictionary) -> Dictionary:
	var raw_instances = params.get("instances", [])
	if not raw_instances is Array or raw_instances.is_empty():
		return ErrorCodes.make(ErrorCodes.MISSING_REQUIRED_PARAM, "Parameter 'instances' must be a non-empty array")

	var _scene_check := McpNodeValidator.require_scene_or_error()
	if _scene_check.has("error"): return _scene_check
	var scene_root: Node = _scene_check.scene_root

	var parent_path: String = params.get("parent_path", "")
	var parent: Node = scene_root
	if not parent_path.is_empty():
		if parent_path.ends_with(".tscn"):
			if scene_root.scene_file_path != parent_path:
				EditorInterface.open_scene_from_path(parent_path)
				scene_root = EditorInterface.get_edited_scene_root()
			parent = scene_root
		else:
			parent = McpScenePath.resolve(parent_path, scene_root)
			if parent == null:
				return ErrorCodes.make(ErrorCodes.NODE_NOT_FOUND, McpScenePath.format_parent_error(parent_path, scene_root))

	var undo_mgr := _get_undo_redo()
	if undo_mgr != null:
		undo_mgr.create_action("MCP: Instantiate batch (%d instances)" % raw_instances.size())

	var scene_cache: Dictionary = {}
	var created_nodes: Array = []

	for item in raw_instances:
		if not item is Dictionary:
			continue
		var scene_path: String = item.get("scene_path", "")
		if scene_path.is_empty() or not ResourceLoader.exists(scene_path):
			continue

		var packed: PackedScene = null
		if scene_cache.has(scene_path):
			packed = scene_cache[scene_path]
		else:
			var res = load(scene_path)
			if res is PackedScene:
				packed = res
				scene_cache[scene_path] = packed

		if packed == null:
			continue

		var inst := packed.instantiate(PackedScene.GEN_EDIT_STATE_INSTANCE)
		if inst == null:
			continue

		var inst_name: String = item.get("name", "")
		if not inst_name.is_empty():
			inst.name = inst_name

		_apply_transform_properties(inst, item)

		if undo_mgr != null:
			undo_mgr.add_do_method(parent, "add_child", inst, true)
			undo_mgr.add_do_method(inst, "set_owner", scene_root)
			undo_mgr.add_do_reference(inst)
			undo_mgr.add_undo_method(parent, "remove_child", inst)
		else:
			parent.add_child(inst, true)
			inst.owner = scene_root

		created_nodes.append({
			"name": String(inst.name),
			"path": McpScenePath.from_node(inst, scene_root),
			"scene_path": scene_path
		})

	if undo_mgr != null:
		undo_mgr.commit_action()

	return {"data": {
		"count": created_nodes.size(),
		"parent_path": McpScenePath.from_node(parent, scene_root),
		"instances": created_nodes,
		"undoable": undo_mgr != null
	}}


func diagnose_scene(params: Dictionary) -> Dictionary:
	var scene_check := McpNodeValidator.require_scene_or_error()
	if scene_check.has("error"):
		return scene_check
	var scene_root: Node = scene_check.scene_root

	var root_path: String = params.get("root_path", "")
	var target_root: Node = scene_root
	if not root_path.is_empty():
		var resolved := McpNodeValidator.resolve_or_error(root_path, "root_path")
		if resolved.has("error"):
			return resolved
		target_root = resolved.node

	var errors: Array[Dictionary] = []
	var warnings: Array[Dictionary] = []
	var info: Array[Dictionary] = []
	var total_nodes: Array[int] = [0]
	var camera_count: Array[int] = [0]
	var current_cameras: Array[String] = []

	_diagnose_node(target_root, scene_root, errors, warnings, info, total_nodes, camera_count, current_cameras)

	if camera_count[0] == 0:
		info.append({
			"rule": "no_camera",
			"path": McpScenePath.from_node(target_root, scene_root),
			"message": "No Camera2D or Camera3D found in scene. Scene will render with default viewport view.",
		})
	elif current_cameras.size() > 1:
		warnings.append({
			"rule": "multiple_current_cameras",
			"path": current_cameras[0],
			"message": "Multiple cameras have current=true (%s). Only one can be active at a time." % ", ".join(current_cameras),
			"fix_suggestion": "Set current=false on secondary cameras.",
		})

	return {
		"scene_file": scene_root.scene_file_path if scene_root else "",
		"root_node": McpScenePath.from_node(target_root, scene_root),
		"total_nodes_checked": total_nodes[0],
		"issue_count": errors.size() + warnings.size(),
		"errors": errors,
		"warnings": warnings,
		"info": info,
		"status": "pass" if errors.is_empty() and warnings.is_empty() else ("warning" if errors.is_empty() else "error"),
	}


static func _diagnose_node(node: Node, scene_root: Node, errors: Array[Dictionary], warnings: Array[Dictionary], info: Array[Dictionary], total_nodes: Array[int], camera_count: Array[int], current_cameras: Array[String]) -> void:
	total_nodes[0] += 1
	var path := McpScenePath.from_node(node, scene_root)

	if node is CollisionObject2D:
		var has_shape := false
		for child in node.get_children():
			if child is CollisionShape2D or child is CollisionPolygon2D:
				has_shape = true
				break
		if not has_shape:
			warnings.append({
				"path": path,
				"node_type": node.get_class(),
				"rule": "missing_collision_shape",
				"message": "CollisionObject2D has no CollisionShape2D or CollisionPolygon2D child and cannot collide.",
				"fix_suggestion": "Add a CollisionShape2D child with a valid Shape2D.",
			})
	elif node is CollisionObject3D:
		var has_shape := false
		for child in node.get_children():
			if child is CollisionShape3D or child is CollisionPolygon3D:
				has_shape = true
				break
		if not has_shape:
			warnings.append({
				"path": path,
				"node_type": node.get_class(),
				"rule": "missing_collision_shape",
				"message": "CollisionObject3D has no CollisionShape3D or CollisionPolygon3D child and cannot collide.",
				"fix_suggestion": "Add a CollisionShape3D child with a valid Shape3D.",
			})

	if node is CollisionShape2D:
		if (node as CollisionShape2D).shape == null:
			errors.append({
				"path": path,
				"node_type": "CollisionShape2D",
				"rule": "empty_shape_resource",
				"message": "CollisionShape2D has no shape resource assigned.",
				"fix_suggestion": "Assign a RectangleShape2D, CircleShape2D, or CapsuleShape2D.",
			})
		var s: Vector2 = (node as CollisionShape2D).scale
		if absf(s.x - s.y) > 0.001:
			warnings.append({
				"path": path,
				"node_type": "CollisionShape2D",
				"rule": "non_uniform_scale",
				"message": "CollisionShape2D has non-uniform scale (%s) which causes physics calculation errors." % str(s),
				"fix_suggestion": "Reset CollisionShape2D scale to (1, 1) and resize the shape resource bounds instead.",
			})
	elif node is CollisionShape3D:
		if (node as CollisionShape3D).shape == null:
			errors.append({
				"path": path,
				"node_type": "CollisionShape3D",
				"rule": "empty_shape_resource",
				"message": "CollisionShape3D has no shape resource assigned.",
				"fix_suggestion": "Assign a BoxShape3D, SphereShape3D, or CapsuleShape3D.",
			})

	if node is Sprite2D:
		if (node as Sprite2D).texture == null:
			warnings.append({
				"path": path,
				"node_type": "Sprite2D",
				"rule": "missing_texture",
				"message": "Sprite2D has no texture assigned.",
				"fix_suggestion": "Assign a Texture2D or replace with ColorRect / Polygon2D.",
			})
	elif node is AnimatedSprite2D:
		if (node as AnimatedSprite2D).sprite_frames == null:
			warnings.append({
				"path": path,
				"node_type": "AnimatedSprite2D",
				"rule": "missing_sprite_frames",
				"message": "AnimatedSprite2D has no SpriteFrames resource assigned.",
				"fix_suggestion": "Assign a SpriteFrames resource with animation frames.",
			})
	elif node is MeshInstance3D:
		if (node as MeshInstance3D).mesh == null:
			warnings.append({
				"path": path,
				"node_type": "MeshInstance3D",
				"rule": "missing_mesh",
				"message": "MeshInstance3D has no Mesh assigned.",
				"fix_suggestion": "Assign a primitive mesh (BoxMesh, SphereMesh) or load a 3D model.",
			})

	if node is Camera2D or node is Camera3D:
		camera_count[0] += 1
		if node.has_method("is_current") and node.call("is_current"):
			current_cameras.append(path)

	if node is Control and not (node is Window):
		var parent = node.get_parent()
		if parent != null and not (parent is Control) and not (parent is CanvasLayer) and not (parent is Window):
			info.append({
				"path": path,
				"node_type": node.get_class(),
				"rule": "control_outside_canvas",
				"message": "Control node '%s' is placed directly under %s (not a Control or CanvasLayer). For UI screens, placing under CanvasLayer is recommended." % [node.name, parent.get_class()],
			})

	for child in node.get_children():
		_diagnose_node(child, scene_root, errors, warnings, info, total_nodes, camera_count, current_cameras)

