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
		return {"error": "url is required", "code": ErrorCodes.INVALID_PARAMS}

	var method_str: String = params.get("method", "GET").to_upper()
	var method := HTTPClient.METHOD_GET
	match method_str:
		"POST": method = HTTPClient.METHOD_POST
		"PUT": method = HTTPClient.METHOD_PUT
		"DELETE": method = HTTPClient.METHOD_DELETE
		"HEAD": method = HTTPClient.METHOD_HEAD
		"OPTIONS": method = HTTPClient.METHOD_OPTIONS
		_: method = HTTPClient.METHOD_GET

	var headers: PackedStringArray = PackedStringArray()
	var raw_headers = params.get("headers", [])
	if raw_headers is Array:
		for h in raw_headers:
			headers.append(str(h))

	var body: String = params.get("body", "")

	var tree := Engine.get_main_loop() as SceneTree
	if tree == null or tree.root == null:
		return {"error": "No active scene tree for HTTP execution", "code": ErrorCodes.EDITOR_NOT_READY}

	var req := HTTPRequest.new()
	req.timeout = float(params.get("timeout", 10.0))
	tree.root.add_child(req)

	var err := req.request(url, headers, method, body)
	if err != OK:
		req.queue_free()
		return {"error": "HTTPRequest.request failed with code: %d" % err, "code": ErrorCodes.INTERNAL_ERROR}

	var result: Array = await req.request_completed
	req.queue_free()

	# result format: [result_code, response_code, headers, body_bytes]
	var res_code: int = result[0]
	var http_status: int = result[1]
	var resp_headers: PackedStringArray = result[2]
	var resp_bytes: PackedByteArray = result[3]

	return {
		"success": (res_code == HTTPRequest.RESULT_SUCCESS),
		"result_code": res_code,
		"status_code": http_status,
		"response_length": resp_bytes.size(),
		"body": resp_bytes.get_string_from_utf8(),
		"header_count": resp_headers.size()
	}


func download_file(params: Dictionary) -> Dictionary:
	var url: String = params.get("url", "")
	var target_path: String = params.get("target_path", "")

	if url.is_empty() or target_path.is_empty():
		return {"error": "url and target_path are required", "code": ErrorCodes.INVALID_PARAMS}

	if not target_path.begins_with("res://") and not target_path.begins_with("user://"):
		target_path = "res://" + target_path

	var tree := Engine.get_main_loop() as SceneTree
	if tree == null or tree.root == null:
		return {"error": "No active scene tree for download", "code": ErrorCodes.EDITOR_NOT_READY}

	var req := HTTPRequest.new()
	req.timeout = float(params.get("timeout", 30.0))
	req.download_file = target_path
	tree.root.add_child(req)

	var err := req.request(url)
	if err != OK:
		req.queue_free()
		return {"error": "Download failed to initiate with code: %d" % err, "code": ErrorCodes.INTERNAL_ERROR}

	var result: Array = await req.request_completed
	req.queue_free()

	var res_code: int = result[0]
	var http_status: int = result[1]

	return {
		"success": (res_code == HTTPRequest.RESULT_SUCCESS and http_status == 200),
		"status_code": http_status,
		"target_path": target_path,
		"file_exists": FileAccess.file_exists(target_path)
	}
