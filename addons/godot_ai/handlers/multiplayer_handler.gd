@tool
extends "res://addons/godot_ai/handlers/command_handler.gd"

const ErrorCodes := preload("res://addons/godot_ai/utils/error_codes.gd")

## Handles Godot High-Level Multiplayer scaffolding:
## ENetMultiplayerPeer network manager generation, MultiplayerSpawner,
## MultiplayerSynchronizer replication config, and runtime network status.

var _undo_redo: EditorUndoRedoManager
var _connection: McpConnection


func _init(undo_redo: EditorUndoRedoManager, connection: McpConnection = null) -> void:
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


func scaffold_network_manager(params: Dictionary) -> Dictionary:
	var save_path: String = params.get("save_path", "res://scripts/network_manager.gd")
	var default_port: int = int(params.get("default_port", 8910))
	var max_clients: int = int(params.get("max_clients", 32))
	var as_autoload: bool = bool(params.get("as_autoload", false))
	var autoload_name: String = params.get("autoload_name", "NetworkManager")

	var script_content := """extends Node

signal peer_connected(id: int)
signal peer_disconnected(id: int)
signal server_disconnected
signal connection_failed

const DEFAULT_PORT := %d
const MAX_CLIENTS := %d

var peer: ENetMultiplayerPeer = null


func _ready() -> void:
	multiplayer.peer_connected.connect(_on_peer_connected)
	multiplayer.peer_disconnected.connect(_on_peer_disconnected)
	multiplayer.server_disconnected.connect(_on_server_disconnected)
	multiplayer.connection_failed.connect(_on_connection_failed)


func host_game(port: int = DEFAULT_PORT, max_peers: int = MAX_CLIENTS) -> Error:
	peer = ENetMultiplayerPeer.new()
	var err := peer.create_server(port, max_peers)
	if err != OK:
		push_error("NetworkManager: Failed to create server on port " + str(port) + " code: " + str(err))
		return err
	multiplayer.multiplayer_peer = peer
	return OK


func join_game(address: String = "localhost", port: int = DEFAULT_PORT) -> Error:
	peer = ENetMultiplayerPeer.new()
	var err := peer.create_client(address, port)
	if err != OK:
		push_error("NetworkManager: Failed to connect to " + address + ":" + str(port) + " code: " + str(err))
		return err
	multiplayer.multiplayer_peer = peer
	return OK


func disconnect_game() -> void:
	if peer != null:
		peer.close()
		multiplayer.multiplayer_peer = null
		peer = null


func is_server() -> bool:
	return multiplayer.has_multiplayer_peer() and multiplayer.is_server()


func get_unique_id() -> int:
	if multiplayer.has_multiplayer_peer():
		return multiplayer.get_unique_id()
	return 0


func _on_peer_connected(id: int) -> void:
	peer_connected.emit(id)


func _on_peer_disconnected(id: int) -> void:
	peer_disconnected.emit(id)


func _on_server_disconnected() -> void:
	disconnect_game()
	server_disconnected.emit()


func _on_connection_failed() -> void:
	disconnect_game()
	connection_failed.emit()
""" % [default_port, max_clients]

	var global_path := ProjectSettings.globalize_path(save_path)
	var dir_path := global_path.get_base_dir()
	if not DirAccess.dir_exists_absolute(dir_path):
		DirAccess.make_dir_recursive_absolute(dir_path)

	var file := FileAccess.open(save_path, FileAccess.WRITE)
	if file == null:
		return ErrorCodes.make(ErrorCodes.RESOURCE_NOT_FOUND, "Failed to open %s for writing: %d" % [save_path, FileAccess.get_open_error()])

	file.store_string(script_content)
	file.close()

	if Engine.has_singleton("EditorInterface"):
		var editor_interface := Engine.get_singleton("EditorInterface")
		var fs = editor_interface.get_resource_filesystem()
		if fs != null:
			fs.update_file(save_path)

	var autoload_added := false
	if as_autoload:
		var setting_key := "autoload/" + autoload_name
		ProjectSettings.set_setting(setting_key, "*" + save_path)
		var err := ProjectSettings.save()
		autoload_added = (err == OK)

	return {
		"data": {
			"save_path": save_path,
			"default_port": default_port,
			"max_clients": max_clients,
			"as_autoload": as_autoload,
			"autoload_name": autoload_name if as_autoload else "",
			"autoload_registered": autoload_added,
		}
	}


