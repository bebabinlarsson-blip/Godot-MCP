@tool
extends "res://addons/godot_ai/handlers/command_handler.gd"

const ErrorCodes := preload("res://addons/godot_ai/utils/error_codes.gd")

## Handles UI-specific (Control) layout helpers: anchor presets, etc.
##
## Anchors/offsets are the worst part of Control layout to set one-property-at-a-time.
## This handler wraps Godot's built-in presets (FULL_RECT, CENTER, TOP_LEFT, ...) so
## callers can set a whole layout with one command, with proper undo.

var _undo_redo: EditorUndoRedoManager


const _PRESETS := {
	"top_left": Control.PRESET_TOP_LEFT,
	"top_right": Control.PRESET_TOP_RIGHT,
	"bottom_left": Control.PRESET_BOTTOM_LEFT,
	"bottom_right": Control.PRESET_BOTTOM_RIGHT,
	"center_left": Control.PRESET_CENTER_LEFT,
	"center_top": Control.PRESET_CENTER_TOP,
	"center_right": Control.PRESET_CENTER_RIGHT,
	"center_bottom": Control.PRESET_CENTER_BOTTOM,
	"center": Control.PRESET_CENTER,
	"left_wide": Control.PRESET_LEFT_WIDE,
	"top_wide": Control.PRESET_TOP_WIDE,
	"right_wide": Control.PRESET_RIGHT_WIDE,
	"bottom_wide": Control.PRESET_BOTTOM_WIDE,
	"vcenter_wide": Control.PRESET_VCENTER_WIDE,
	"hcenter_wide": Control.PRESET_HCENTER_WIDE,
	"full_rect": Control.PRESET_FULL_RECT,
}

const _RESIZE_MODES := {
	"minsize": Control.PRESET_MODE_MINSIZE,
	"keep_width": Control.PRESET_MODE_KEEP_WIDTH,
	"keep_height": Control.PRESET_MODE_KEEP_HEIGHT,
	"keep_size": Control.PRESET_MODE_KEEP_SIZE,
}

const _ANCHOR_OFFSET_PROPS := [
	"anchor_left", "anchor_top", "anchor_right", "anchor_bottom",
	"offset_left", "offset_top", "offset_right", "offset_bottom",
]


func _init(undo_redo: EditorUndoRedoManager) -> void:
	_undo_redo = undo_redo


