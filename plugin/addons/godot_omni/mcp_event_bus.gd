@tool
extends RefCounted

## Compatibility shim for McpEventBus.
## The canonical class is McpEventBus in res://addons/godot_ai/utils/mcp_event_bus.gd.
## inspection of AI tool operations within the Godot Editor.

static var _listeners: Array[Callable] = []
static var _history: Array[Dictionary] = []
const MAX_HISTORY := 150


## Register a callable to be notified on every tool invocation.
## Signature: func(entry: Dictionary) -> void
static func subscribe(listener: Callable) -> void:
	if not _listeners.has(listener):
		_listeners.append(listener)


## Unregister a previously registered listener callable.
static func unsubscribe(listener: Callable) -> void:
	_listeners.erase(listener)


## Record a tool call from the dispatcher and broadcast to all active listeners.
static func record_tool_call(tool_name: String, params: Dictionary, result: Dictionary, duration_ms: float) -> void:
	var is_ok: bool = true
	if result.get("status", "") == "error" or result.has("error"):
		is_ok = false
	if bool(result.get("ok", true)) == false:
		is_ok = false

	var entry := {
		"timestamp": Time.get_time_string_from_system(),
		"ticks_msec": Time.get_ticks_msec(),
		"tool": tool_name,
		"params": params,
		"result": result,
		"duration_ms": duration_ms,
		"ok": is_ok,
	}

	_history.append(entry)
	if _history.size() > MAX_HISTORY:
		_history.pop_front()

	var valid_listeners: Array[Callable] = []
	for listener in _listeners:
		if listener.is_valid():
			valid_listeners.append(listener)
			listener.call(entry)
	_listeners = valid_listeners


## Retrieve the historical log of tool calls (up to MAX_HISTORY).
static func get_history() -> Array[Dictionary]:
	return _history.duplicate()


## Clear the recorded tool invocation history.
static func clear_history() -> void:
	_history.clear()
