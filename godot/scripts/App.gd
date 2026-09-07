extends Control

const SNAPSHOT_PATH := "res://data/ui_snapshot.json"
const COL_BG := Color("1a0c0e")
const COL_SIDE := Color("140808")
const COL_PANEL := Color("2a1418")
const COL_CRIMSON := Color("8b1e2d")
const COL_CRIMSON_ON := Color("c4283a")
const COL_BLUE := Color("8b1e2d")
const COL_BLUE_ON := Color("c4283a")
const COL_GREEN := Color("c9a227")
const COL_GREEN_DIM := Color("5c4a18")
const COL_TEXT := Color("f7f4ee")
const COL_MUTED := Color("c4b8a8")
const COL_GOLD := Color("d4a017")
const COL_LINE := Color("8a5a28")

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
var hearing_held := false
var era_book := "pinnacle"
var profile_team := ""
var profile_driver := ""
var profile_season := ""


func _ready() -> void:
	snapshot = _load_snapshot()
	_build_office()
	selected_mail_id = str(_office().get("selected_mail_id", ""))
	if selected_mail_id == "" and not _inbox().is_empty():
		selected_mail_id = str(_inbox()[0].get("id", ""))
	var live_era := ""
	var settings_info: Variant = snapshot.get("settings", {})
	if typeof(settings_info) == TYPE_DICTIONARY:
		live_era = str(settings_info.get("era_book", ""))
	if live_era != "":
		era_book = live_era
	_show_section("mail")
	print("UI_READY")
	print("OFFICE_READY")
	print("PALETTE=", str(snapshot.get("palette", "")))
	print("LAYOUT=commissioner-desk")
	print("SERIES=", str(snapshot.get("series", "")))
	print("SCREEN=", screen_name)
	print("CHECKLIST=", str(_checklist().size()))
	print("NAV=", str(_nav().size()))
	print("INBOX=", str(_inbox().size()))
	print("INBOX_HEARINGS=", str(_hearing_letters().size()))
	print("MAIL_OPEN=", selected_mail_id)
	print("APPLY_SCRIPT=", str(_office().get("apply_script", "")))
	print("ALERT_MAIL=", str(_alert_letters().size()))
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
	var hearing := _first_hearing()
	if not hearing.is_empty():
		var choices: Array = hearing.get("choices", [])
		if not choices.is_empty() and typeof(choices[0]) == TYPE_DICTIONARY:
			var first: Dictionary = choices[0]
			_on_hearing_choice(
				str(hearing.get("hearing_id", "")),
				str(first.get("id", "1")),
				str(first.get("label", "")),
			)
	_on_advance()
	print("ADVANCE_STATE=", "unlocked" if _checklist_complete() else "blocked")
	_on_advance()
	_show_section("standings")
	_show_section("schedule")
	_show_section("teams")
	_show_section("drivers")
	_show_section("prospects")
	_show_section("treasury")
	_show_section("television")
	_show_section("sponsors")
	_show_section("hearings")
	_show_section("mail")
	var shops: Array = _as_array(snapshot.get("teams", []))
	if not shops.is_empty() and typeof(shops[0]) == TYPE_DICTIONARY:
		profile_team = str(shops[0].get("id", shops[0].get("name", "")))
		_show_section("teams")
		print("PROFILE_TEAM=", profile_team)
	var grid: Array = _as_array(snapshot.get("drivers", []))
	if not grid.is_empty() and typeof(grid[0]) == TYPE_DICTIONARY:
		profile_driver = str(grid[0].get("id", grid[0].get("name", "")))
		_show_section("drivers")
		print("PROFILE_DRIVER=", profile_driver)
	_show_section("history")
	var seasons: Array = _as_array(_as_dict(snapshot.get("history", {})).get("seasons", []))
	if not seasons.is_empty() and typeof(seasons[0]) == TYPE_DICTIONARY:
		profile_season = str(seasons[0].get("id", seasons[0].get("season", "")))
		_show_section("history")
		print("HISTORY_SEASON=", profile_season)
	_show_section("settings")
	_on_office_save("desk")
	_on_new_career("1970s")
	_on_office_load("desk")
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
	sidebar.add_child(_gold_rule())
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
	if section_id == "teams":
		profile_team = ""
	if section_id == "drivers":
		profile_driver = ""
	if section_id == "history":
		profile_season = ""
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
		"history":
			_fill_history()
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
	if not hearing.is_empty() and not hearing_held:
		hearing_held = true
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
	_run_office_week()


func _run_office_week() -> void:
	var python := str(_office().get("advance_python", ""))
	var script := str(_office().get("advance_script", ""))
	if python == "" or script == "":
		print("WEEK_OK=0")
		print("WEEK_ERROR=missing-advance-command")
		center_body.add_child(_title("Advance failed"))
		center_body.add_child(_muted("The office session is missing the week script."))
		return
	var output: Array = []
	var code := OS.execute(python, PackedStringArray([script]), output, true)
	var text := ""
	for line in output:
		text += str(line) + "\n"
		print(str(line))
	if code != 0 or text.find("WEEK_OK=1") < 0:
		print("WEEK_OK=0")
		center_body.add_child(_title("Advance failed"))
		center_body.add_child(_muted("The week script did not finish. Check the Python career."))
		center_body.add_child(_line(text.substr(0, 800)))
		return
	hearing_held = false
	_reload_office()
	print("WEEK_RELOADED=1")
	print("CALENDAR=", str(snapshot.get("calendar", "")))
	_show_section("mail")
	_style_advance(true)


