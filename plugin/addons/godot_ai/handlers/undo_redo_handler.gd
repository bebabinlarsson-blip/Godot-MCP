@tool
extends "res://addons/godot_ai/handlers/command_handler.gd"

const ErrorCodes := preload("res://addons/godot_ai/utils/error_codes.gd")

## Handles EditorUndoRedoManager history introspection and undo/redo execution.

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


func get_history(_params: Dictionary) -> Dictionary:
	if _undo_redo == null:
		return {
			"data": {
				"available": false,
				"current_action_name": "",
				"has_undo": false,
				"has_redo": false,
			}
		}

	var action_name = _undo_redo.get_current_action_name()
	var has_undo = _undo_redo.has_undo()
	var has_redo = _undo_redo.has_redo()

	var history_id := 0
	var scene_root := _get_scene_root()
	if scene_root != null:
		history_id = _undo_redo.get_object_history_id(scene_root)

	return {
		"data": {
			"available": true,
			"current_action_name": action_name,
			"has_undo": has_undo,
			"has_redo": has_redo,
			"history_id": history_id,
		}
	}


func undo(_params: Dictionary) -> Dictionary:
	if _undo_redo == null:
		return ErrorCodes.make(ErrorCodes.INTERNAL_ERROR, "EditorUndoRedoManager is not available")

	if not _undo_redo.has_undo():
		return {
			"data": {
				"undone": false,
				"message": "Nothing to undo in active history stack",
			}
		}

	var prev_action = _undo_redo.get_current_action_name()
	var success = _undo_redo.undo()

	return {
		"data": {
			"undone": success,
			"action_name": prev_action,
		}
	}


func redo(_params: Dictionary) -> Dictionary:
	if _undo_redo == null:
		return ErrorCodes.make(ErrorCodes.INTERNAL_ERROR, "EditorUndoRedoManager is not available")

	if not _undo_redo.has_redo():
		return {
			"data": {
				"redone": false,
				"message": "Nothing to redo in active history stack",
			}
		}

	var success = _undo_redo.redo()
	var new_action = _undo_redo.get_current_action_name()

	return {
		"data": {
			"redone": success,
			"action_name": new_action,
		}
	}
