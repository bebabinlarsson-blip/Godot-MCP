@tool
extends "res://addons/godot_ai/handlers/command_handler.gd"

const ErrorCodes := preload("res://addons/godot_ai/utils/error_codes.gd")

var _undo_redo: EditorUndoRedoManager
var _connection


func _init(undo_redo: EditorUndoRedoManager, connection = null) -> void:
	_undo_redo = undo_redo
	_connection = connection


func scaffold_fsm(params: Dictionary) -> Dictionary:
	var target_node_path: String = params.get("target_node_path", "")
	var fsm_name: String = params.get("name", "StateMachine")
	var script_dir: String = params.get("script_dir", "res://scripts/fsm/")
	var preset: String = params.get("preset", "enemy_ai").to_lower()
	var custom_states: Array = params.get("custom_states", [])
	var initial_state_name: String = params.get("initial_state", "")

	if not script_dir.ends_with("/"):
		script_dir += "/"

	var path_err = McpPathValidator.path_error(script_dir, "script_dir")
	if path_err != null:
		return path_err

	if not DirAccess.dir_exists_absolute(script_dir):
		DirAccess.make_dir_recursive_absolute(script_dir)

	# 1. Base State.gd
	var state_base_path := script_dir.path_join("state.gd")
	var state_base_code := """class_name State
extends Node

signal transitioned(new_state_name: String, msg: Dictionary)

var state_machine = null

func enter(_msg: Dictionary = {}) -> void:
	pass

func exit() -> void:
	pass

func update(_delta: float) -> void:
	pass

func physics_update(_delta: float) -> void:
	pass

func handle_input(_event: InputEvent) -> void:
	pass
"""
	var f_state := FileAccess.open(state_base_path, FileAccess.WRITE)
	if f_state:
		f_state.store_string(state_base_code)
		f_state.close()

	# 2. StateMachine.gd
	var sm_path := script_dir.path_join("state_machine.gd")
	var sm_code := """class_name StateMachine
extends Node

signal state_changed(old_state: String, new_state: String)

@export var initial_state: NodePath

var current_state: State = null
var previous_state: State = null
var states: Dictionary = {}

func _ready() -> void:
	if owner != null:
		await owner.ready
	for child in get_children():
		if child is State:
			var key: String = child.name.to_lower()
			states[key] = child
			child.state_machine = self
			child.transitioned.connect(func(next_name: String, msg: Dictionary = {}): change_state(next_name, msg))
	if not initial_state.is_empty():
		var init_node = get_node_or_null(initial_state)
		if init_node is State:
			current_state = init_node
			current_state.enter()
	elif not states.is_empty():
		current_state = states.values()[0]
		current_state.enter()

func _process(delta: float) -> void:
	if current_state:
		current_state.update(delta)

func _physics_process(delta: float) -> void:
	if current_state:
		current_state.physics_update(delta)

func _unhandled_input(event: InputEvent) -> void:
	if current_state:
		current_state.handle_input(event)

func change_state(target_state_name: String, msg: Dictionary = {}) -> void:
	var key: String = target_state_name.to_lower()
	if not states.has(key):
		push_warning("StateMachine: State '%s' does not exist." % target_state_name)
		return
	var new_state: State = states[key]
	if new_state == current_state:
		return
	var old_name := current_state.name if current_state else ""
	if current_state:
		current_state.exit()
	previous_state = current_state
	current_state = new_state
	current_state.enter(msg)
	state_changed.emit(old_name, current_state.name)
"""
	var f_sm := FileAccess.open(sm_path, FileAccess.WRITE)
	if f_sm:
		f_sm.store_string(sm_code)
		f_sm.close()

	# 3. Determine state list and generate concrete state scripts
	var state_configs: Array[Dictionary] = []
	if preset == "character":
		state_configs = [
			{
				"name": "Idle",
				"filename": "idle_state.gd",
				"code": """extends State

func enter(_msg: Dictionary = {}) -> void:
	pass

func update(_delta: float) -> void:
	if Input.is_action_just_pressed("jump"):
		transitioned.emit("Jump", {})
	elif Input.get_axis("move_left", "move_right") != 0.0 or Input.get_axis("move_up", "move_down") != 0.0:
		transitioned.emit("Move", {})
"""
			},
			{
				"name": "Move",
				"filename": "move_state.gd",
				"code": """extends State

func physics_update(_delta: float) -> void:
	if Input.is_action_just_pressed("jump"):
		transitioned.emit("Jump", {})
		return
	var input_x := Input.get_axis("move_left", "move_right")
	var input_y := Input.get_axis("move_up", "move_down")
	if input_x == 0.0 and input_y == 0.0:
		transitioned.emit("Idle", {})
"""
			},
			{
				"name": "Jump",
				"filename": "jump_state.gd",
				"code": """extends State

func enter(_msg: Dictionary = {}) -> void:
	pass

func physics_update(_delta: float) -> void:
	var body = owner as CharacterBody2D
	if body and body.velocity.y >= 0.0:
		transitioned.emit("Fall", {})
"""
			},
			{
				"name": "Fall",
				"filename": "fall_state.gd",
				"code": """extends State

func physics_update(_delta: float) -> void:
	var body = owner as CharacterBody2D
	if body and body.is_on_floor():
		if Input.get_axis("move_left", "move_right") != 0.0:
			transitioned.emit("Move", {})
		else:
			transitioned.emit("Idle", {})
"""
			}
		]
	elif preset == "custom" and not custom_states.is_empty():
		for s in custom_states:
			var s_name := str(s).capitalize().replace(" ", "")
			var s_file := s_name.to_snake_case() + "_state.gd"
			state_configs.append({
				"name": s_name,
				"filename": s_file,
				"code": """extends State

func enter(_msg: Dictionary = {}) -> void:
	pass

func exit() -> void:
	pass

func update(_delta: float) -> void:
	pass

func physics_update(_delta: float) -> void:
	pass
"""
			})
	else: # Default: enemy_ai
		state_configs = [
			{
				"name": "Idle",
				"filename": "idle_state.gd",
				"code": """extends State

@export var wander_timer: float = 2.0
var _timer: float = 0.0

func enter(_msg: Dictionary = {}) -> void:
	_timer = wander_timer

func update(delta: float) -> void:
	_timer -= delta
	if _timer <= 0.0:
		transitioned.emit("Patrol", {})
"""
			},
			{
				"name": "Patrol",
				"filename": "patrol_state.gd",
				"code": """extends State

@export var patrol_duration: float = 3.0
var _timer: float = 0.0

func enter(_msg: Dictionary = {}) -> void:
	_timer = patrol_duration

func update(delta: float) -> void:
	_timer -= delta
	if _timer <= 0.0:
		transitioned.emit("Idle", {})
"""
			},
			{
				"name": "Chase",
				"filename": "chase_state.gd",
				"code": """extends State

@export var attack_range: float = 40.0

func physics_update(_delta: float) -> void:
	# Check distance to target if available
	pass
"""
			},
			{
				"name": "Attack",
				"filename": "attack_state.gd",
				"code": """extends State

@export var attack_duration: float = 0.6
var _timer: float = 0.0

func enter(_msg: Dictionary = {}) -> void:
	_timer = attack_duration

func update(delta: float) -> void:
	_timer -= delta
	if _timer <= 0.0:
		transitioned.emit("Idle", {})
"""
			},
			{
				"name": "Hurt",
				"filename": "hurt_state.gd",
				"code": """extends State

@export var recovery_time: float = 0.3
var _timer: float = 0.0

func enter(_msg: Dictionary = {}) -> void:
	_timer = recovery_time

func update(delta: float) -> void:
	_timer -= delta
	if _timer <= 0.0:
		transitioned.emit("Chase", {})
"""
			},
			{
				"name": "Dead",
				"filename": "dead_state.gd",
				"code": """extends State

func enter(_msg: Dictionary = {}) -> void:
	var actor = owner
	if actor and actor.has_node("CollisionShape2D"):
		actor.get_node("CollisionShape2D").set_deferred("disabled", true)
"""
			}
		]

	var created_scripts: Array[String] = [state_base_path, sm_path]
	for cfg in state_configs:
		var script_file: String = script_dir.path_join(cfg["filename"])
		var f := FileAccess.open(script_file, FileAccess.WRITE)
		if f:
			f.store_string(cfg["code"])
			f.close()
			created_scripts.append(script_file)

	# 4. If target_node_path is specified and scene is open, construct node hierarchy
	var attached := false
	var sm_node_path := ""
	if not target_node_path.is_empty():
		var scene_check := McpNodeValidator.require_scene_or_error()
		if not scene_check.has("error"):
			var scene_root: Node = scene_check.scene_root
			var resolved := McpNodeValidator.resolve_or_error(target_node_path, "target_node_path")
			if not resolved.has("error"):
				var target_node: Node = resolved.node

				var sm_node := Node.new()
				sm_node.name = fsm_name
				var sm_script := load(sm_path)
				if sm_script:
					sm_node.set_script(sm_script)

				var first_child_path := NodePath()
				for cfg in state_configs:
					var st_node := Node.new()
					st_node.name = cfg["name"]
					var st_script := load(script_dir.path_join(cfg["filename"]))
					if st_script:
						st_node.set_script(st_script)
					sm_node.add_child(st_node)
					st_node.owner = scene_root
					if first_child_path.is_empty() and (initial_state_name.is_empty() or cfg["name"].to_lower() == initial_state_name.to_lower()):
						first_child_path = NodePath(cfg["name"])

				if not first_child_path.is_empty():
					sm_node.set("initial_state", first_child_path)

				_undo_redo.create_action("MCP: Scaffold StateMachine on '%s'" % target_node.name)
				_undo_redo.add_do_method(target_node, "add_child", sm_node, true)
				_undo_redo.add_do_method(sm_node, "set_owner", scene_root)
				_undo_redo.add_do_reference(sm_node)
				_undo_redo.add_undo_method(target_node, "remove_child", sm_node)
				_undo_redo.commit_action()

				attached = true
				sm_node_path = McpScenePath.from_node(sm_node, scene_root)

	var efs := EditorInterface.get_resource_filesystem()
	if efs != null:
		for sc in created_scripts:
			efs.update_file(sc)

	var state_names: Array[String] = []
	for cfg in state_configs:
		state_names.append(cfg["name"])

	return {
		"data": {
			"preset": preset,
			"script_dir": script_dir,
			"state_machine_script": sm_path,
			"state_base_script": state_base_path,
			"states": state_names,
			"attached_to_scene": attached,
			"state_machine_node_path": sm_node_path,
		}
	}