func _reload_office() -> void:
	snapshot = _load_snapshot()
	if status_label != null:
		var header_info: Variant = _office().get("header", {})
		var status_text := str(snapshot.get("calendar", ""))
		if typeof(header_info) == TYPE_DICTIONARY:
			status_text = str(header_info.get("status_line", status_text))
		status_label.text = status_text
	if advance_button != null:
		advance_button.text = str(_office().get("advance_label", "Advance"))
	selected_mail_id = str(_office().get("selected_mail_id", ""))
	mail_read.clear()


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


func _alert_letters() -> Array:
	var memos: Array = []
	for row in _inbox():
		if typeof(row) == TYPE_DICTIONARY and str(row.get("kind", "")) == "alert":
			memos.append(row)
	return memos


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
		var letter: Dictionary = row
		var letter_id := str(letter.get("id", ""))
		if mail_read.get(letter_id, false):
			continue
		if letter.has("unread") and not bool(letter.get("unread", true)):
			continue
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
		"recap":
			return "Recap · "
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
	_style_inbox_button(button, active, kind)
	button.pressed.connect(_open_letter.bind(letter_id))
	return button


func _style_inbox_button(button: Button, active: bool, kind: String) -> void:
	var style := StyleBoxFlat.new()
	if active:
		style.bg_color = COL_BLUE_ON
	elif kind == "hearing":
		style.bg_color = Color("3d2b1f")
	elif kind == "recap":
		style.bg_color = COL_GREEN_DIM
	else:
		style.bg_color = COL_PANEL
	style.set_corner_radius_all(2)
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
			button.pressed.connect(_on_hearing_choice.bind(
				str(letter.get("hearing_id", "")),
				str(row.get("id", "")),
				str(row.get("label", "")),
			))
			container.add_child(button)
		container.add_child(_muted("Pick a ruling. It writes back to the career."))


func _on_hearing_choice(hearing_id: String, choice_id: String, label: String) -> void:
	print("CHOICE_DISPLAY=", choice_id)
	print("CHOICE_LABEL=", label)
	print("HEARING_ID=", hearing_id)
	var python := str(_office().get("apply_python", _office().get("advance_python", "")))
	var script := str(_office().get("apply_script", ""))
	if python == "" or script == "" or hearing_id == "" or choice_id == "":
		print("HEARING_OK=0")
		print("HEARING_ERROR=missing-apply-command")
		return
	var output: Array = []
	var code := OS.execute(python, PackedStringArray([script, hearing_id, choice_id]), output, true)
	var text := ""
	for line in output:
		text += str(line) + "\n"
		print(str(line))
	if code != 0 or text.find("HEARING_OK=1") < 0:
		print("HEARING_OK=0")
		return
	hearing_held = true
	_reload_office()
	print("HEARING_RELOADED=1")
	_show_section("mail")


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
	print("ALERT_MAIL=", str(_alert_letters().size()))
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
	center_body.add_child(_gold_rule())
	center_body.add_child(_muted("Cup points. The table updates when you Advance a weekend."))
	_fill_recap_card()
	var rows: Array = _as_array(snapshot.get("standings", snapshot.get("drivers", [])))
	if rows.is_empty():
		center_body.add_child(_muted("No drivers in this snapshot."))
		print("STANDINGS_TOP=")
		print("STANDINGS_RANK=")
		return
	rows.sort_custom(func(left, right):
		var a: Dictionary = left
		var b: Dictionary = right
		var a_pts := _as_int(a.get("points", 0))
		var b_pts := _as_int(b.get("points", 0))
		if a_pts == b_pts:
			return _as_int(a.get("wins", 0)) > _as_int(b.get("wins", 0))
		return a_pts > b_pts
	)
	var leader: Dictionary = rows[0]
	print("STANDINGS_TOP=", str(leader.get("name", "")))
	print("STANDINGS_POINTS=", str(_as_int(leader.get("points", 0))))
	print("STANDINGS_RANK=", str(_as_int(leader.get("rank", 1))))
	var index := 1
	for row in rows:
		var item: Dictionary = row
		var rank := _as_int(item.get("rank", index))
		var wins := _as_int(item.get("wins", 0))
		var win_word := "win" if wins == 1 else "wins"
		var line := "#%s  %s    %s pts    %s %s" % [
			str(rank),
			str(item.get("name", "")),
			str(_as_int(item.get("points", 0))),
			str(wins),
			win_word,
		]
		if index == 1:
			center_body.add_child(_gold_line(line))
		else:
			center_body.add_child(_line(line))
		center_body.add_child(_muted(str(item.get("team", ""))))
		index += 1


