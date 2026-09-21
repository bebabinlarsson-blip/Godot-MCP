@tool
extends "res://addons/godot_ai/handlers/command_handler.gd"

const ErrorCodes := preload("res://addons/godot_ai/utils/error_codes.gd")

## Handles Theme resource authoring: creating, modifying color/constant/font-size/
## stylebox slots, and applying a theme to a Control subtree.
##
## Themes are Godot's equivalent of USS: a Theme holds (class, name) -> value
## entries (colors, constants, fonts, font_sizes, styleboxes, icons) which
## cascade down a Control subtree when the theme is assigned at any ancestor.
## One well-authored theme replaces hundreds of per-node property sets.

const _COLOR_HINT := "expected hex #rrggbb, named color, or {r,g,b,a} dict"

var _undo_redo: EditorUndoRedoManager
var _connection: McpConnection


func _init(undo_redo: EditorUndoRedoManager, connection: McpConnection = null) -> void:
	_undo_redo = undo_redo
	_connection = connection


# ============================================================================
# theme_create
# ============================================================================

func create_theme(params: Dictionary) -> Dictionary:
	var path: String = params.get("path", "")
	var overwrite: bool = params.get("overwrite", false)

	var err := _validate_res_path(path, ".tres", "path", true)
	if err != null:
		return err

	# Capture whether the file was already there BEFORE the save so we can
	# report `overwritten` accurately (after save the file always exists).
	var existed_before := FileAccess.file_exists(path)
	if existed_before and not overwrite:
		return ErrorCodes.make(
			ErrorCodes.INVALID_PARAMS,
			"Theme already exists at %s (pass overwrite=true to replace)" % path
		)

	# Ensure parent directory exists. make_dir_recursive is idempotent —
	# no need to check dir_exists first (avoids TOCTOU race).
	var dir_path := path.get_base_dir()
	var mkdir_err := DirAccess.make_dir_recursive_absolute(dir_path)
	if mkdir_err != OK and mkdir_err != ERR_ALREADY_EXISTS:
		return ErrorCodes.make(
			ErrorCodes.INTERNAL_ERROR,
			"Failed to create directory: %s (error %d)" % [dir_path, mkdir_err]
		)

	var theme := Theme.new()
	var save_err := McpResourceIO.guarded_save(theme, path, _connection)
	if save_err != OK:
		return ErrorCodes.make(
			ErrorCodes.INTERNAL_ERROR,
			"Failed to save theme to %s: %s (error %d)" % [path, error_string(save_err), save_err]
		)

	# Make sure the editor's filesystem picks up the new file.
	var efs := EditorInterface.get_resource_filesystem()
	if efs != null:
		efs.update_file(path)

	return {
		"data": {
			"path": path,
			"overwritten": existed_before,
			"undoable": false,
			"reason": "File creation is persistent; delete the file manually to revert",
		}
	}


# ============================================================================
# theme_set_color / theme_set_constant / theme_set_font_size
# ============================================================================

func set_color(params: Dictionary) -> Dictionary:
	return _set_scalar(params, "color", func(theme, name, cls): return theme.get_color(name, cls),
		func(theme, name, cls, val): theme.set_color(name, cls, val),
		func(theme, name, cls): theme.clear_color(name, cls),
		func(theme, name, cls): return theme.has_color(name, cls),
		func(v): return _parse_color(v))


# constant / font_size parsers validate before coercing: int("abc")/int({})/int([])
# all return 0 in GDScript (never null), so a bare `int(v)` would silently store
# garbage as 0 and report success. Returning null for non-numeric input lets
# _set_scalar's null guard surface a VALUE_OUT_OF_RANGE error, matching the
# color path's contract.
func set_constant(params: Dictionary) -> Dictionary:
	return _set_scalar(params, "constant", func(theme, name, cls): return theme.get_constant(name, cls),
		func(theme, name, cls, val): theme.set_constant(name, cls, int(val)),
		func(theme, name, cls): theme.clear_constant(name, cls),
		func(theme, name, cls): return theme.has_constant(name, cls),
		func(v): return int(v) if (v is int or v is float or (v is String and v.is_valid_int())) else null)