func scaffold_spawner(params: Dictionary) -> Dictionary:
	var scene_root := _get_scene_root()
	if scene_root == null:
		return ErrorCodes.make(ErrorCodes.EDITOR_NOT_READY, "No active scene to scaffold MultiplayerSpawner in")

	var parent_path: String = params.get("parent_path", "")
	var parent := _resolve_node(scene_root, parent_path)
	if parent == null:
		return ErrorCodes.make(ErrorCodes.NODE_NOT_FOUND, "Parent node not found at %s" % parent_path)

	var spawner_name: String = params.get("spawner_name", "MultiplayerSpawner")
	var spawn_path: String = params.get("spawn_path", "..")
	var scenes_raw: Array = params.get("spawnable_scenes", [])
	var auto_spawn: bool = bool(params.get("auto_spawn", true))

	var spawner := MultiplayerSpawner.new()
	spawner.name = spawner_name
	spawner.spawn_path = NodePath(spawn_path)
	spawner.auto_spawn = auto_spawn

	for scene_item in scenes_raw:
		var s_path: String = str(scene_item)
		if not s_path.is_empty():
			spawner.add_spawnable_scene(s_path)

	if _undo_redo != null:
		_undo_redo.create_action("Scaffold MultiplayerSpawner " + spawner_name)
		_undo_redo.add_do_method(parent, "add_child", spawner)
		_undo_redo.add_do_property(spawner, "owner", scene_root)
		_undo_redo.add_undo_method(parent, "remove_child", spawner)
		_undo_redo.commit_action()
	else:
		parent.add_child(spawner)
		spawner.owner = scene_root

	var registered_count: int = spawner.get_spawnable_scene_count()

	return {
		"data": {
			"spawner_name": str(spawner.name),
			"spawner_path": str(spawner.get_path()),
			"spawn_path": spawn_path,
			"auto_spawn": auto_spawn,
			"spawnable_scene_count": registered_count,
		}
	}


func scaffold_synchronizer(params: Dictionary) -> Dictionary:
	var scene_root := _get_scene_root()
	if scene_root == null:
		return ErrorCodes.make(ErrorCodes.EDITOR_NOT_READY, "No active scene to scaffold MultiplayerSynchronizer in")

	var parent_path: String = params.get("parent_path", "")
	var parent := _resolve_node(scene_root, parent_path)
	if parent == null:
		return ErrorCodes.make(ErrorCodes.NODE_NOT_FOUND, "Parent node not found at %s" % parent_path)

	var sync_name: String = params.get("synchronizer_name", "MultiplayerSynchronizer")
	var root_path: String = params.get("root_path", "..")
	var props_raw: Array = params.get("properties", [":position", ":rotation"])

	var synchronizer := MultiplayerSynchronizer.new()
	synchronizer.name = sync_name
	synchronizer.root_path = NodePath(root_path)

	var rep_config := SceneReplicationConfig.new()
	var configured_count := 0

	for item in props_raw:
		var prop_path := ""
		var do_spawn := true
		var do_sync := true

		if item is Dictionary:
			prop_path = str(item.get("path", ""))
			do_spawn = bool(item.get("spawn", true))
			do_sync = bool(item.get("sync", true))
		elif item is String:
			prop_path = item

		if not prop_path.is_empty():
			var npath := NodePath(prop_path)
			rep_config.add_property(npath)
			rep_config.property_set_spawn(npath, do_spawn)
			rep_config.property_set_sync(npath, do_sync)
			configured_count += 1

	synchronizer.replication_config = rep_config

	if _undo_redo != null:
		_undo_redo.create_action("Scaffold MultiplayerSynchronizer " + sync_name)
		_undo_redo.add_do_method(parent, "add_child", synchronizer)
		_undo_redo.add_do_property(synchronizer, "owner", scene_root)
		_undo_redo.add_undo_method(parent, "remove_child", synchronizer)
		_undo_redo.commit_action()
	else:
		parent.add_child(synchronizer)
		synchronizer.owner = scene_root

	return {
		"data": {
			"synchronizer_name": str(synchronizer.name),
			"synchronizer_path": str(synchronizer.get_path()),
			"root_path": root_path,
			"property_count": configured_count,
		}
	}


func get_network_status(params: Dictionary) -> Dictionary:
	var tree := Engine.get_main_loop() as SceneTree
	var mp: MultiplayerAPI = null
	if tree != null:
		mp = tree.get_multiplayer()

	if mp == null or not mp.has_multiplayer_peer():
		return {
			"data": {
				"has_peer": false,
				"is_server": false,
				"unique_id": 0,
				"connected_peers": [],
				"connection_status": "disconnected",
			}
		}

	var peer := mp.multiplayer_peer
	var status_code := peer.get_connection_status()
	var status_str := "unknown"
	match status_code:
		MultiplayerPeer.CONNECTION_DISCONNECTED:
			status_str = "disconnected"
		MultiplayerPeer.CONNECTION_CONNECTING:
			status_str = "connecting"
		MultiplayerPeer.CONNECTION_CONNECTED:
			status_str = "connected"

	var raw_peers := mp.get_peers()
	var peers_list: Array = []
	for p in raw_peers:
		peers_list.append(int(p))

	return {
		"data": {
			"has_peer": true,
			"is_server": mp.is_server(),
			"unique_id": mp.get_unique_id(),
			"connected_peers": peers_list,
			"connection_status": status_str,
		}
	}
