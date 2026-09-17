@tool
class_name OmniReflection
extends RefCounted

## Universal Object Reflection handler for Godot Omni.
## Resolves instance IDs and handles, invokes methods with typed arguments,
## reads/writes properties, and inspects object metadata.

static func resolve_object(target_ref: Variant) -> Object:
	if target_ref is Object:
		if is_instance_valid(target_ref):
			return target_ref
		return null
	elif target_ref is int:
		return instance_from_id(int(target_ref))
	elif target_ref is String:
		var s := str(target_ref).strip_edges()
		if s.begins_with("obj://"):
			var parts := s.split("/")
			if parts.size() >= 4:
				var obj_id := int(parts[3])
				return instance_from_id(obj_id)
		elif s.begins_with("/root") or s.begins_with("."):
			var tree := Engine.get_main_loop() as SceneTree
			if tree and tree.root:
				return tree.root.get_node_or_null(NodePath(s))
	return null


static func inspect_object(target: Object) -> Dictionary:
	if not is_instance_valid(target):
		return {"ok": false, "error": "OBJECT_FREED: Object is null or no longer valid."}

	var methods: Array = []
	for m in target.get_method_list():
		methods.append({
			"name": m.name,
			"args": m.args.map(func(a): return {"name": a.name, "type": type_string(a.type)}),
			"return_type": type_string(m.return.type),
			"flags": m.flags,
		})

	var properties: Array = []
	for p in target.get_property_list():
		if p.usage & PROPERTY_USAGE_STORAGE or p.usage & PROPERTY_USAGE_EDITOR:
			properties.append({
				"name": p.name,
				"type": type_string(p.type),
				"value": target.get(p.name),
			})

	var signals: Array = []
	for sig in target.get_signal_list():
		signals.append({
			"name": sig.name,
			"args": sig.args.map(func(a): return {"name": a.name, "type": type_string(a.type)}),
		})

	return {
		"ok": true,
		"instance_id": target.get_instance_id(),
		"class": target.get_class(),
		"is_node": target is Node,
		"is_resource": target is Resource,
		"node_path": str((target as Node).get_path()) if target is Node else "",
		"methods": methods,
		"properties": properties,
		"signals": signals,
	}


static func call_method(target: Object, method: StringName, args: Array = []) -> Dictionary:
	if not is_instance_valid(target):
		return {"ok": false, "error": "OBJECT_FREED: Target object is no longer valid."}

	if not target.has_method(method):
		return {"ok": false, "error": "Method '%s' does not exist on class '%s'." % [method, target.get_class()]}

	var result = target.callv(method, args)
	return {
		"ok": true,
		"result": result,
	}


static func get_property(target: Object, prop: StringName) -> Dictionary:
	if not is_instance_valid(target):
		return {"ok": false, "error": "OBJECT_FREED: Target object is no longer valid."}

	var val = target.get(prop)
	return {
		"ok": true,
		"value": val,
	}


static func set_property(target: Object, prop: StringName, val: Variant) -> Dictionary:
	if not is_instance_valid(target):
		return {"ok": false, "error": "OBJECT_FREED: Target object is no longer valid."}

	target.set(prop, val)
	return {
		"ok": true,
		"value": target.get(prop),
	}
