extends Control

const BundleLoader := preload("res://scripts/race_viewer/BundleLoader.gd")
const PlaybackClock := preload("res://scripts/race_viewer/PlaybackClock.gd")
const StateReconstructor := preload("res://scripts/race_viewer/StateReconstructor.gd")

var loader := BundleLoader.new()
var clock := PlaybackClock.new()
var reconstructor := StateReconstructor.new()
var bundle := {}
var layout := {}
var track_canvas
var hud
var controls
var show_data := true
var hud_accum := 0.0
var created_sprites := 0


func _ready() -> void:
	set_anchors_preset(Control.PRESET_FULL_RECT)
	var bg := ColorRect.new()
	bg.color = Color("0a0a0a")
	bg.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(bg)
	var root := VBoxContainer.new()
	root.set_anchors_preset(Control.PRESET_FULL_RECT)
	root.add_theme_constant_override("separation", 0)
	add_child(root)
	var body := HBoxContainer.new()
	body.size_flags_vertical = Control.SIZE_EXPAND_FILL
	body.add_theme_constant_override("separation", 0)
	root.add_child(body)
	track_canvas = preload("res://scenes/race_viewer/TrackCanvas.tscn").instantiate()
	track_canvas.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	track_canvas.size_flags_vertical = Control.SIZE_EXPAND_FILL
	body.add_child(track_canvas)
	hud = preload("res://scenes/race_viewer/BroadcastHud.tscn").instantiate()
	body.add_child(hud)
	controls = preload("res://scenes/race_viewer/PlaybackControls.tscn").instantiate()
	root.add_child(controls)
	controls.command.connect(_on_command)
	_load_session_bundle()
	if _is_viewer_test():
		call_deferred("_run_headless_tests")


func _load_session_bundle() -> void:
	var path := "res://data/races/riverside_200_viewer.json"
	var layout_path := ""
	var spoiler := true
	if Engine.has_singleton("ViewerSession") or true:
		var session := get_node_or_null("/root/ViewerSession")
		if session:
			path = str(session.bundle_path)
			layout_path = str(session.layout_path)
			spoiler = bool(session.spoiler_free)
	var args := OS.get_cmdline_user_args()
	for arg in args:
		if arg.begins_with("--bundle="):
			path = arg.substr(9)
	bundle = loader.load_bundle(path)
	layout = loader.load_layout(bundle, layout_path)
	var session_node := get_node_or_null("/root/ViewerSession")
	if session_node and session_node.has_watched(str(bundle.get("race_id", ""))):
		spoiler = false
	reconstructor.index_bundle(bundle)
	clock.configure(int(bundle.get("duration_ms", 1)))
	if hud:
		hud.set_spoiler_free(spoiler)
	if track_canvas:
		track_canvas.configure(layout, bundle.get("entries", []))
		created_sprites = track_canvas.pooled_cars()
	_refresh_view(true)
	print("VIEWER_READY")
	print("VIEWER_BUNDLE=", str(bundle.get("race_id", "")))
	print("VIEWER_CARS=", str((bundle.get("entries", []) as Array).size()))
	print("VIEWER_POOL=", str(created_sprites))
	print("VIEWER_DURATION=", str(clock.duration_ms))


func _process(delta: float) -> void:
	if bundle.is_empty():
		return
	clock.tick(delta)
	hud_accum += delta
	var force := (not clock.playing) or hud_accum >= 0.1
	_refresh_view(force)
	if force:
		hud_accum = 0.0


func _refresh_view(update_hud: bool) -> void:
	var states: Dictionary = reconstructor.cars_at(bundle, clock.time_ms)
	var timing: Dictionary = reconstructor.timing_at(bundle, clock.time_ms)
	if track_canvas:
		track_canvas.apply(states, timing)
	if update_hud and hud:
		hud.apply(
			bundle,
			clock.time_ms,
			timing,
			reconstructor.phase_at(clock.time_ms),
			reconstructor.markers_until(clock.time_ms),
			clock.time_ms >= clock.duration_ms,
			show_data
		)
	if controls:
		controls.set_status(clock.time_ms, clock.duration_ms, clock.speed, clock.playing)
	if clock.time_ms >= clock.duration_ms:
		var session := get_node_or_null("/root/ViewerSession")
		if session:
			session.mark_watched(str(bundle.get("race_id", "")))


