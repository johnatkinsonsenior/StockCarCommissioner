extends Control

const SNAPSHOT_PATH := "res://data/ui_snapshot.json"

var snapshot: Dictionary = {}
var screen_name := "menu"
var chrome: VBoxContainer
var body: Control
var status_label: Label


func _ready() -> void:
	snapshot = _load_snapshot()
	_build_shell()
	_show_menu()
	print("UI_READY")
	print("SERIES=", str(snapshot.get("series", "")))
	print("SCREEN=", screen_name)
	if DisplayServer.get_name() == "headless":
		call_deferred("_quit_headless")


func _quit_headless() -> void:
	get_tree().quit()


func _load_snapshot() -> Dictionary:
	if not FileAccess.file_exists(SNAPSHOT_PATH):
		push_warning("UI snapshot missing: " + SNAPSHOT_PATH)
		return {
			"game": "Stock Car Commissioner",
			"series": "Stock Car Series",
			"settings_line": "Settings: Normal | 3 seasons | Autosave Off",
			"menu_items": [],
			"dashboard": {},
			"settings": {},
			"decision": null,
		}
	var file := FileAccess.open(SNAPSHOT_PATH, FileAccess.READ)
	var parsed: Variant = JSON.parse_string(file.get_as_text())
	file.close()
	if typeof(parsed) != TYPE_DICTIONARY:
		push_warning("UI snapshot was not a dictionary")
		return {}
	return parsed


func _build_shell() -> void:
	var bg := ColorRect.new()
	bg.color = Color("0d1117")
	bg.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(bg)

	chrome = VBoxContainer.new()
	chrome.set_anchors_preset(Control.PRESET_FULL_RECT)
	chrome.add_theme_constant_override("separation", 0)
	add_child(chrome)

	var header := PanelContainer.new()
	header.add_theme_stylebox_override("panel", _panel(Color("161b22"), Color("d4a017")))
	var header_row := HBoxContainer.new()
	header_row.add_theme_constant_override("separation", 16)
	header.add_child(header_row)

	var title := Label.new()
	title.text = str(snapshot.get("game", "Stock Car Commissioner")).to_upper()
	title.add_theme_color_override("font_color", Color("d4a017"))
	title.add_theme_font_size_override("font_size", 22)
	header_row.add_child(title)

	var series := Label.new()
	series.text = str(snapshot.get("series", ""))
	series.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	series.add_theme_color_override("font_color", Color("e8e6e3"))
	header_row.add_child(series)

	status_label = Label.new()
	status_label.text = str(snapshot.get("settings_line", ""))
	status_label.add_theme_color_override("font_color", Color("8b9aab"))
	header_row.add_child(status_label)
	chrome.add_child(header)

	var nav := HBoxContainer.new()
	nav.add_theme_constant_override("separation", 8)
	for item in [
		["Menu", "_show_menu"],
		["Dashboard", "_show_dashboard"],
		["Settings", "_show_settings"],
		["Decision", "_show_decision"],
	]:
		var button := Button.new()
		button.text = item[0]
		button.pressed.connect(Callable(self, item[1]))
		nav.add_child(button)
	chrome.add_child(_padded(nav, 12, 8))

	body = Control.new()
	body.size_flags_vertical = Control.SIZE_EXPAND_FILL
	chrome.add_child(body)


func _clear_body() -> void:
	for child in body.get_children():
		child.queue_free()