func set_font_size(params: Dictionary) -> Dictionary:
	return _set_scalar(params, "font_size", func(theme, name, cls): return theme.get_font_size(name, cls),
		func(theme, name, cls, val): theme.set_font_size(name, cls, int(val)),
		func(theme, name, cls): theme.clear_font_size(name, cls),
		func(theme, name, cls): return theme.has_font_size(name, cls),
		func(v): return int(v) if (v is int or v is float or (v is String and v.is_valid_int())) else null)


# Shared implementation for scalar Theme slots (color, constant, font_size).
# Captures old value, applies new value, saves to disk, registers undo that
# restores the old value and saves again.
func _set_scalar(
	params: Dictionary,
	kind: String,
	getter: Callable,
	setter: Callable,
	clearer: Callable,
	has_fn: Callable,
	parser: Callable,
) -> Dictionary:
	var load_result := _load_theme_from_params(params)
	if load_result.has("error"):
		return load_result
	var theme: Theme = load_result.theme
	var theme_path: String = load_result.path

	var class_name_param: String = params.get("class_name", "")
	if class_name_param.is_empty():
		return ErrorCodes.make(ErrorCodes.MISSING_REQUIRED_PARAM, "Missing required param: class_name")

	var name: String = params.get("name", "")
	if name.is_empty():
		return ErrorCodes.make(ErrorCodes.MISSING_REQUIRED_PARAM, "Missing required param: name")

	if not "value" in params:
		return ErrorCodes.make(ErrorCodes.MISSING_REQUIRED_PARAM, "Missing required param: value")

	var raw_value = params.get("value")
	if raw_value == null:
		return ErrorCodes.make(
			ErrorCodes.VALUE_OUT_OF_RANGE,
			"Invalid %s value: null (pass a concrete value; use the appropriate clear command to remove a slot)" % kind
		)
	var parsed = parser.call(raw_value)
	if parsed == null:
		## color slots want a color hint; constant/font_size are integer slots.
		var hint := _COLOR_HINT if kind == "color" else "expected an integer"
		return ErrorCodes.make(ErrorCodes.VALUE_OUT_OF_RANGE,
			"Invalid %s value: %s (%s)" % [kind, raw_value, hint])

	var had_before: bool = has_fn.call(theme, name, class_name_param)
	var before_value = getter.call(theme, name, class_name_param) if had_before else null

	_undo_redo.create_action("MCP: Theme set %s %s/%s" % [kind, class_name_param, name])
	_undo_redo.add_do_method(self, "_apply_scalar", theme_path, setter, name, class_name_param, parsed)
	if had_before:
		_undo_redo.add_undo_method(self, "_apply_scalar", theme_path, setter, name, class_name_param, before_value)
	else:
		_undo_redo.add_undo_method(self, "_clear_scalar", theme_path, clearer, name, class_name_param)
	_undo_redo.commit_action()

	return {
		"data": {
			"path": theme_path,
			"kind": kind,
			"class_name": class_name_param,
			"name": name,
			"value": _serialize_value(parsed),
			"previous_value": _serialize_value(before_value) if had_before else null,
			"undoable": true,
		}
	}


func _apply_scalar(theme_path: String, setter: Callable, name: String, class_name_param: String, value: Variant) -> void:
	var theme: Theme = ResourceLoader.load(theme_path)
	if theme == null:
		push_warning("MCP: Failed to load theme for undo/redo: %s" % theme_path)
		return
	setter.call(theme, name, class_name_param, value)
	McpResourceIO.guarded_save(theme, theme_path, _connection)


func _clear_scalar(theme_path: String, clearer: Callable, name: String, class_name_param: String) -> void:
	var theme: Theme = ResourceLoader.load(theme_path)
	if theme == null:
		push_warning("MCP: Failed to load theme for undo/redo: %s" % theme_path)
		return
	clearer.call(theme, name, class_name_param)
	McpResourceIO.guarded_save(theme, theme_path, _connection)


# ============================================================================
# theme_set_stylebox_flat
# ============================================================================

