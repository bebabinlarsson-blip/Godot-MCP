@tool
extends "res://addons/godot_ai/handlers/command_handler.gd"

const ErrorCodes := preload("res://addons/godot_ai/utils/error_codes.gd")

## Handles HTTPRequest scaffolding, in-engine REST calls, and file downloads.

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


func scaffold_http_request(params: Dictionary) -> Dictionary:
	var scene_root := _get_scene_root()
	if scene_root == null:
		return {"error": "No edited scene root available", "code": ErrorCodes.NODE_NOT_FOUND}

	var parent_path: String = params.get("parent_path", "")
	var parent: Node = _resolve_node(scene_root, parent_path)
	if parent == null:
		return {"error": "Parent node not found: %s" % parent_path, "code": ErrorCodes.NODE_NOT_FOUND}

	var req := HTTPRequest.new()
	req.name = params.get("name", "HTTPRequest")
	req.timeout = float(params.get("timeout", 30.0))

	parent.add_child(req)
	req.owner = scene_root

	return {
		"success": true,
		"request_path": str(req.get_path()),
		"timeout": req.timeout
	}


func send_request(params: Dictionary) -> Dictionary:
	var url: String = params.get("url", "")
	if url.is_empty():
		return ErrorCodes.make(ErrorCodes.INVALID_PARAMS, "url is required")
	var request_id: String = params.get("_request_id", "")
	if _connection == null or request_id.is_empty():
		return ErrorCodes.make(
			ErrorCodes.INVALID_PARAMS,
			"HTTP requests must be sent as a direct MCP tool call"
		)
	var timeout := float(params.get("timeout", 10.0))
	if not is_finite(timeout) or timeout <= 0.0:
		return ErrorCodes.make(ErrorCodes.INVALID_PARAMS, "timeout must be a positive finite number")
	var deferred: Dictionary = McpDispatcher.DEFERRED_RESPONSE.duplicate()
	deferred["_deferred_timeout_ms"] = int(ceil((timeout + 4.5) * 1000.0))
	_finish_send_request_deferred(_connection, request_id, params.duplicate(true))
	return deferred


static func _finish_send_request_deferred(connection, request_id: String, params: Dictionary) -> void:
	var work := ScriptWork.begin("http_send_request")
	await _run_send_request_deferred(connection, request_id, params)
	ScriptWork.finish(work)


static func _run_send_request_deferred(connection, request_id: String, params: Dictionary) -> void:
	if not is_instance_valid(connection):
		return
	var tree: SceneTree = connection.get_tree()
	if tree == null or tree.root == null:
		return
	# Let the dispatcher register the pending request before any completion path
	# can send its response.
	await tree.process_frame
	if not is_instance_valid(connection):
		return
	var method_str: String = str(params.get("method", "GET")).to_upper()
	var method := HTTPClient.METHOD_GET
	match method_str:
		"POST": method = HTTPClient.METHOD_POST
		"PUT": method = HTTPClient.METHOD_PUT
		"DELETE": method = HTTPClient.METHOD_DELETE
		"HEAD": method = HTTPClient.METHOD_HEAD
		"OPTIONS": method = HTTPClient.METHOD_OPTIONS
		_: method = HTTPClient.METHOD_GET
	var headers := PackedStringArray()
	var raw_headers = params.get("headers", [])
	if raw_headers is Array:
		for header in raw_headers:
			headers.append(str(header))
	var req := HTTPRequest.new()
	req.timeout = float(params.get("timeout", 10.0))
	tree.root.add_child(req)
	var err := req.request(str(params.get("url", "")), headers, method, str(params.get("body", "")))
	if err != OK:
		req.queue_free()
		if is_instance_valid(connection):
			connection.send_deferred_response(
				request_id,
				ErrorCodes.make(
					ErrorCodes.INTERNAL_ERROR,
					"HTTPRequest.request failed: %s" % error_string(err)
				)
			)
		return
	var result: Array = await req.request_completed
	req.queue_free()
	if not is_instance_valid(connection) or result.size() < 4:
		return
	var res_code: int = result[0]
	var http_status: int = result[1]
	var resp_headers: PackedStringArray = result[2]
	var resp_bytes: PackedByteArray = result[3]
	connection.send_deferred_response(request_id, {
		"data": {
			"success": res_code == HTTPRequest.RESULT_SUCCESS,
			"result_code": res_code,
			"status_code": http_status,
			"response_length": resp_bytes.size(),
			"body": resp_bytes.get_string_from_utf8(),
			"header_count": resp_headers.size(),
		}
	})


func download_file(params: Dictionary) -> Dictionary:
	var url: String = params.get("url", "")
	var target_path: String = params.get("target_path", "")

	if url.is_empty() or target_path.is_empty():
		return ErrorCodes.make(ErrorCodes.INVALID_PARAMS, "url and target_path are required")
	var request_id: String = params.get("_request_id", "")
	if _connection == null or request_id.is_empty():
		return ErrorCodes.make(
			ErrorCodes.INVALID_PARAMS,
			"Downloads must be started as a direct MCP tool call"
		)
	var timeout := float(params.get("timeout", 30.0))
	if not is_finite(timeout) or timeout <= 0.0:
		return ErrorCodes.make(ErrorCodes.INVALID_PARAMS, "timeout must be a positive finite number")

	if not target_path.begins_with("res://") and not target_path.begins_with("user://"):
		target_path = "res://" + target_path
	params["target_path"] = target_path
	var deferred: Dictionary = McpDispatcher.DEFERRED_RESPONSE.duplicate()
	deferred["_deferred_timeout_ms"] = int(ceil((timeout + 4.5) * 1000.0))
	_finish_download_file_deferred(_connection, request_id, params.duplicate(true))
	return deferred


static func _finish_download_file_deferred(connection, request_id: String, params: Dictionary) -> void:
	var work := ScriptWork.begin("http_download_file")
	await _run_download_file_deferred(connection, request_id, params)
	ScriptWork.finish(work)


static func _run_download_file_deferred(connection, request_id: String, params: Dictionary) -> void:
	if not is_instance_valid(connection):
		return
	var tree: SceneTree = connection.get_tree()
	if tree == null or tree.root == null:
		return
	await tree.process_frame
	if not is_instance_valid(connection):
		return
	var target_path: String = str(params.get("target_path", ""))
	var req := HTTPRequest.new()
	req.timeout = float(params.get("timeout", 30.0))
	req.download_file = target_path
	tree.root.add_child(req)
	var err := req.request(str(params.get("url", "")))
	if err != OK:
		req.queue_free()
		if is_instance_valid(connection):
			connection.send_deferred_response(
				request_id,
				ErrorCodes.make(
					ErrorCodes.INTERNAL_ERROR,
					"Download failed to initiate: %s" % error_string(err)
				)
			)
		return
	var result: Array = await req.request_completed
	req.queue_free()
	if not is_instance_valid(connection) or result.size() < 4:
		return
	var res_code: int = result[0]
	var http_status: int = result[1]
	connection.send_deferred_response(request_id, {
		"data": {
			"success": res_code == HTTPRequest.RESULT_SUCCESS and http_status == 200,
			"status_code": http_status,
			"target_path": target_path,
			"file_exists": FileAccess.file_exists(target_path),
		}
	})
