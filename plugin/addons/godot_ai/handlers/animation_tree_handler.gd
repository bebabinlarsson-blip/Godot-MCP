@tool
extends "res://addons/godot_ai/handlers/command_handler.gd"

const ErrorCodes := preload("res://addons/godot_ai/utils/error_codes.gd")

## Handles AnimationTree state machines, blend trees, and transitions.

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


func scaffold_state_machine(params: Dictionary) -> Dictionary:
	var scene_root := _get_scene_root()
	if scene_root == null:
		return {"error": "No edited scene root available", "code": ErrorCodes.NODE_NOT_FOUND}

	var parent_path: String = params.get("parent_path", "")
	var parent: Node = _resolve_node(scene_root, parent_path)
	if parent == null:
		return {"error": "Parent node not found: %s" % parent_path, "code": ErrorCodes.NODE_NOT_FOUND}

	var at := AnimationTree.new()
	at.name = params.get("node_name", "AnimationTree")
	var sm := AnimationNodeStateMachine.new()
	at.tree_root = sm

	var anim_player: String = params.get("anim_player_path", "")
	if not anim_player.is_empty():
		at.anim_player = NodePath(anim_player)

	parent.add_child(at)
	at.owner = scene_root

	return {
		"success": true,
		"node_path": str(at.get_path()),
		"root_type": "AnimationNodeStateMachine"
	}


func add_state(params: Dictionary) -> Dictionary:
	var scene_root := _get_scene_root()
	if scene_root == null:
		return {"error": "No edited scene root available", "code": ErrorCodes.NODE_NOT_FOUND}

	var tree_path: String = params.get("tree_path", "")
	var tree_node: Node = _resolve_node(scene_root, tree_path)
	if not tree_node is AnimationTree:
		return {"error": "Target node is not an AnimationTree: %s" % tree_path, "code": ErrorCodes.WRONG_TYPE}

	var at: AnimationTree = tree_node
	if not at.tree_root is AnimationNodeStateMachine:
		return {"error": "AnimationTree root is not an AnimationNodeStateMachine", "code": ErrorCodes.WRONG_TYPE}

	var sm: AnimationNodeStateMachine = at.tree_root
	var state_name: String = params.get("state_name", "")
	if state_name.is_empty():
		return {"error": "state_name is required", "code": ErrorCodes.INVALID_PARAMS}

	var anim_name: String = params.get("animation_name", "")
	var node_anim := AnimationNodeAnimation.new()
	if not anim_name.is_empty():
		node_anim.animation = StringName(anim_name)

	var pos_array: Array = params.get("position", [0, 0])
	var pos := Vector2(0, 0)
	if pos_array.size() >= 2:
		pos = Vector2(float(pos_array[0]), float(pos_array[1]))

	sm.add_node(StringName(state_name), node_anim, pos)

	return {
		"success": true,
		"tree_path": tree_path,
		"state_name": state_name,
		"animation": anim_name
	}


func add_transition(params: Dictionary) -> Dictionary:
	var scene_root := _get_scene_root()
	if scene_root == null:
		return {"error": "No edited scene root available", "code": ErrorCodes.NODE_NOT_FOUND}

	var tree_path: String = params.get("tree_path", "")
	var tree_node: Node = _resolve_node(scene_root, tree_path)
	if not tree_node is AnimationTree:
		return {"error": "Target node is not an AnimationTree: %s" % tree_path, "code": ErrorCodes.WRONG_TYPE}

	var at: AnimationTree = tree_node
	if not at.tree_root is AnimationNodeStateMachine:
		return {"error": "AnimationTree root is not an AnimationNodeStateMachine", "code": ErrorCodes.WRONG_TYPE}

	var sm: AnimationNodeStateMachine = at.tree_root
	var from_state: String = params.get("from_state", "")
	var to_state: String = params.get("to_state", "")
	var auto_advance: bool = params.get("auto_advance", false)

	if from_state.is_empty() or to_state.is_empty():
		return {"error": "from_state and to_state are required", "code": ErrorCodes.INVALID_PARAMS}

	var tr := AnimationNodeStateMachineTransition.new()
	tr.advance_mode = AnimationNodeStateMachineTransition.ADVANCE_MODE_AUTO if auto_advance else AnimationNodeStateMachineTransition.ADVANCE_MODE_ENABLED

	sm.add_transition(StringName(from_state), StringName(to_state), tr)

	return {
		"success": true,
		"from_state": from_state,
		"to_state": to_state,
		"auto_advance": auto_advance
	}


func scaffold_blend_tree(params: Dictionary) -> Dictionary:
	var scene_root := _get_scene_root()
	if scene_root == null:
		return {"error": "No edited scene root available", "code": ErrorCodes.NODE_NOT_FOUND}

	var parent_path: String = params.get("parent_path", "")
	var parent: Node = _resolve_node(scene_root, parent_path)
	if parent == null:
		return {"error": "Parent node not found: %s" % parent_path, "code": ErrorCodes.NODE_NOT_FOUND}

	var at := AnimationTree.new()
	at.name = params.get("node_name", "AnimationTreeBlend")
	var bt := AnimationNodeBlendTree.new()
	at.tree_root = bt

	var anim_player: String = params.get("anim_player_path", "")
	if not anim_player.is_empty():
		at.anim_player = NodePath(anim_player)

	parent.add_child(at)
	at.owner = scene_root

	return {
		"success": true,
		"node_path": str(at.get_path()),
		"root_type": "AnimationNodeBlendTree"
	}


func get_tree_info(params: Dictionary) -> Dictionary:
	var scene_root := _get_scene_root()
	if scene_root == null:
		return {"error": "No edited scene root available", "code": ErrorCodes.NODE_NOT_FOUND}

	var tree_path: String = params.get("tree_path", "")
	var tree_node: Node = _resolve_node(scene_root, tree_path)
	if not tree_node is AnimationTree:
		return {"error": "Target node is not an AnimationTree: %s" % tree_path, "code": ErrorCodes.WRONG_TYPE}

	var at: AnimationTree = tree_node
	var root_class := ""
	if at.tree_root != null:
		root_class = at.tree_root.get_class()

	return {
		"success": true,
		"tree_path": tree_path,
		"root_class": root_class,
		"anim_player": str(at.anim_player),
		"active": at.active
	}
