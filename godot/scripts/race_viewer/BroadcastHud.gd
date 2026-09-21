extends Control

const TimingTower := preload("res://scripts/race_viewer/TimingTower.gd")
const EventTicker := preload("res://scripts/race_viewer/EventTicker.gd")

var tower := TimingTower.new()
var ticker := EventTicker.new()
var title_label: Label
var meta_label: Label
var flag_label: Label
var tower_box: VBoxContainer
var ticker_box: VBoxContainer
var data_label: Label


func _ready() -> void:
	custom_minimum_size = Vector2(300, 0)
	var panel := ColorRect.new()
	panel.color = Color("000000")
	panel.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(panel)
	var column := VBoxContainer.new()
	column.set_anchors_preset(Control.PRESET_FULL_RECT)
	column.offset_left = 12
	column.offset_right = -12
	column.offset_top = 12
	column.offset_bottom = -12
	column.add_theme_constant_override("separation", 8)
	add_child(column)
	title_label = _label("RACE", Color("f5c400"), 18)
	column.add_child(title_label)
	meta_label = _label("", Color("b8b8b8"), 13)
	column.add_child(meta_label)
	flag_label = _label("GREEN", Color("f5c400"), 16)
	column.add_child(flag_label)
	column.add_child(_label("TIMING", Color("f5c400"), 13))
	tower_box = VBoxContainer.new()
	tower_box.add_theme_constant_override("separation", 2)
	column.add_child(tower_box)
	column.add_child(_label("TICKER", Color("f5c400"), 13))
	ticker_box = VBoxContainer.new()
	ticker_box.add_theme_constant_override("separation", 2)
	column.add_child(ticker_box)
	data_label = _label("", Color("b8b8b8"), 12)
	data_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	column.add_child(data_label)


func apply(bundle: Dictionary, time_ms: int, timing: Dictionary, phase: Dictionary, markers: Array, finished: bool, show_data: bool) -> void:
	var race: Dictionary = bundle.get("race", {})
	var track: Dictionary = bundle.get("track", {})
	title_label.text = str(race.get("title", track.get("name", "RACE"))).to_upper()
	var hide_winner := tower.hide_final and not finished
	var weather := str(race.get("weather", ""))
	meta_label.text = "Lap %s / %s   %s" % [
		str(int(timing.get("race_lap", 0))),
		str(int(track.get("official_distance_laps", 0))),
		weather,
	]
	flag_label.text = str(phase.get("phase", "GREEN"))
	flag_label.add_theme_color_override("font_color", _flag_color(str(phase.get("phase", ""))))
	_fill(tower_box, tower.lines(bundle, timing, finished))
	_fill(ticker_box, ticker.visible_lines(markers, bundle.get("entries", [])))
	if show_data:
		var winner := "" if hide_winner else str(race.get("winner_entry_id", ""))
		data_label.text = "Clock %s   Lead changes %s   Cautions %s%s" % [
			_clock(time_ms),
			str(int(race.get("lead_changes", 0))),
			str(int(race.get("caution_count", 0))),
			"" if winner == "" else "   Winner locked",
		]
	else:
		data_label.text = ""


func set_spoiler_free(enabled: bool) -> void:
	tower.hide_final = enabled


func _fill(box: VBoxContainer, lines: PackedStringArray) -> void:
	while box.get_child_count() > lines.size():
		box.get_child(box.get_child_count() - 1).queue_free()
	while box.get_child_count() < lines.size():
		box.add_child(_label("", Color("f4f4f4"), 12))
	for index in range(lines.size()):
		(box.get_child(index) as Label).text = lines[index]


func _label(text: String, color: Color, size: int) -> Label:
	var label := Label.new()
	label.text = text
	label.add_theme_color_override("font_color", color)
	label.add_theme_font_size_override("font_size", size)
	return label


func _flag_color(phase: String) -> Color:
	if phase == "CAUTION":
		return Color("f5c400")
	if phase == "FINISHED":
		return Color("f4f4f4")
	if phase == "RESTART":
		return Color("d46500")
	return Color("3adf6b")


func _clock(time_ms: int) -> String:
	var seconds := time_ms / 1000
	return "%d:%02d" % [int(seconds / 60), seconds % 60]