## Apply a Control layout preset (anchors + offsets) to a UI node.
##
## Params:
##   path        - scene path to a Control node (required)
##   preset      - preset name: full_rect, center, top_left, ... (required)
##   resize_mode - minsize | keep_width | keep_height | keep_size (default: minsize)
##   margin      - integer margin in pixels from the anchor edges (default: 0)
func set_anchor_preset(params: Dictionary) -> Dictionary:
	var node_path: String = params.get("path", "")
	if node_path.is_empty():
		return ErrorCodes.make(ErrorCodes.MISSING_REQUIRED_PARAM, "Missing required param: path")

	var preset_name: String = str(params.get("preset", "")).to_lower()
	if preset_name.is_empty():
		return ErrorCodes.make(ErrorCodes.MISSING_REQUIRED_PARAM, "Missing required param: preset")
	if not _PRESETS.has(preset_name):
		var names := _PRESETS.keys()
		names.sort()
		return ErrorCodes.make(
			ErrorCodes.VALUE_OUT_OF_RANGE,
			"Unknown preset '%s'. Valid: %s" % [preset_name, ", ".join(names)]
		)

	var resize_mode_name: String = str(params.get("resize_mode", "minsize")).to_lower()
	if not _RESIZE_MODES.has(resize_mode_name):
		var names := _RESIZE_MODES.keys()
		names.sort()
		return ErrorCodes.make(
			ErrorCodes.VALUE_OUT_OF_RANGE,
			"Unknown resize_mode '%s'. Valid: %s" % [resize_mode_name, ", ".join(names)]
		)

	var margin: int = int(params.get("margin", 0))

	var _resolved := McpNodeValidator.resolve_or_error(node_path, "node_path")
	if _resolved.has("error"):
		return _resolved
	var node: Node = _resolved.node
	var scene_root: Node = _resolved.scene_root
	if not node is Control:
		var got_class: String = node.get_class()
		return ErrorCodes.make(
			ErrorCodes.WRONG_TYPE,
			"Node %s is not a Control (got %s)%s" % [
				node_path, got_class, _canvas_layer_overlay_hint(got_class)
			]
		)

	var control := node as Control
	var preset_value: int = _PRESETS[preset_name]
	var resize_mode_value: int = _RESIZE_MODES[resize_mode_name]

	# Snapshot before so we can undo every property the preset may have touched.
	var before: Dictionary = {}
	for prop in _ANCHOR_OFFSET_PROPS:
		before[prop] = control.get(prop)

	_undo_redo.create_action("MCP: Set %s anchor preset %s" % [control.name, preset_name])
	_undo_redo.add_do_method(
		control, "set_anchors_and_offsets_preset", preset_value, resize_mode_value, margin
	)
	for prop in _ANCHOR_OFFSET_PROPS:
		_undo_redo.add_undo_property(control, prop, before[prop])
	_undo_redo.commit_action()

	var after: Dictionary = {}
	for prop in _ANCHOR_OFFSET_PROPS:
		after[prop] = control.get(prop)

	return {
		"data": {
			"path": node_path,
			"preset": preset_name,
			"resize_mode": resize_mode_name,
			"margin": margin,
			"anchors": {
				"left": after.anchor_left,
				"top": after.anchor_top,
				"right": after.anchor_right,
				"bottom": after.anchor_bottom,
			},
			"offsets": {
				"left": after.offset_left,
				"top": after.offset_top,
				"right": after.offset_right,
				"bottom": after.offset_bottom,
			},
			"undoable": true,
		}
	}


## Set the visible `text` property on a UI Control (Label, Button + subclasses,
## LineEdit, TextEdit, RichTextLabel, LinkButton). Undoable.
func set_text(params: Dictionary) -> Dictionary:
	var node_path: String = params.get("path", "")
	if node_path.is_empty():
		return ErrorCodes.make(ErrorCodes.MISSING_REQUIRED_PARAM, "Missing required param: path")

	if not params.has("text"):
		return ErrorCodes.make(ErrorCodes.MISSING_REQUIRED_PARAM, "Missing required param: text")
	var text_value: Variant = params["text"]
	if typeof(text_value) != TYPE_STRING:
		return ErrorCodes.make(ErrorCodes.WRONG_TYPE, "text must be a string")

	var _resolved := McpNodeValidator.resolve_or_error(node_path, "node_path")
	if _resolved.has("error"):
		return _resolved
	var node: Node = _resolved.node
	var scene_root: Node = _resolved.scene_root
	var node_type := node.get_class()
	if not node is Control:
		return ErrorCodes.make(
			ErrorCodes.WRONG_TYPE,
			"Node %s is not a Control (got %s)" % [node_path, node_type]
		)
	# Scan get_property_list() (matches set_property / _apply_property in this
	# repo) so we can both confirm `text` exists and that it's actually a String
	# — guards against a custom Control whose `text` happens to be some other
	# type, where set()-ing a String would silently mis-coerce.
	var text_prop_type := TYPE_NIL
	var has_text := false
	for prop in node.get_property_list():
		if prop.get("name", "") == "text":
			has_text = true
			text_prop_type = prop.get("type", TYPE_NIL)
			break
	if not has_text:
		return ErrorCodes.make(
			ErrorCodes.PROPERTY_NOT_ON_CLASS,
			"Control %s has no 'text' property (got %s)" % [node_path, node_type]
		)
	if text_prop_type != TYPE_STRING:
		return ErrorCodes.make(
			ErrorCodes.PROPERTY_NOT_ON_CLASS,
			"Control %s has a non-string 'text' property (got %s)" % [node_path, node_type]
		)

	var old_value: String = node.get("text")

	_undo_redo.create_action("MCP: Set %s text" % node.name)
	_undo_redo.add_do_property(node, "text", text_value)
	_undo_redo.add_undo_property(node, "text", old_value)
	_undo_redo.commit_action()

	return {
		"data": {
			"path": node_path,
			"text": text_value,
			"old_text": old_value,
			"node_type": node_type,
			"undoable": true,
		}
	}


