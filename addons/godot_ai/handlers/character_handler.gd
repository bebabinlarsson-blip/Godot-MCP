@tool
extends "res://addons/godot_ai/handlers/command_handler.gd"

const ErrorCodes := preload("res://addons/godot_ai/utils/error_codes.gd")

var _undo_redo: EditorUndoRedoManager
var _connection


func _init(undo_redo: EditorUndoRedoManager, connection = null) -> void:
	_undo_redo = undo_redo
	_connection = connection


func scaffold_2d(params: Dictionary) -> Dictionary:
	var scene_check := McpNodeValidator.require_scene_or_error()
	if scene_check.has("error"):
		return scene_check
	var scene_root: Node = scene_check.scene_root

	var parent_path: String = params.get("parent_path", "")
	var parent: Node = scene_root
	if not parent_path.is_empty():
		var resolved := McpNodeValidator.resolve_or_error(parent_path, "parent_path")
		if resolved.has("error"):
			return resolved
		parent = resolved.node

	var char_name: String = params.get("name", "Player")
	var genre: String = params.get("genre", "platformer").to_lower()
	var speed: float = float(params.get("speed", 200.0))
	var jump_velocity: float = float(params.get("jump_velocity", -350.0))
	var acceleration: float = float(params.get("acceleration", 1200.0))
	var friction: float = float(params.get("friction", 1000.0))
	var coyote_time: float = float(params.get("coyote_time", 0.12))
	var jump_buffering: float = float(params.get("jump_buffering", 0.1))
	var attach_camera: bool = bool(params.get("attach_camera", true))
	var script_path: String = params.get("script_path", "")

	var body := CharacterBody2D.new()
	body.name = char_name

	var col_shape := CollisionShape2D.new()
	col_shape.name = "CollisionShape2D"
	var capsule := CapsuleShape2D.new()
	capsule.radius = 16.0
	capsule.height = 48.0
	col_shape.shape = capsule
	body.add_child(col_shape)

	var visual := ColorRect.new()
	visual.name = "PlaceholderVisual"
	visual.size = Vector2(32.0, 48.0)
	visual.position = Vector2(-16.0, -24.0)
	visual.color = Color(0.2, 0.6, 1.0, 0.9)
	body.add_child(visual)

	if attach_camera:
		var cam := Camera2D.new()
		cam.name = "FollowCamera2D"
		cam.position_smoothing_enabled = true
		cam.position_smoothing_speed = 5.0
		var shake_script := GDScript.new()
		shake_script.source_code = "@tool\nextends Camera2D\n\n@export var decay: float = 0.8\n@export var max_offset: Vector2 = Vector2(25.0, 15.0)\n@export var max_roll: float = 0.05\n\nvar trauma: float = 0.0\nvar trauma_power: int = 2\n\nfunc _process(delta: float) -> void:\n\tif trauma > 0.0:\n\t\ttrauma = max(trauma - decay * delta, 0.0)\n\t\tvar s: float = pow(trauma, trauma_power)\n\t\toffset.x = max_offset.x * s * randf_range(-1.0, 1.0)\n\t\toffset.y = max_offset.y * s * randf_range(-1.0, 1.0)\n\t\trotation = max_roll * s * randf_range(-1.0, 1.0)\n\nfunc add_trauma(amount: float) -> void:\n\ttrauma = clamp(trauma + amount, 0.0, 1.0)\n"
		cam.set_script(shake_script)
		body.add_child(cam)

	var code := ""
	if genre == "topdown":
		code = """extends CharacterBody2D

@export var speed: float = %s
@export var acceleration: float = %s
@export var friction: float = %s

func _physics_process(delta: float) -> void:
	var input_vector := Vector2.ZERO
	if Input.is_action_pressed("move_right") or Input.is_action_pressed("ui_right"):
		input_vector.x += 1.0
	if Input.is_action_pressed("move_left") or Input.is_action_pressed("ui_left"):
		input_vector.x -= 1.0
	if Input.is_action_pressed("move_down") or Input.is_action_pressed("ui_down"):
		input_vector.y += 1.0
	if Input.is_action_pressed("move_up") or Input.is_action_pressed("ui_up"):
		input_vector.y -= 1.0

	input_vector = input_vector.normalized()

	if input_vector != Vector2.ZERO:
		velocity = velocity.move_toward(input_vector * speed, acceleration * delta)
	else:
		velocity = velocity.move_toward(Vector2.ZERO, friction * delta)

	move_and_slide()
""" % [str(speed), str(acceleration), str(friction)]
	else:
		code = """extends CharacterBody2D

@export var speed: float = %s
@export var jump_velocity: float = %s
@export var acceleration: float = %s
@export var friction: float = %s
@export var coyote_time_max: float = %s
@export var jump_buffer_max: float = %s

var gravity: float = float(ProjectSettings.get_setting("physics/2d/default_gravity", 980.0))
var coyote_timer: float = 0.0
var jump_buffer_timer: float = 0.0

func _physics_process(delta: float) -> void:
	if is_on_floor():
		coyote_timer = coyote_time_max
	else:
		coyote_timer = max(coyote_timer - delta, 0.0)
		velocity.y += gravity * delta

	if Input.is_action_just_pressed("jump") or Input.is_action_just_pressed("ui_accept"):
		jump_buffer_timer = jump_buffer_max
	else:
		jump_buffer_timer = max(jump_buffer_timer - delta, 0.0)

	if jump_buffer_timer > 0.0 and coyote_timer > 0.0:
		velocity.y = jump_velocity
		jump_buffer_timer = 0.0
		coyote_timer = 0.0

	var dir: float = 0.0
	if Input.is_action_pressed("move_right") or Input.is_action_pressed("ui_right"):
		dir += 1.0
	if Input.is_action_pressed("move_left") or Input.is_action_pressed("ui_left"):
		dir -= 1.0

	if dir != 0.0:
		velocity.x = move_toward(velocity.x, dir * speed, acceleration * delta)
	else:
		velocity.x = move_toward(velocity.x, 0.0, friction * delta)

	move_and_slide()
""" % [str(speed), str(jump_velocity), str(acceleration), str(friction), str(coyote_time), str(jump_buffering)]

	if script_path.is_empty():
		var scripts_dir := "res://scripts"
		if not DirAccess.dir_exists_absolute(scripts_dir):
			DirAccess.make_dir_recursive_absolute(scripts_dir)
		script_path = "%s/%s.gd" % [scripts_dir, char_name.to_snake_case()]

	var script_file := FileAccess.open(script_path, FileAccess.WRITE)
	if script_file != null:
		script_file.store_string(code)
		script_file.close()
		EditorInterface.get_resource_filesystem().reindex_file(script_path)
		var res := load(script_path)
		if res is Script:
			body.set_script(res)
	else:
		var script_res := GDScript.new()
		script_res.source_code = code
		body.set_script(script_res)

	_undo_redo.create_action("Scaffold 2D Character: %s" % char_name)
	_undo_redo.add_do_method(parent, "add_child", body)
	_undo_redo.add_do_reference(body)
	_undo_redo.add_undo_method(parent, "remove_child", body)
	_undo_redo.commit_action()

	_set_owner_recursive(body, scene_root)

	return {
		"character_path": McpScenePath.from_node(body, scene_root),
		"genre": genre,
		"speed": speed,
		"jump_velocity": jump_velocity if genre == "platformer" else 0.0,
		"camera_attached": attach_camera,
		"script_path": script_path,
	}