## Compose a StyleBoxFlat and assign it to a theme slot.
##
## Parameters (beyond theme_path / class_name / name):
##   bg_color       (Color, "#rrggbb", "#rrggbbaa", or {r,g,b,a})
##   border_color   (Color)
##   border         {all|top|bottom|left|right: int}  — side keys override `all`
##   corners        {all|top_left|top_right|bottom_left|bottom_right: int}
##   margins        {all|top|bottom|left|right: float}
##   shadow         {color, size: int, offset_x: float, offset_y: float}
##   anti_aliasing  (bool)
##
## Unknown keys inside any nested dict are rejected with INVALID_PARAMS so
## typos fail loudly instead of silently being ignored.
func set_stylebox_flat(params: Dictionary) -> Dictionary:
	var load_result := _load_theme_from_params(params)
	if load_result.has("error"):
		return load_result
	var theme: Theme = load_result.theme
	var theme_path: String = load_result.path

	var class_name_param: String = params.get("class_name", "")
	if class_name_param.is_empty():
		return ErrorCodes.make(ErrorCodes.MISSING_REQUIRED_PARAM, "Missing required param: class_name")

	var name: String = params.get("name", "")
	if name.is_empty():
		return ErrorCodes.make(ErrorCodes.MISSING_REQUIRED_PARAM, "Missing required param: name")

	var sb := StyleBoxFlat.new()
	if params.has("bg_color"):
		var bg := _parse_color(params.bg_color)
		if bg == null:
			return ErrorCodes.make(ErrorCodes.VALUE_OUT_OF_RANGE, "Invalid bg_color: %s (%s)" % [str(params.bg_color), _COLOR_HINT])
		sb.bg_color = bg
	if params.has("border_color"):
		var bc := _parse_color(params.border_color)
		if bc == null:
			return ErrorCodes.make(ErrorCodes.VALUE_OUT_OF_RANGE, "Invalid border_color: %s (%s)" % [str(params.border_color), _COLOR_HINT])
		sb.border_color = bc

	# border: {all, top, bottom, left, right} — int widths
	if params.has("border"):
		var err := _apply_sides(sb, params.border, "border",
			["top", "bottom", "left", "right"],
			"border_width_",
			TYPE_INT)
		if err != "":
			return ErrorCodes.make(ErrorCodes.INVALID_PARAMS, err)

	# corners: {all, top_left, top_right, bottom_left, bottom_right} — int radii
	if params.has("corners"):
		var err2 := _apply_sides(sb, params.corners, "corners",
			["top_left", "top_right", "bottom_left", "bottom_right"],
			"corner_radius_",
			TYPE_INT)
		if err2 != "":
			return ErrorCodes.make(ErrorCodes.INVALID_PARAMS, err2)

	# margins: {all, top, bottom, left, right} — float padding
	if params.has("margins"):
		var err3 := _apply_sides(sb, params.margins, "margins",
			["top", "bottom", "left", "right"],
			"content_margin_",
			TYPE_FLOAT)
		if err3 != "":
			return ErrorCodes.make(ErrorCodes.INVALID_PARAMS, err3)

	# shadow: {color, size, offset_x, offset_y}
	if params.has("shadow"):
		if typeof(params.shadow) != TYPE_DICTIONARY:
			return ErrorCodes.make(ErrorCodes.INVALID_PARAMS, "'shadow' must be a dict with color/size/offset_x/offset_y")
		var shadow: Dictionary = params.shadow
		var allowed_shadow_keys := {"color": true, "size": true, "offset_x": true, "offset_y": true}
		for k in shadow.keys():
			if not allowed_shadow_keys.has(k):
				return ErrorCodes.make(ErrorCodes.INVALID_PARAMS,
					"Unknown key in 'shadow': %s (valid: color, size, offset_x, offset_y)" % k)
		if shadow.has("color"):
			var sc := _parse_color(shadow.color)
			if sc == null:
				return ErrorCodes.make(ErrorCodes.INVALID_PARAMS,
					"Invalid shadow.color: %s (%s)" % [str(shadow.color), _COLOR_HINT])
			sb.shadow_color = sc
		if shadow.has("size"):
			sb.shadow_size = int(shadow.size)
		if shadow.has("offset_x") or shadow.has("offset_y"):
			sb.shadow_offset = Vector2(
				float(shadow.get("offset_x", 0)),
				float(shadow.get("offset_y", 0)),
			)

	if params.has("anti_aliasing"):
		sb.anti_aliasing = bool(params.anti_aliasing)

	var had_before := theme.has_stylebox(name, class_name_param)
	var before_sb: StyleBox = theme.get_stylebox(name, class_name_param) if had_before else null

	_undo_redo.create_action("MCP: Theme set stylebox %s/%s" % [class_name_param, name])
	_undo_redo.add_do_method(self, "_apply_stylebox", theme_path, name, class_name_param, sb)
	if had_before:
		_undo_redo.add_undo_method(self, "_apply_stylebox", theme_path, name, class_name_param, before_sb)
	else:
		_undo_redo.add_undo_method(self, "_clear_stylebox", theme_path, name, class_name_param)
	_undo_redo.commit_action()

	return {
		"data": {
			"path": theme_path,
			"class_name": class_name_param,
			"name": name,
			"stylebox_class": "StyleBoxFlat",
			"bg_color": _serialize_value(sb.bg_color),
			"border": {
				"top": sb.border_width_top,
				"bottom": sb.border_width_bottom,
				"left": sb.border_width_left,
				"right": sb.border_width_right,
			},
			"corners": {
				"top_left": sb.corner_radius_top_left,
				"top_right": sb.corner_radius_top_right,
				"bottom_left": sb.corner_radius_bottom_left,
				"bottom_right": sb.corner_radius_bottom_right,
			},
			"margins": {
				"top": sb.content_margin_top,
				"bottom": sb.content_margin_bottom,
				"left": sb.content_margin_left,
				"right": sb.content_margin_right,
			},
			"undoable": true,
		}
	}


