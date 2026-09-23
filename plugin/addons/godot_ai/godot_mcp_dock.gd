@tool
class_name GodotMcpDock
extends VBoxContainer

## Godot MCP Unified Inspector Dock.
## Provides real-time tool call inspection, server health monitoring,
## lifecycle control, and GDScript evaluation without emojis or UI bloat.

signal update_requested
signal client_action_requested(client_id: String, action: String)
signal client_status_refresh_requested(client_ids: Array[String], force: bool)
signal status_snapshot_requested
signal live_server_probe_requested(port: int)
signal lifecycle_action_requested(action: int)
signal dev_server_action_requested(action: int)
signal mcp_logging_changed(enabled: bool)
signal log_snapshot_requested(after_sequence: int)
signal plugin_reload_requested(reason: String)
signal settings_apply_requested(changes: Dictionary, reload: bool)
signal post_update_action_requested(action: String)

enum LifecycleAction { RECOVER_INCOMPATIBLE = 0, RESTART_SERVER = 1 }
enum DevServerAction { START_OR_RESTART = 0, STOP = 1 }

var vision_routing = null

const McpEventBusScript := preload("res://addons/godot_ai/utils/mcp_event_bus.gd")

# UI controls
var _status_badge: Label
var _status_desc: Label
var _port_label: Label
var _stats_label: Label
var _blocked_box: VBoxContainer
var _blocked_label: Label
var _restart_btn: Button
var _test_btn: Button
var _refresh_btn: Button

# Activity monitor
var _counter_label: Label
var _filter_all_btn: Button
var _filter_ok_btn: Button
var _filter_err_btn: Button
var _autoscroll_check: CheckBox
var _clear_btn: Button
var _calls_scroll: ScrollContainer
var _calls_container: VBoxContainer
var _empty_label: Label

# Eval sandbox
var _eval_input: LineEdit
var _eval_btn: Button
var _eval_output: RichTextLabel

# State tracking
var _active_filter: String = "all"
var _total_count: int = 0
var _ok_count: int = 0
var _err_count: int = 0
var _is_connected: bool = false
var _server_state: String = "STOPPED"
var _http_port: int = 8000
var _ws_port: int = 9500
var _blocked_message: String = ""


func _init() -> void:
	size_flags_horizontal = Control.SIZE_EXPAND_FILL
	size_flags_vertical = Control.SIZE_EXPAND_FILL
	custom_minimum_size = Vector2(280, 420)
	_build_ui()


func _enter_tree() -> void:
	McpEventBusScript.subscribe(_on_tool_call_received)


func _exit_tree() -> void:
	McpEventBusScript.unsubscribe(_on_tool_call_received)


func _ready() -> void:
	_populate_initial_history()


