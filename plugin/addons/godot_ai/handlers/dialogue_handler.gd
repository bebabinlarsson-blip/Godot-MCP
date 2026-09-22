@tool
extends "res://addons/godot_ai/handlers/command_handler.gd"

const ErrorCodes := preload("res://addons/godot_ai/utils/error_codes.gd")

var _undo_redo: EditorUndoRedoManager
var _connection


func _init(undo_redo: EditorUndoRedoManager, connection = null) -> void:
	_undo_redo = undo_redo
	_connection = connection


func scaffold_system(params: Dictionary) -> Dictionary:
	var name: String = params.get("name", "DialogueManager")
	var script_path: String = params.get("script_path", "res://scripts/dialogue_manager.gd")
	var scene_path: String = params.get("scene_path", "res://scenes/dialogue_box.tscn")
	var register_autoload: bool = bool(params.get("register_autoload", true))
	var typewriter_speed: float = float(params.get("typewriter_speed", 0.03))

	var script_err = McpPathValidator.path_error(script_path, "script_path")
	if script_err != null:
		return script_err
	var scene_err = McpPathValidator.path_error(scene_path, "scene_path")
	if scene_err != null:
		return scene_err

	# 1. Ensure directories exist
	var script_dir := script_path.get_base_dir()
	if not DirAccess.dir_exists_absolute(script_dir):
		DirAccess.make_dir_recursive_absolute(script_dir)

	var scene_dir := scene_path.get_base_dir()
	if not DirAccess.dir_exists_absolute(scene_dir):
		DirAccess.make_dir_recursive_absolute(scene_dir)

	# 2. Generate DialogueManager script
	var manager_code := """extends Node

signal dialogue_started(dialogue_id: String)
signal line_displayed(speaker: String, text: String)
signal choices_presented(choices: Array)
signal choice_selected(index: int, text: String)
signal dialogue_ended(dialogue_id: String)

var current_dialogue: Dictionary = {}
var current_node_id: String = ""
var is_active: bool = false
var dialogue_box: CanvasLayer = null

func _ready() -> void:
	_setup_dialogue_box()

func _setup_dialogue_box() -> void:
	if ResourceLoader.exists("%s"):
		var scene: PackedScene = load("%s")
		if scene:
			dialogue_box = scene.instantiate()
			add_child(dialogue_box)
			if dialogue_box.has_signal("choice_clicked"):
				dialogue_box.connect("choice_clicked", Callable(self, "_on_choice_clicked"))
			if dialogue_box.has_signal("advance_requested"):
				dialogue_box.connect("advance_requested", Callable(self, "_on_advance_requested"))

func start_dialogue(dialogue_data: Variant, start_node: String = "start") -> void:
	if dialogue_data is String:
		if FileAccess.file_exists(dialogue_data):
			var file := FileAccess.open(dialogue_data, FileAccess.READ)
			if file:
				var json := JSON.new()
				var parse_err := json.parse(file.get_as_text())
				if parse_err == OK and json.data is Dictionary:
					current_dialogue = json.data
				file.close()
	elif dialogue_data is Dictionary:
		current_dialogue = dialogue_data
	else:
		push_error("DialogueManager: Invalid dialogue data type.")
		return

	if current_dialogue.is_empty():
		push_error("DialogueManager: Empty dialogue.")
		return

	is_active = true
	var dialogue_id: String = current_dialogue.get("id", "dialogue")
	dialogue_started.emit(dialogue_id)
	show_node(start_node)

func show_node(node_id: String) -> void:
	var nodes: Dictionary = current_dialogue.get("nodes", {})
	if not nodes.has(node_id):
		end_dialogue()
		return

	current_node_id = node_id
	var node: Dictionary = nodes[node_id]
	if node.get("is_end", false):
		end_dialogue()
		return

	var speaker: String = node.get("speaker", "")
	var text: String = node.get("text", "")
	var choices: Array = node.get("choices", [])

	line_displayed.emit(speaker, text)
	if dialogue_box and dialogue_box.has_method("display_line"):
		dialogue_box.display_line(speaker, text, choices)

	if not choices.is_empty():
		choices_presented.emit(choices)

func advance() -> void:
	if not is_active:
		return
	var nodes: Dictionary = current_dialogue.get("nodes", {})
	var node: Dictionary = nodes.get(current_node_id, {})
	var choices: Array = node.get("choices", [])
	if not choices.is_empty():
		return # Must select a choice

	var next_id: String = node.get("next", "")
	if next_id.is_empty() or next_id == "end":
		end_dialogue()
	else:
		show_node(next_id)

func select_choice(index: int) -> void:
	if not is_active:
		return
	var nodes: Dictionary = current_dialogue.get("nodes", {})
	var node: Dictionary = nodes.get(current_node_id, {})
	var choices: Array = node.get("choices", [])
	if index >= 0 and index < choices.size():
		var choice: Dictionary = choices[index]
		var text: String = choice.get("text", "")
		var next_id: String = choice.get("next", "")
		choice_selected.emit(index, text)
		if next_id.is_empty() or next_id == "end":
			end_dialogue()
		else:
			show_node(next_id)

func end_dialogue() -> void:
	if not is_active:
		return
	is_active = false
	var dialogue_id: String = current_dialogue.get("id", "")
	if dialogue_box and dialogue_box.has_method("hide_box"):
		dialogue_box.hide_box()
	dialogue_ended.emit(dialogue_id)

func _on_advance_requested() -> void:
	advance()

func _on_choice_clicked(index: int) -> void:
	select_choice(index)
""" % [scene_path, scene_path]

	var file := FileAccess.open(script_path, FileAccess.WRITE)
	if file == null:
		return ErrorCodes.make(ErrorCodes.INTERNAL_ERROR, "Failed to create dialogue manager script at: %s" % script_path)
	file.store_string(manager_code)
	file.close()

	# 3. Generate DialogueBox Scene
	var box_root := CanvasLayer.new()
	box_root.name = "DialogueBox"
	box_root.layer = 100

	var margin := MarginContainer.new()
	margin.name = "MarginContainer"
	margin.anchor_left = 0.05
	margin.anchor_right = 0.95
	margin.anchor_top = 0.70
	margin.anchor_bottom = 0.95
	margin.offset_left = 0
	margin.offset_right = 0
	margin.offset_top = 0
	margin.offset_bottom = 0
	box_root.add_child(margin)

	var panel := PanelContainer.new()
	panel.name = "PanelContainer"
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(0.1, 0.12, 0.16, 0.95)
	sb.border_color = Color(0.3, 0.5, 0.8, 1.0)
	sb.border_width_left = 2
	sb.border_width_right = 2
	sb.border_width_top = 2
	sb.border_width_bottom = 2
	sb.corner_radius_top_left = 8
	sb.corner_radius_top_right = 8
	sb.corner_radius_bottom_left = 8
	sb.corner_radius_bottom_right = 8
	sb.content_margin_left = 16.0
	sb.content_margin_right = 16.0
	sb.content_margin_top = 12.0
	sb.content_margin_bottom = 12.0
	panel.add_theme_stylebox_override("panel", sb)
	margin.add_child(panel)

	var vbox := VBoxContainer.new()
	vbox.name = "VBoxContainer"
	vbox.add_theme_constant_override("separation", 8)
	panel.add_child(vbox)

	var speaker_lbl := Label.new()
	speaker_lbl.name = "SpeakerLabel"
	speaker_lbl.text = "Speaker"
	speaker_lbl.add_theme_color_override("font_color", Color(1.0, 0.85, 0.3))
	speaker_lbl.add_theme_font_size_override("font_size", 16)
	vbox.add_child(speaker_lbl)

	var text_lbl := RichTextLabel.new()
	text_lbl.name = "TextLabel"
	text_lbl.bbcode_enabled = true
	text_lbl.text = "Dialogue text appears here..."
	text_lbl.size_flags_vertical = Control.SIZE_EXPAND_FILL
	text_lbl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	vbox.add_child(text_lbl)

	var choices_vbox := VBoxContainer.new()
	choices_vbox.name = "ChoicesContainer"
	choices_vbox.add_theme_constant_override("separation", 4)
	vbox.add_child(choices_vbox)

	var indicator := Label.new()
	indicator.name = "ContinueIndicator"
	indicator.text = "[Click or Space to Continue]"
	indicator.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	indicator.add_theme_font_size_override("font_size", 11)
	indicator.add_theme_color_override("font_color", Color(0.7, 0.7, 0.7, 0.8))
	vbox.add_child(indicator)

	# DialogueBox UI Script
	var box_script := GDScript.new()
	box_script.source_code = """extends CanvasLayer

signal advance_requested
signal choice_clicked(index: int)

@export var typewriter_speed: float = %s

@onready var speaker_label: Label = $MarginContainer/PanelContainer/VBoxContainer/SpeakerLabel
@onready var text_label: RichTextLabel = $MarginContainer/PanelContainer/VBoxContainer/TextLabel
@onready var choices_container: VBoxContainer = $MarginContainer/PanelContainer/VBoxContainer/ChoicesContainer
@onready var continue_indicator: Label = $MarginContainer/PanelContainer/VBoxContainer/ContinueIndicator

var _tween: Tween
var _is_typing: bool = false
var _full_text: String = ""

func _ready() -> void:
	visible = false

func _unhandled_input(event: InputEvent) -> void:
	if not visible:
		return
	if event.is_action_pressed("ui_accept") or (event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT and event.pressed):
		if _is_typing:
			# Skip typewriter to end of line
			if _tween and _tween.is_running():
				_tween.kill()
			text_label.visible_characters = -1
			_is_typing = false
			continue_indicator.visible = choices_container.get_child_count() == 0
		elif choices_container.get_child_count() == 0:
			advance_requested.emit()

func display_line(speaker: String, text: String, choices: Array = []) -> void:
	visible = true
	speaker_label.text = speaker
	speaker_label.visible = not speaker.is_empty()
	_full_text = text
	text_label.text = text
	text_label.visible_characters = 0
	continue_indicator.visible = false

	# Clear previous choice buttons
	for child in choices_container.get_children():
		child.queue_free()

	_is_typing = true
	var char_count: int = text.length()
	var duration: float = char_count * typewriter_speed

	if _tween and _tween.is_running():
		_tween.kill()
	_tween = create_tween()
	_tween.tween_property(text_label, "visible_characters", char_count, duration)
	_tween.finished.connect(func():
		_is_typing = false
		_render_choices(choices)
	)

func _render_choices(choices: Array) -> void:
	if choices.is_empty():
		continue_indicator.visible = true
		return
	continue_indicator.visible = false
	for i in range(choices.size()):
		var choice: Dictionary = choices[i]
		var btn := Button.new()
		btn.text = choice.get("text", "Option " + str(i + 1))
		btn.alignment = HORIZONTAL_ALIGNMENT_LEFT
		var idx := i
		btn.pressed.connect(func():
			choice_clicked.emit(idx)
		)
		choices_container.add_child(btn)

func hide_box() -> void:
	visible = false
	if _tween and _tween.is_running():
		_tween.kill()
""" % [str(typewriter_speed)]

	box_root.set_script(box_script)

	var packed := PackedScene.new()
	var pack_err := packed.pack(box_root)
	if pack_err == OK:
		ResourceSaver.save(packed, scene_path)
	box_root.free()

	# 4. Register Autoload if requested
	var autoload_ok := false
	if register_autoload:
		var key := "autoload/%s" % name
		ProjectSettings.set_setting(key, "*" + script_path)
		ProjectSettings.set_initial_value(key, "")
		ProjectSettings.set_as_basic(key, true)
		var p_err := ProjectSettings.save()
		autoload_ok = (p_err == OK)

	var efs := EditorInterface.get_resource_filesystem()
	if efs != null:
		efs.update_file(script_path)
		efs.update_file(scene_path)

	return {
		"data": {
			"name": name,
			"script_path": script_path,
			"scene_path": scene_path,
			"register_autoload": register_autoload,
			"autoload_saved": autoload_ok,
			"typewriter_speed": typewriter_speed,
		}
	}


