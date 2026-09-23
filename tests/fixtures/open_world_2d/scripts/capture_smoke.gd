extends Node2D


func _draw() -> void:
	var size := get_viewport_rect().size
	var half := size / 2.0
	draw_rect(Rect2(Vector2.ZERO, half), Color(1, 0, 0))
	draw_rect(Rect2(Vector2(half.x, 0), half), Color(0, 1, 0))
	draw_rect(Rect2(Vector2(0, half.y), half), Color(0, 0, 1))
	draw_rect(Rect2(half, half), Color(1, 1, 1))