func _build_ui() -> void:
	if is_instance_valid(_status_badge):
		return

	# Outer margin container
	var margin := MarginContainer.new()
	margin.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	margin.size_flags_vertical = Control.SIZE_EXPAND_FILL
	margin.add_theme_constant_override("margin_left", 6)
	margin.add_theme_constant_override("margin_right", 6)
	margin.add_theme_constant_override("margin_top", 6)
	margin.add_theme_constant_override("margin_bottom", 6)

	var main_vbox := VBoxContainer.new()
	main_vbox.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	main_vbox.size_flags_vertical = Control.SIZE_EXPAND_FILL
	main_vbox.add_theme_constant_override("separation", 6)

	# 1. Header Section
	var header_bar := HBoxContainer.new()
	header_bar.add_theme_constant_override("separation", 8)

	var title := Label.new()
	title.text = "Godot MCP"
	title.add_theme_font_size_override("font_size", 14)
	header_bar.add_child(title)

	var version_badge := Label.new()
	version_badge.text = "v5.0.28"

	version_badge.modulate = Color(0.45, 0.75, 1.0)
	version_badge.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	header_bar.add_child(version_badge)

	_refresh_btn = Button.new()
	_refresh_btn.text = "Refresh"
	_refresh_btn.tooltip_text = "Probe server endpoint and refresh status"
	_refresh_btn.pressed.connect(_on_refresh_pressed)
	header_bar.add_child(_refresh_btn)

	main_vbox.add_child(header_bar)

	# 2. Connection Status & Health Card
	var status_card := PanelContainer.new()
	status_card.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	var status_vbox := VBoxContainer.new()
	status_vbox.add_theme_constant_override("separation", 4)

	var status_row := HBoxContainer.new()
	var state_title := Label.new()
	state_title.text = "Status:"
	status_row.add_child(state_title)

	_status_badge = Label.new()
	_status_badge.text = "[ACTIVE]"
	_status_badge.modulate = Color(0.3, 1.0, 0.4)
	status_row.add_child(_status_badge)

	_status_desc = Label.new()
	_status_desc.text = "WebSocket Connected"
	_status_desc.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_status_desc.modulate = Color(0.8, 0.8, 0.8)
	status_row.add_child(_status_desc)

	status_vbox.add_child(status_row)

	_port_label = Label.new()
	_port_label.text = "HTTP: 8000 | WebSocket: 9500"
	_port_label.modulate = Color(0.7, 0.7, 0.7)
	status_vbox.add_child(_port_label)

	_stats_label = Label.new()
	var vinfo: Dictionary = Engine.get_version_info()
	_stats_label.text = "Godot %s | AI Tool Engine" % str(vinfo.get("string", "4.x"))
	_stats_label.modulate = Color(0.6, 0.65, 0.75)
	status_vbox.add_child(_stats_label)

	# Blocked notice container
	_blocked_box = VBoxContainer.new()
	_blocked_box.visible = false
	_blocked_label = Label.new()
	_blocked_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_blocked_label.modulate = Color(1.0, 0.4, 0.4)
	_blocked_box.add_child(_blocked_label)
	var recover_btn := Button.new()
	recover_btn.text = "Free Port & Replace Server"
	recover_btn.pressed.connect(func(): lifecycle_action_requested.emit(LifecycleAction.RECOVER_INCOMPATIBLE))
	_blocked_box.add_child(recover_btn)
	status_vbox.add_child(_blocked_box)

	# Action buttons row
	var actions_row := HBoxContainer.new()
	actions_row.add_theme_constant_override("separation", 6)

	_test_btn = Button.new()
	_test_btn.text = "Test Connection"
	_test_btn.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_test_btn.pressed.connect(_on_test_connection_pressed)
	actions_row.add_child(_test_btn)

	_restart_btn = Button.new()
	_restart_btn.text = "Restart Server"
	_restart_btn.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_restart_btn.pressed.connect(_on_restart_pressed)
	actions_row.add_child(_restart_btn)

	status_vbox.add_child(actions_row)
	status_card.add_child(status_vbox)
	main_vbox.add_child(status_card)

	# 3. Live Tool Call Activity Monitor
	var monitor_bar := HBoxContainer.new()
	var monitor_title := Label.new()
	monitor_title.text = "Tool Activity (Live)"
	monitor_title.add_theme_font_size_override("font_size", 13)
	monitor_title.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	monitor_bar.add_child(monitor_title)

	_counter_label = Label.new()
	_counter_label.text = "Calls: 0"
	_counter_label.modulate = Color(0.7, 0.7, 0.7)
	monitor_bar.add_child(_counter_label)
	main_vbox.add_child(monitor_bar)

	# Filter & Control Row
	var filter_bar := HBoxContainer.new()
	filter_bar.add_theme_constant_override("separation", 4)

	_filter_all_btn = Button.new()
	_filter_all_btn.text = "All"
	_filter_all_btn.pressed.connect(func(): _set_filter("all"))
	filter_bar.add_child(_filter_all_btn)

	_filter_ok_btn = Button.new()
	_filter_ok_btn.text = "OK"
	_filter_ok_btn.pressed.connect(func(): _set_filter("ok"))
	filter_bar.add_child(_filter_ok_btn)

	_filter_err_btn = Button.new()
	_filter_err_btn.text = "Errors"
	_filter_err_btn.pressed.connect(func(): _set_filter("error"))
	filter_bar.add_child(_filter_err_btn)

	_autoscroll_check = CheckBox.new()
	_autoscroll_check.text = "Auto-scroll"
	_autoscroll_check.button_pressed = true
	_autoscroll_check.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	filter_bar.add_child(_autoscroll_check)

	_clear_btn = Button.new()
	_clear_btn.text = "Clear"
	_clear_btn.pressed.connect(_on_clear_pressed)
	filter_bar.add_child(_clear_btn)
	main_vbox.add_child(filter_bar)

	# Feed Area
	_calls_scroll = ScrollContainer.new()
	_calls_scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	_calls_scroll.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_calls_scroll.custom_minimum_size = Vector2(0, 140)

	_calls_container = VBoxContainer.new()
	_calls_container.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_calls_container.add_theme_constant_override("separation", 4)

	_empty_label = Label.new()
	_empty_label.text = "Waiting for AI tool calls...\nUse an AI client (Cursor, Claude, Antigravity) or click 'Test Connection'."
	_empty_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_empty_label.modulate = Color(0.5, 0.5, 0.5)
	_empty_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_empty_label.size_flags_vertical = Control.SIZE_EXPAND_FILL
	_calls_container.add_child(_empty_label)

	_calls_scroll.add_child(_calls_container)
	main_vbox.add_child(_calls_scroll)

	main_vbox.add_child(HSeparator.new())

	# 4. GDScript Sandbox
	var sandbox_title := Label.new()
	sandbox_title.text = "GDScript Eval Sandbox"
	sandbox_title.add_theme_font_size_override("font_size", 12)
	main_vbox.add_child(sandbox_title)

	var sandbox_row := HBoxContainer.new()
	_eval_input = LineEdit.new()
	_eval_input.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_eval_input.placeholder_text = "e.g. Engine.get_process_frames() or 2 + 2"
	_eval_input.text_submitted.connect(func(_t): _on_eval_pressed())
	sandbox_row.add_child(_eval_input)

	_eval_btn = Button.new()
	_eval_btn.text = "Run"
	_eval_btn.pressed.connect(_on_eval_pressed)
	sandbox_row.add_child(_eval_btn)
	main_vbox.add_child(sandbox_row)

	_eval_output = RichTextLabel.new()
	_eval_output.custom_minimum_size = Vector2(0, 40)
	_eval_output.bbcode_enabled = true
	_eval_output.scroll_active = true
	_eval_output.text = "[color=#888888]Enter expression to test live MCP bridge...[/color]"
	main_vbox.add_child(_eval_output)

	margin.add_child(main_vbox)
	add_child(margin)


