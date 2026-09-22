@tool
extends "res://addons/godot_ai/handlers/command_handler.gd"

const ErrorCodes := preload("res://addons/godot_ai/utils/error_codes.gd")

## Handles DisplayServer and Window configuration, multi-window scaffolding,
## VSync modes, and mouse capture modes.

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


func set_mode(params: Dictionary) -> Dictionary:
	var mode_str: String = params.get("mode", "windowed").to_lower()
	var mode := DisplayServer.WINDOW_MODE_WINDOWED
	match mode_str:
		"minimized":
			mode = DisplayServer.WINDOW_MODE_MINIMIZED
		"maximized":
			mode = DisplayServer.WINDOW_MODE_MAXIMIZED
		"fullscreen":
			mode = DisplayServer.WINDOW_MODE_FULLSCREEN
		"exclusive_fullscreen":
			mode = DisplayServer.WINDOW_MODE_EXCLUSIVE_FULLSCREEN
		_:
			mode = DisplayServer.WINDOW_MODE_WINDOWED

	DisplayServer.window_set_mode(mode)

	if params.has("borderless"):
		DisplayServer.window_set_flag(DisplayServer.WINDOW_FLAG_BORDERLESS, bool(params["borderless"]))

	if params.has("always_on_top"):
		DisplayServer.window_set_flag(DisplayServer.WINDOW_FLAG_ALWAYS_ON_TOP, bool(params["always_on_top"]))

	return {
		"data": {
			"mode": mode_str,
			"borderless": DisplayServer.window_get_flag(DisplayServer.WINDOW_FLAG_BORDERLESS),
			"always_on_top": DisplayServer.window_get_flag(DisplayServer.WINDOW_FLAG_ALWAYS_ON_TOP),
		}
	}


func get_display_info(_params: Dictionary) -> Dictionary:
	var screen_count := DisplayServer.get_screen_count()
	var primary_screen := DisplayServer.get_primary_screen()
	var screen_size := DisplayServer.screen_get_size()
	var screen_refresh := DisplayServer.screen_get_refresh_rate()
	var win_size := DisplayServer.window_get_size()
	var win_pos := DisplayServer.window_get_position()
	var win_mode := DisplayServer.window_get_mode()
	var vsync_mode := DisplayServer.window_get_vsync_mode()
	var mouse_mode := Input.get_mouse_mode()

	var win_mode_str := "windowed"
	match win_mode:
		DisplayServer.WINDOW_MODE_MINIMIZED: win_mode_str = "minimized"
		DisplayServer.WINDOW_MODE_MAXIMIZED: win_mode_str = "maximized"
		DisplayServer.WINDOW_MODE_FULLSCREEN: win_mode_str = "fullscreen"
		DisplayServer.WINDOW_MODE_EXCLUSIVE_FULLSCREEN: win_mode_str = "exclusive_fullscreen"

	var vsync_str := "enabled"
	match vsync_mode:
		DisplayServer.VSYNC_DISABLED: vsync_str = "disabled"
		DisplayServer.VSYNC_ENABLED: vsync_str = "enabled"
		DisplayServer.VSYNC_ADAPTIVE: vsync_str = "adaptive"
		DisplayServer.VSYNC_MAILBOX: vsync_str = "mailbox"

	var mouse_mode_str := "visible"
	match mouse_mode:
		Input.MOUSE_MODE_VISIBLE: mouse_mode_str = "visible"
		Input.MOUSE_MODE_HIDDEN: mouse_mode_str = "hidden"
		Input.MOUSE_MODE_CAPTURED: mouse_mode_str = "captured"
		Input.MOUSE_MODE_CONFINED: mouse_mode_str = "confined"
		Input.MOUSE_MODE_CONFINED_HIDDEN: mouse_mode_str = "confined_hidden"

	return {
		"data": {
			"screen_count": screen_count,
			"primary_screen": primary_screen,
			"screen_size": [screen_size.x, screen_size.y],
			"screen_refresh_rate": screen_refresh,
			"window_size": [win_size.x, win_size.y],
			"window_position": [win_pos.x, win_pos.y],
			"window_mode": win_mode_str,
			"vsync_mode": vsync_str,
			"mouse_mode": mouse_mode_str,
		}
	}


