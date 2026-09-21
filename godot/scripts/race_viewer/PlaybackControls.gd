extends Control

signal command(name, value)

var clock_label: Label
var speed_label: Label


func _ready() -> void:
	custom_minimum_size = Vector2(0, 72)
	var panel := ColorRect.new()
	panel.color = Color("000000")
	panel.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(panel)
	var row := HBoxContainer.new()
	row.set_anchors_preset(Control.PRESET_FULL_RECT)
	row.offset_left = 10
	row.offset_right = -10
	row.offset_top = 8
	row.offset_bottom = -8
	row.add_theme_constant_override("separation", 6)
	add_child(row)
	_button(row, "BACK", "back")
	_button(row, "PAUSE", "pause")
	for speed in [0.5, 1.0, 2.0, 4.0, 8.0]:
		_button(row, "%sx" % str(speed), "speed", speed)
	_button(row, "EVENT", "event")
	_button(row, "CAUTION", "caution")
	_button(row, "FINISH", "finish")
	_button(row, "FIELD", "camera", "FULL_FIELD")
	_button(row, "LEADER", "camera", "LEADER")
	_button(row, "BATTLE", "camera", "BATTLE")
	_button(row, "CAR", "camera", "SELECTED")
	_button(row, "DATA", "data")
	_button(row, "SCRUB", "scrub")
	clock_label = Label.new()
	clock_label.add_theme_color_override("font_color", Color("f5c400"))
	row.add_child(clock_label)
	speed_label = Label.new()
	speed_label.add_theme_color_override("font_color", Color("b8b8b8"))
	row.add_child(speed_label)


func set_status(time_ms: int, duration_ms: int, speed: float, playing: bool) -> void:
	clock_label.text = "%s / %s" % [_clock(time_ms), _clock(duration_ms)]
	speed_label.text = ("%s  %sx" % ["LIVE" if playing else "PAUSE", str(speed)])


func _button(host: HBoxContainer, text: String, name: String, value: Variant = null) -> void:
	var button := Button.new()
	button.text = text
	var style := StyleBoxFlat.new()
	style.bg_color = Color("101010")
	style.border_color = Color("f5c400")
	style.set_border_width_all(1)
	style.content_margin_left = 8
	style.content_margin_right = 8
	style.content_margin_top = 4
	style.content_margin_bottom = 4
	button.add_theme_stylebox_override("normal", style)
	button.add_theme_stylebox_override("hover", style)
	button.add_theme_stylebox_override("pressed", style)
	button.add_theme_color_override("font_color", Color("f5c400"))
	button.pressed.connect(func(): command.emit(name, value))
	host.add_child(button)


func _clock(time_ms: int) -> String:
	var seconds := time_ms / 1000
	return "%d:%02d" % [int(seconds / 60), seconds % 60]
