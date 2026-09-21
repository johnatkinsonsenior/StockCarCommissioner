extends Node2D

var layout := {}


func _draw() -> void:
	var width := int(layout.get("canvas_width", 1400))
	var height := int(layout.get("canvas_height", 800))
	draw_rect(Rect2(0, 0, width, height), Color("0b1a10"))
	_ribbon(layout.get("racing_polyline", []), Color("2f2f2f"), 52.0, true)
	_ribbon(layout.get("racing_polyline", []), Color("6d6d6d"), 34.0, true)
	_ribbon(layout.get("racing_polyline", []), Color("ececec"), 3.0, true)
	_ribbon(layout.get("pit_polyline", []), Color("8a7040"), 16.0, false)
	var interpolator := preload("res://scripts/race_viewer/CarInterpolator.gd").new()
	var mark: Dictionary = interpolator.polyline_sample(layout.get("racing_polyline", []), int(layout.get("start_finish_ppm", 0)), true)
	var pos: Vector2 = mark.get("position", Vector2.ZERO)
	var angle: float = float(mark.get("angle", 0.0))
	var across := Vector2.RIGHT.rotated(angle + PI * 0.5) * 26.0
	draw_line(pos - across, pos + across, Color("f4f4f4"), 4.0)


func _ribbon(points: Array, color: Color, width: float, closed: bool) -> void:
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
	# Compatibility renderer can ignore fat polyline widths; stamp the ribbon.
	var radius := width * 0.5
	for index in range(converted.size()):
		draw_circle(converted[index], radius, color)
