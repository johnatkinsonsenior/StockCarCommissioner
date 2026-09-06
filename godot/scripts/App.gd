extends Control

const SNAPSHOT_PATH := "res://data/ui_snapshot.json"
const COL_BG := Color("1e1e1e")
const COL_SIDE := Color("141414")
const COL_PANEL := Color("252525")
const COL_BLUE := Color("3a7bd5")
const COL_BLUE_ON := Color("2b6cb0")
const COL_GREEN := Color("2d6a4f")
const COL_GREEN_DIM := Color("1b4332")
const COL_TEXT := Color("f4f4f4")
const COL_MUTED := Color("9aa3ad")
const COL_GOLD := Color("d4a017")
const COL_LINE := Color("3a3a3a")

var snapshot: Dictionary = {}
var screen_name := "mail"
var visited: Dictionary = {}
var selected_mail_id := ""
var mail_read: Dictionary = {}
var sidebar: VBoxContainer
var status_label: Label
var advance_button: Button
var center_body: VBoxContainer
var checklist_box: VBoxContainer
var checklist_progress: Label
var nav_buttons: Dictionary = {}


func _ready() -> void:
	snapshot = _load_snapshot()
	_build_office()
	selected_mail_id = str(_office().get("selected_mail_id", ""))
	if selected_mail_id == "" and not _inbox().is_empty():
		selected_mail_id = str(_inbox()[0].get("id", ""))
	_show_section("mail")
	print("UI_READY")
	print("OFFICE_READY")
	print("LAYOUT=commissioner-desk")
	print("SERIES=", str(snapshot.get("series", "")))
	print("SCREEN=", screen_name)
	print("CHECKLIST=", str(_checklist().size()))
	print("NAV=", str(_nav().size()))
	print("INBOX=", str(_inbox().size()))
	print("INBOX_HEARINGS=", str(_hearing_letters().size()))
	print("MAIL_OPEN=", selected_mail_id)
	if DisplayServer.get_name() == "headless":
		call_deferred("_headless_tour")


func _headless_tour() -> void:
	for item in _checklist():
		var section := str(item.get("section", item.get("id", "")))
		_show_section(section)
		print("VISIT=", section)
		if section == "mail":
			for letter in _inbox():
				var letter_id := str(letter.get("id", ""))
				_open_letter(letter_id)
				print("READ=", letter_id)
				print("READ_KIND=", str(letter.get("kind", "")))
	print("CHECKLIST_DONE=", "%s/%s" % [_completed_count(), _checklist().size()])
	_on_advance()
	print("ADVANCE_STATE=", "unlocked" if _checklist_complete() else "blocked")
	call_deferred("_quit_headless")


func _quit_headless() -> void:
	get_tree().quit()


func _load_snapshot() -> Dictionary:
	if not FileAccess.file_exists(SNAPSHOT_PATH):
		push_warning("UI snapshot missing: " + SNAPSHOT_PATH)
		return {
			"game": "Stock Car Commissioner",
			"series": "Stock Car Series",
			"layout": "commissioner-desk",
			"office": {},
			"dashboard": {},
			"settings": {},
			"decision": null,
			"drivers": [],
			"schedule": [],
		}
	var file := FileAccess.open(SNAPSHOT_PATH, FileAccess.READ)
	var parsed: Variant = JSON.parse_string(file.get_as_text())
	file.close()
	if typeof(parsed) != TYPE_DICTIONARY:
		push_warning("UI snapshot was not a dictionary")
		return {}
	return parsed


func _office() -> Dictionary:
	var office: Variant = snapshot.get("office", {})
	if typeof(office) == TYPE_DICTIONARY:
		return office
	return {}


func _nav() -> Array:
	var nav: Array = _office().get("nav", [])
	if nav.is_empty():
		return [
			{"id": "dashboard", "label": "Dashboard", "group": ""},
			{"id": "mail", "label": "Mail", "group": ""},
			{"id": "settings", "label": "Settings", "group": ""},
			{"id": "quit", "label": "Quit", "group": ""},
		]
	return nav


func _checklist() -> Array:
	return _office().get("checklist", [])