## Parse a {all, <side1>, <side2>, ...} dict and apply it to StyleBoxFlat via
## its set_<prop_prefix><side> properties. Returns "" on success, an error
## message on failure. Validates that only known keys are present.
func _apply_sides(sb: StyleBoxFlat, sides_dict: Variant, dict_name: String,
		side_names: Array, prop_prefix: String, value_type: int) -> String:
	if typeof(sides_dict) != TYPE_DICTIONARY:
		return "'%s' must be a dict with 'all' and/or side-specific keys" % dict_name
	var valid_keys := {"all": true}
	for s in side_names:
		valid_keys[s] = true
	for k in sides_dict.keys():
		if not valid_keys.has(k):
			return "Unknown key in '%s': %s (valid: all, %s)" % [
				dict_name, k, ", ".join(side_names)
			]
	# Apply `all` first, then override with side-specific keys.
	if sides_dict.has("all"):
		var all_val: Variant = sides_dict.all
		for s in side_names:
			var v: Variant = int(all_val) if value_type == TYPE_INT else float(all_val)
			sb.set(prop_prefix + s, v)
	for s in side_names:
		if sides_dict.has(s):
			var v2: Variant = int(sides_dict[s]) if value_type == TYPE_INT else float(sides_dict[s])
			sb.set(prop_prefix + s, v2)
	return ""


func _apply_stylebox(theme_path: String, name: String, class_name_param: String, sb: StyleBox) -> void:
	var theme: Theme = ResourceLoader.load(theme_path)
	if theme == null:
		push_warning("MCP: Failed to load theme for undo/redo: %s" % theme_path)
		return
	theme.set_stylebox(name, class_name_param, sb)
	McpResourceIO.guarded_save(theme, theme_path, _connection)


func _clear_stylebox(theme_path: String, name: String, class_name_param: String) -> void:
	var theme: Theme = ResourceLoader.load(theme_path)
	if theme == null:
		push_warning("MCP: Failed to load theme for undo/redo: %s" % theme_path)
		return
	theme.clear_stylebox(name, class_name_param)
	McpResourceIO.guarded_save(theme, theme_path, _connection)


# ============================================================================
# theme_apply — assign a theme to a Control
# ============================================================================

