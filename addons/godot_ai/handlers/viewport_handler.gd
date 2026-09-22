@tool
extends "res://addons/godot_ai/handlers/command_handler.gd"

const ErrorCodes := preload("res://addons/godot_ai/utils/error_codes.gd")

## Handles Viewport and SubViewport lifecycle, splitscreen scaffolding,
## render texture wiring, and viewport property configuration.

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


func create_subviewport(params: Dictionary) -> Dictionary:
	var scene_root := _get_scene_root()
	if scene_root == null:
		return ErrorCodes.make(ErrorCodes.EDITOR_NOT_READY, "No active scene to create SubViewport in")

	var parent_path: String = params.get("parent_path", "")
	var parent := _resolve_node(scene_root, parent_path)
	if parent == null:
		return ErrorCodes.make(ErrorCodes.NODE_NOT_FOUND, "Parent node not found at %s" % parent_path)

	var vp_name: String = params.get("name", "SubViewport")
	var size_raw: Array = params.get("size", [512, 512])
	var width: int = int(size_raw[0]) if size_raw.size() >= 1 else 512
	var height: int = int(size_raw[1]) if size_raw.size() >= 2 else 512
	var update_mode: int = int(params.get("render_target_update_mode", SubViewport.UPDATE_ALWAYS))
	var transparent_bg: bool = bool(params.get("transparent_bg", false))
	var own_world_3d: bool = bool(params.get("own_world_3d", false))
	var as_container: bool = bool(params.get("as_container", false))

	var sub_viewport := SubViewport.new()
	sub_viewport.name = vp_name
	sub_viewport.size = Vector2i(width, height)
	sub_viewport.render_target_update_mode = update_mode
	sub_viewport.transparent_bg = transparent_bg
	sub_viewport.own_world_3d = own_world_3d

	var container: SubViewportContainer = null
	var node_to_add: Node = sub_viewport

	if as_container:
		container = SubViewportContainer.new()
		container.name = vp_name + "Container"
		container.stretch = true
		container.add_child(sub_viewport)
		sub_viewport.owner = scene_root
		node_to_add = container

	if _undo_redo != null:
		_undo_redo.create_action("Create SubViewport " + vp_name)
		_undo_redo.add_do_method(parent, "add_child", node_to_add)
		_undo_redo.add_do_property(node_to_add, "owner", scene_root)
		if container != null:
			_undo_redo.add_do_property(sub_viewport, "owner", scene_root)
		_undo_redo.add_undo_method(parent, "remove_child", node_to_add)
		_undo_redo.commit_action()
	else:
		parent.add_child(node_to_add)
		node_to_add.owner = scene_root
		if container != null:
			sub_viewport.owner = scene_root

	return {
		"data": {
			"viewport_name": str(sub_viewport.name),
			"viewport_path": str(sub_viewport.get_path()),
			"container_path": str(container.get_path()) if container != null else "",
			"size": [width, height],
			"update_mode": update_mode,
			"transparent_bg": transparent_bg,
			"own_world_3d": own_world_3d,
		}
	}


