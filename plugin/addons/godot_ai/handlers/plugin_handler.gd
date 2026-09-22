@tool
extends "res://addons/godot_ai/handlers/command_handler.gd"

const ErrorCodes := preload("res://addons/godot_ai/utils/error_codes.gd")

## Handles Godot editor plugin and addon discovery, enable/disable toggling,
## and custom EditorPlugin scaffolding.

var _undo_redo: EditorUndoRedoManager
var _connection: McpConnection


func _init(undo_redo: EditorUndoRedoManager = null, connection: McpConnection = null) -> void:
	_undo_redo = undo_redo
	_connection = connection


func list_plugins(params: Dictionary) -> Dictionary:
	var addons_dir_path: String = params.get("addons_dir", "res://addons")
	if not addons_dir_path.begins_with("res://"):
		addons_dir_path = "res://" + addons_dir_path

	var dir := DirAccess.open(addons_dir_path)
	if dir == null:
		return {"success": true, "plugins": []}

	var enabled_plugins: PackedStringArray = PackedStringArray()
	if ProjectSettings.has_setting("editor_plugins/enabled"):
		enabled_plugins = ProjectSettings.get_setting("editor_plugins/enabled")

	var plugins: Array = []
	dir.list_dir_begin()
	var item := dir.get_next()
	while not item.is_empty():
		if dir.current_is_dir() and not item.begins_with("."):
			var cfg_path := addons_dir_path.path_join(item).path_join("plugin.cfg")
			if FileAccess.file_exists(cfg_path):
				var cfg := ConfigFile.new()
				var err := cfg.load(cfg_path)
				if err == OK:
					var p_name: String = cfg.get_value("plugin", "name", item)
					var p_desc: String = cfg.get_value("plugin", "description", "")
					var p_auth: String = cfg.get_value("plugin", "author", "")
					var p_ver: String = cfg.get_value("plugin", "version", "1.0.0")
					var p_script: String = cfg.get_value("plugin", "script", "plugin.gd")
					var is_enabled := false
					for ep in enabled_plugins:
						if ep.ends_with(item) or ep.ends_with(item + "/plugin.cfg"):
							is_enabled = true
							break

					if Engine.has_singleton("EditorInterface"):
						var ei := Engine.get_singleton("EditorInterface")
						if ei.has_method("is_plugin_enabled"):
							is_enabled = ei.is_plugin_enabled(item)

					plugins.append({
						"id": item,
						"name": p_name,
						"description": p_desc,
						"author": p_auth,
						"version": p_ver,
						"script": p_script,
						"config_path": cfg_path,
						"enabled": is_enabled
					})
		item = dir.get_next()
	dir.list_dir_end()

	return {
		"success": true,
		"addons_path": addons_dir_path,
		"count": plugins.size(),
		"plugins": plugins
	}


func set_plugin_enabled(params: Dictionary) -> Dictionary:
	var plugin_id: String = params.get("plugin_name", "")
	if plugin_id.is_empty():
		plugin_id = params.get("plugin_id", "")
	if plugin_id.is_empty():
		return {"error": "plugin_name or plugin_id is required", "code": ErrorCodes.INVALID_PARAMS}

	var enabled: bool = bool(params.get("enabled", true))

	if Engine.has_singleton("EditorInterface"):
		var ei := Engine.get_singleton("EditorInterface")
		if ei.has_method("set_plugin_enabled"):
			ei.set_plugin_enabled(plugin_id, enabled)

	# Also update ProjectSettings
	var setting_key := "editor_plugins/enabled"
	var current: PackedStringArray = PackedStringArray()
	if ProjectSettings.has_setting(setting_key):
		current = ProjectSettings.get_setting(setting_key)

	var plugin_subpath := "res://addons/" + plugin_id + "/plugin.cfg"
	var updated := false
	var new_arr: PackedStringArray = PackedStringArray()
	for p in current:
		if p == plugin_subpath or p == plugin_id or p.ends_with("/" + plugin_id + "/plugin.cfg"):
			continue
		new_arr.append(p)

	if enabled:
		new_arr.append(plugin_subpath)
		updated = true
	else:
		updated = (new_arr.size() != current.size())

	ProjectSettings.set_setting(setting_key, new_arr)
	ProjectSettings.save()

	return {
		"success": true,
		"plugin_id": plugin_id,
		"enabled": enabled,
		"settings_updated": updated
	}


func scaffold_plugin(params: Dictionary) -> Dictionary:
	var plugin_id: String = params.get("plugin_id", "")
	if plugin_id.is_empty():
		plugin_id = "my_custom_addon"

	var p_name: String = params.get("plugin_name", "My Custom Addon")
	var p_desc: String = params.get("description", "A custom Godot EditorPlugin")
	var p_auth: String = params.get("author", "Developer")
	var p_ver: String = params.get("version", "1.0.0")
	var with_dock: bool = params.get("with_dock", true)

	var base_dir := "res://addons/" + plugin_id
	var dir := DirAccess.open("res://")
	if not dir.dir_exists(base_dir):
		dir.make_dir_recursive(base_dir)

	var cfg_content := '[plugin]\n\nname="%s"\ndescription="%s"\nauthor="%s"\nversion="%s"\nscript="plugin.gd"\n' % [
		p_name, p_desc, p_auth, p_ver
	]
	var cfg_file := FileAccess.open(base_dir.path_join("plugin.cfg"), FileAccess.WRITE)
	if cfg_file != null:
		cfg_file.store_string(cfg_content)
		cfg_file.close()

	var script_content := ""
	if with_dock:
		script_content = "@tool\nextends EditorPlugin\n\nvar _dock: Control\n\nfunc _enter_tree() -> void:\n\t_dock = preload(\"res://addons/%s/dock.tscn\").instantiate()\n\tadd_control_to_dock(DOCK_SLOT_RIGHT_UL, _dock)\n\nfunc _exit_tree() -> void:\n\tif _dock != null:\n\t\tremove_control_from_docks(_dock)\n\t\t_dock.queue_free()\n" % plugin_id

		var dock_tscn := '[gd_scene format=3 uid="uid://dock_%s"]\n\n[node name="CustomDock" type="VBoxContainer"]\nanchors_preset = 15\nanchor_right = 1.0\nanchor_bottom = 1.0\ngrow_horizontal = 2\ngrow_vertical = 2\n\n[node name="Label" type="Label" parent="."]\nlayout_mode = 2\ntext = "%s Active"\n' % [plugin_id, p_name]
		var dock_file := FileAccess.open(base_dir.path_join("dock.tscn"), FileAccess.WRITE)
		if dock_file != null:
			dock_file.store_string(dock_tscn)
			dock_file.close()
	else:
		script_content = "@tool\nextends EditorPlugin\n\nfunc _enter_tree() -> void:\n\tpass\n\nfunc _exit_tree() -> void:\n\tpass\n"

	var script_file := FileAccess.open(base_dir.path_join("plugin.gd"), FileAccess.WRITE)
	if script_file != null:
		script_file.store_string(script_content)
		script_file.close()

	return {
		"success": true,
		"plugin_id": plugin_id,
		"plugin_path": base_dir,
		"with_dock": with_dock
	}