func _build_office() -> void:
	var bg := ColorRect.new()
	bg.color = COL_BG
	bg.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(bg)

	var root := HBoxContainer.new()
	root.set_anchors_preset(Control.PRESET_FULL_RECT)
	root.add_theme_constant_override("separation", 0)
	add_child(root)

	sidebar = VBoxContainer.new()
	sidebar.custom_minimum_size = Vector2(220, 0)
	sidebar.size_flags_vertical = Control.SIZE_EXPAND_FILL
	sidebar.add_theme_constant_override("separation", 6)
	var side_panel := PanelContainer.new()
	side_panel.add_theme_stylebox_override("panel", _panel(COL_SIDE, COL_LINE))
	side_panel.custom_minimum_size = Vector2(220, 0)
	side_panel.size_flags_vertical = Control.SIZE_EXPAND_FILL
	var side_margin := _padded(sidebar, 12, 12)
	side_panel.add_child(side_margin)
	root.add_child(side_panel)
	_build_sidebar()

	var main := VBoxContainer.new()
	main.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	main.size_flags_vertical = Control.SIZE_EXPAND_FILL
	main.add_theme_constant_override("separation", 0)
	root.add_child(main)

	main.add_child(_build_header())
	main.add_child(_build_workspace())


func _build_sidebar() -> void:
	var title := Label.new()
	title.text = "STOCK CAR\nCOMMISSIONER"
	title.add_theme_font_size_override("font_size", 16)
	title.add_theme_color_override("font_color", COL_GOLD)
	sidebar.add_child(title)
	sidebar.add_child(_muted(str(snapshot.get("series", ""))))

	var nav_list := VBoxContainer.new()
	nav_list.add_theme_constant_override("separation", 4)
	var last_group := "___"
	for item in _nav():
		var row: Dictionary = item
		var section_id := str(row.get("id", ""))
		if section_id in ["settings", "quit"]:
			continue
		var group := str(row.get("group", ""))
		if group != last_group:
			last_group = group
			if group != "":
				nav_list.add_child(_group_label(group))
		nav_list.add_child(_make_nav_button(row))

	var scroller := ScrollContainer.new()
	scroller.size_flags_vertical = Control.SIZE_EXPAND_FILL
	scroller.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	scroller.add_child(nav_list)
	nav_list.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	sidebar.add_child(scroller)

	for item in _nav():
		var row: Dictionary = item
		if str(row.get("id", "")) in ["settings", "quit"]:
			sidebar.add_child(_make_nav_button(row))


func _make_nav_button(row: Dictionary) -> Button:
	var button := Button.new()
	button.text = str(row.get("label", ""))
	button.alignment = HORIZONTAL_ALIGNMENT_CENTER
	_style_nav(button, false)
	var section_id := str(row.get("id", ""))
	button.pressed.connect(_on_nav.bind(section_id))
	nav_buttons[section_id] = button
	return button


func _build_header() -> Control:
	var header := PanelContainer.new()
	header.add_theme_stylebox_override("panel", _panel(COL_PANEL, COL_LINE))
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 16)
	header.add_child(row)

	var spacer := Control.new()
	spacer.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	row.add_child(spacer)

	status_label = Label.new()
	status_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	status_label.add_theme_font_size_override("font_size", 20)
	status_label.add_theme_color_override("font_color", COL_TEXT)
	var header_info: Variant = _office().get("header", {})
	var status_text := str(snapshot.get("calendar", ""))
	if typeof(header_info) == TYPE_DICTIONARY:
		status_text = str(header_info.get("status_line", status_text))
	status_label.text = status_text
	row.add_child(status_label)

	var spacer2 := Control.new()
	spacer2.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	row.add_child(spacer2)

	advance_button = Button.new()
	advance_button.text = str(_office().get("advance_label", "Advance"))
	advance_button.custom_minimum_size = Vector2(160, 40)
	advance_button.pressed.connect(_on_advance)
	_style_advance(false)
	row.add_child(advance_button)
	return header