func _fill_schedule() -> void:
	center_body.add_child(_title("Schedule"))
	center_body.add_child(_gold_rule())
	var races: Array = _as_array(snapshot.get("schedule", []))
	if races.is_empty():
		center_body.add_child(_muted("No calendar in this snapshot."))
		print("SCHEDULE_COMPLETE=0")
		print("SCHEDULE_NEXT=")
		return
	_fill_recap_card()
	var done := 0
	var next_name := ""
	for row in races:
		var item: Dictionary = row
		var finished := bool(item.get("complete", false))
		var is_next := bool(item.get("next", false))
		if finished:
			done += 1
		if is_next:
			next_name = str(item.get("name", ""))
		var tag := "    "
		if finished:
			tag = "DONE"
		elif is_next:
			tag = "NEXT"
		center_body.add_child(_line("%s  R%s  %s" % [
			tag,
			str(_as_int(item.get("race", 0))),
			str(item.get("name", "")),
		]))
		center_body.add_child(_muted(str(item.get("type", ""))))
	print("SCHEDULE_COMPLETE=", str(done))
	print("SCHEDULE_NEXT=", next_name)


func _fill_hearings() -> void:
	center_body.add_child(_title("Hearings"))
	center_body.add_child(_gold_rule())
	var hearings := _hearing_letters()
	print("HEARINGS=", str(hearings.size()))
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
	if profile_team != "":
		_fill_team_profile()
		return
	center_body.add_child(_title("Teams"))
	center_body.add_child(_gold_rule())
	center_body.add_child(_muted("Shops on the Cup charter. Click a shop for the full card. You run the series, not a car."))
	var shops: Array = _as_array(snapshot.get("teams", _dash().get("teams", [])))
	print("TEAMS=", str(shops.size()))
	if shops.is_empty():
		center_body.add_child(_muted("No teams in this snapshot."))
		return
	for team in shops:
		var row: Dictionary = team
		var team_id := str(row.get("id", row.get("name", "")))
		center_body.add_child(_profile_button(str(row.get("name", "")), _open_team_profile.bind(team_id)))
		center_body.add_child(_line("Owner: %s  ·  %s" % [
			str(row.get("owner", "")),
			str(row.get("owner_priority", "")),
		]))
		center_body.add_child(_muted("%s  ·  car %s  ·  crew %s  ·  prestige %s" % [
			str(row.get("manufacturer", "")),
			str(_as_int(row.get("car_rating", 0))),
			str(_as_int(row.get("crew_rating", 0))),
			str(_as_int(row.get("prestige", 0))),
		]))
		center_body.add_child(_muted("Budget $%s  ·  %s" % [
			_comma(row.get("budget", 0)),
			str(row.get("sponsor", "unsponsored")),
		]))
		center_body.add_child(_muted("Factory: %s" % str(row.get("factory", ""))))


func _fill_team_profile() -> void:
	var shops: Array = _as_array(snapshot.get("teams", []))
	var row := _row_by_id(shops, profile_team)
	center_body.add_child(_title("Team profile"))
	center_body.add_child(_gold_rule())
	center_body.add_child(_profile_button("All shops", _open_team_profile.bind("")))
	if row.is_empty():
		center_body.add_child(_muted("That shop is not on the charter."))
		print("PROFILE_TEAM=")
		return
	print("PROFILE_TEAM=", str(row.get("id", row.get("name", ""))))
	center_body.add_child(_gold_line(str(row.get("name", ""))))
	center_body.add_child(_line("%s  ·  owner %s (%s)" % [
		str(row.get("manufacturer", "")),
		str(row.get("owner", "")),
		str(row.get("owner_personality", row.get("owner_priority", ""))),
	]))
	center_body.add_child(_muted("Priority %s  ·  factory %s" % [
		str(row.get("owner_priority", "")),
		str(row.get("factory", "")),
	]))
	center_body.add_child(_line("Car %s  ·  crew %s  ·  reliability %s  ·  engineering %s" % [
		str(_as_int(row.get("car_rating", 0))),
		str(_as_int(row.get("crew_rating", 0))),
		str(_as_int(row.get("reliability", 0))),
		str(_as_int(row.get("engineering", 0))),
	]))
	center_body.add_child(_muted("Prestige %s  ·  facility %s  ·  garage morale %s  ·  trust %s" % [
		str(_as_int(row.get("prestige", 0))),
		str(_as_int(row.get("facility", 0))),
		str(_as_int(row.get("morale", 0))),
		str(_as_int(row.get("trust", 0))),
	]))
	center_body.add_child(_muted("Career wins %s  ·  titles %s  ·  budget $%s" % [
		str(_as_int(row.get("career_wins", 0))),
		str(_as_int(row.get("titles", row.get("championships", 0)))),
		_comma(row.get("budget", 0)),
	]))
	center_body.add_child(_muted("Sponsor: %s" % str(row.get("sponsor", "unsponsored"))))
	center_body.add_child(_gold_line("Roster"))
	var roster: Array = _as_array(row.get("roster", []))
	if roster.is_empty():
		center_body.add_child(_muted("No drivers listed."))
		return
	for seat in roster:
		var item: Dictionary = seat
		var driver_id := str(item.get("id", item.get("name", "")))
		center_body.add_child(_profile_button(str(item.get("name", "")), _open_driver_profile.bind(driver_id)))
		center_body.add_child(_muted("%s  ·  %s pts  ·  morale %s" % [
			str(item.get("personality", "")),
			str(_as_int(item.get("points", 0))),
			str(_as_int(item.get("morale", 0))),
		]))