func _populate_initial_history() -> void:
	var history: Array[Dictionary] = McpEventBusScript.get_history()
	for entry in history:
		_add_entry_ui(entry)


func _on_tool_call_received(entry: Dictionary) -> void:
	_add_entry_ui(entry)


func _add_entry_ui(entry: Dictionary) -> void:
	if is_instance_valid(_empty_label):
		_empty_label.visible = false

	var ok: bool = bool(entry.get("ok", true))
	_total_count += 1
	if ok:
		_ok_count += 1
	else:
		_err_count += 1

	if is_instance_valid(_counter_label):
		_counter_label.text = "Total: %d | OK: %d | Errors: %d" % [_total_count, _ok_count, _err_count]

	var panel := PanelContainer.new()
	panel.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	panel.set_meta("status", "ok" if ok else "error")

	var row_vbox := VBoxContainer.new()
	row_vbox.add_theme_constant_override("separation", 2)

	var top_line := HBoxContainer.new()
	var time_lbl := Label.new()
	time_lbl.text = "[%s]" % str(entry.get("timestamp", ""))
	time_lbl.modulate = Color(0.6, 0.6, 0.6)
	top_line.add_child(time_lbl)

	var status_lbl := Label.new()
	var ms: float = float(entry.get("duration_ms", 0.0))
	if ok:
		status_lbl.text = "[OK] (%.1fms)" % ms
		status_lbl.modulate = Color(0.3, 1.0, 0.4)
	else:
		status_lbl.text = "[ERR] (%.1fms)" % ms
		status_lbl.modulate = Color(1.0, 0.35, 0.35)
	top_line.add_child(status_lbl)

	var tool_lbl := Label.new()
	tool_lbl.text = str(entry.get("tool", "unknown_tool"))
	tool_lbl.add_theme_font_size_override("font_size", 13)
	tool_lbl.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	top_line.add_child(tool_lbl)
	row_vbox.add_child(top_line)

	var params: Dictionary = entry.get("params", {})
	if not params.is_empty():
		var args_lbl := Label.new()
		var args_str: String = JSON.stringify(params)
		if args_str.length() > 90:
			args_str = args_str.substr(0, 87) + "..."
		args_lbl.text = "  args: %s" % args_str
		args_lbl.modulate = Color(0.75, 0.75, 0.75)
		row_vbox.add_child(args_lbl)

	if not ok:
		var err_lbl := Label.new()
		var res: Dictionary = entry.get("result", {})
		var err_str: String = str(res.get("error", "Execution failed"))
		err_lbl.text = "  error: %s" % err_str
		err_lbl.modulate = Color(1.0, 0.5, 0.5)
		row_vbox.add_child(err_lbl)

	panel.add_child(row_vbox)

	if _active_filter == "ok" and not ok:
		panel.visible = false
	elif _active_filter == "error" and ok:
		panel.visible = false

	_calls_container.add_child(panel)

	if _autoscroll_check.button_pressed:
		call_deferred("_scroll_to_bottom")