func _build_workspace() -> Control:
	var workspace := HBoxContainer.new()
	workspace.size_flags_vertical = Control.SIZE_EXPAND_FILL
	workspace.add_theme_constant_override("separation", 12)

	var center_panel := PanelContainer.new()
	center_panel.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	center_panel.size_flags_stretch_ratio = 1.6
	center_panel.add_theme_stylebox_override("panel", _panel(COL_PANEL, COL_LINE))
	center_body = VBoxContainer.new()
	center_body.add_theme_constant_override("separation", 10)
	var center_scroll := ScrollContainer.new()
	center_scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	center_scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	var inner := _padded(center_body, 18, 16)
	center_scroll.add_child(inner)
	inner.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	center_panel.add_child(center_scroll)
	workspace.add_child(center_panel)

	var right_panel := PanelContainer.new()
	right_panel.custom_minimum_size = Vector2(280, 0)
	right_panel.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	right_panel.size_flags_stretch_ratio = 0.7
	right_panel.add_theme_stylebox_override("panel", _panel(Color("1a1a1a"), COL_LINE))
	checklist_box = VBoxContainer.new()
	checklist_box.add_theme_constant_override("separation", 8)
	right_panel.add_child(_padded(checklist_box, 16, 16))
	workspace.add_child(right_panel)
	_refresh_checklist()
	return workspace


func _on_nav(section_id: String) -> void:
	if section_id == "quit":
		get_tree().quit()
		return
	_show_section(section_id)


func _show_section(section_id: String) -> void:
	screen_name = section_id
	visited[section_id] = true
	for key in nav_buttons.keys():
		_style_nav(nav_buttons[key], str(key) == section_id)
	_clear_center()
	match section_id:
		"dashboard":
			_fill_dashboard()
		"mail":
			_fill_mail()
		"standings":
			_fill_standings()
		"schedule":
			_fill_schedule()
		"hearings":
			_fill_hearings()
		"teams":
			_fill_teams()
		"drivers":
			_fill_drivers()
		"prospects":
			_fill_prospects()
		"treasury":
			_fill_treasury()
		"television":
			_fill_television()
		"sponsors":
			_fill_sponsors()
		"rulebook":
			_fill_rulebook()
		"board":
			_fill_board()
		"settings":
			_fill_settings()
		_:
			_fill_mail()
	_refresh_checklist()
	_style_advance(_checklist_complete())


func _on_advance() -> void:
	_clear_center()
	if not _checklist_complete():
		print("ADVANCE_BLOCKED")
		center_body.add_child(_title("Advance locked"))
		center_body.add_child(_muted(str(_office().get("advance_hint", "Visit each section first."))))
		center_body.add_child(_line("Completed %s / %s." % [_completed_count(), _checklist().size()]))
		return
	print("ADVANCE_UNLOCKED")
	var hearing := _first_hearing()
	if not hearing.is_empty():
		screen_name = "mail"
		visited["mail"] = true
		selected_mail_id = str(hearing.get("id", ""))
		mail_read[selected_mail_id] = true
		for key in nav_buttons.keys():
			_style_nav(nav_buttons[key], str(key) == "mail")
		print("ADVANCE_HEARING=", str(hearing.get("subject", hearing.get("title", ""))))
		print("MAIL_OPEN=", selected_mail_id)
		print("MAIL_KIND=", "hearing")
		_fill_mail()
		_refresh_checklist()
		_style_advance(true)
		return
	center_body.add_child(_title("Office ready"))
	center_body.add_child(_line("The first weekend will sim from this button in Day 93."))


func _clear_center() -> void:
	for child in center_body.get_children():
		child.queue_free()


func _inbox() -> Array:
	var letters: Array = _office().get("inbox", [])
	if letters.is_empty():
		var mail: Variant = _office().get("mail", {})
		if typeof(mail) == TYPE_DICTIONARY and str(mail.get("body", "")) != "":
			return [{
				"id": str(mail.get("id", "welcome")),
				"kind": str(mail.get("kind", "letter")),
				"from": str(mail.get("from", "Series Office")),
				"subject": str(mail.get("title", "Mail")),
				"body": str(mail.get("body", "")),
				"choices": [],
			}]
	return letters


func _letter_by_id(letter_id: String) -> Dictionary:
	for row in _inbox():
		if typeof(row) == TYPE_DICTIONARY and str(row.get("id", "")) == letter_id:
			return row
	return {}


func _hearing_letters() -> Array:
	var hearings: Array = []
	for row in _inbox():
		if typeof(row) == TYPE_DICTIONARY and str(row.get("kind", "")) == "hearing":
			hearings.append(row)
	return hearings