func _fill_drivers() -> void:
	if profile_driver != "":
		_fill_driver_profile()
		return
	center_body.add_child(_title("Drivers"))
	center_body.add_child(_gold_rule())
	center_body.add_child(_muted("The premier grid. Click a name for the full card. Morale and trust are the garage."))
	var rows: Array = _as_array(snapshot.get("drivers", []))
	print("DRIVERS=", str(rows.size()))
	if rows.is_empty():
		center_body.add_child(_muted("No drivers in this snapshot."))
		return
	for row in rows:
		var item: Dictionary = row
		var driver_id := str(item.get("id", item.get("name", "")))
		center_body.add_child(_profile_button(str(item.get("name", "")), _open_driver_profile.bind(driver_id)))
		center_body.add_child(_line("%s  ·  %s" % [
			str(item.get("team", "")),
			str(item.get("personality", "")),
		]))
		center_body.add_child(_muted("Age %s  ·  %s pts  ·  morale %s  ·  trust %s" % [
			str(_as_int(item.get("age", 0))),
			str(_as_int(item.get("points", 0))),
			str(_as_int(item.get("morale", 0))),
			str(_as_int(item.get("trust", 0))),
		]))


func _fill_driver_profile() -> void:
	var rows: Array = _as_array(snapshot.get("drivers", []))
	var item := _row_by_id(rows, profile_driver)
	center_body.add_child(_title("Driver profile"))
	center_body.add_child(_gold_rule())
	center_body.add_child(_profile_button("All drivers", _open_driver_profile.bind("")))
	if item.is_empty():
		center_body.add_child(_muted("That driver is not on the grid."))
		print("PROFILE_DRIVER=")
		return
	print("PROFILE_DRIVER=", str(item.get("id", item.get("name", ""))))
	center_body.add_child(_gold_line(str(item.get("name", ""))))
	var team_id := str(item.get("team_id", item.get("team", "")))
	center_body.add_child(_profile_button(str(item.get("team", "")), _open_team_profile.bind(team_id)))
	center_body.add_child(_line("%s  ·  age %s  ·  overall %s" % [
		str(item.get("personality", "")),
		str(_as_int(item.get("age", 0))),
		str(_as_int(item.get("overall", 0))),
	]))
	center_body.add_child(_muted("Speed %s  ·  consistency %s  ·  aggression %s" % [
		str(_as_int(item.get("speed", 0))),
		str(_as_int(item.get("consistency", 0))),
		str(_as_int(item.get("aggression", 0))),
	]))
	center_body.add_child(_line("%s pts  ·  %s wins  ·  morale %s  ·  trust %s" % [
		str(_as_int(item.get("points", 0))),
		str(_as_int(item.get("wins", 0))),
		str(_as_int(item.get("morale", 0))),
		str(_as_int(item.get("trust", 0))),
	]))
	center_body.add_child(_muted("Career %s wins  ·  %s pts  ·  %s starts  ·  %s titles" % [
		str(_as_int(item.get("career_wins", 0))),
		str(_as_int(item.get("career_points", 0))),
		str(_as_int(item.get("career_starts", 0))),
		str(_as_int(item.get("championships", 0))),
	]))
	center_body.add_child(_muted("Salary $%s  ·  %s yr contract" % [
		_comma(item.get("salary", 0)),
		str(_as_int(item.get("contract_years", 0))),
	]))
	center_body.add_child(_muted("Short %s  ·  road %s  ·  intermediate %s  ·  superspeedway %s" % [
		str(_as_int(item.get("short_track", 0))),
		str(_as_int(item.get("road_course", 0))),
		str(_as_int(item.get("intermediate", 0))),
		str(_as_int(item.get("superspeedway", 0))),
	]))
	if str(item.get("rival", "")) != "":
		center_body.add_child(_muted("Rival: %s" % str(item.get("rival", ""))))
	if str(item.get("ally", "")) != "":
		center_body.add_child(_muted("Ally: %s" % str(item.get("ally", ""))))


func _fill_prospects() -> void:
	center_body.add_child(_title("Prospects"))
	center_body.add_child(_gold_rule())
	var pool: Array = _as_array(snapshot.get("prospects", []))
	print("PROSPECTS=", str(pool.size()))
	center_body.add_child(_muted(str(_dash().get("development", "National Development Series"))))
	if pool.is_empty():
		center_body.add_child(_line(str(_dash().get("prospects", "No prospect book."))))
		return
	center_body.add_child(_line("%s drivers waiting outside the Cup." % str(pool.size())))
	for row in pool:
		var item: Dictionary = row
		center_body.add_child(_gold_line("%s  ·  %s" % [
			str(item.get("name", "")),
			str(item.get("readiness_label", "")),
		]))
		center_body.add_child(_muted("%s  ·  %s  ·  overall %s  ·  age %s" % [
			str(item.get("pathway", "")),
			str(item.get("team", "")),
			str(_as_int(item.get("overall", 0))),
			str(_as_int(item.get("age", 0))),
		]))
		center_body.add_child(_muted("%s pts  ·  %s wins in the feeder" % [
			str(_as_int(item.get("points", 0))),
			str(_as_int(item.get("wins", 0))),
		]))


