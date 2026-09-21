extends Node2D

const POOL_SIZE := 40
const CAR_TEXTURE := preload("res://assets/cars/stock_car_topdown.png")

var _cars: Array[Node2D] = []
var _by_entry := {}


func setup_pool() -> void:
	if not _cars.is_empty():
		return
	var marker_script := preload("res://scripts/race_viewer/CarMarker.gd")
	for index in range(POOL_SIZE):
		var car := Node2D.new()
		car.name = "Car_%02d" % index
		car.set_script(marker_script)
		var sprite := Sprite2D.new()
		sprite.texture = CAR_TEXTURE
		sprite.centered = true
		sprite.name = "Sprite"
		car.add_child(sprite)
		car.visible = false
		add_child(car)
		_cars.append(car)


func bind_entries(entries: Array) -> void:
	setup_pool()
	_by_entry.clear()
	for car in _cars:
		car.visible = false
	var count := mini(entries.size(), _cars.size())
	for index in range(count):
		var entry: Dictionary = entries[index]
		var car := _cars[index]
		var sprite: Sprite2D = car.get_node("Sprite")
		sprite.modulate = Color.html("#%s" % str(entry.get("primary_color", "f5c400")))
		car.set_meta("entry_id", str(entry.get("entry_id", "")))
		car.set_meta("car_number", str(entry.get("car_number", "")))
		car.visible = true
		_by_entry[str(entry.get("entry_id", ""))] = car


func apply_states(states: Dictionary, interpolator: RefCounted, layout: Dictionary, selected_id: String) -> void:
	var racing: Array = layout.get("racing_polyline", [])
	var pit: Array = layout.get("pit_polyline", [])
	var lane_offset := float(layout.get("lane_offset_px", 9))
	for entry_id in _by_entry.keys():
		var car: Node2D = _by_entry[entry_id]
		if not states.has(entry_id):
			car.visible = false
			continue
		var state: Dictionary = states[entry_id]
		var path := str(state.get("path", "RACING"))
		var points: Array = pit if path == "PIT" else racing
		var sample: Dictionary = interpolator.polyline_sample(points, int(state.get("path_progress_ppm", 0)), path != "PIT")
		var pos: Vector2 = sample.get("position", Vector2.ZERO)
		var angle: float = float(sample.get("angle", 0.0))
		var lane := float(state.get("lane_index", 0))
		var normal := Vector2.RIGHT.rotated(angle + PI * 0.5)
		car.position = pos + normal * lane * lane_offset
		car.rotation = angle
		car.modulate.a = 0.35 if str(state.get("status", "RUNNING")) != "RUNNING" and str(state.get("status", "")) != "FINISHED" else 1.0
		car.z_index = 20 if entry_id == selected_id else 10
		car.visible = true
		car.queue_redraw()


func car_position(entry_id: String) -> Vector2:
	if _by_entry.has(entry_id):
		return (_by_entry[entry_id] as Node2D).position
	return Vector2.ZERO


func spawned_count() -> int:
	return _cars.size()


func _draw() -> void:
	pass