# ============================================================================
# build_layout — declarative nested-dict → Control tree in one undo action
# ============================================================================

## Build a tree of Control nodes atomically.
##
## Params:
##   tree         - Dictionary describing the root node. Required fields: "type".
##                  Optional: "name", "properties" (dict), "anchor_preset",
##                  "anchor_margin", "theme" (res://, uid:// or user:// path), "children" (array).
##   parent_path  - Parent scene path. Empty or "/" = scene root.
##
## Validation is done before any scene mutation: class names, property
## existence, and res:// paths are all checked up-front. If anything is
## invalid, no node is created.
func build_layout(params: Dictionary) -> Dictionary:
	var tree = params.get("tree")
	if not params.has("tree"):
		return ErrorCodes.make(ErrorCodes.MISSING_REQUIRED_PARAM, "Missing required param: tree")
	if typeof(tree) != TYPE_DICTIONARY:
		return ErrorCodes.make(ErrorCodes.WRONG_TYPE, "tree must be a dictionary")

	var _scene_check := McpNodeValidator.require_scene_or_error()
	if _scene_check.has("error"):
		return _scene_check
	var scene_root: Node = _scene_check.scene_root

	var parent_path: String = params.get("parent_path", "")
	var parent: Node = scene_root
	if not parent_path.is_empty() and parent_path != "/":
		parent = McpScenePath.resolve(parent_path, scene_root)
		if parent == null:
			return ErrorCodes.make(ErrorCodes.NODE_NOT_FOUND, McpScenePath.format_parent_error(parent_path, scene_root))

	# Validate + build in memory first; if anything fails, free and bail.
	var built := _build_subtree(tree)
	if built.has("error"):
		return built
	var root_node: Node = built.node
	var created: Array[Node] = built.created

	_undo_redo.create_action("MCP: Build UI layout (%d nodes)" % created.size())
	_undo_redo.add_do_method(parent, "add_child", root_node, true)
	_undo_redo.add_do_method(root_node, "set_owner", scene_root)
	for n in created:
		_undo_redo.add_do_method(n, "set_owner", scene_root)
		_undo_redo.add_do_reference(n)
	_undo_redo.add_undo_method(parent, "remove_child", root_node)
	_undo_redo.commit_action()

	return {
		"data": {
			"root_path": McpScenePath.from_node(root_node, scene_root),
			"node_count": created.size(),
			"undoable": true,
		}
	}