func _fill_treasury() -> void:
	center_body.add_child(_title("Treasury"))
	center_body.add_child(_gold_rule())
	var book := _as_dict(snapshot.get("treasury", {}))
	var balance := _as_int(book.get("balance", _dash().get("treasury", 0)))
	print("TREASURY=", str(balance))
	center_body.add_child(_gold_line("$%s" % _comma(balance)))
	center_body.add_child(_muted("The sanctioning body, not a race team."))
	center_body.add_child(_line("Season TV: $%s" % _comma(book.get("season_tv", 0))))
	center_body.add_child(_line("Season commercial: $%s" % _comma(book.get("season_commercial", 0))))
	center_body.add_child(_line("Career TV: $%s" % _comma(book.get("career_tv", 0))))
	center_body.add_child(_line("Career commercial: $%s" % _comma(book.get("career_commercial", 0))))
	center_body.add_child(_line("Fines collected: $%s" % _comma(book.get("fines", 0))))


func _fill_television() -> void:
	center_body.add_child(_title("Television"))
	center_body.add_child(_gold_rule())
	var book := _as_dict(snapshot.get("television", {}))
	print("TV_RIGHTS=", str(book.get("rights", _dash().get("tv_rights", "unsigned"))))
	center_body.add_child(_line("Naming rights: %s" % str(book.get("naming", _dash().get("naming_rights", "unsponsored")))))
	center_body.add_child(_line("TV rights: %s" % str(book.get("rights", _dash().get("tv_rights", "unsigned")))))
	if str(book.get("network", "")) != "":
		center_body.add_child(_muted("Network: %s" % str(book.get("network", ""))))
	var rating = book.get("last_rating", null)
	if rating != null:
		center_body.add_child(_line("Last rating: %s" % str(_as_int(rating))))
		center_body.add_child(_muted("Viewers: %s  ·  trend %s" % [
			str(book.get("last_viewers", "n/a")),
			str(_as_int(book.get("trend", 0))),
		]))
	else:
		center_body.add_child(_muted("No weekend rating yet. Advance a race to put a number on the board."))
	if book.get("last_gate", null) != null:
		center_body.add_child(_line("Last gate: %s" % _comma(book.get("last_gate", 0))))


func _fill_sponsors() -> void:
	center_body.add_child(_title("Sponsors"))
	center_body.add_child(_gold_rule())
	var book := _as_dict(snapshot.get("sponsors", {}))
	var shops: Array = _as_array(book.get("teams", []))
	if shops.is_empty():
		for team in _dash().get("teams", []):
			shops.append(team)
	print("SPONSORS=", str(shops.size()))
	center_body.add_child(_line("Series: %s" % str(book.get("naming", _dash().get("naming_rights", "unsponsored")))))
	center_body.add_child(_muted("Companies waiting: %s" % str(_as_int(book.get("market", 0)))))
	for partner in _as_array(book.get("partners", [])):
		if typeof(partner) != TYPE_DICTIONARY:
			continue
		var row: Dictionary = partner
		center_body.add_child(_line("%s — %s" % [str(row.get("category", "partner")), str(row.get("label", ""))]))
	center_body.add_child(_title("Shop deals"))
	for shop in shops:
		var item: Dictionary = shop
		center_body.add_child(_gold_line(str(item.get("team", item.get("name", "")))))
		center_body.add_child(_muted(str(item.get("sponsor", ""))))


func _fill_rulebook() -> void:
	center_body.add_child(_title("Rulebook"))
	center_body.add_child(_gold_rule())
	center_body.add_child(_muted("Series-wide Cup rules. Hearings change these in Day 98."))
	var policies: Array = _as_array(snapshot.get("rulebook", _dash().get("policies", [])))
	print("RULEBOOK=", str(policies.size()))
	if policies.is_empty():
		center_body.add_child(_muted("No policies in this snapshot."))
		return
	for policy in policies:
		if typeof(policy) == TYPE_DICTIONARY:
			var row: Dictionary = policy
			center_body.add_child(_gold_line(str(row.get("label", row.get("id", "Rule")))))
			center_body.add_child(_muted(str(row.get("key", ""))))
		else:
			center_body.add_child(_line(str(policy)))


