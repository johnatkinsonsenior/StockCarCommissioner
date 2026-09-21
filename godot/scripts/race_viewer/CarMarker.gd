extends Node2D


func _draw() -> void:
	var number := str(get_meta("car_number", ""))
	if number == "":
		return
	draw_circle(Vector2.ZERO, 11.0, Color(0, 0, 0, 0.55))
	draw_string(
		ThemeDB.fallback_font,
		Vector2(-8, -4),
		number,
		HORIZONTAL_ALIGNMENT_LEFT,
		-1,
		11,
		Color("f4f4f4")
	)
