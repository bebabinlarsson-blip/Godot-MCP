extends Node2D

const TILE_SIZE := 64
const BASE_GRASS := Color("668c58")
const LIGHT_GRASS := Color("719760")
const DARK_GRASS := Color("5b7d50")
const WATER := Color("4f91a3")
const PATH := Color("b99b6a")
const TREE := Color("345b3e")
const HOUSE_WALL := Color("c9b27d")
const HOUSE_ROOF := Color("8f5146")


func _ready() -> void:
	print("OPEN_WORLD_2D_READY")


func _process(_delta: float) -> void:
	queue_redraw()


func _draw() -> void:
	var view_size := get_viewport_rect().size
	var camera := get_viewport().get_camera_2d()
	var center := camera.get_screen_center_position() if camera != null else Vector2.ZERO
	var half_view := view_size / 2.0 + Vector2(TILE_SIZE, TILE_SIZE)
	var first_x := floori((center.x - half_view.x) / TILE_SIZE)
	var last_x := ceili((center.x + half_view.x) / TILE_SIZE)
	var first_y := floori((center.y - half_view.y) / TILE_SIZE)
	var last_y := ceili((center.y + half_view.y) / TILE_SIZE)

	for tile_y in range(first_y, last_y + 1):
		for tile_x in range(first_x, last_x + 1):
			var tile_position := Vector2(tile_x * TILE_SIZE, tile_y * TILE_SIZE)
			var roll := _tile_hash(tile_x, tile_y) % 100
			var tile_color := BASE_GRASS
			if roll < 5:
				tile_color = WATER
			elif roll < 26:
				tile_color = DARK_GRASS
			elif roll < 55:
				tile_color = LIGHT_GRASS
			draw_rect(Rect2(tile_position, Vector2(TILE_SIZE, TILE_SIZE)), tile_color)

			if tile_y % 18 == 0 or tile_x % 27 == 0:
				draw_rect(
					Rect2(tile_position + Vector2(4.0, 22.0), Vector2(TILE_SIZE - 8.0, 20.0)),
					PATH
				)
			elif roll > 82 and tile_color != WATER:
				_draw_tree(tile_position + Vector2(32.0, 32.0), roll)

			if tile_x % 41 == 0 and tile_y % 33 == 0:
				_draw_house(tile_position + Vector2(32.0, 10.0))


func _draw_tree(position: Vector2, variation: int) -> void:
	draw_rect(Rect2(position + Vector2(-3.0, 5.0), Vector2(6.0, 16.0)), Color("79583b"))
	draw_circle(position, 13.0 + float(variation % 5), TREE)
	draw_circle(position + Vector2(-4.0, -4.0), 7.0, Color("47714a"))


func _draw_house(position: Vector2) -> void:
	draw_rect(Rect2(position, Vector2(44.0, 34.0)), HOUSE_WALL)
	draw_colored_polygon(
		PackedVector2Array([
			position + Vector2(-5.0, 2.0),
			position + Vector2(22.0, -18.0),
			position + Vector2(49.0, 2.0),
		]),
		HOUSE_ROOF
	)
	draw_rect(Rect2(position + Vector2(17.0, 17.0), Vector2(10.0, 17.0)), Color("654538"))


func _tile_hash(x: int, y: int) -> int:
	var value := x * 374761393 + y * 668265263
	value = (value ^ (value >> 13)) * 1274126177
	return absi(value ^ (value >> 16))