func create_dialogue(params: Dictionary) -> Dictionary:
	var path: String = params.get("path", "res://dialogues/dialogue.json")
	var dialogue_id: String = params.get("dialogue_id", "intro_conversation")
	var custom_nodes: Variant = params.get("nodes", null)
	var overwrite: bool = bool(params.get("overwrite", false))

	var path_err = McpPathValidator.path_error(path, "path")
	if path_err != null:
		return path_err

	if FileAccess.file_exists(path) and not overwrite:
		return ErrorCodes.make(ErrorCodes.INVALID_PARAMS, "Dialogue file already exists at: %s (set overwrite=true)" % path)

	var base_dir := path.get_base_dir()
	if not DirAccess.dir_exists_absolute(base_dir):
		DirAccess.make_dir_recursive_absolute(base_dir)

	var nodes: Dictionary = {}
	if custom_nodes is Dictionary and not custom_nodes.is_empty():
		nodes = custom_nodes
	else:
		nodes = {
			"start": {
				"speaker": "Guide",
				"text": "Greetings adventurer! Are you prepared to face the trial ahead?",
				"choices": [
					{"text": "I was born ready.", "next": "brave"},
					{"text": "Tell me what awaits me first.", "next": "curious"}
				]
			},
			"brave": {
				"speaker": "Guide",
				"text": "Splendid! Take courage and step into the dungeon.",
				"next": "end"
			},
			"curious": {
				"speaker": "Guide",
				"text": "Dark beasts lurk in the ruins, but ancient treasures reward the bold.",
				"choices": [
					{"text": "Then I will brave the dangers!", "next": "brave"}
				]
			},
			"end": {
				"is_end": true
			}
		}

	var data := {
		"id": dialogue_id,
		"nodes": nodes
	}

	var json_str := JSON.stringify(data, "\t")
	var file := FileAccess.open(path, FileAccess.WRITE)
	if file == null:
		return ErrorCodes.make(ErrorCodes.INTERNAL_ERROR, "Failed to write dialogue file to: %s" % path)
	file.store_string(json_str)
	file.close()

	var efs := EditorInterface.get_resource_filesystem()
	if efs != null:
		efs.update_file(path)

	return {
		"data": {
			"path": path,
			"dialogue_id": dialogue_id,
			"node_count": nodes.size(),
			"overwrite": overwrite,
		}
	}
