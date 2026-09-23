@tool
extends McpTestSuite


func suite_name() -> String:
	return "open_world"


func test_main_scene_exists() -> void:
	assert_true(ResourceLoader.exists("res://scenes/open_world.tscn"))


func test_main_scene_is_packed_scene() -> void:
	assert_true(load("res://scenes/open_world.tscn") is PackedScene)


func test_main_scene_instantiates_as_2d() -> void:
	var scene: Node = (load("res://scenes/open_world.tscn") as PackedScene).instantiate()
	track(scene)
	assert_true(scene is Node2D)


func test_player_node_is_character_body() -> void:
	var scene: Node = (load("res://scenes/open_world.tscn") as PackedScene).instantiate()
	track(scene)
	assert_true(scene.get_node("Player") is CharacterBody2D)


func test_player_has_camera() -> void:
	var scene: Node = (load("res://scenes/open_world.tscn") as PackedScene).instantiate()
	track(scene)
	assert_true(scene.get_node("Player/Camera2D") is Camera2D)


func test_player_has_collision_shape() -> void:
	var scene: Node = (load("res://scenes/open_world.tscn") as PackedScene).instantiate()
	track(scene)
	assert_true(scene.get_node("Player/CollisionShape2D") is CollisionShape2D)


func test_world_script_has_ready_beacon() -> void:
	var source := FileAccess.get_file_as_string("res://scripts/world.gd")
	assert_true(source.contains("OPEN_WORLD_2D_READY"))


func test_capture_scene_exists() -> void:
	assert_true(ResourceLoader.exists("res://scenes/capture_smoke.tscn"))