func _first_hearing() -> Dictionary:
	var hearings := _hearing_letters()
	if hearings.is_empty():
		return {}
	return hearings[0]


func _unread_count() -> int:
	var count := 0
	for row in _inbox():
		if typeof(row) != TYPE_DICTIONARY:
			continue
		var letter_id := str(row.get("id", ""))
		if not mail_read.get(letter_id, false):
			count += 1
	return count


func _open_letter(letter_id: String) -> void:
	selected_mail_id = letter_id
	mail_read[letter_id] = true
	_show_section("mail")


func _kind_tag(kind: String) -> String:
	match kind:
		"hearing":
			return "Hearing · "
		"alert":
			return "Memo · "
		"press":
			return "Press · "
		_:
			return ""


func _make_inbox_button(letter: Dictionary) -> Button:
	var letter_id := str(letter.get("id", ""))
	var kind := str(letter.get("kind", "letter"))
	var read: bool = mail_read.get(letter_id, false)
	var mark := "○" if read else "●"
	if kind == "hearing" and not read:
		mark = "!"
	var button := Button.new()
	button.text = "%s  %s%s" % [mark, _kind_tag(kind), str(letter.get("subject", "Mail"))]
	button.alignment = HORIZONTAL_ALIGNMENT_LEFT
	button.clip_text = true
	button.tooltip_text = "From: %s" % str(letter.get("from", ""))
	var active := letter_id == selected_mail_id
	_style_inbox_button(button, active, kind == "hearing")
	button.pressed.connect(_open_letter.bind(letter_id))
	return button


func _style_inbox_button(button: Button, active: bool, hearing: bool) -> void:
	var style := StyleBoxFlat.new()
	if active:
		style.bg_color = COL_BLUE_ON
	elif hearing:
		style.bg_color = Color("3d2b1f")
	else:
		style.bg_color = COL_PANEL
	style.set_corner_radius_all(4)
	style.content_margin_left = 8
	style.content_margin_right = 8
	style.content_margin_top = 8
	style.content_margin_bottom = 8
	button.add_theme_stylebox_override("normal", style)
	button.add_theme_stylebox_override("hover", style)
	button.add_theme_stylebox_override("pressed", style)
	button.add_theme_color_override("font_color", Color.WHITE)


func _fill_letter_into(container: VBoxContainer, letter: Dictionary) -> void:
	if letter.is_empty():
		container.add_child(_muted("Select a letter."))
		return
	var kind := str(letter.get("kind", "letter"))
	container.add_child(_title(str(letter.get("subject", "Mail"))))
	container.add_child(_muted("From: %s" % str(letter.get("from", "Series Office"))))
	if str(letter.get("category", "")) != "":
		container.add_child(_muted(str(letter.get("category", ""))))
	var body := Label.new()
	body.text = str(letter.get("prompt", letter.get("body", "")))
	if str(letter.get("prompt", "")) == "":
		body.text = str(letter.get("body", ""))
	body.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	body.add_theme_color_override("font_color", COL_TEXT)
	body.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	container.add_child(body)
	if kind == "hearing":
		for choice in letter.get("choices", []):
			if typeof(choice) != TYPE_DICTIONARY:
				continue
			var row: Dictionary = choice
			var button := Button.new()
			button.text = "%s. %s" % [str(row.get("id", "")), str(row.get("label", ""))]
			button.alignment = HORIZONTAL_ALIGNMENT_LEFT
			button.pressed.connect(_on_hearing_choice.bind(str(row.get("id", "")), str(row.get("label", ""))))
			container.add_child(button)
		container.add_child(_muted("Choices display here. Day 98 writes them back to the sim."))


func _on_hearing_choice(choice_id: String, label: String) -> void:
	print("CHOICE_DISPLAY=", choice_id)
	print("CHOICE_LABEL=", label)


func _refresh_mail_badge() -> void:
	if not nav_buttons.has("mail"):
		return
	var unread := _unread_count()
	nav_buttons["mail"].text = "Mail (%s)" % str(unread) if unread > 0 else "Mail"