## Recursively instantiate + configure a node and its children in memory.
## Returns {"node": root, "created": [all descendants incl. root]} or {"error": ...}.
func _build_subtree(spec: Dictionary) -> Dictionary:
	var node_type: String = spec.get("type", "")
	if node_type.is_empty():
		return ErrorCodes.make(ErrorCodes.MISSING_REQUIRED_PARAM, "Every layout node requires a 'type'")
	if not ClassDB.class_exists(node_type):
		return ErrorCodes.make(ErrorCodes.VALUE_OUT_OF_RANGE, "Unknown type: %s" % node_type)
	if not ClassDB.is_parent_class(node_type, "Node"):
		return ErrorCodes.make(ErrorCodes.WRONG_TYPE, "%s is not a Node type" % node_type)

	var node: Node = ClassDB.instantiate(node_type)
	if node == null:
		return ErrorCodes.make(ErrorCodes.INTERNAL_ERROR, "Failed to instantiate %s" % node_type)

	var node_name: String = spec.get("name", "")
	if not node_name.is_empty():
		node.name = node_name

	# Properties.
	if spec.has("properties"):
		var props = spec.get("properties")
		if typeof(props) != TYPE_DICTIONARY:
			node.free()
			return ErrorCodes.make(ErrorCodes.WRONG_TYPE, "properties must be a dictionary")
		for key in props:
			var value = props[key]
			var apply_err := _apply_property(node, str(key), value)
			if apply_err != null:
				node.free()
				return apply_err

	# Theme (res:// / uid:// / user:// path -> Resource).
	if spec.has("theme"):
		var theme_path: String = str(spec.get("theme", ""))
		if not theme_path.is_empty():
			var theme_path_err = McpPathValidator.loadable_error(theme_path, "theme")
			if theme_path_err != null:
				node.free()
				return theme_path_err
			if not ResourceLoader.exists(theme_path):
				node.free()
				return ErrorCodes.make(ErrorCodes.RESOURCE_NOT_FOUND, "Theme not found: %s" % theme_path)
			var theme_res: Resource = ResourceLoader.load(theme_path)
			if theme_res == null or not theme_res is Theme:
				node.free()
				return ErrorCodes.make(ErrorCodes.WRONG_TYPE, "theme path must point to a Theme resource: %s" % theme_path)
			if not node is Control and not node is Window:
				node.free()
				return ErrorCodes.make(
					ErrorCodes.INVALID_PARAMS,
					"theme can only be set on Control / Window (got %s)%s" % [
						node_type, _canvas_layer_overlay_hint(node_type)
					]
				)
			node.theme = theme_res as Theme

	# Anchor preset — applied before children so children inherit sensible anchors.
	if spec.has("anchor_preset"):
		var preset_name: String = str(spec.get("anchor_preset", "")).to_lower()
		if not _PRESETS.has(preset_name):
			node.free()
			return ErrorCodes.make(ErrorCodes.VALUE_OUT_OF_RANGE, "Unknown anchor_preset: %s" % preset_name)
		if not node is Control:
			node.free()
			return ErrorCodes.make(
				ErrorCodes.INVALID_PARAMS,
				"anchor_preset requires a Control (got %s)%s" % [
					node_type, _canvas_layer_overlay_hint(node_type)
				]
			)
		var preset_value: int = _PRESETS[preset_name]
		var margin: int = int(spec.get("anchor_margin", 0))
		(node as Control).set_anchors_and_offsets_preset(preset_value, Control.PRESET_MODE_MINSIZE, margin)

	var created: Array[Node] = [node]
	if spec.has("children"):
		var children = spec.get("children")
		if typeof(children) != TYPE_ARRAY:
			node.free()
			return ErrorCodes.make(ErrorCodes.WRONG_TYPE, "children must be an array")
		for child_spec in children:
			if typeof(child_spec) != TYPE_DICTIONARY:
				node.free()
				return ErrorCodes.make(ErrorCodes.WRONG_TYPE, "each child must be a dictionary")
			var child_result := _build_subtree(child_spec)
			if child_result.has("error"):
				node.free()
				return child_result
			var child_node: Node = child_result.node
			node.add_child(child_node)
			for n in child_result.created:
				created.append(n)
	return {"node": node, "created": created}


## Mapping from theme_override_* property prefixes to their add/remove methods.
const _THEME_OVERRIDE_MAP := {
	"theme_override_colors/": {
		"add": "add_theme_color_override",
		"remove": "remove_theme_color_override",
		"coerce_type": TYPE_COLOR,
	},
	"theme_override_constants/": {
		"add": "add_theme_constant_override",
		"remove": "remove_theme_constant_override",
		"coerce_type": TYPE_INT,
	},
	"theme_override_font_sizes/": {
		"add": "add_theme_font_size_override",
		"remove": "remove_theme_font_size_override",
		"coerce_type": TYPE_INT,
	},
	"theme_override_styles/": {
		"add": "add_theme_stylebox_override",
		"remove": "remove_theme_stylebox_override",
		"coerce_type": TYPE_OBJECT,
	},
}


