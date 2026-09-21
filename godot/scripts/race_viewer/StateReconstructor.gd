extends RefCounted

const CarInterpolator := preload("res://scripts/race_viewer/CarInterpolator.gd")

var _frames := {}
var _markers: Array = []
var _phases: Array = []
var _timing: Array = []
var _interpolator := CarInterpolator.new()


func index_bundle(bundle: Dictionary) -> void:
	_frames = {}
	for frame in bundle.get("keyframes", []):
		if typeof(frame) != TYPE_DICTIONARY:
			continue
		var entry_id := str(frame.get("entry_id", ""))
		if not _frames.has(entry_id):
			_frames[entry_id] = []
		_frames[entry_id].append(frame)
	for entry_id in _frames.keys():
		var rows: Array = _frames[entry_id]
		rows.sort_custom(func(a, b): return int(a.get("sim_time_ms", 0)) < int(b.get("sim_time_ms", 0)))
		_frames[entry_id] = rows
	_markers = _sorted(bundle.get("markers", []))
	_phases = _sorted(bundle.get("phase_timeline", []))
	_timing = _sorted(bundle.get("timing_frames", []))


func cars_at(bundle: Dictionary, time_ms: int) -> Dictionary:
	var states := {}
	for entry in bundle.get("entries", []):
		if typeof(entry) != TYPE_DICTIONARY:
			continue
		var entry_id := str(entry.get("entry_id", ""))
		var frames: Array = _frames.get(entry_id, [])
		var previous := _latest(frames, time_ms)
		var nxt := {}
		if not previous.is_empty():
			nxt = _next_after(frames, int(previous.get("sim_time_ms", 0)))
		elif not frames.is_empty():
			nxt = frames[0]
		var state := _interpolator.interpolate_car(previous, nxt, time_ms)
		if not state.is_empty():
			states[entry_id] = state
	return states


func timing_at(bundle: Dictionary, time_ms: int) -> Dictionary:
	var row := _latest(_timing, time_ms)
	if not row.is_empty():
		return row
	var order: Array = []
	for item in bundle.get("classification", []):
		if typeof(item) == TYPE_DICTIONARY:
			order.append(str(item.get("entry_id", "")))
	return {"leader_entry_id": str(order[0]) if not order.is_empty() else "", "order": order, "race_lap": 0}


func phase_at(time_ms: int) -> Dictionary:
	var row := _latest(_phases, time_ms)
	return row if not row.is_empty() else {"phase": "FORMATION", "race_lap": 0}


func markers_until(time_ms: int) -> Array:
	var rows: Array = []
	for row in _markers:
		if int(row.get("sim_time_ms", 0)) <= time_ms:
			rows.append(row)
	return rows


func next_marker_time(time_ms: int, kind: String, duration_ms: int) -> int:
	for row in _markers:
		if int(row.get("sim_time_ms", 0)) <= time_ms:
			continue
		if kind != "" and str(row.get("kind", "")) != kind:
			continue
		return int(row.get("sim_time_ms", duration_ms))
	return duration_ms


func state_digest(bundle: Dictionary, time_ms: int) -> String:
	var cars := cars_at(bundle, time_ms)
	var timing := timing_at(bundle, time_ms)
	var compact := {
		"phase": str(phase_at(time_ms).get("phase", "")),
		"lap": int(timing.get("race_lap", 0)),
		"order": timing.get("order", []),
		"cars": {},
	}
	var car_map := {}
	for entry_id in cars.keys():
		var row: Dictionary = cars[entry_id]
		car_map[entry_id] = "%s:%s:%s:%s" % [
			str(row.get("path", "")),
			str(int(row.get("path_progress_ppm", 0))),
			str(int(row.get("laps_completed", 0))),
			str(row.get("status", "")),
		]
	compact["cars"] = car_map
	return JSON.stringify(compact)


func _sorted(rows: Variant) -> Array:
	var copy: Array = []
	for row in rows:
		if typeof(row) == TYPE_DICTIONARY:
			copy.append(row)
	copy.sort_custom(func(a, b): return int(a.get("sim_time_ms", 0)) < int(b.get("sim_time_ms", 0)))
	return copy


func _latest(rows: Array, time_ms: int) -> Dictionary:
	var chosen := {}
	for row in rows:
		if int(row.get("sim_time_ms", 0)) <= time_ms:
			chosen = row
		else:
			break
	return chosen


func _next_after(rows: Array, time_ms: int) -> Dictionary:
	for row in rows:
		if int(row.get("sim_time_ms", 0)) > time_ms:
			return row
	return {}