func scaffold_3d(params: Dictionary) -> Dictionary:
	var scene_check := McpNodeValidator.require_scene_or_error()
	if scene_check.has("error"):
		return scene_check
	var scene_root: Node = scene_check.scene_root

	var parent_path: String = params.get("parent_path", "")
	var parent: Node = scene_root
	if not parent_path.is_empty():
		var resolved := McpNodeValidator.resolve_or_error(parent_path, "parent_path")
		if resolved.has("error"):
			return resolved
		parent = resolved.node

	var char_name: String = params.get("name", "Player3D")
	var genre: String = params.get("genre", "first_person").to_lower()
	var speed: float = float(params.get("speed", 5.0))
	var sprint_speed: float = float(params.get("sprint_speed", 8.0))
	var jump_velocity: float = float(params.get("jump_velocity", 4.5))
	var mouse_sensitivity: float = float(params.get("mouse_sensitivity", 0.002))
	var script_path: String = params.get("script_path", "")

	var body := CharacterBody3D.new()
	body.name = char_name

	var col_shape := CollisionShape3D.new()
	col_shape.name = "CollisionShape3D"
	var capsule := CapsuleShape3D.new()
	capsule.radius = 0.4
	capsule.height = 1.8
	col_shape.shape = capsule
	col_shape.position = Vector3(0.0, 0.9, 0.0)
	body.add_child(col_shape)

	var mesh_inst := MeshInstance3D.new()
	mesh_inst.name = "CharacterMesh"
	var mesh := CapsuleMesh.new()
	mesh.radius = 0.4
	mesh.height = 1.8
	mesh_inst.mesh = mesh
	mesh_inst.position = Vector3(0.0, 0.9, 0.0)
	body.add_child(mesh_inst)

	var cam := Camera3D.new()
	cam.name = "Camera3D"

	if genre == "third_person":
		var spring_arm := SpringArm3D.new()
		spring_arm.name = "SpringArm3D"
		spring_arm.spring_length = 3.5
		spring_arm.position = Vector3(0.0, 1.5, 0.0)
		spring_arm.add_child(cam)
		body.add_child(spring_arm)
	else:
		var head := Node3D.new()
		head.name = "Head"
		head.position = Vector3(0.0, 1.6, 0.0)
		head.add_child(cam)
		body.add_child(head)

	var code := ""
	if genre == "third_person":
		code = """extends CharacterBody3D

@export var speed: float = %s
@export var sprint_speed: float = %s
@export var jump_velocity: float = %s
@export var mouse_sensitivity: float = %s

var gravity: float = float(ProjectSettings.get_setting("physics/3d/default_gravity", 9.8))
@onready var spring_arm: SpringArm3D = $SpringArm3D

func _ready() -> void:
	Input.mouse_mode = Input.MOUSE_MODE_CAPTURED

func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventMouseMotion and Input.mouse_mode == Input.MOUSE_MODE_CAPTURED:
		rotate_y(-event.relative.x * mouse_sensitivity)
		if spring_arm:
			spring_arm.rotate_x(-event.relative.y * mouse_sensitivity)
			spring_arm.rotation.x = clamp(spring_arm.rotation.x, -1.2, 0.8)
	elif event.is_action_pressed("ui_cancel"):
		if Input.mouse_mode == Input.MOUSE_MODE_CAPTURED:
			Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
		else:
			Input.mouse_mode = Input.MOUSE_MODE_CAPTURED

func _physics_process(delta: float) -> void:
	if not is_on_floor():
		velocity.y -= gravity * delta

	if Input.is_action_just_pressed("jump") or Input.is_action_just_pressed("ui_accept"):
		if is_on_floor():
			velocity.y = jump_velocity

	var input_dir := Vector2.ZERO
	if Input.is_action_pressed("move_right") or Input.is_action_pressed("ui_right"):
		input_dir.x += 1.0
	if Input.is_action_pressed("move_left") or Input.is_action_pressed("ui_left"):
		input_dir.x -= 1.0
	if Input.is_action_pressed("move_backward") or Input.is_action_pressed("ui_down"):
		input_dir.y += 1.0
	if Input.is_action_pressed("move_forward") or Input.is_action_pressed("ui_up"):
		input_dir.y -= 1.0

	var direction := (transform.basis * Vector3(input_dir.x, 0, input_dir.y)).normalized()
	var cur_speed := sprint_speed if Input.is_key_pressed(KEY_SHIFT) else speed

	if direction != Vector3.ZERO:
		velocity.x = direction.x * cur_speed
		velocity.z = direction.z * cur_speed
	else:
		velocity.x = move_toward(velocity.x, 0.0, cur_speed)
		velocity.z = move_toward(velocity.z, 0.0, cur_speed)

	move_and_slide()
""" % [str(speed), str(sprint_speed), str(jump_velocity), str(mouse_sensitivity)]
	else:
		code = """extends CharacterBody3D

@export var speed: float = %s
@export var sprint_speed: float = %s
@export var jump_velocity: float = %s
@export var mouse_sensitivity: float = %s

var gravity: float = float(ProjectSettings.get_setting("physics/3d/default_gravity", 9.8))
@onready var head: Node3D = $Head

func _ready() -> void:
	Input.mouse_mode = Input.MOUSE_MODE_CAPTURED

func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventMouseMotion and Input.mouse_mode == Input.MOUSE_MODE_CAPTURED:
		rotate_y(-event.relative.x * mouse_sensitivity)
		if head:
			head.rotate_x(-event.relative.y * mouse_sensitivity)
			head.rotation.x = clamp(head.rotation.x, -1.4, 1.4)
	elif event.is_action_pressed("ui_cancel"):
		if Input.mouse_mode == Input.MOUSE_MODE_CAPTURED:
			Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
		else:
			Input.mouse_mode = Input.MOUSE_MODE_CAPTURED

func _physics_process(delta: float) -> void:
	if not is_on_floor():
		velocity.y -= gravity * delta

	if Input.is_action_just_pressed("jump") or Input.is_action_just_pressed("ui_accept"):
		if is_on_floor():
			velocity.y = jump_velocity

	var input_dir := Vector2.ZERO
	if Input.is_action_pressed("move_right") or Input.is_action_pressed("ui_right"):
		input_dir.x += 1.0
	if Input.is_action_pressed("move_left") or Input.is_action_pressed("ui_left"):
		input_dir.x -= 1.0
	if Input.is_action_pressed("move_backward") or Input.is_action_pressed("ui_down"):
		input_dir.y += 1.0
	if Input.is_action_pressed("move_forward") or Input.is_action_pressed("ui_up"):
		input_dir.y -= 1.0

	var direction := (transform.basis * Vector3(input_dir.x, 0, input_dir.y)).normalized()
	var cur_speed := sprint_speed if Input.is_key_pressed(KEY_SHIFT) else speed

	if direction != Vector3.ZERO:
		velocity.x = direction.x * cur_speed
		velocity.z = direction.z * cur_speed
	else:
		velocity.x = move_toward(velocity.x, 0.0, cur_speed)
		velocity.z = move_toward(velocity.z, 0.0, cur_speed)

	move_and_slide()
""" % [str(speed), str(sprint_speed), str(jump_velocity), str(mouse_sensitivity)]

	if script_path.is_empty():
		var scripts_dir := "res://scripts"
		if not DirAccess.dir_exists_absolute(scripts_dir):
			DirAccess.make_dir_recursive_absolute(scripts_dir)
		script_path = "%s/%s.gd" % [scripts_dir, char_name.to_snake_case()]

	var script_file := FileAccess.open(script_path, FileAccess.WRITE)
	if script_file != null:
		script_file.store_string(code)
		script_file.close()
		EditorInterface.get_resource_filesystem().reindex_file(script_path)
		var res := load(script_path)
		if res is Script:
			body.set_script(res)
	else:
		var script_res := GDScript.new()
		script_res.source_code = code
		body.set_script(script_res)

	_undo_redo.create_action("Scaffold 3D Character: %s" % char_name)
	_undo_redo.add_do_method(parent, "add_child", body)
	_undo_redo.add_do_reference(body)
	_undo_redo.add_undo_method(parent, "remove_child", body)
	_undo_redo.commit_action()

	_set_owner_recursive(body, scene_root)

	return {
		"character_path": McpScenePath.from_node(body, scene_root),
		"genre": genre,
		"speed": speed,
		"sprint_speed": sprint_speed,
		"jump_velocity": jump_velocity,
		"script_path": script_path,
	}


static func _set_owner_recursive(node: Node, scene_root: Node) -> void:
	if node != scene_root:
		node.owner = scene_root
	for child in node.get_children():
		_set_owner_recursive(child, scene_root)