func scaffold_splitscreen(params: Dictionary) -> Dictionary:
	var scene_root := _get_scene_root()
	if scene_root == null:
		return ErrorCodes.make(ErrorCodes.EDITOR_NOT_READY, "No active scene to scaffold splitscreen in")

	var parent_path: String = params.get("parent_path", "")
	var parent := _resolve_node(scene_root, parent_path)
	if parent == null:
		return ErrorCodes.make(ErrorCodes.NODE_NOT_FOUND, "Parent node not found at %s" % parent_path)

	var layout: String = params.get("layout", "2p_horizontal").to_lower()
	var is_3d: bool = bool(params.get("is_3d", false))

	var player_count := 2
	var root_container: BoxContainer = null

	if layout == "4p_quad":
		player_count = 4
	elif layout == "2p_vertical":
		player_count = 2
	else:
		layout = "2p_horizontal"
		player_count = 2

	var grid_container: GridContainer = null
	if layout == "4p_quad":
		grid_container = GridContainer.new()
		grid_container.name = "SplitscreenGrid"
		grid_container.columns = 2
	elif layout == "2p_vertical":
		root_container = VBoxContainer.new()
		root_container.name = "SplitscreenVBox"
	else:
		root_container = HBoxContainer.new()
		root_container.name = "SplitscreenHBox"

	var layout_root: Control = grid_container if grid_container != null else root_container
	layout_root.set_anchors_preset(Control.PRESET_FULL_RECT)
	layout_root.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	layout_root.size_flags_vertical = Control.SIZE_EXPAND_FILL

	var players_info: Array = []

	for i in range(player_count):
		var p_idx := i + 1
		var cont := SubViewportContainer.new()
		cont.name = "Player%dContainer" % p_idx
		cont.stretch = true
		cont.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		cont.size_flags_vertical = Control.SIZE_EXPAND_FILL

		var vp := SubViewport.new()
		vp.name = "Player%dViewport" % p_idx
		vp.handle_input_locally = true
		cont.add_child(vp)

		var cam_path := ""
		if is_3d:
			var cam3d := Camera3D.new()
			cam3d.name = "Player%dCamera3D" % p_idx
			if i == 0:
				vp.audio_listener_enable_3d = true
			vp.add_child(cam3d)
			cam_path = str(cam3d.get_path())
		else:
			var cam2d := Camera2D.new()
			cam2d.name = "Player%dCamera2D" % p_idx
			if i == 0:
				vp.audio_listener_enable_2d = true
			vp.add_child(cam2d)
			cam_path = str(cam2d.get_path())

		layout_root.add_child(cont)
		players_info.append({
			"player_id": p_idx,
			"container_name": cont.name,
			"viewport_name": vp.name,
			"camera_type": "Camera3D" if is_3d else "Camera2D",
		})

	if _undo_redo != null:
		_undo_redo.create_action("Scaffold Splitscreen " + layout)
		_undo_redo.add_do_method(parent, "add_child", layout_root)
		_undo_redo.add_do_property(layout_root, "owner", scene_root)
		for child in layout_root.get_children():
			_undo_redo.add_do_property(child, "owner", scene_root)
			for sub in child.get_children():
				_undo_redo.add_do_property(sub, "owner", scene_root)
				for sub_sub in sub.get_children():
					_undo_redo.add_do_property(sub_sub, "owner", scene_root)
		_undo_redo.add_undo_method(parent, "remove_child", layout_root)
		_undo_redo.commit_action()
	else:
		parent.add_child(layout_root)
		layout_root.owner = scene_root
		for child in layout_root.get_children():
			child.owner = scene_root
			for sub in child.get_children():
				sub.owner = scene_root
				for sub_sub in sub.get_children():
					sub_sub.owner = scene_root

	return {
		"data": {
			"layout": layout,
			"is_3d": is_3d,
			"container_path": str(layout_root.get_path()),
			"player_count": player_count,
			"players": players_info,
		}
	}


func wire_render_texture(params: Dictionary) -> Dictionary:
	var scene_root := _get_scene_root()
	if scene_root == null:
		return ErrorCodes.make(ErrorCodes.EDITOR_NOT_READY, "No active scene to wire render texture in")

	var vp_path: String = params.get("viewport_path", "")
	if vp_path.is_empty():
		return ErrorCodes.make(ErrorCodes.INVALID_PARAMS, "viewport_path must be specified")

	var target_path: String = params.get("target_node_path", "")
	if target_path.is_empty():
		return ErrorCodes.make(ErrorCodes.INVALID_PARAMS, "target_node_path must be specified")

	var vp_node := _resolve_node(scene_root, vp_path)
	if vp_node == null or not (vp_node is Viewport):
		return ErrorCodes.make(ErrorCodes.NODE_NOT_FOUND, "Viewport not found at %s" % vp_path)

	var target_node := _resolve_node(scene_root, target_path)
	if target_node == null:
		return ErrorCodes.make(ErrorCodes.NODE_NOT_FOUND, "Target node not found at %s" % target_path)

	var tex := (vp_node as Viewport).get_texture()
	var target_property: String = params.get("target_property", "")

	if target_property.is_empty():
		if target_node is Sprite2D:
			target_property = "texture"
		elif target_node is TextureRect:
			target_property = "texture"
		elif target_node is MeshInstance3D:
			target_property = "material_override:albedo_texture"
		else:
			target_property = "texture"

	if _undo_redo != null:
		_undo_redo.create_action("Wire Viewport Texture to " + target_node.name)
		if target_property.begins_with("material_override"):
			var mat = target_node.get("material_override")
			if mat == null or not (mat is BaseMaterial3D):
				mat = StandardMaterial3D.new()
				_undo_redo.add_do_property(target_node, "material_override", mat)
			_undo_redo.add_do_property(mat, "albedo_texture", tex)
		else:
			_undo_redo.add_do_property(target_node, target_property, tex)
		_undo_redo.commit_action()
	else:
		if target_property.begins_with("material_override"):
			var mat = target_node.get("material_override")
			if mat == null or not (mat is BaseMaterial3D):
				mat = StandardMaterial3D.new()
				target_node.set("material_override", mat)
			mat.set("albedo_texture", tex)
		else:
			target_node.set(target_property, tex)

	return {
		"data": {
			"viewport_path": str(vp_node.get_path()),
			"target_node_path": str(target_node.get_path()),
			"target_property": target_property,
			"wired": true,
		}
	}


