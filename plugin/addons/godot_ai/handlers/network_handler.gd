@tool
extends "res://addons/godot_ai/handlers/command_handler.gd"

const ErrorCodes := preload("res://addons/godot_ai/utils/error_codes.gd")

## Handles low-level networking components (TCP, UDP, WebSocket) and interface queries.

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


func scaffold_tcp_server(params: Dictionary) -> Dictionary:
	var scene_root := _get_scene_root()
	if scene_root == null:
		return {"error": "No edited scene root available", "code": ErrorCodes.NODE_NOT_FOUND}

	var parent_path: String = params.get("parent_path", "")
	var parent: Node = _resolve_node(scene_root, parent_path)
	if parent == null:
		return {"error": "Parent node not found: %s" % parent_path, "code": ErrorCodes.NODE_NOT_FOUND}

	var node := Node.new()
	node.name = params.get("node_name", "TcpServer")
	node.set_meta("network_type", "tcp_server")
	node.set_meta("port", int(params.get("port", 8080)))
	node.set_meta("bind_address", str(params.get("bind_address", "*")))

	parent.add_child(node)
	node.owner = scene_root

	return {
		"success": true,
		"node_path": str(node.get_path()),
		"port": params.get("port", 8080),
		"bind_address": params.get("bind_address", "*")
	}


func scaffold_websocket_peer(params: Dictionary) -> Dictionary:
	var scene_root := _get_scene_root()
	if scene_root == null:
		return {"error": "No edited scene root available", "code": ErrorCodes.NODE_NOT_FOUND}

	var parent_path: String = params.get("parent_path", "")
	var parent: Node = _resolve_node(scene_root, parent_path)
	if parent == null:
		return {"error": "Parent node not found: %s" % parent_path, "code": ErrorCodes.NODE_NOT_FOUND}

	var node := Node.new()
	node.name = params.get("node_name", "WebSocketClient")
	node.set_meta("network_type", "websocket_peer")
	node.set_meta("url", str(params.get("url", "")))

	parent.add_child(node)
	node.owner = scene_root

	return {
		"success": true,
		"node_path": str(node.get_path()),
		"url": params.get("url", "")
	}


func scaffold_udp_peer(params: Dictionary) -> Dictionary:
	var scene_root := _get_scene_root()
	if scene_root == null:
		return {"error": "No edited scene root available", "code": ErrorCodes.NODE_NOT_FOUND}

	var parent_path: String = params.get("parent_path", "")
	var parent: Node = _resolve_node(scene_root, parent_path)
	if parent == null:
		return {"error": "Parent node not found: %s" % parent_path, "code": ErrorCodes.NODE_NOT_FOUND}

	var node := Node.new()
	node.name = params.get("node_name", "UdpPeer")
	node.set_meta("network_type", "udp_peer")
	node.set_meta("port", int(params.get("port", 9000)))

	parent.add_child(node)
	node.owner = scene_root

	return {
		"success": true,
		"node_path": str(node.get_path()),
		"port": params.get("port", 9000)
	}


func get_network_interfaces(params: Dictionary) -> Dictionary:
	var addresses: Array = IP.get_local_addresses()
	var interfaces: Array = IP.get_local_interfaces()
	return {
		"success": true,
		"local_addresses": addresses,
		"interfaces": interfaces
	}
