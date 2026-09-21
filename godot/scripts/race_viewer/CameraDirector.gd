extends RefCounted

var mode := "FULL_FIELD"
var selected_entry_id := ""


func set_mode(next_mode: String) -> void:
	mode = next_mode


func select(entry_id: String) -> void:
	selected_entry_id = entry_id
	if entry_id != "":
		mode = "SELECTED"


func apply(camera: Camera2D, layout: Dictionary, timing: Dictionary, pool: Node2D) -> void:
	var bounds: Dictionary = layout.get("camera_bounds", {})
	var width := float(bounds.get("width", layout.get("canvas_width", 1400)))
	var height := float(bounds.get("height", layout.get("canvas_height", 800)))
	var center := Vector2(width * 0.5, height * 0.5)
	var target := center
	var zoom := Vector2(0.72, 0.72)
	if mode == "FULL_FIELD":
		target = center
		zoom = Vector2(0.70, 0.70)
	else:
		var order: Array = timing.get("order", [])
		var focus_id := selected_entry_id
		if mode == "LEADER" and not order.is_empty():
			focus_id = str(order[0])
		elif mode == "BATTLE" and order.size() >= 2:
			var a: Vector2 = pool.car_position(str(order[0]))
			var b: Vector2 = pool.car_position(str(order[1]))
			target = (a + b) * 0.5
			zoom = Vector2(1.35, 1.35)
			camera.position = target
			camera.zoom = zoom
			return
		if focus_id != "":
			target = pool.car_position(focus_id)
			zoom = Vector2(1.55, 1.55)
	camera.position = target
	camera.zoom = zoom