func _show_menu() -> void:
	screen_name = "menu"
	_clear_body()
	var box := VBoxContainer.new()
	box.add_theme_constant_override("separation", 10)
	body.add_child(_padded(box, 24, 16))
	box.set_anchors_preset(Control.PRESET_FULL_RECT)

	var heading := Label.new()
	heading.text = "MAIN MENU"
	heading.add_theme_font_size_override("font_size", 28)
	heading.add_theme_color_override("font_color", Color("e8e6e3"))
	box.add_child(heading)

	var blurb := Label.new()
	blurb.text = "Godot 4 prototype. Live career numbers come from the Python sim snapshot."
	blurb.add_theme_color_override("font_color", Color("8b9aab"))
	box.add_child(blurb)

	var items: Array = snapshot.get("menu_items", [])
	if items.is_empty():
		items = [
			{"id": "1", "label": "Start new career"},
			{"id": "5", "label": "Game settings"},
			{"id": "7", "label": "Exit"},
		]
	for item in items:
		var row: Dictionary = item
		var button := Button.new()
		button.text = "%s. %s" % [str(row.get("id", "")), str(row.get("label", ""))]
		button.alignment = HORIZONTAL_ALIGNMENT_LEFT
		var action := str(row.get("id", ""))
		button.pressed.connect(_on_menu_item.bind(action))
		box.add_child(button)


func _on_menu_item(action: String) -> void:
	if action == "5":
		_show_settings()
	elif action == "7":
		get_tree().quit()
	else:
		_show_dashboard()


func _show_dashboard() -> void:
	screen_name = "dashboard"
	_clear_body()
	var dash: Dictionary = snapshot.get("dashboard", {})
	var root := HBoxContainer.new()
	root.add_theme_constant_override("separation", 16)
	root.set_anchors_preset(Control.PRESET_FULL_RECT)
	body.add_child(_padded(root, 16, 12))

	var left := VBoxContainer.new()
	left.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	left.add_theme_constant_override("separation", 8)
	root.add_child(left)

	left.add_child(_section_title("Commissioner Dashboard"))
	left.add_child(_muted(str(dash.get("calendar", snapshot.get("calendar", "")))))
	left.add_child(_meter("Integrity", int(dash.get("integrity", 0)), Color("3d9b6e")))
	left.add_child(_meter("Fan interest", int(dash.get("fan_interest", 0)), Color("d4a017")))
	left.add_child(_meter("Controversy", int(dash.get("controversy", 0)), Color("c44536")))
	left.add_child(_meter("Owner pressure", int(dash.get("owner_pressure", 0)), Color("c44536")))
	left.add_child(_meter("Driver sentiment", int(dash.get("driver_sentiment", 0)), Color("3d9b6e")))
	left.add_child(_line("Grade %s (%s/100)" % [str(dash.get("grade", "—")), str(dash.get("score", 0))]))
	left.add_child(_line(str(dash.get("approval", ""))))
	left.add_child(_line(str(dash.get("board", ""))))
	left.add_child(_line("Treasury $%s" % _comma(dash.get("treasury", 0))))
	left.add_child(_line("Naming rights: %s" % str(dash.get("naming_rights", "unsponsored"))))
	left.add_child(_line("TV rights: %s" % str(dash.get("tv_rights", "unsigned"))))
	left.add_child(_muted(str(dash.get("prospects", ""))))
	left.add_child(_muted(str(dash.get("development", ""))))
	left.add_child(_muted(str(dash.get("factory", ""))))

	var right := VBoxContainer.new()
	right.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	right.add_theme_constant_override("separation", 8)
	root.add_child(right)

	right.add_child(_section_title("Grid"))
	for team in dash.get("teams", []):
		var row: Dictionary = team
		right.add_child(_line("%s [%s]  $%s  %s" % [
			str(row.get("name", "")),
			str(row.get("manufacturer", "")),
			_comma(row.get("budget", 0)),
			str(row.get("sponsor", "")),
		]))

	right.add_child(_section_title("Alerts"))
	var alerts: Array = dash.get("alerts", [])
	if alerts.is_empty():
		right.add_child(_muted("No alerts."))
	else:
		for alert in alerts:
			right.add_child(_line("• " + str(alert)))


func _show_settings() -> void:
	screen_name = "settings"
	_clear_body()
	var settings: Dictionary = snapshot.get("settings", {})
	var box := VBoxContainer.new()
	box.add_theme_constant_override("separation", 10)
	body.add_child(_padded(box, 24, 16))
	box.add_child(_section_title("Game Settings"))
	box.add_child(_line("Difficulty: %s" % str(settings.get("difficulty_label", "Normal"))))
	box.add_child(_line("Career length: %s seasons" % str(settings.get("career_seasons", 3))))
	box.add_child(_line("Autosave: %s" % str(settings.get("autosave_label", "Off"))))
	box.add_child(_muted("The Python sim still owns these values. This screen is the Godot prototype."))