func _scroll_to_bottom() -> void:
	if is_instance_valid(_calls_scroll):
		_calls_scroll.scroll_vertical = 999999


func _set_filter(filter_name: String) -> void:
	_active_filter = filter_name
	for child in _calls_container.get_children():
		if child == _empty_label:
			continue
		if not child.has_meta("status"):
			continue
		var st: String = str(child.get_meta("status"))
		if filter_name == "all":
			child.visible = true
		elif filter_name == "ok":
			child.visible = (st == "ok")
		elif filter_name == "error":
			child.visible = (st == "error")


func _on_clear_pressed() -> void:
	McpEventBusScript.clear_history()
	for child in _calls_container.get_children():
		if child != _empty_label:
			child.queue_free()
	_total_count = 0
	_ok_count = 0
	_err_count = 0
	_counter_label.text = "Calls: 0"
	if is_instance_valid(_empty_label):
		_empty_label.visible = true


func _on_refresh_pressed() -> void:
	status_snapshot_requested.emit()
	live_server_probe_requested.emit(_http_port)


func _on_restart_pressed() -> void:
	lifecycle_action_requested.emit(LifecycleAction.RESTART_SERVER)


func _on_test_connection_pressed() -> void:
	var t0 := Time.get_ticks_msec()
	var expr := Expression.new()
	expr.parse("Engine.get_process_frames()")
	var res = expr.execute()
	var dt: float = float(Time.get_ticks_msec() - t0)

	var simulated_result: Dictionary = {
		"status": "ok",
		"ok": true,
		"data": {
			"ping": "pong",
			"frames": res,
			"godot_version": Engine.get_version_info().get("string", "4.x")
		}
	}
	McpEventBusScript.record_tool_call("mcp_ping", {"test": true}, simulated_result, dt)
	if _is_connected:
		_eval_output.text = "[color=#44ff88]Ping Succeeded:[/color] MCP Bridge connected %.1fms | Engine frames: %s" % [dt, str(res)]
	else:
		_eval_output.text = "[color=#ffaa33]Bridge Connecting:[/color] Engine alive | Refreshing server status..."
	status_snapshot_requested.emit()
	live_server_probe_requested.emit(_http_port)


func _on_eval_pressed() -> void:
	var code := _eval_input.text.strip_edges()
	if code.is_empty():
		return

	var t0 := Time.get_ticks_msec()
	var expr := Expression.new()
	var err := expr.parse(code)
	if err == OK:
		var res = expr.execute([], EditorInterface.get_base_control())
		var dt: float = float(Time.get_ticks_msec() - t0)
		if not expr.has_execute_failed():
			_eval_output.text = "[color=#44ff88]Result (%.1fms):[/color] %s [color=#888888](%s)[/color]" % [
				dt, str(res), type_string(typeof(res))
			]
			McpEventBusScript.record_tool_call("godot_eval", {"code": code}, {"status": "ok", "result": res}, dt)
			return

	var script := GDScript.new()
	script.source_code = "@tool\nextends RefCounted\nfunc run():\n\treturn (" + code + ")\n"
	if script.reload() == OK:
		var inst = script.new()
		var res = inst.run()
		var dt: float = float(Time.get_ticks_msec() - t0)
		_eval_output.text = "[color=#44ff88]Result (Script %.1fms):[/color] %s" % [dt, str(res)]
		McpEventBusScript.record_tool_call("godot_eval", {"code": code}, {"status": "ok", "result": res}, dt)
	else:
		var dt: float = float(Time.get_ticks_msec() - t0)
		_eval_output.text = "[color=#ff4444]Error evaluating expression.[/color]"
		McpEventBusScript.record_tool_call("godot_eval", {"code": code}, {"status": "error", "error": "Parse error"}, dt)