func apply_theme(params: Dictionary) -> Dictionary:
	var node_path: String = params.get("node_path", "")
	if node_path.is_empty():
		return ErrorCodes.make(ErrorCodes.MISSING_REQUIRED_PARAM, "Missing required param: node_path")

	var theme_path: String = params.get("theme_path", "")
	var theme: Theme = null
	if not theme_path.is_empty():
		var path_err := _validate_res_path(theme_path, ".tres")
		if path_err != null:
			return path_err
		if not ResourceLoader.exists(theme_path):
			return ErrorCodes.make(ErrorCodes.RESOURCE_NOT_FOUND, "Theme not found: %s" % theme_path)
		theme = ResourceLoader.load(theme_path)
		if theme == null or not theme is Theme:
			return ErrorCodes.make(ErrorCodes.WRONG_TYPE, "Resource at %s is not a Theme" % theme_path)

	var _resolved := McpNodeValidator.resolve_or_error(node_path, "node_path")
	if _resolved.has("error"):
		return _resolved
	var node: Node = _resolved.node
	var _scene_root: Node = _resolved.scene_root
	if not node is Control and not node is Window:
		return ErrorCodes.make(
			ErrorCodes.WRONG_TYPE,
			"Node %s is not a Control or Window (got %s)" % [node_path, node.get_class()]
		)

	var before_theme: Theme = node.theme
	_undo_redo.create_action("MCP: Apply theme to %s" % node.name)
	_undo_redo.add_do_property(node, "theme", theme)
	_undo_redo.add_undo_property(node, "theme", before_theme)
	_undo_redo.commit_action()

	return {
		"data": {
			"node_path": node_path,
			"theme_path": theme_path if theme != null else "",
			"cleared": theme == null,
			"undoable": true,
		}
	}


# ============================================================================
# theme_apply_preset
# ============================================================================