func _show_decision() -> void:
	screen_name = "decision"
	_clear_body()
	var decision: Variant = snapshot.get("decision")
	var box := VBoxContainer.new()
	box.add_theme_constant_override("separation", 10)
	body.add_child(_padded(box, 24, 16))
	box.add_child(_section_title("Commissioner Decision"))
	if typeof(decision) != TYPE_DICTIONARY or decision == null:
		box.add_child(_muted("No hearing is queued in this snapshot."))
		return
	var card: Dictionary = decision
	box.add_child(_line(str(card.get("title", "Hearing"))))
	box.add_child(_muted(str(card.get("category", ""))))
	var prompt := Label.new()
	prompt.text = str(card.get("prompt", ""))
	prompt.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	prompt.add_theme_color_override("font_color", Color("e8e6e3"))
	box.add_child(prompt)
	for choice in card.get("choices", []):
		var row: Dictionary = choice
		var button := Button.new()
		button.text = "%s. %s" % [str(row.get("id", "")), str(row.get("label", ""))]
		button.alignment = HORIZONTAL_ALIGNMENT_LEFT
		button.pressed.connect(_show_dashboard)
		box.add_child(button)


func _section_title(text: String) -> Label:
	var label := Label.new()
	label.text = text
	label.add_theme_font_size_override("font_size", 20)
	label.add_theme_color_override("font_color", Color("d4a017"))
	return label


func _line(text: String) -> Label:
	var label := Label.new()
	label.text = text
	label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	label.add_theme_color_override("font_color", Color("e8e6e3"))
	return label


func _muted(text: String) -> Label:
	var label := _line(text)
	label.add_theme_color_override("font_color", Color("8b9aab"))
	return label


func _meter(label_text: String, value: int, fill: Color) -> VBoxContainer:
	var wrap := VBoxContainer.new()
	var caption := Label.new()
	caption.text = "%s  %s/100" % [label_text, str(value)]
	caption.add_theme_color_override("font_color", Color("e8e6e3"))
	wrap.add_child(caption)
	var bar := ProgressBar.new()
	bar.max_value = 100
	bar.value = clamp(value, 0, 100)
	bar.show_percentage = false
	bar.custom_minimum_size = Vector2(0, 14)
	var fill_style := StyleBoxFlat.new()
	fill_style.bg_color = fill
	bar.add_theme_stylebox_override("fill", fill_style)
	wrap.add_child(bar)
	return wrap


func _panel(bg: Color, border: Color) -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = bg
	style.border_color = border
	style.set_border_width_all(1)
	style.content_margin_left = 16
	style.content_margin_right = 16
	style.content_margin_top = 10
	style.content_margin_bottom = 10
	return style


func _padded(child: Control, x: int, y: int) -> MarginContainer:
	var margin := MarginContainer.new()
	margin.set_anchors_preset(Control.PRESET_FULL_RECT)
	margin.add_theme_constant_override("margin_left", x)
	margin.add_theme_constant_override("margin_right", x)
	margin.add_theme_constant_override("margin_top", y)
	margin.add_theme_constant_override("margin_bottom", y)
	margin.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	margin.size_flags_vertical = Control.SIZE_EXPAND_FILL
	margin.add_child(child)
	child.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	child.size_flags_vertical = Control.SIZE_EXPAND_FILL
	return margin


func _comma(value: Variant) -> String:
	var number := int(value)
	var sign := "-" if number < 0 else ""
	var digits := str(abs(number))
	var parts: PackedStringArray = []
	while digits.length() > 3:
		parts.insert(0, digits.substr(digits.length() - 3, 3))
		digits = digits.substr(0, digits.length() - 3)
	parts.insert(0, digits)
	return sign + ",".join(parts)