func _fill_board() -> void:
	center_body.add_child(_title("Board"))
	center_body.add_child(_gold_rule())
	var book := _as_dict(snapshot.get("board", {}))
	var councils := _as_dict(snapshot.get("councils", {}))
	print("BOARD_CONFIDENCE=", str(book.get("confidence_label", "")))
	center_body.add_child(_line("Confidence: %s (%s)" % [
		str(book.get("confidence_label", "—")),
		str(book.get("confidence", "—")),
	]))
	center_body.add_child(_line("Dismissal risk: %s (%s)" % [
		str(book.get("risk_label", "—")),
		str(book.get("risk", "—")),
	]))
	if book.get("confidence") != null:
		center_body.add_child(_meter("Board confidence", _as_int(book.get("confidence", 0)), COL_GOLD))
		center_body.add_child(_meter("Dismissal risk", _as_int(book.get("risk", 0)), Color("c44536")))
	center_body.add_child(_title("Approval"))
	center_body.add_child(_line("%s (%s)" % [
		str(book.get("approval_label", "—")),
		str(book.get("approval", "—")),
	]))
	if book.get("fans") != null:
		center_body.add_child(_meter("Fans", _as_int(book.get("fans", 0)), COL_GOLD))
		center_body.add_child(_meter("Owners", _as_int(book.get("owners", 0)), COL_CRIMSON))
		center_body.add_child(_meter("Drivers", _as_int(book.get("drivers", 0)), Color("3d9b6e")))
	var owners := _as_dict(councils.get("owners", {}))
	var garage := _as_dict(councils.get("drivers", {}))
	print("COUNCIL_OWNER=", str(owners.get("chair", "")))
	print("COUNCIL_DRIVER=", str(garage.get("chair", "")))
	center_body.add_child(_title("Owner Council"))
	center_body.add_child(_line("Chair: %s  (%s)" % [
		str(owners.get("chair", "—")),
		str(owners.get("team", "")),
	]))
	center_body.add_child(_muted("Mood: %s  ·  %s seats" % [
		str(owners.get("mood", "quiet")),
		str(_as_int(owners.get("seats", 0))),
	]))
	if str(owners.get("last", "")) != "":
		center_body.add_child(_muted("Last vote: %s" % str(owners.get("last", ""))))
	else:
		center_body.add_child(_muted("No rebuke vote this career yet."))
	center_body.add_child(_title("Driver Council"))
	center_body.add_child(_line("Chair: %s" % str(garage.get("chair", "—"))))
	center_body.add_child(_muted("Mood: %s  ·  %s seats" % [
		str(garage.get("mood", "settled")),
		str(_as_int(garage.get("seats", 0))),
	]))
	if str(garage.get("last", "")) != "":
		center_body.add_child(_muted("Last feedback: %s" % str(garage.get("last", ""))))
	else:
		center_body.add_child(_muted("The garage has not filed this career yet."))
	center_body.add_child(_muted("Rule docket: %s paper(s)" % str(_as_int(councils.get("docket", 0)))))


func _fill_history() -> void:
	if profile_season != "":
		_fill_season_file()
		return
	center_body.add_child(_title("History"))
	center_body.add_child(_gold_rule())
	var book := _as_dict(snapshot.get("history", {}))
	var seasons: Array = _as_array(book.get("seasons", []))
	print("HISTORY=", str(seasons.size()))
	center_body.add_child(_muted("Reopen a completed season. Preseason of year one is an empty file."))
	var records: Array = _as_array(book.get("records", []))
	if not records.is_empty():
		center_body.add_child(_gold_line("All-time records"))
		for row in records:
			var item: Dictionary = row
			center_body.add_child(_muted(str(item.get("text", item.get("label", "")))))
	if seasons.is_empty():
		center_body.add_child(_line("No seasons on file yet. Advance a championship to open the book."))
		return
	center_body.add_child(_gold_line("Season files"))
	for row in seasons:
		var item: Dictionary = row
		var season_id := str(item.get("id", item.get("season", "")))
		center_body.add_child(_profile_button(
			"Season %s — %s" % [str(item.get("season", "")), str(item.get("champion", ""))],
			_open_season_file.bind(season_id)
		))
		center_body.add_child(_muted("%s  ·  %s pts  ·  grade %s" % [
			str(item.get("champion_team", "")),
			str(_as_int(item.get("champion_points", 0))),
			str(item.get("grade", "")),
		]))


func _fill_season_file() -> void:
	var book := _as_dict(snapshot.get("history", {}))
	var seasons: Array = _as_array(book.get("seasons", []))
	var item := _row_by_id(seasons, profile_season)
	center_body.add_child(_title("Season file"))
	center_body.add_child(_gold_rule())
	center_body.add_child(_profile_button("All seasons", _open_season_file.bind("")))
	if item.is_empty():
		center_body.add_child(_muted("That season is not on file."))
		print("HISTORY_SEASON=")
		return
	print("HISTORY_SEASON=", str(item.get("id", item.get("season", ""))))
	center_body.add_child(_gold_line("Season %s champion: %s" % [
		str(item.get("season", "")),
		str(item.get("champion", "")),
	]))
	center_body.add_child(_line("%s  ·  %s pts  ·  %s wins" % [
		str(item.get("champion_team", "")),
		str(_as_int(item.get("champion_points", 0))),
		str(_as_int(item.get("champion_wins", 0))),
	]))
	center_body.add_child(_muted("Commissioner grade %s (%s)  ·  %s races" % [
		str(item.get("grade", "")),
		str(_as_int(item.get("score", 0))),
		str(_as_int(item.get("races", 0))),
	]))
	center_body.add_child(_muted("Integrity %s  ·  fans %s  ·  controversy %s" % [
		str(_as_int(item.get("integrity", 0))),
		str(_as_int(item.get("fan_interest", 0))),
		str(_as_int(item.get("controversy", 0))),
	]))
	if str(item.get("finale", "")) != "":
		center_body.add_child(_muted("Finale: %s" % str(item.get("finale", ""))))
	center_body.add_child(_gold_line("Standings"))
	for row in _as_array(item.get("standings", [])):
		var entry: Dictionary = row
		center_body.add_child(_line("%s. %s  ·  %s  ·  %s pts" % [
			str(_as_int(entry.get("position", 0))),
			str(entry.get("driver", "")),
			str(entry.get("team", "")),
			str(_as_int(entry.get("points", 0))),
		]))


