extends RefCounted


func total_progress(frame: Dictionary) -> int:
	return int(frame.get("laps_completed", 0)) * 1000000 + int(frame.get("path_progress_ppm", 0))


func interpolate_car(previous: Dictionary, nxt: Dictionary, time_ms: int) -> Dictionary:
	if previous.is_empty():
		return nxt.duplicate(true)
	if nxt.is_empty() or int(nxt.get("sim_time_ms", 0)) <= int(previous.get("sim_time_ms", 0)):
		return previous.duplicate(true)
	var span := int(nxt.get("sim_time_ms", 0)) - int(previous.get("sim_time_ms", 0))
	var done := clampi(time_ms - int(previous.get("sim_time_ms", 0)), 0, span)
	if str(previous.get("path", "RACING")) != str(nxt.get("path", "RACING")):
		var chosen := nxt if done * 2 >= span else previous
		var mixed: Dictionary = chosen.duplicate(true)
		mixed["sim_time_ms"] = time_ms
		return mixed
	var start := total_progress(previous)
	var finish := total_progress(nxt)
	var total := start + (finish - start) * done / span
	var mixed: Dictionary = previous.duplicate(true)
	mixed["laps_completed"] = int(total / 1000000)
	mixed["path_progress_ppm"] = int(total % 1000000)
	mixed["sim_time_ms"] = time_ms
	mixed["race_lap"] = int(nxt.get("race_lap", previous.get("race_lap", 0)))
	return mixed


func polyline_sample(points: Array, ppm: int, closed: bool) -> Dictionary:
	if points.is_empty():
		return {"position": Vector2.ZERO, "angle": 0.0}
	var lengths: Array[float] = []
	var total := 0.0
	var count := points.size()
	var edges := count if closed else count - 1
	for index in range(edges):
		var a: Vector2 = _as_point(points[index])
		var b: Vector2 = _as_point(points[(index + 1) % count])
		var length := a.distance_to(b)
		lengths.append(length)
		total += length
	if total <= 0.0:
		return {"position": _as_point(points[0]), "angle": 0.0}
	var target := total * float(clampi(ppm, 0, 1000000)) / 1000000.0
	var acc := 0.0
	for index in range(edges):
		var length: float = lengths[index]
		if acc + length >= target or index == edges - 1:
			var a: Vector2 = _as_point(points[index])
			var b: Vector2 = _as_point(points[(index + 1) % count])
			var t := 0.0 if length <= 0.0 else (target - acc) / length
			return {"position": a.lerp(b, t), "angle": (b - a).angle()}
		acc += length
	return {"position": _as_point(points[0]), "angle": 0.0}


func _as_point(value: Variant) -> Vector2:
	if typeof(value) == TYPE_ARRAY and value.size() >= 2:
		return Vector2(float(value[0]), float(value[1]))
	return Vector2.ZERO