func _dash() -> Dictionary:
	var dash: Variant = snapshot.get("dashboard", {})
	if typeof(dash) == TYPE_DICTIONARY:
		return dash
	return {}


func _fill_mail() -> void:
	var letters := _inbox()
	if letters.is_empty():
		var mail: Dictionary = {}
		var raw: Variant = _office().get("mail", {})
		if typeof(raw) == TYPE_DICTIONARY:
			mail = raw
		center_body.add_child(_title(str(mail.get("title", "Mail"))))
		center_body.add_child(_muted("From: %s" % str(mail.get("from", "Series Office"))))
		var body := Label.new()
		body.text = str(mail.get("body", ""))
		body.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		body.add_theme_color_override("font_color", COL_TEXT)
		center_body.add_child(body)
		print("INBOX=0")
		print("MAIL_OPEN=")
		print("MAIL_KIND=letter")
		return
	if selected_mail_id == "":
		selected_mail_id = str(_office().get("selected_mail_id", ""))
	if selected_mail_id == "":
		selected_mail_id = str(letters[0].get("id", ""))
	mail_read[selected_mail_id] = true
	var split := HBoxContainer.new()
	split.add_theme_constant_override("separation", 18)
	split.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	split.size_flags_vertical = Control.SIZE_EXPAND_FILL
	var list_col := VBoxContainer.new()
	list_col.custom_minimum_size = Vector2(280, 0)
	list_col.add_theme_constant_override("separation", 6)
	list_col.add_child(_title("Inbox"))
	list_col.add_child(_muted("%s letters · %s unread" % [str(letters.size()), str(_unread_count())]))
	for letter in letters:
		list_col.add_child(_make_inbox_button(letter))
	split.add_child(list_col)
	var body_col := VBoxContainer.new()
	body_col.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	body_col.add_theme_constant_override("separation", 10)
	_fill_letter_into(body_col, _letter_by_id(selected_mail_id))
	split.add_child(body_col)
	center_body.add_child(split)
	var opened := _letter_by_id(selected_mail_id)
	print("INBOX=", str(letters.size()))
	print("INBOX_HEARINGS=", str(_hearing_letters().size()))
	print("MAIL_OPEN=", selected_mail_id)
	print("MAIL_KIND=", str(opened.get("kind", "letter")))


func _fill_dashboard() -> void:
	var dash := _dash()
	center_body.add_child(_title("Commissioner Dashboard"))
	center_body.add_child(_muted(str(dash.get("calendar", snapshot.get("calendar", "")))))
	center_body.add_child(_meter("Integrity", int(dash.get("integrity", 0)), Color("3d9b6e")))
	center_body.add_child(_meter("Fan interest", int(dash.get("fan_interest", 0)), COL_GOLD))
	center_body.add_child(_meter("Controversy", int(dash.get("controversy", 0)), Color("c44536")))
	center_body.add_child(_meter("Owner pressure", int(dash.get("owner_pressure", 0)), Color("c44536")))
	center_body.add_child(_meter("Driver sentiment", int(dash.get("driver_sentiment", 0)), Color("3d9b6e")))
	center_body.add_child(_line("Grade %s (%s/100)" % [str(dash.get("grade", "—")), str(dash.get("score", 0))]))
	center_body.add_child(_line(str(dash.get("approval", ""))))
	center_body.add_child(_line(str(dash.get("board", ""))))
	center_body.add_child(_line("Treasury $%s" % _comma(dash.get("treasury", 0))))
	var alerts: Array = dash.get("alerts", [])
	center_body.add_child(_title("Alerts"))
	if alerts.is_empty():
		center_body.add_child(_muted("No alerts."))
	else:
		for alert in alerts:
			center_body.add_child(_line("• " + str(alert)))


func _fill_standings() -> void:
	center_body.add_child(_title("Standings"))
	center_body.add_child(_muted("Premier grid. Points update when weekends are Advanced."))
	var drivers: Array = snapshot.get("drivers", [])
	if drivers.is_empty():
		center_body.add_child(_muted("No drivers in this snapshot."))
		return
	for row in drivers:
		var item: Dictionary = row
		center_body.add_child(_line("%s  (%s)  %s pts  %s wins" % [
			str(item.get("name", "")),
			str(item.get("team", "")),
			str(item.get("points", 0)),
			str(item.get("wins", 0)),
		]))