func _fill_settings() -> void:
	var settings: Dictionary = snapshot.get("settings", {})
	center_body.add_child(_title("Settings"))
	center_body.add_child(_line("Difficulty: %s" % str(settings.get("difficulty_label", "Normal"))))
	center_body.add_child(_line("Career length: %s seasons" % str(settings.get("career_seasons", 3))))
	center_body.add_child(_line("Autosave: %s" % str(settings.get("autosave_label", "Off"))))
	center_body.add_child(_line("Era book: %s" % str(settings.get("era_book_label", "Pinnacle (late '80s–mid '90s)"))))
	print("ERA_BOOK=", str(settings.get("era_book", era_book)))
	center_body.add_child(_muted(str(snapshot.get("settings_line", ""))))
	center_body.add_child(_muted("Era books store the start decade. The full rewind lands in Day 112."))
	for book in ["1970s", "1980s", "pinnacle", "beyond"]:
		var era_button := Button.new()
		var mark := "●" if book == era_book else "○"
		era_button.text = "%s  %s" % [mark, book]
		era_button.alignment = HORIZONTAL_ALIGNMENT_LEFT
		era_button.pressed.connect(_on_era_book.bind(book))
		center_body.add_child(era_button)
	var new_button := Button.new()
	new_button.text = "New career"
	new_button.alignment = HORIZONTAL_ALIGNMENT_LEFT
	new_button.pressed.connect(_on_new_career.bind(era_book))
	center_body.add_child(new_button)
	var continue_button := Button.new()
	continue_button.text = "Continue desk"
	continue_button.alignment = HORIZONTAL_ALIGNMENT_LEFT
	continue_button.pressed.connect(_on_office_load.bind("office"))
	center_body.add_child(continue_button)
	center_body.add_child(_gold_rule())
	center_body.add_child(_title("Career files"))
	center_body.add_child(_muted("Saves use the same JSON slots as the terminal career."))
	var save_button := Button.new()
	save_button.text = "Save desk career"
	save_button.alignment = HORIZONTAL_ALIGNMENT_LEFT
	save_button.pressed.connect(_on_office_save.bind("desk"))
	center_body.add_child(save_button)
	var saves: Array = _office().get("saves", [])
	if saves.is_empty():
		saves = snapshot.get("saves", [])
	print("SAVES=", str(saves.size()))
	if saves.is_empty():
		center_body.add_child(_muted("No career files yet. Save writes desk.json."))
		return
	for item in saves:
		if typeof(item) != TYPE_DICTIONARY:
			continue
		var row: Dictionary = item
		var filename := str(row.get("filename", ""))
		var load_button := Button.new()
		load_button.text = "Load  %s" % str(row.get("label", filename))
		load_button.alignment = HORIZONTAL_ALIGNMENT_LEFT
		load_button.pressed.connect(_on_office_load.bind(filename))
		center_body.add_child(load_button)


func _on_office_save(slot_name: String) -> void:
	print("SAVE_SLOT=", slot_name)
	var python := str(_office().get("save_python", _office().get("advance_python", "")))
	var script := str(_office().get("save_script", ""))
	if python == "" or script == "":
		print("SAVE_OK=0")
		print("SAVE_ERROR=missing-save-command")
		return
	var output: Array = []
	var code := OS.execute(python, PackedStringArray([script, slot_name]), output, true)
	var text := ""
	for line in output:
		text += str(line) + "\n"
		print(str(line))
	if code != 0 or text.find("SAVE_OK=1") < 0:
		print("SAVE_OK=0")
		return
	_reload_office()
	print("SAVE_RELOADED=1")
	_show_section("settings")


func _on_office_load(slot_name: String) -> void:
	print("LOAD_SLOT=", slot_name)
	var python := str(_office().get("save_python", _office().get("advance_python", "")))
	var script := str(_office().get("load_script", ""))
	if python == "" or script == "" or slot_name == "":
		print("LOAD_OK=0")
		print("LOAD_ERROR=missing-load-command")
		return
	var output: Array = []
	var code := OS.execute(python, PackedStringArray([script, slot_name]), output, true)
	var text := ""
	for line in output:
		text += str(line) + "\n"
		print(str(line))
	if code != 0 or text.find("LOAD_OK=1") < 0:
		print("LOAD_OK=0")
		return
	hearing_held = false
	mail_read.clear()
	_reload_office()
	print("LOAD_RELOADED=1")
	print("CALENDAR=", str(snapshot.get("calendar", "")))
	_show_section("settings")


func _on_era_book(book: String) -> void:
	era_book = book
	print("ERA_PICK=", book)
	_show_section("settings")


func _on_new_career(book: String) -> void:
	if book == "":
		book = era_book
	print("NEW_ERA=", book)
	var python := str(_office().get("save_python", _office().get("advance_python", "")))
	var script := str(_office().get("new_script", ""))
	if python == "" or script == "":
		print("NEW_OK=0")
		print("NEW_ERROR=missing-new-command")
		return
	var output: Array = []
	var code := OS.execute(
		python,
		PackedStringArray([script, "normal", "3", "off", book]),
		output,
		true,
	)
	var text := ""
	for line in output:
		text += str(line) + "\n"
		print(str(line))
	if code != 0 or text.find("NEW_OK=1") < 0:
		print("NEW_OK=0")
		return
	era_book = book
	hearing_held = false
	mail_read.clear()
	_reload_office()
	print("NEW_RELOADED=1")
	print("CALENDAR=", str(snapshot.get("calendar", "")))
	_show_section("settings")


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
	label.add_theme_color_override("font_color", COL_GOLD)
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