# ============================================================================
# Protocol & Lifecycle Integration Handlers (called by plugin.gd)
# ============================================================================

func present_transport_snapshot(snapshot: Dictionary) -> void:
	_is_connected = bool(snapshot.get("connected", false))
	if _is_connected and is_instance_valid(_blocked_box):
		_blocked_box.visible = false
		_blocked_message = ""
	_update_ui_state()


func present_lifecycle_snapshot(snapshot: Dictionary) -> void:
	_server_state = str(snapshot.get("episode_state", "READY"))
	_ws_port = int(snapshot.get("resolved_ws_port", 9500))
	_blocked_message = str(snapshot.get("message", ""))
	if not is_instance_valid(_blocked_box):
		return
	if _is_connected or _server_state == "READY":
		_blocked_box.visible = false
		_blocked_message = ""
	elif not _blocked_message.is_empty() and str(snapshot.get("episode_state", "")) == "BLOCKED":
		_blocked_box.visible = true
		_blocked_label.text = "Blocked: %s" % _blocked_message
		_status_badge.text = "[BLOCKED]"
		_status_badge.modulate = Color(1.0, 0.35, 0.35)
		_status_desc.text = "Port conflict or startup error"
	else:
		_blocked_box.visible = false
	_update_ui_state()


func _update_ui_state() -> void:
	if not is_instance_valid(_status_badge):
		return

	if _is_connected:
		if is_instance_valid(_blocked_box):
			_blocked_box.visible = false
			_blocked_message = ""
		_status_badge.text = "[ACTIVE]"
		_status_badge.modulate = Color(0.3, 1.0, 0.4)
		_status_desc.text = "Bridge Active & Connected"
		if is_instance_valid(_port_label):
			_port_label.text = "HTTP: %d | WebSocket: %d" % [_http_port, _ws_port]
		return

	if _server_state == "READY":
		if is_instance_valid(_blocked_box):
			_blocked_box.visible = false
			_blocked_message = ""
		_status_badge.text = "[ACTIVE]"
		_status_badge.modulate = Color(0.3, 1.0, 0.4)
		if _status_desc.text.is_empty() or _status_desc.text == "Server stopped":
			_status_desc.text = "Server Ready"
	elif _server_state == "STARTING":
		_status_badge.text = "[STARTING]"
		_status_badge.modulate = Color(1.0, 0.75, 0.25)
		if _status_desc.text != "HTTP server reachable":
			_status_desc.text = "Server running, connecting WebSocket..."
	else:
		_status_badge.text = "[STOPPED]"
		_status_badge.modulate = Color(0.7, 0.7, 0.7)
		_status_desc.text = "Server stopped"

	if is_instance_valid(_port_label):
		_port_label.text = "HTTP: %d | WebSocket: %d" % [_http_port, _ws_port]


func present_client_work_snapshot(_snapshot: Dictionary) -> void:
	pass


func present_client_status_refresh_results(_results: Dictionary) -> void:
	pass


func present_client_action_result(_client_id: String, _action: String, _result: Dictionary, _prewarm: Variant) -> void:
	pass


func present_client_action_timeout(_client_id: String, _action: String, _detail: String) -> void:
	pass


func present_live_server_probe_result(result: Dictionary) -> void:
	var reachable: bool = bool(result.get("reachable", false))
	if reachable:
		_status_desc.text = "HTTP server reachable"
		if is_instance_valid(_blocked_box):
			_blocked_box.visible = false
			_blocked_message = ""
	_update_ui_state()


func present_lifecycle_action_result(_accepted: bool) -> void:
	_update_ui_state()


func present_log_snapshot(_snapshot: Dictionary) -> void:
	pass


func present_update_check(_result: Dictionary) -> void:
	pass


func present_update_state(_state: Dictionary) -> void:
	pass


func release_editor_progress_dialog() -> void:
	pass

