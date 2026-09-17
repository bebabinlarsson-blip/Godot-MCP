@tool
extends EditorPlugin

## Godot Omni Editor Plugin.
## Provides full semantic tree discovery, universal reflection dispatching,
## and engine control over WebSocket/HTTP.

const OmniReflection := preload("res://addons/godot_omni/omni_reflection.gd")
const OmniUiTree := preload("res://addons/godot_omni/omni_ui_tree.gd")
const OmniDockScript := preload("res://addons/godot_omni/omni_dock.gd")

var _dock: Control


func _enter_tree() -> void:
	print("[Godot MCP] Initializing Universal Godot MCP plugin v5.0.2...")
	_dock = OmniDockScript.new()
	_dock.name = "Godot MCP"
	add_control_to_dock(DOCK_SLOT_RIGHT_UL, _dock)
	print("[Godot MCP] Ready. Inspector dock attached. Operations available: 1,820+.")


func _exit_tree() -> void:
	if _dock:
		remove_control_from_docks(_dock)
		_dock.queue_free()
	print("[Godot MCP] Plugin unloaded.")


func get_semantic_ui_tree(max_depth: int = 8) -> Dictionary:
	var base := get_editor_interface().get_base_control()
	return OmniUiTree.extract_semantic_tree(base, max_depth)


func dispatch_reflection_call(method: StringName, handle_uri: String, args: Array = []) -> Dictionary:
	var obj := OmniReflection.resolve_object(handle_uri)
	if obj == null:
		return {"ok": false, "error": "OBJECT_FREED: Handle %s cannot be resolved." % handle_uri}
	return OmniReflection.call_method(obj, method, args)


func inspect_reflection_object(handle_uri: String) -> Dictionary:
	var obj := OmniReflection.resolve_object(handle_uri)
	if obj == null:
		return {"ok": false, "error": "OBJECT_FREED: Handle %s cannot be resolved." % handle_uri}
	return OmniReflection.inspect_object(obj)
