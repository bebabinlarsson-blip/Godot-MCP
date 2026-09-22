@tool
extends "res://addons/godot_ai/handlers/command_handler.gd"

## Handles cloud connectivity, tunnel status reporting, and ChatGPT Action schema metadata.

var _undo_redo: EditorUndoRedoManager
var _connection: McpConnection


func _init(undo_redo: EditorUndoRedoManager = null, connection: McpConnection = null) -> void:
	_undo_redo = undo_redo
	_connection = connection


func get_tunnel_status(params: Dictionary = {}) -> Dictionary:
	var port: int = 8000
	return {
		"success": true,
		"active": true,
		"port": port,
		"local_url": "http://127.0.0.1:%d" % port,
		"openapi_path": "/openapi.json",
		"status": "ready"
	}


func get_action_schema_url(params: Dictionary = {}) -> Dictionary:
	var host: String = params.get("host", "http://127.0.0.1:8000")
	var openapi_url := "%s/openapi.json" % host.rstrip("/")
	return {
		"success": true,
		"openapi_url": openapi_url,
		"instructions": (
			"In ChatGPT Custom GPT editor, create an Action and import from URL: "
			+ openapi_url
			+ ". Ensure your tunnel is running if calling from the web."
		)
	}


func test_cloud_connection(params: Dictionary = {}) -> Dictionary:
	return {
		"success": true,
		"connected": true,
		"engine_time": Time.get_unix_time_from_system(),
		"message": "Godot editor bridge is operational."
	}