## Apply a property to a newly-instantiated node. Handles Color/Vector2/NodePath
## coercion from JSON-friendly forms. Returns null on success, error dict on failure.
func _apply_property(node: Node, prop: String, value: Variant) -> Variant:
	# Handle theme_override_* pseudo-properties before the regular property scan.
	for prefix in _THEME_OVERRIDE_MAP:
		if prop.begins_with(prefix):
			if not node is Control:
				return ErrorCodes.make(
					ErrorCodes.INVALID_PARAMS,
					"theme_override_* requires a Control node (got %s)" % node.get_class()
				)
			var override_name := prop.substr(prefix.length())
			var info: Dictionary = _THEME_OVERRIDE_MAP[prefix]
			var coerce_type: int = info.coerce_type

			# For stylebox overrides, load from a res:// / uid:// / user:// path.
			if coerce_type == TYPE_OBJECT:
				if value is String and (value.begins_with("res://") or value.begins_with("uid://") or value.begins_with("user://")):
					var style_path_err = McpPathValidator.loadable_error(value, "stylebox")
					if style_path_err != null:
						return style_path_err
					var res := ResourceLoader.load(value)
					if res == null or not res is StyleBox:
						return ErrorCodes.make(
							ErrorCodes.INVALID_PARAMS,
							"Style resource not found or not a StyleBox: %s" % value
						)
					node.call(info.add, override_name, res)
				else:
					return ErrorCodes.make(
						ErrorCodes.INVALID_PARAMS,
						"theme_override_styles/ expects a res:// / uid:// / user:// path to a StyleBox"
					)
			else:
				var coercion := _coerce_for_type(value, coerce_type)
				if not coercion.ok:
					return ErrorCodes.make(
						ErrorCodes.WRONG_TYPE,
						"Cannot coerce '%s' for %s" % [value, prop]
					)
				node.call(info.add, override_name, coercion.value)
			return null

	var found := false
	var prop_type := TYPE_NIL
	for p in node.get_property_list():
		if p.name == prop:
			found = true
			prop_type = p.get("type", TYPE_NIL)
			break
	if not found:
		return ErrorCodes.make(
			ErrorCodes.PROPERTY_NOT_ON_CLASS,
			McpPropertyErrors.build_message(node, prop)
		)

	var coercion := _coerce_for_type(value, prop_type)
	if not coercion.ok:
		return ErrorCodes.make(
			ErrorCodes.WRONG_TYPE,
			"Property '%s' on %s expects type %s (cannot coerce %s)" % [
				prop, node.get_class(), type_string(prop_type), value
			]
		)
	node.set(prop, coercion.value)
	return null