func apply_preset(params: Dictionary) -> Dictionary:
	var preset: String = params.get("preset", "dark_modern").to_lower()
	var theme_path: String = params.get("theme_path", "")
	var node_path: String = params.get("node_path", "")
	var set_as_default: bool = bool(params.get("set_as_default", false))
	var overwrite: bool = bool(params.get("overwrite", true))

	if theme_path.is_empty():
		theme_path = "res://assets/themes/" + preset + ".tres"

	var path_err := _validate_res_path(theme_path, ".tres", "theme_path", true)
	if path_err != null:
		return path_err

	var dir_path := theme_path.get_base_dir()
	if not DirAccess.dir_exists_absolute(dir_path):
		DirAccess.make_dir_recursive_absolute(dir_path)

	var theme := Theme.new()

	# Helper to create flat stylebox
	var make_sb = func(bg: Color, border: Color, bw: int, radius: int, pad_x: int, pad_y: int) -> StyleBoxFlat:
		var sb := StyleBoxFlat.new()
		sb.bg_color = bg
		sb.border_color = border
		sb.border_width_left = bw
		sb.border_width_right = bw
		sb.border_width_top = bw
		sb.border_width_bottom = bw
		sb.corner_radius_top_left = radius
		sb.corner_radius_top_right = radius
		sb.corner_radius_bottom_left = radius
		sb.corner_radius_bottom_right = radius
		sb.content_margin_left = float(pad_x)
		sb.content_margin_right = float(pad_x)
		sb.content_margin_top = float(pad_y)
		sb.content_margin_bottom = float(pad_y)
		return sb

	if preset == "cyberpunk_neon":
		var cyan := Color(0.0, 0.94, 1.0)
		var magenta := Color(1.0, 0.0, 0.33)
		var dark_bg := Color(0.04, 0.05, 0.09, 0.95)
		var btn_norm := Color(0.07, 0.1, 0.15)
		var btn_hov := Color(0.0, 0.23, 0.27)
		var btn_press := Color(0.35, 0.0, 0.15)
		var text_col := Color(0.88, 0.97, 1.0)

		theme.set_stylebox("normal", "Button", make_sb.call(btn_norm, cyan, 2, 2, 12, 6))
		theme.set_stylebox("hover", "Button", make_sb.call(btn_hov, cyan, 2, 2, 12, 6))
		theme.set_stylebox("pressed", "Button", make_sb.call(btn_press, magenta, 2, 2, 12, 6))
		theme.set_stylebox("disabled", "Button", make_sb.call(Color(0.05, 0.05, 0.07, 0.6), Color(0.2, 0.3, 0.4), 1, 2, 12, 6))
		theme.set_stylebox("focus", "Button", make_sb.call(Color(0, 0, 0, 0), cyan, 2, 2, 12, 6))
		theme.set_color("font_color", "Button", text_col)
		theme.set_color("font_hover_color", "Button", Color(1.0, 1.0, 1.0))
		theme.set_color("font_pressed_color", "Button", magenta)

		theme.set_stylebox("panel", "Panel", make_sb.call(dark_bg, cyan, 2, 4, 12, 12))
		theme.set_stylebox("panel", "PanelContainer", make_sb.call(dark_bg, cyan, 2, 4, 12, 12))
		theme.set_stylebox("normal", "LineEdit", make_sb.call(Color(0.05, 0.07, 0.12), cyan, 1, 2, 8, 6))
		theme.set_stylebox("focus", "LineEdit", make_sb.call(Color(0.05, 0.07, 0.12), magenta, 2, 2, 8, 6))
		theme.set_color("font_color", "LineEdit", text_col)
		theme.set_color("font_color", "Label", text_col)
		theme.set_stylebox("background", "ProgressBar", make_sb.call(Color(0.05, 0.07, 0.12), cyan, 1, 2, 2, 2))
		theme.set_stylebox("fill", "ProgressBar", make_sb.call(cyan, Color(0, 0, 0, 0), 0, 2, 2, 2))

	elif preset == "retro_pixel":
		var white := Color(1.0, 1.0, 1.0)
		var gold := Color(0.96, 0.82, 0.25)
		var bg_dark := Color(0.06, 0.06, 0.11)
		var btn_norm := Color(0.17, 0.17, 0.27)
		var btn_hov := Color(0.26, 0.26, 0.42)
		var btn_press := Color(0.1, 0.1, 0.16)
		var border_col := Color(0.34, 0.34, 0.51)

		theme.set_stylebox("normal", "Button", make_sb.call(btn_norm, border_col, 2, 0, 10, 6))
		theme.set_stylebox("hover", "Button", make_sb.call(btn_hov, white, 2, 0, 10, 6))
		theme.set_stylebox("pressed", "Button", make_sb.call(btn_press, gold, 2, 0, 10, 6))
		theme.set_stylebox("disabled", "Button", make_sb.call(Color(0.1, 0.1, 0.15), Color(0.2, 0.2, 0.25), 1, 0, 10, 6))
		theme.set_stylebox("focus", "Button", make_sb.call(Color(0, 0, 0, 0), gold, 2, 0, 10, 6))
		theme.set_color("font_color", "Button", white)
		theme.set_color("font_hover_color", "Button", gold)

		theme.set_stylebox("panel", "Panel", make_sb.call(bg_dark, border_col, 2, 0, 10, 10))
		theme.set_stylebox("panel", "PanelContainer", make_sb.call(bg_dark, border_col, 2, 0, 10, 10))
		theme.set_color("font_color", "Label", white)
		theme.set_stylebox("normal", "LineEdit", make_sb.call(btn_press, border_col, 2, 0, 8, 4))
		theme.set_stylebox("background", "ProgressBar", make_sb.call(btn_press, border_col, 2, 0, 2, 2))
		theme.set_stylebox("fill", "ProgressBar", make_sb.call(gold, Color(0, 0, 0, 0), 0, 0, 2, 2))

	elif preset == "fantasy_parchment":
		var gold := Color(0.83, 0.69, 0.22)
		var dark_parch := Color(0.17, 0.11, 0.05, 0.95)
		var btn_norm := Color(0.26, 0.18, 0.09)
		var btn_hov := Color(0.35, 0.25, 0.12)
		var btn_press := Color(0.17, 0.11, 0.05)
		var border_col := Color(0.72, 0.53, 0.04)
		var text_col := Color(0.98, 0.92, 0.84)

		theme.set_stylebox("normal", "Button", make_sb.call(btn_norm, border_col, 2, 4, 14, 6))
		theme.set_stylebox("hover", "Button", make_sb.call(btn_hov, gold, 2, 4, 14, 6))
		theme.set_stylebox("pressed", "Button", make_sb.call(btn_press, gold, 2, 4, 14, 6))
		theme.set_stylebox("disabled", "Button", make_sb.call(Color(0.15, 0.1, 0.06), Color(0.4, 0.3, 0.15), 1, 4, 14, 6))
		theme.set_stylebox("focus", "Button", make_sb.call(Color(0, 0, 0, 0), gold, 2, 4, 14, 6))
		theme.set_color("font_color", "Button", text_col)
		theme.set_color("font_hover_color", "Button", Color(1.0, 0.95, 0.8))

		theme.set_stylebox("panel", "Panel", make_sb.call(dark_parch, border_col, 2, 6, 12, 12))
		theme.set_stylebox("panel", "PanelContainer", make_sb.call(dark_parch, border_col, 2, 6, 12, 12))
		theme.set_color("font_color", "Label", text_col)
		theme.set_stylebox("normal", "LineEdit", make_sb.call(btn_press, border_col, 1, 4, 8, 6))
		theme.set_stylebox("background", "ProgressBar", make_sb.call(btn_press, border_col, 1, 3, 2, 2))
		theme.set_stylebox("fill", "ProgressBar", make_sb.call(gold, Color(0, 0, 0, 0), 0, 3, 2, 2))

	elif preset == "clean_light":
		var blue := Color(0.06, 0.65, 0.91)
		var bg_panel := Color(1.0, 1.0, 1.0)
		var btn_norm := Color(0.97, 0.98, 0.99)
		var btn_hov := Color(0.95, 0.96, 0.98)
		var btn_press := Color(0.89, 0.91, 0.94)
		var border_col := Color(0.8, 0.84, 0.88)
		var text_dark := Color(0.06, 0.09, 0.16)

		theme.set_stylebox("normal", "Button", make_sb.call(btn_norm, border_col, 1, 6, 14, 8))
		theme.set_stylebox("hover", "Button", make_sb.call(btn_hov, blue, 1, 6, 14, 8))
		theme.set_stylebox("pressed", "Button", make_sb.call(btn_press, blue, 1, 6, 14, 8))
		theme.set_stylebox("disabled", "Button", make_sb.call(Color(0.95, 0.95, 0.95), Color(0.88, 0.88, 0.88), 1, 6, 14, 8))
		theme.set_stylebox("focus", "Button", make_sb.call(Color(0, 0, 0, 0), blue, 2, 6, 14, 8))
		theme.set_color("font_color", "Button", text_dark)
		theme.set_color("font_hover_color", "Button", blue)

		theme.set_stylebox("panel", "Panel", make_sb.call(bg_panel, border_col, 1, 8, 14, 14))
		theme.set_stylebox("panel", "PanelContainer", make_sb.call(bg_panel, border_col, 1, 8, 14, 14))
		theme.set_color("font_color", "Label", text_dark)
		theme.set_stylebox("normal", "LineEdit", make_sb.call(Color(1, 1, 1), border_col, 1, 6, 8, 6))
		theme.set_stylebox("background", "ProgressBar", make_sb.call(Color(0.93, 0.94, 0.96), border_col, 1, 4, 2, 2))
		theme.set_stylebox("fill", "ProgressBar", make_sb.call(blue, Color(0, 0, 0, 0), 0, 4, 2, 2))

	else: # Default: dark_modern
		var blue := Color(0.23, 0.51, 0.96)
		var panel_bg := Color(0.12, 0.13, 0.17, 0.95)
		var btn_norm := Color(0.15, 0.16, 0.21)
		var btn_hov := Color(0.2, 0.22, 0.27)
		var btn_press := Color(0.11, 0.31, 0.85)
		var border_col := Color(0.22, 0.25, 0.32)
		var text_light := Color(0.95, 0.96, 0.96)

		theme.set_stylebox("normal", "Button", make_sb.call(btn_norm, border_col, 1, 6, 14, 8))
		theme.set_stylebox("hover", "Button", make_sb.call(btn_hov, blue, 1, 6, 14, 8))
		theme.set_stylebox("pressed", "Button", make_sb.call(btn_press, blue, 1, 6, 14, 8))
		theme.set_stylebox("disabled", "Button", make_sb.call(Color(0.1, 0.1, 0.13), Color(0.16, 0.18, 0.22), 1, 6, 14, 8))
		theme.set_stylebox("focus", "Button", make_sb.call(Color(0, 0, 0, 0), blue, 2, 6, 14, 8))
		theme.set_color("font_color", "Button", text_light)
		theme.set_color("font_hover_color", "Button", Color(1, 1, 1))

		theme.set_stylebox("panel", "Panel", make_sb.call(panel_bg, border_col, 1, 8, 14, 14))
		theme.set_stylebox("panel", "PanelContainer", make_sb.call(panel_bg, border_col, 1, 8, 14, 14))
		theme.set_color("font_color", "Label", text_light)
		theme.set_stylebox("normal", "LineEdit", make_sb.call(Color(0.09, 0.1, 0.13), border_col, 1, 6, 8, 6))
		theme.set_stylebox("background", "ProgressBar", make_sb.call(Color(0.09, 0.1, 0.13), border_col, 1, 4, 2, 2))
		theme.set_stylebox("fill", "ProgressBar", make_sb.call(blue, Color(0, 0, 0, 0), 0, 4, 2, 2))

	var save_err := McpResourceIO.guarded_save(theme, theme_path, _connection)
	if save_err != OK:
		return ErrorCodes.make(ErrorCodes.INTERNAL_ERROR, "Failed to save theme: %s" % error_string(save_err))

	var node_applied := false
	if not node_path.is_empty():
		var res := McpNodeValidator.resolve_or_error(node_path, "node_path")
		if not res.has("error") and res.node is Control:
			var ctrl: Control = res.node
			_undo_redo.create_action("MCP: Apply preset theme to %s" % ctrl.name)
			_undo_redo.add_do_property(ctrl, "theme", theme)
			_undo_redo.add_undo_property(ctrl, "theme", ctrl.theme)
			_undo_redo.commit_action()
			node_applied = true

	var default_set := false
	if set_as_default:
		ProjectSettings.set_setting("gui/theme/custom", theme_path)
		ProjectSettings.set_initial_value("gui/theme/custom", "")
		ProjectSettings.set_as_basic("gui/theme/custom", true)
		default_set = (ProjectSettings.save() == OK)

	var efs := EditorInterface.get_resource_filesystem()
	if efs != null:
		efs.update_file(theme_path)

	return {
		"data": {
			"preset": preset,
			"theme_path": theme_path,
			"applied_to_node": node_applied,
			"set_as_project_default": default_set,
		}
	}


