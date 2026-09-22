@tool
extends "res://addons/godot_ai/handlers/command_handler.gd"

const ErrorCodes := preload("res://addons/godot_ai/utils/error_codes.gd")

## Handles AR/VR OpenXR player rig scaffolding, XRServer status inspection,
## and OpenXR bootstrap script generation.

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


func scaffold_xr_rig(params: Dictionary) -> Dictionary:
	var scene_root := _get_scene_root()
	if scene_root == null:
		return ErrorCodes.make(ErrorCodes.EDITOR_NOT_READY, "No active scene to scaffold XR rig in")

	var parent_path: String = params.get("parent_path", "")
	var parent := _resolve_node(scene_root, parent_path)
	if parent == null:
		return ErrorCodes.make(ErrorCodes.NODE_NOT_FOUND, "Parent node not found at %s" % parent_path)

	var rig_name: String = params.get("rig_name", "XROrigin3D")
	var origin := XROrigin3D.new()
	origin.name = rig_name

	var camera := XRCamera3D.new()
	camera.name = "XRCamera3D"
	origin.add_child(camera)

	var left_controller := XRController3D.new()
	left_controller.name = "LeftHand"
	left_controller.tracker = &"left_hand"
	left_controller.pose = &"aim"
	origin.add_child(left_controller)

	var right_controller := XRController3D.new()
	right_controller.name = "RightHand"
	right_controller.tracker = &"right_hand"
	right_controller.pose = &"aim"
	origin.add_child(right_controller)

	if _undo_redo != null:
		_undo_redo.create_action("Scaffold XR Rig " + rig_name)
		_undo_redo.add_do_method(parent, "add_child", origin)
		_undo_redo.add_do_property(origin, "owner", scene_root)
		_undo_redo.add_do_property(camera, "owner", scene_root)
		_undo_redo.add_do_property(left_controller, "owner", scene_root)
		_undo_redo.add_do_property(right_controller, "owner", scene_root)
		_undo_redo.add_undo_method(parent, "remove_child", origin)
		_undo_redo.commit_action()
	else:
		parent.add_child(origin)
		origin.owner = scene_root
		camera.owner = scene_root
		left_controller.owner = scene_root
		right_controller.owner = scene_root

	return {
		"data": {
			"rig_name": rig_name,
			"origin_path": str(origin.get_path()),
			"camera_path": str(camera.get_path()),
			"left_controller_path": str(left_controller.get_path()),
			"right_controller_path": str(right_controller.get_path()),
		}
	}


func get_xr_status(_params: Dictionary) -> Dictionary:
	var primary: XRInterface = XRServer.primary_interface
	var is_initialized := false
	var primary_name := ""
	if primary != null:
		is_initialized = primary.is_initialized()
		primary_name = primary.get_name()

	var interfaces_list: Array = []
	for iface in XRServer.get_interfaces():
		if iface != null:
			var iface_name: String = iface.get("name", "")
			var xr_iface: XRInterface = XRServer.find_interface(iface_name)
			interfaces_list.append({
				"name": iface_name,
				"is_initialized": xr_iface.is_initialized() if xr_iface != null else false,
			})

	return {
		"data": {
			"primary_interface": primary_name,
			"is_initialized": is_initialized,
			"available_interfaces": interfaces_list,
			"interface_count": interfaces_list.size(),
		}
	}


func generate_xr_startup_script(params: Dictionary) -> Dictionary:
	var save_path: String = params.get("save_path", "res://scripts/xr_initializer.gd")

	var script_content := """extends Node3D

var xr_interface: XRInterface


func _ready() -> void:
	xr_interface = XRServer.find_interface("OpenXR")
	if xr_interface and xr_interface.is_initialized():
		print("OpenXR initialized successfully")
		DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
		get_viewport().use_xr = true
	else:
		print("OpenXR not initialized or headset not connected")
"""

	var global_path := ProjectSettings.globalize_path(save_path)
	var dir_path := global_path.get_base_dir()
	if not DirAccess.dir_exists_absolute(dir_path):
		DirAccess.make_dir_recursive_absolute(dir_path)

	var file := FileAccess.open(save_path, FileAccess.WRITE)
	if file == null:
		return ErrorCodes.make(ErrorCodes.RESOURCE_NOT_FOUND, "Failed to write %s: %d" % [save_path, FileAccess.get_open_error()])

	file.store_string(script_content)
	file.close()

	if Engine.has_singleton("EditorInterface"):
		var editor_interface := Engine.get_singleton("EditorInterface")
		var fs = editor_interface.get_resource_filesystem()
		if fs != null:
			fs.update_file(save_path)

	return {
		"data": {
			"save_path": save_path,
			"generated": true,
		}
	}