func _fill_schedule() -> void:
	center_body.add_child(_title("Schedule"))
	var races: Array = snapshot.get("schedule", [])
	if races.is_empty():
		center_body.add_child(_muted("No calendar in this snapshot."))
		return
	for row in races:
		var item: Dictionary = row
		center_body.add_child(_line("R%s  %s  (%s)" % [
			str(item.get("race", "")),
			str(item.get("name", "")),
			str(item.get("type", "")),
		]))


func _fill_hearings() -> void:
	center_body.add_child(_title("Hearings"))
	var hearings := _hearing_letters()
	if hearings.is_empty():
		center_body.add_child(_muted("No hearing is in the inbox."))
		return
	center_body.add_child(_muted("Open a letter from the inbox to rule. Choices display here until Day 98 writes them back."))
	for letter in hearings:
		var row: Dictionary = letter
		center_body.add_child(_line(str(row.get("subject", "Hearing"))))
		center_body.add_child(_muted("From: %s" % str(row.get("from", ""))))
		var button := Button.new()
		button.text = "Open in Mail"
		button.alignment = HORIZONTAL_ALIGNMENT_LEFT
		button.pressed.connect(_open_letter.bind(str(row.get("id", ""))))
		center_body.add_child(button)


func _fill_teams() -> void:
	center_body.add_child(_title("Teams"))
	for team in _dash().get("teams", []):
		var row: Dictionary = team
		center_body.add_child(_line("%s — %s" % [str(row.get("name", "")), str(row.get("owner", ""))]))
		center_body.add_child(_muted("%s  $%s  %s" % [
			str(row.get("manufacturer", "")),
			_comma(row.get("budget", 0)),
			str(row.get("sponsor", "")),
		]))


func _fill_drivers() -> void:
	center_body.add_child(_title("Drivers"))
	for row in snapshot.get("drivers", []):
		var item: Dictionary = row
		center_body.add_child(_line("%s  %s  (%s)" % [
			str(item.get("name", "")),
			str(item.get("team", "")),
			str(item.get("personality", "")),
		]))


func _fill_prospects() -> void:
	center_body.add_child(_title("Prospects"))
	center_body.add_child(_line(str(_dash().get("prospects", "No prospect book."))))
	center_body.add_child(_muted(str(_dash().get("development", ""))))


func _fill_treasury() -> void:
	center_body.add_child(_title("Treasury"))
	center_body.add_child(_line("$%s" % _comma(_dash().get("treasury", 0))))
	center_body.add_child(_muted("Fines, purses, and rights fees land here. Advance weekends to move money."))


func _fill_television() -> void:
	center_body.add_child(_title("Television"))
	center_body.add_child(_line("Naming rights: %s" % str(_dash().get("naming_rights", "unsponsored"))))
	center_body.add_child(_line("TV rights: %s" % str(_dash().get("tv_rights", "unsigned"))))


func _fill_sponsors() -> void:
	center_body.add_child(_title("Sponsors"))
	for team in _dash().get("teams", []):
		var row: Dictionary = team
		center_body.add_child(_line("%s — %s" % [str(row.get("name", "")), str(row.get("sponsor", ""))]))


func _fill_rulebook() -> void:
	center_body.add_child(_title("Rulebook"))
	var policies: Array = _dash().get("policies", [])
	if policies.is_empty():
		center_body.add_child(_muted("No policies in this snapshot."))
		return
	for policy in policies:
		center_body.add_child(_line(str(policy)))


func _fill_board() -> void:
	center_body.add_child(_title("Board"))
	center_body.add_child(_line(str(_dash().get("board", "Board not seated."))))
	center_body.add_child(_line(str(_dash().get("approval", ""))))


func _fill_settings() -> void:
	var settings: Dictionary = snapshot.get("settings", {})
	center_body.add_child(_title("Settings"))
	center_body.add_child(_line("Difficulty: %s" % str(settings.get("difficulty_label", "Normal"))))
	center_body.add_child(_line("Career length: %s seasons" % str(settings.get("career_seasons", 3))))
	center_body.add_child(_line("Autosave: %s" % str(settings.get("autosave_label", "Off"))))
	center_body.add_child(_muted(str(snapshot.get("settings_line", ""))))


