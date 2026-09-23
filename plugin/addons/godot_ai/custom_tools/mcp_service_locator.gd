@tool
class_name McpServiceLocator
extends RefCounted

const McpConnection := preload("res://addons/godot_ai/connection.gd")
const McpLogBuffer := preload("res://addons/godot_ai/utils/log_buffer.gd")

var _connection: McpConnection = null
var _log_buffer: McpLogBuffer = null

func setup(connection: McpConnection, log_buffer: McpLogBuffer) -> void:
	_connection = connection
	_log_buffer = log_buffer

func get_connection() -> McpConnection:
	return _connection

func get_log_buffer() -> McpLogBuffer:
	return _log_buffer