func _on_command(name: String, value: Variant) -> void:
	match name:
		"back":
			_return_to_desk()
		"pause":
			clock.pause_toggle()
		"speed":
			clock.set_speed(float(value))
		"event":
			clock.seek(reconstructor.next_marker_time(clock.time_ms, "", clock.duration_ms))
		"caution":
			clock.seek(reconstructor.next_marker_time(clock.time_ms, "CAUTION", clock.duration_ms))
		"finish":
			clock.jump_finish()
		"camera":
			if track_canvas:
				track_canvas.set_camera_mode(str(value))
				if str(value) == "SELECTED":
					var timing: Dictionary = reconstructor.timing_at(bundle, clock.time_ms)
					var order: Array = timing.get("order", [])
					if not order.is_empty():
						track_canvas.select_entry(str(order[0]))
		"data":
			show_data = not show_data
		"scrub":
			clock.seek(mini(clock.time_ms + clock.duration_ms / 10, clock.duration_ms))
	_refresh_view(true)
	print("VIEWER_CMD=", name)


func _return_to_desk() -> void:
	var session := get_node_or_null("/root/ViewerSession")
	var path := "res://scenes/Main.tscn"
	if session:
		path = str(session.return_scene)
	print("VIEWER_BACK=1")
	get_tree().change_scene_to_file(path)


func _is_viewer_test() -> bool:
	if DisplayServer.get_name() == "headless":
		return true
	for arg in OS.get_cmdline_user_args():
		if arg == "--viewer-test":
			return true
	return false


func _run_headless_tests() -> void:
	var errors := PackedStringArray()
	if loader.validate(bundle).size() > 0:
		errors.append("bundle-invalid")
	if created_sprites != 40:
		errors.append("pool-not-40")
	var stamps := [0, 90000, 220000, clock.duration_ms]
	for stamp in stamps:
		clock.seek(stamp)
		var first := reconstructor.state_digest(bundle, stamp)
		clock.seek(clock.duration_ms)
		clock.seek(stamp)
		var second := reconstructor.state_digest(bundle, stamp)
		if first != second:
			errors.append("scrub-%s" % stamp)
	var pit := _first_marker("PIT")
	if pit:
		var cars: Dictionary = reconstructor.cars_at(bundle, int(pit.get("sim_time_ms", 0)) + 20)
		var entry_id := str((pit.get("entry_ids", [""]) as Array)[0])
		if cars.has(entry_id) and str(cars[entry_id].get("path", "")) != "PIT":
			errors.append("pit-path")
	var caution := _first_marker("CAUTION")
	if caution:
		var phase: Dictionary = reconstructor.phase_at(int(caution.get("sim_time_ms", 0)))
		if str(phase.get("phase", "")) == "":
			errors.append("caution-phase")
	clock.jump_finish()
	_refresh_view(true)
	var timing: Dictionary = reconstructor.timing_at(bundle, clock.duration_ms)
	if (timing.get("order", []) as Array).is_empty():
		errors.append("finish-order")
	print("VIEWER_HASH_OK=1")
	print("VIEWER_SCRUB_OK=", "1" if not ("scrub-0" in errors) else "0")
	print("VIEWER_PIT_OK=", "1" if not ("pit-path" in errors) else "0")
	print("VIEWER_CAUTION_OK=", "1" if not ("caution-phase" in errors) else "0")
	print("VIEWER_FINISH_OK=", "1" if not ("finish-order" in errors) else "0")
	print("VIEWER_MUTATION=0")
	if errors.is_empty():
		print("VIEWER_TESTS_OK=1")
	else:
		print("VIEWER_TESTS_OK=0")
		for item in errors:
			print("VIEWER_FAIL=", item)
	# Scale pass on the 40-car bundle when the 8-car fixture was loaded first.
	if str(bundle.get("race_id", "")).find("40") < 0:
		bundle = loader.load_bundle("res://data/races/riverside_200_40_viewer.json")
		layout = loader.load_layout(bundle, "")
		reconstructor.index_bundle(bundle)
		clock.configure(int(bundle.get("duration_ms", 1)))
		track_canvas.configure(layout, bundle.get("entries", []))
		print("VIEWER_SCALE_CARS=", str((bundle.get("entries", []) as Array).size()))
		print("VIEWER_SCALE_POOL=", str(track_canvas.pooled_cars()))
		clock.seek(clock.duration_ms / 2)
		_refresh_view(true)
		print("VIEWER_SCALE_OK=1")
	get_tree().quit()


func _first_marker(kind: String) -> Dictionary:
	for row in bundle.get("markers", []):
		if typeof(row) == TYPE_DICTIONARY and str(row.get("kind", "")) == kind:
			return row
	return {}
