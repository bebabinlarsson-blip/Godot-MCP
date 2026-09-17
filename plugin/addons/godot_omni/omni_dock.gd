@tool
class_name OmniDock
extends VBoxContainer

## Godot Omni Editor Control Panel Dock
## Displays server status, 1,763 canonical operations, reflection metrics,
## and quick diagnostics for AI agents and developers.

var status_label: Label
var stats_label: Label
var eval_input: LineEdit
var eval_output: RichTextLabel


func _ready() -> void:
	custom_minimum_size = Vector2(300, 200)
	_build_ui()


func _build_ui() -> void:
	# Clear existing children
	for child in get_children():
		child.queue_free()

	# Header
	var header := HBoxContainer.new()
	var title := Label.new()
	title.text = "Godot Omni AI MCP"
	title.add_theme_font_size_override("font_size", 16)
	header.add_child(title)

	var version_badge := Label.new()
	var engine_info: Dictionary = Engine.get_version_info()
	var engine_str: String = str(engine_info.get("string", "4.x"))
	version_badge.text = "v5.0.0 (Godot %s)" % engine_str
	version_badge.modulate = Color(0.4, 0.8, 1.0)
	header.add_child(version_badge)
	add_child(header)

	add_child(HSeparator.new())

	# Status Section
	var status_box := HBoxContainer.new()
	var dot := Label.new()
	dot.text = "●"
	dot.modulate = Color(0.2, 1.0, 0.4)
	status_box.add_child(dot)

	status_label = Label.new()
	status_label.text = "Server Bridge: Listening on port 9500"
	status_box.add_child(status_label)
	add_child(status_box)

	# Stats Section
	stats_label = Label.new()
	stats_label.text = "Canonical Operations: 1,776  |  Domains: 59\nUniversal Reflection: Active  |  UI Automation: Active"
	stats_label.modulate = Color(0.85, 0.85, 0.85)
	add_child(stats_label)

	add_child(HSeparator.new())

	# Quick AI Eval Test Box
	var eval_title := Label.new()
	eval_title.text = "Quick GDScript Eval (AI Omnipotence Test):"
	add_child(eval_title)

	var eval_box := HBoxContainer.new()
	eval_input = LineEdit.new()
	eval_input.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	eval_input.placeholder_text = "e.g. Engine.get_process_frames() or 2 + 2"
	eval_input.text = "EditorInterface.get_editor_settings().get_setting('interface/editor/main_font_size')"
	eval_box.add_child(eval_input)

	var eval_btn := Button.new()
	eval_btn.text = "Evaluate"
	eval_btn.pressed.connect(_on_eval_pressed)
	eval_box.add_child(eval_btn)
	add_child(eval_box)

	eval_output = RichTextLabel.new()
	eval_output.custom_minimum_size = Vector2(0, 60)
	eval_output.scroll_active = true
	eval_output.bbcode_enabled = true
	eval_output.text = "[color=#888888]Result will appear here...[/color]"
	add_child(eval_output)


func _on_eval_pressed() -> void:
	var code := eval_input.text.strip_edges()
	if code.is_empty():
		return

	var expr := Expression.new()
	var err := expr.parse(code)
	if err == OK:
		var res = expr.execute([], EditorInterface.get_base_control())
		if not expr.has_execute_failed():
			eval_output.text = "[color=#44ff88]Result:[/color] " + str(res) + " [color=#888888](" + type_string(typeof(res)) + ")[/color]"
			return

	# Block execution fallback
	var script := GDScript.new()
	script.source_code = "@tool\nextends RefCounted\nfunc run():\n\treturn (" + code + ")\n"
	if script.reload() == OK:
		var inst = script.new()
		var res = inst.run()
		eval_output.text = "[color=#44ff88]Result (Script):[/color] " + str(res) + " [color=#888888](" + type_string(typeof(res)) + ")[/color]"
	else:
		eval_output.text = "[color=#ff4444]Error evaluating expression.[/color]"