func _gold_line(text: String) -> Label:
	var label := _line(text)
	label.add_theme_color_override("font_color", COL_GOLD)
	return label


func _profile_button(text: String, callback: Callable) -> Button:
	var button := Button.new()
	button.text = text
	button.alignment = HORIZONTAL_ALIGNMENT_LEFT
	var style := StyleBoxFlat.new()
	style.bg_color = COL_PANEL
	style.border_color = COL_GOLD
	style.set_border_width_all(1)
	style.set_corner_radius_all(0)
	style.content_margin_left = 10
	style.content_margin_right = 10
	style.content_margin_top = 6
	style.content_margin_bottom = 6
	button.add_theme_stylebox_override("normal", style)
	button.add_theme_stylebox_override("hover", style)
	button.add_theme_stylebox_override("pressed", style)
	button.add_theme_color_override("font_color", COL_GOLD)
	button.pressed.connect(callback)
	return button


func _row_by_id(rows: Array, key: String) -> Dictionary:
	for row in rows:
		if typeof(row) != TYPE_DICTIONARY:
			continue
		var item: Dictionary = row
		var ident := str(item.get("id", ""))
		var name := str(item.get("name", ""))
		if ident == key or name == key:
			return item
	return {}


func _open_team_profile(team_id: String) -> void:
	profile_team = team_id
	profile_driver = ""
	print("OPEN_TEAM=", team_id)
	_show_section("teams")


func _open_driver_profile(driver_id: String) -> void:
	profile_driver = driver_id
	profile_team = ""
	print("OPEN_DRIVER=", driver_id)
	_show_section("drivers")


func _open_season_file(season_id: String) -> void:
	profile_season = season_id
	print("OPEN_SEASON=", season_id)
	_show_section("history")


func _gold_rule() -> ColorRect:
	var rule := ColorRect.new()
	rule.color = COL_GOLD
	rule.custom_minimum_size = Vector2(0, 2)
	rule.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	return rule


func _as_int(value: Variant) -> int:
	return int(float(str(value)))


func _as_dict(value: Variant) -> Dictionary:
	if typeof(value) == TYPE_DICTIONARY:
		return value
	return {}


func _as_array(value: Variant) -> Array:
	if typeof(value) == TYPE_ARRAY:
		return value
	return []


func _recap() -> Dictionary:
	return _as_dict(snapshot.get("recap", {}))


func _fill_recap_card() -> void:
	var recap := _recap()
	if recap.is_empty() or str(recap.get("title", "")) == "":
		print("RECAP_WINNER=")
		return
	center_body.add_child(_line(str(recap.get("title", "Week recap"))))
	var winner := str(recap.get("winner", ""))
	print("RECAP_WINNER=", winner)
	print("RECAP_TRACK=", str(recap.get("track", "")))
	print("RECAP_KIND=", str(recap.get("kind", "")))
	if winner != "":
		center_body.add_child(_muted("Winner: %s" % winner))
	if str(recap.get("pole", "")) != "":
		center_body.add_child(_muted("Pole: %s" % str(recap.get("pole", ""))))
	if recap.get("cautions") != null:
		center_body.add_child(_muted("Cautions: %s" % str(_as_int(recap.get("cautions", 0)))))
		print("RECAP_CAUTIONS=", str(_as_int(recap.get("cautions", 0))))
	if str(recap.get("weather", "")) != "":
		center_body.add_child(_muted("Weather: %s" % str(recap.get("weather", ""))))
	var qualifying := _as_array(recap.get("qualifying", []))
	print("RECAP_QUALIFYING=", str(qualifying.size()))
	if not qualifying.is_empty():
		center_body.add_child(_muted("Qualifying"))
		for row in qualifying:
			if typeof(row) != TYPE_DICTIONARY:
				continue
			var start_row: Dictionary = row
			center_body.add_child(_line("Q%s  %s" % [
				str(_as_int(start_row.get("position", 0))),
				str(start_row.get("driver", "")),
			]))
	for row in _as_array(recap.get("podium", [])):
		if typeof(row) != TYPE_DICTIONARY:
			continue
		var item: Dictionary = row
		center_body.add_child(_line("P%s  %s  (%s)" % [
			str(_as_int(item.get("position", 0))),
			str(item.get("driver", "")),
			str(item.get("team", "")),
		]))
	var probes := _as_array(recap.get("investigations", []))
	print("RECAP_INVESTIGATIONS=", str(probes.size()))
	if str(recap.get("pole", "")) != "":
		print("RECAP_POLE=", str(recap.get("pole", "")))
	if _as_int(recap.get("wrecks", 0)) > 0:
		center_body.add_child(_muted("Wrecks: %s" % str(_as_int(recap.get("wrecks", 0)))))
	for row in probes:
		if typeof(row) != TYPE_DICTIONARY:
			continue
		var probe: Dictionary = row
		center_body.add_child(_muted("Investigation: blame %s (%s)" % [
			str(probe.get("blame", "")),
			str(probe.get("confidence", "")),
		]))
	center_body.add_child(_gold_rule())


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
	style.set_corner_radius_all(2)
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
	style.set_corner_radius_all(2)
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
	style.set_border_width_all(2)
	style.set_corner_radius_all(0)
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
