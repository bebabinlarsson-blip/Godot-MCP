@tool
class_name OmniUiTree
extends RefCounted

## Semantic UI tree inspector and automation for Godot Editor.
## Traverses the Editor's GUI Control hierarchy, extracts accessible nodes,
## and simulates click, text typing, and action shortcuts.

static func extract_semantic_tree(root: Node, max_depth: int = 8) -> Dictionary:
	if not is_instance_valid(root):
		return {}
	return _walk_node(root, 0, max_depth)


static func _walk_node(node: Node, depth: int, max_depth: int) -> Dictionary:
	var info: Dictionary = {
		"name": node.name,
		"class": node.get_class(),
		"path": str(node.get_path()),
	}

	if node is Control:
		var ctrl := node as Control
		info["visible"] = ctrl.is_visible_in_tree()
		info["rect"] = {
			"x": ctrl.global_position.x,
			"y": ctrl.global_position.y,
			"w": ctrl.size.x,
			"h": ctrl.size.y,
		}
		if ctrl.tooltip_text:
			info["tooltip"] = ctrl.tooltip_text
		if ctrl is Button:
			info["text"] = ctrl.text
			info["disabled"] = ctrl.disabled
		elif ctrl is LineEdit:
			info["text"] = ctrl.text
			info["placeholder"] = ctrl.placeholder_text
			info["editable"] = ctrl.editable
		elif ctrl is Label:
			info["text"] = ctrl.text
		elif ctrl is TabBar:
			info["current_tab"] = ctrl.current_tab
			info["tab_count"] = ctrl.tab_count

	if depth < max_depth:
		var children: Array = []
		for child in node.get_children():
			if child is Control and not (child as Control).is_visible():
				continue
			children.append(_walk_node(child, depth + 1, max_depth))
		if children.size() > 0:
			info["children"] = children

	return info


static func find_control_by_text(root: Node, text_query: String) -> Control:
	var norm := text_query.to_lower()
	var stack: Array[Node] = [root]
	while stack.size() > 0:
		var current = stack.pop_back()
		if current is Control and current.is_visible_in_tree():
			if current is Button and (current as Button).text.to_lower() == norm:
				return current as Control
			if current.tooltip_text.to_lower().contains(norm):
				return current as Control
		for child in current.get_children():
			stack.push_back(child)
	return null


static func click_control(ctrl: Control) -> bool:
	if not is_instance_valid(ctrl) or not ctrl.is_visible_in_tree():
		return false

	var center := ctrl.global_position + ctrl.size * 0.5

	var press := InputEventMouseButton.new()
	press.button_index = MOUSE_BUTTON_LEFT
	press.pressed = true
	press.position = center
	press.global_position = center
	Input.parse_input_event(press)

	var release := InputEventMouseButton.new()
	release.button_index = MOUSE_BUTTON_LEFT
	release.pressed = false
	release.position = center
	release.global_position = center
	Input.parse_input_event(release)

	return true


static func type_text_into(ctrl: Control, text: String) -> bool:
	if not is_instance_valid(ctrl):
		return false
	if ctrl is LineEdit:
		var le := ctrl as LineEdit
		le.text = text
		le.text_submitted.emit(text)
		return true
	elif ctrl is TextEdit:
		var te := ctrl as TextEdit
		te.text = text
		te.text_changed.emit()
		return true
	return false