# ============================================================================
# Helpers
# ============================================================================

func _load_theme_from_params(params: Dictionary) -> Dictionary:
	var theme_path: String = params.get("theme_path", "")
	var err := _validate_res_path(theme_path, ".tres", "theme_path", true)
	if err != null:
		return err
	if not ResourceLoader.exists(theme_path):
		return ErrorCodes.make(ErrorCodes.RESOURCE_NOT_FOUND, "Theme not found: %s" % theme_path)
	var theme: Theme = ResourceLoader.load(theme_path)
	if theme == null or not theme is Theme:
		return ErrorCodes.make(ErrorCodes.WRONG_TYPE, "Resource at %s is not a Theme" % theme_path)
	return {"theme": theme, "path": theme_path}


static func _validate_res_path(path: String, required_suffix: String, param_name: String = "theme_path", for_write: bool = false) -> Variant:
	if path.is_empty():
		return ErrorCodes.make(ErrorCodes.MISSING_REQUIRED_PARAM, "Missing required param: %s" % param_name)
	var path_err := McpPathValidator.validate_resource_path(path, for_write)
	if not path_err.is_empty():
		return ErrorCodes.make(ErrorCodes.VALUE_OUT_OF_RANGE, "%s: %s" % [param_name, path_err])
	if not path.ends_with(required_suffix):
		return ErrorCodes.make(
			ErrorCodes.VALUE_OUT_OF_RANGE,
			"%s must end with %s (got %s)" % [param_name, required_suffix, path]
		)
	return null


## Parse a color from Color, "#rrggbb", "#rrggbbaa", named (red/blue/...) or dict.
## Returns null if the input cannot be parsed.
## Delegates to the canonical parser (#714) — gains [r,g,b(,a)] array
## support and strict key/component checking, same shapes as every other
## color-accepting handler.
static func _parse_color(value: Variant) -> Variant:
	return McpJsonValues.parse_color(value)


static func _serialize_value(value: Variant) -> Variant:
	if value == null:
		return null
	if value is Color:
		return {"r": value.r, "g": value.g, "b": value.b, "a": value.a}
	if value is Vector2:
		return {"x": value.x, "y": value.y}
	return value