## Coerce a JSON-friendly value to the target Godot type. Returns
## {"ok": true, "value": coerced} on success, {"ok": false} on failure.
## For types we don't explicitly coerce, the value is returned as-is
## (Godot will typecheck at set() time and fail loudly if it disagrees).
static func _coerce_for_type(value: Variant, prop_type: int) -> Dictionary:
	match prop_type:
		TYPE_COLOR:
			## Canonical parser (#714): adds [r,g,b(,a)] array support and
			## strict key/component checking, same shapes everywhere.
			var parsed_color = McpJsonValues.parse_color(value)
			if parsed_color != null:
				return {"ok": true, "value": parsed_color}
			return {"ok": false}
		TYPE_VECTOR2:
			## Same canonical parser as TYPE_COLOR (CodeRabbit review):
			## keeping the inline copy here would re-introduce exactly the
			## permissive-vs-strict drift this PR removes elsewhere.
			var parsed_v2 = McpJsonValues.parse_vector2(value)
			if parsed_v2 != null:
				return {"ok": true, "value": parsed_v2}
			return {"ok": false}
		TYPE_VECTOR2I:
			if value is Vector2i:
				return {"ok": true, "value": value}
			if value is Dictionary and value.has("x") and value.has("y"):
				return {"ok": true, "value": Vector2i(int(value.x), int(value.y))}
			if value is Array and value.size() == 2:
				return {"ok": true, "value": Vector2i(int(value[0]), int(value[1]))}
			return {"ok": false}
		TYPE_RECT2:
			if value is Rect2:
				return {"ok": true, "value": value}
			if value is Array and value.size() == 4:
				return {
					"ok": true,
					"value":
					Rect2(float(value[0]), float(value[1]), float(value[2]), float(value[3])),
				}
			if value is Dictionary:
				if value.has("x") and value.has("y") and value.has("w") and value.has("h"):
					return {
						"ok": true,
						"value":
						Rect2(float(value.x), float(value.y), float(value.w), float(value.h)),
					}
				if value.has("position") and value.has("size"):
					var pos := _coerce_for_type(value.position, TYPE_VECTOR2)
					var sz := _coerce_for_type(value.size, TYPE_VECTOR2)
					if pos.ok and sz.ok:
						return {"ok": true, "value": Rect2(pos.value, sz.value)}
			return {"ok": false}
		TYPE_NODE_PATH:
			if value is NodePath:
				return {"ok": true, "value": value}
			if value is String:
				return {"ok": true, "value": NodePath(value)}
			return {"ok": false}
	return {"ok": true, "value": value}


# CanvasLayer is the canonical HUD parent but isn't a Control, so applying
# Control-only properties (theme, anchor_preset) to it is a common mistake.
# The recovery shape is always the same: nest a Control child under the layer.
static func _canvas_layer_overlay_hint(node_class: String) -> String:
	if node_class != "CanvasLayer":
		return ""
	return (
		". CanvasLayer is not a Control — add a Control (e.g. Panel or Control "
		+ "with anchor_preset=full_rect) as its child and apply theme / "
		+ "anchor_preset to that overlay."
	)


# ============================================================================
# scaffold_screen
# ============================================================================

