extends Node2D

var layout := {}


func _draw() -> void:
	var width := int(layout.get("canvas_width", 1400))
	var height := int(layout.get("canvas_height", 800))
	draw_rect(Rect2(0, 0, width, height), Color("07140d"))
	_polyline(layout.get("racing_polyline", []), Color("2b2b2b"), 46.0, true)
	_polyline(layout.get("racing_polyline", []), Color("5a5a5a"), 28.0, true)
	_polyline(layout.get("racing_polyline", []), Color("d8d8d8"), 2.0, true)
	_polyline(layout.get("pit_polyline", []), Color("3a3324"), 14.0, false)
	var interpolator := preload("res://scripts/race_viewer/CarInterpolator.gd").new()
	var mark: Dictionary = interpolator.polyline_sample(layout.get("racing_polyline", []), int(layout.get("start_finish_ppm", 0)), true)
	var pos: Vector2 = mark.get("position", Vector2.ZERO)
	var angle: float = float(mark.get("angle", 0.0))
	var across := Vector2.RIGHT.rotated(angle + PI * 0.5) * 26.0
	draw_line(pos - across, pos + across, Color("f4f4f4"), 4.0)


func _polyline(points: Array, color: Color, width: float, closed: bool) -> void:
	if points.size() < 2:
		return
	var converted: PackedVector2Array = PackedVector2Array()
	for point in points:
		if typeof(point) == TYPE_ARRAY and point.size() >= 2:
			converted.append(Vector2(float(point[0]), float(point[1])))
	if converted.size() < 2:
		return
	if closed:
		converted.append(converted[0])
	draw_polyline(converted, color, width, true)