func _refresh_checklist() -> void:
	for child in checklist_box.get_children():
		child.queue_free()
	checklist_box.add_child(_title("Before You Begin"))
	checklist_box.add_child(_muted("Visit each section to unlock the first weekend."))
	for item in _checklist():
		var row: Dictionary = item
		var section := str(row.get("section", row.get("id", "")))
		var mark := "●" if visited.get(section, false) else "○"
		checklist_box.add_child(_line("%s  %s" % [mark, str(row.get("label", ""))]))
	checklist_progress = _muted("%s / %s completed" % [_completed_count(), _checklist().size()])
	checklist_box.add_child(checklist_progress)
	_refresh_mail_badge()


func _completed_count() -> int:
	var count := 0
	for item in _checklist():
		var section := str(item.get("section", item.get("id", "")))
		if visited.get(section, false):
			count += 1
	return count


func _checklist_complete() -> bool:
	var total := _checklist().size()
	return total > 0 and _completed_count() >= total


func _title(text: String) -> Label:
	var label := Label.new()
	label.text = text
	label.add_theme_font_size_override("font_size", 22)
	label.add_theme_color_override("font_color", COL_TEXT)
	return label


func _line(text: String) -> Label:
	var label := Label.new()
	label.text = text
	label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	label.add_theme_color_override("font_color", COL_TEXT)
	return label


func _muted(text: String) -> Label:
	var label := _line(text)
	label.add_theme_color_override("font_color", COL_MUTED)
	return label


func _group_label(text: String) -> Control:
	var wrap := HBoxContainer.new()
	var left := ColorRect.new()
	left.color = COL_LINE
	left.custom_minimum_size = Vector2(16, 1)
	left.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	var label := Label.new()
	label.text = "  %s  " % text
	label.add_theme_color_override("font_color", COL_MUTED)
	var right := ColorRect.new()
	right.color = COL_LINE
	right.custom_minimum_size = Vector2(16, 1)
	right.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	right.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	wrap.add_child(left)
	wrap.add_child(label)
	wrap.add_child(right)
	return wrap


func _meter(label_text: String, value: int, fill: Color) -> VBoxContainer:
	var wrap := VBoxContainer.new()
	var caption := Label.new()
	caption.text = "%s  %s/100" % [label_text, str(value)]
	caption.add_theme_color_override("font_color", COL_TEXT)
	wrap.add_child(caption)
	var bar := ProgressBar.new()
	bar.max_value = 100
	bar.value = clamp(value, 0, 100)
	bar.show_percentage = false
	bar.custom_minimum_size = Vector2(0, 12)
	var fill_style := StyleBoxFlat.new()
	fill_style.bg_color = fill
	bar.add_theme_stylebox_override("fill", fill_style)
	wrap.add_child(bar)
	return wrap


func _style_nav(button: Button, active: bool) -> void:
	var style := StyleBoxFlat.new()
	style.bg_color = COL_BLUE_ON if active else COL_BLUE
	style.set_corner_radius_all(6)
	style.content_margin_left = 8
	style.content_margin_right = 8
	style.content_margin_top = 5
	style.content_margin_bottom = 5
	button.add_theme_stylebox_override("normal", style)
	button.add_theme_stylebox_override("hover", style)
	button.add_theme_stylebox_override("pressed", style)
	button.add_theme_color_override("font_color", Color.WHITE)


func _style_advance(unlocked: bool) -> void:
	if advance_button == null:
		return
	var style := StyleBoxFlat.new()
	style.bg_color = COL_GREEN if unlocked else COL_GREEN_DIM
	style.set_corner_radius_all(6)
	style.content_margin_left = 16
	style.content_margin_right = 16
	style.content_margin_top = 10
	style.content_margin_bottom = 10
	advance_button.add_theme_stylebox_override("normal", style)
	advance_button.add_theme_stylebox_override("hover", style)
	advance_button.add_theme_stylebox_override("pressed", style)
	advance_button.add_theme_color_override("font_color", Color.WHITE)


func _panel(bg: Color, border: Color) -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = bg
	style.border_color = border
	style.set_border_width_all(1)
	style.content_margin_left = 12
	style.content_margin_right = 12
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