func scaffold_screen(params: Dictionary) -> Dictionary:
	var kind: String = params.get("kind", "main_menu").to_lower()
	var parent_path: String = params.get("parent_path", "")
	var screen_name: String = params.get("name", "")
	var title: String = params.get("title", "")
	var layer_num: int = int(params.get("layer", 10))
	var buttons_param = params.get("buttons", null)

	var buttons: Array[String] = []
	if buttons_param is Array:
		for b in buttons_param:
			buttons.append(str(b))
	elif buttons.is_empty():
		match kind:
			"main_menu":
				buttons = ["Start Game", "Options", "Quit"]
				if title.is_empty():
					title = "My Game"
			"pause_menu":
				buttons = ["Resume", "Options", "Main Menu"]
				if title.is_empty():
					title = "Paused"
			"game_over":
				buttons = ["Try Again", "Main Menu"]
				if title.is_empty():
					title = "Game Over"
			"dialog_box":
				buttons = ["Continue"]
				if title.is_empty():
					title = "Message"
			"hud":
				buttons = []
				if title.is_empty():
					title = "HUD"

	var scene_check := McpNodeValidator.require_scene_or_error()
	if scene_check.has("error"):
		return scene_check
	var scene_root: Node = scene_check.scene_root

	var parent: Node = scene_root
	if not parent_path.is_empty():
		var resolved := McpNodeValidator.resolve_or_error(parent_path, "parent_path")
		if resolved.has("error"):
			return resolved
		parent = resolved.node

	if screen_name.is_empty():
		match kind:
			"main_menu":
				screen_name = "MainMenu"
			"pause_menu":
				screen_name = "PauseMenu"
			"game_over":
				screen_name = "GameOverScreen"
			"dialog_box":
				screen_name = "DialogBox"
			"hud":
				screen_name = "HUD"
			_:
				screen_name = "UIScreen"

	var canvas_layer := CanvasLayer.new()
	canvas_layer.name = screen_name
	canvas_layer.layer = layer_num

	var root_control := Control.new()
	root_control.name = "RootOverlay"
	root_control.set_anchors_preset(Control.PRESET_FULL_RECT)
	canvas_layer.add_child(root_control)

	var created_button_paths: Array[String] = []

	if kind in ["pause_menu", "game_over", "dialog_box"]:
		var backdrop := ColorRect.new()
		backdrop.name = "Backdrop"
		backdrop.set_anchors_preset(Control.PRESET_FULL_RECT)
		backdrop.color = Color(0.0, 0.0, 0.0, 0.55)
		root_control.add_child(backdrop)

	if kind == "hud":
		var margin_top := MarginContainer.new()
		margin_top.name = "TopBar"
		margin_top.set_anchors_preset(Control.PRESET_TOP_WIDE)
		margin_top.add_theme_constant_override("margin_left", 16)
		margin_top.add_theme_constant_override("margin_right", 16)
		margin_top.add_theme_constant_override("margin_top", 16)
		root_control.add_child(margin_top)

		var hbox := HBoxContainer.new()
		hbox.name = "StatsBox"
		margin_top.add_child(hbox)

		var score_label := Label.new()
		score_label.name = "ScoreLabel"
		score_label.text = "Score: 0"
		score_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		hbox.add_child(score_label)

		var health_label := Label.new()
		health_label.name = "HealthLabel"
		health_label.text = "Health: 100"
		hbox.add_child(health_label)
	else:
		var center := CenterContainer.new()
		center.name = "CenterContainer"
		center.set_anchors_preset(Control.PRESET_FULL_RECT)
		root_control.add_child(center)

		var panel := PanelContainer.new()
		panel.name = "CardPanel"
		center.add_child(panel)

		var vbox := VBoxContainer.new()
		vbox.name = "ContentBox"
		vbox.add_theme_constant_override("separation", 10)
		panel.add_child(vbox)

		if not title.is_empty():
			var title_lbl := Label.new()
			title_lbl.name = "TitleLabel"
			title_lbl.text = title
			title_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
			title_lbl.add_theme_font_size_override("font_size", 24)
			vbox.add_child(title_lbl)

			var sep := HSeparator.new()
			sep.name = "TitleSeparator"
			vbox.add_child(sep)

		for btn_text in buttons:
			var btn := Button.new()
			btn.name = btn_text.replace(" ", "") + "Button"
			btn.text = btn_text
			btn.custom_minimum_size = Vector2(160, 36)
			vbox.add_child(btn)

	# Commit to UndoRedo and assign owners recursively
	_undo_redo.create_action("Scaffold UI Screen: %s" % screen_name)
	_undo_redo.add_do_method(parent, "add_child", canvas_layer)
	_undo_redo.add_do_reference(canvas_layer)
	_undo_redo.add_undo_method(parent, "remove_child", canvas_layer)
	_undo_redo.commit_action()

	# Set owners after add_child
	_set_owner_recursive(canvas_layer, scene_root)

	# Collect button paths
	_collect_button_paths(canvas_layer, scene_root, created_button_paths)

	return {
		"root_path": McpScenePath.from_node(canvas_layer, scene_root),
		"kind": kind,
		"title": title,
		"buttons": created_button_paths,
	}


static func _set_owner_recursive(node: Node, scene_root: Node) -> void:
	if node != scene_root:
		node.owner = scene_root
	for child in node.get_children():
		_set_owner_recursive(child, scene_root)


static func _collect_button_paths(node: Node, scene_root: Node, out: Array[String]) -> void:
	if node is Button:
		out.append(McpScenePath.from_node(node, scene_root))
	for child in node.get_children():
		_collect_button_paths(child, scene_root, out)