func get_viewport_tree(params: Dictionary) -> Dictionary:
	var scene_root := _get_scene_root()
	if scene_root == null:
		return ErrorCodes.make(ErrorCodes.EDITOR_NOT_READY, "No active scene to inspect viewports in")

	var viewports: Array = []
	_collect_viewports(scene_root, viewports)

	return {
		"data": {
			"viewports": viewports,
			"count": viewports.size(),
		}
	}


func _collect_viewports(node: Node, out_viewports: Array) -> void:
	if node is Viewport:
		var vp := node as Viewport
		var active_cam := ""
		if vp.has_method("get_camera_2d"):
			var c2d = vp.get_camera_2d()
			if c2d != null:
				active_cam = str(c2d.get_path())
		if active_cam.is_empty() and vp.has_method("get_camera_3d"):
			var c3d = vp.get_camera_3d()
			if c3d != null:
				active_cam = str(c3d.get_path())

		var update_mode := -1
		var transparent_bg := false
		var own_world := false
		if vp is SubViewport:
			var svp := vp as SubViewport
			update_mode = svp.render_target_update_mode
			transparent_bg = svp.transparent_bg
			own_world = svp.own_world_3d

		out_viewports.append({
			"name": str(vp.name),
			"path": str(vp.get_path()),
			"class": vp.get_class(),
			"size": [vp.size.x, vp.size.y],
			"active_camera": active_cam,
			"render_target_update_mode": update_mode,
			"transparent_bg": transparent_bg,
			"own_world_3d": own_world,
		})

	for child in node.get_children():
		_collect_viewports(child, out_viewports)


func set_viewport_properties(params: Dictionary) -> Dictionary:
	var scene_root := _get_scene_root()
	if scene_root == null:
		return ErrorCodes.make(ErrorCodes.EDITOR_NOT_READY, "No active scene")

	var vp_path: String = params.get("viewport_path", "")
	var target_node := _resolve_node(scene_root, vp_path)
	if target_node == null or not (target_node is Viewport):
		return ErrorCodes.make(ErrorCodes.NODE_NOT_FOUND, "Viewport not found at %s" % vp_path)

	var vp := target_node as Viewport
	var updated_props: Dictionary = {}

	if params.has("size") and params["size"] is Array:
		var s: Array = params["size"]
		if s.size() >= 2:
			vp.size = Vector2i(int(s[0]), int(s[1]))
			updated_props["size"] = [vp.size.x, vp.size.y]

	if params.has("transparent_bg") and vp is SubViewport:
		(vp as SubViewport).transparent_bg = bool(params["transparent_bg"])
		updated_props["transparent_bg"] = (vp as SubViewport).transparent_bg

	if params.has("render_target_update_mode") and vp is SubViewport:
		(vp as SubViewport).render_target_update_mode = int(params["render_target_update_mode"])
		updated_props["render_target_update_mode"] = (vp as SubViewport).render_target_update_mode

	if params.has("own_world_3d") and vp is SubViewport:
		(vp as SubViewport).own_world_3d = bool(params["own_world_3d"])
		updated_props["own_world_3d"] = (vp as SubViewport).own_world_3d

	if params.has("msaa_2d"):
		vp.msaa_2d = int(params["msaa_2d"])
		updated_props["msaa_2d"] = vp.msaa_2d

	if params.has("msaa_3d"):
		vp.msaa_3d = int(params["msaa_3d"])
		updated_props["msaa_3d"] = vp.msaa_3d

	if params.has("screen_space_aa"):
		vp.screen_space_aa = int(params["screen_space_aa"])
		updated_props["screen_space_aa"] = vp.screen_space_aa

	if params.has("use_hdr_2d"):
		vp.use_hdr_2d = bool(params["use_hdr_2d"])
		updated_props["use_hdr_2d"] = vp.use_hdr_2d

	return {
		"data": {
			"viewport_path": str(vp.get_path()),
			"updated_properties": updated_props,
		}
	}