func set_window_rect(params: Dictionary) -> Dictionary:
	var updated: Dictionary = {}
	if params.has("size") and params["size"] is Array:
		var s: Array = params["size"]
		if s.size() >= 2:
			DisplayServer.window_set_size(Vector2i(int(s[0]), int(s[1])))
			var cur_s := DisplayServer.window_get_size()
			updated["size"] = [cur_s.x, cur_s.y]

	if params.has("position") and params["position"] is Array:
		var p: Array = params["position"]
		if p.size() >= 2:
			DisplayServer.window_set_position(Vector2i(int(p[0]), int(p[1])))
			var cur_p := DisplayServer.window_get_position()
			updated["position"] = [cur_p.x, cur_p.y]

	return {"data": {"updated": updated}}


func set_vsync(params: Dictionary) -> Dictionary:
	var vsync_str: String = params.get("vsync_mode", "enabled").to_lower()
	var mode := DisplayServer.VSYNC_ENABLED
	match vsync_str:
		"disabled": mode = DisplayServer.VSYNC_DISABLED
		"enabled": mode = DisplayServer.VSYNC_ENABLED
		"adaptive": mode = DisplayServer.VSYNC_ADAPTIVE
		"mailbox": mode = DisplayServer.VSYNC_MAILBOX
		_: mode = DisplayServer.VSYNC_ENABLED

	DisplayServer.window_set_vsync_mode(mode)
	return {"data": {"vsync_mode": vsync_str}}


func set_mouse_mode(params: Dictionary) -> Dictionary:
	var mode_str: String = params.get("mouse_mode", "visible").to_lower()
	var mode := Input.MOUSE_MODE_VISIBLE
	match mode_str:
		"visible": mode = Input.MOUSE_MODE_VISIBLE
		"hidden": mode = Input.MOUSE_MODE_HIDDEN
		"captured": mode = Input.MOUSE_MODE_CAPTURED
		"confined": mode = Input.MOUSE_MODE_CONFINED
		"confined_hidden": mode = Input.MOUSE_MODE_CONFINED_HIDDEN
		_: mode = Input.MOUSE_MODE_VISIBLE

	Input.set_mouse_mode(mode)
	return {"data": {"mouse_mode": mode_str}}


func scaffold_subwindow(params: Dictionary) -> Dictionary:
	var scene_root := _get_scene_root()
	if scene_root == null:
		return ErrorCodes.make(ErrorCodes.EDITOR_NOT_READY, "No active scene to scaffold subwindow in")

	var parent_path: String = params.get("parent_path", "")
	var parent := _resolve_node(scene_root, parent_path)
	if parent == null:
		return ErrorCodes.make(ErrorCodes.NODE_NOT_FOUND, "Parent node not found at %s" % parent_path)

	var win_type: String = params.get("window_type", "Window").to_lower()
	var win_name: String = params.get("name", "SubWindow")
	var title: String = params.get("title", "Window")
	var size_raw: Array = params.get("size", [400, 300])
	var w: int = int(size_raw[0]) if size_raw.size() >= 1 else 400
	var h: int = int(size_raw[1]) if size_raw.size() >= 2 else 300
	var transient: bool = bool(params.get("transient", true))
	var exclusive: bool = bool(params.get("exclusive", false))

	var win_node: Window = null
	match win_type:
		"confirmation_dialog":
			var cd := ConfirmationDialog.new()
			cd.dialog_text = params.get("dialog_text", "Are you sure?")
			win_node = cd
		"accept_dialog":
			var ad := AcceptDialog.new()
			ad.dialog_text = params.get("dialog_text", "Notice")
			win_node = ad
		_:
			win_node = Window.new()

	win_node.name = win_name
	win_node.title = title
	win_node.size = Vector2i(w, h)
	win_node.transient = transient
	win_node.exclusive = exclusive

	if _undo_redo != null:
		_undo_redo.create_action("Scaffold SubWindow " + win_name)
		_undo_redo.add_do_method(parent, "add_child", win_node)
		_undo_redo.add_do_property(win_node, "owner", scene_root)
		_undo_redo.add_undo_method(parent, "remove_child", win_node)
		_undo_redo.commit_action()
	else:
		parent.add_child(win_node)
		win_node.owner = scene_root

	return {
		"data": {
			"window_name": str(win_node.name),
			"window_path": str(win_node.get_path()),
			"window_type": win_node.get_class(),
			"title": title,
			"size": [w, h],
			"transient": transient,
			"exclusive": exclusive,
		}
	}
