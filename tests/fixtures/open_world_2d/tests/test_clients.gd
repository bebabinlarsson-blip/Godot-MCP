@tool
extends McpTestSuite


func suite_name() -> String:
	return "clients"


func test_project_enables_core_addon() -> void:
	var project := FileAccess.get_file_as_string("res://project.godot")
	assert_true(project.contains("res://addons/godot_ai/plugin.cfg"))


func test_project_enables_omni_addon() -> void:
	var project := FileAccess.get_file_as_string("res://project.godot")
	assert_true(project.contains("res://addons/godot_omni/plugin.cfg"))


func test_core_plugin_configuration_exists() -> void:
	assert_true(FileAccess.file_exists("res://addons/godot_ai/plugin.cfg"))


func test_omni_plugin_configuration_exists() -> void:
	assert_true(FileAccess.file_exists("res://addons/godot_omni/plugin.cfg"))


func test_core_exposes_session_activation() -> void:
	var source := FileAccess.get_file_as_string("res://addons/godot_ai/tool_catalog.gd")
	assert_true(source.contains("session_activate"))


func test_core_exposes_editor_state() -> void:
	var source := FileAccess.get_file_as_string("res://addons/godot_ai/tool_catalog.gd")
	assert_true(source.contains("editor_state"))


func test_core_exposes_scene_hierarchy() -> void:
	var source := FileAccess.get_file_as_string("res://addons/godot_ai/tool_catalog.gd")
	assert_true(source.contains("scene_get_hierarchy"))


func test_core_exposes_node_properties() -> void:
	var source := FileAccess.get_file_as_string("res://addons/godot_ai/tool_catalog.gd")
	assert_true(source.contains("node_get_properties"))


func test_curve_creation_tool_has_handler() -> void:
	var plugin := FileAccess.get_file_as_string("res://addons/godot_ai/plugin.gd")
	var source := FileAccess.get_file_as_string("res://addons/godot_ai/handlers/curve_handler.gd")
	assert_true(plugin.contains("curve_create_curve_1d"))
	assert_true(source.contains("func create_curve_1d("))
