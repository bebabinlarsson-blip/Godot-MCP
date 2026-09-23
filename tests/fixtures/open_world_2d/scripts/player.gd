extends CharacterBody2D

const MOVE_SPEED := 260.0


func _physics_process(_delta: float) -> void:
	var direction := Input.get_vector("ui_left", "ui_right", "ui_up", "ui_down")
	if Input.is_key_pressed(KEY_A):
		direction.x -= 1.0
	if Input.is_key_pressed(KEY_D):
		direction.x += 1.0
	if Input.is_key_pressed(KEY_W):
		direction.y -= 1.0
	if Input.is_key_pressed(KEY_S):
		direction.y += 1.0
	velocity = direction.normalized() * MOVE_SPEED
	move_and_slide()


func _draw() -> void:
	draw_circle(Vector2(0.0, 0.0), 12.0, Color("f4c95d"))
	draw_circle(Vector2(-3.5, -2.0), 2.0, Color("382f2f"))
	draw_circle(Vector2(3.5, -2.0), 2.0, Color("382f2f"))
	draw_arc(Vector2(0.0, 1.0), 5.0, 0.3, 2.8, 8, Color("382f2f"), 1.5)
