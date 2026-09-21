extends RefCounted

const VIEWER_CONTRACT := "scc-viewer-v1"


func load_json(path: String) -> Dictionary:
	if path == "" or not FileAccess.file_exists(path):
		return {}
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
	if typeof(parsed) != TYPE_DICTIONARY:
		return {}
	return parsed


func load_bundle(path: String) -> Dictionary:
	var bundle := load_json(path)
	var errors := validate(bundle)
	if not errors.is_empty():
		push_error("Viewer bundle failed validation: %s" % ", ".join(errors))
	return bundle


func load_layout(bundle: Dictionary, explicit_path: String = "") -> Dictionary:
	if explicit_path != "":
		return load_json(explicit_path)
	var layout_id := str((bundle.get("track", {}) as Dictionary).get("track_layout_id", "riverside_short_v1"))
	var mapped := {
		"riverside_short_v1": "res://assets/tracks/riverside_short.json",
		"oval_template_v1": "res://assets/tracks/oval_template_v1.json",
		"intermediate_template_v1": "res://assets/tracks/intermediate_template_v1.json",
		"superspeedway_template_v1": "res://assets/tracks/superspeedway_template_v1.json",
		"road_template_v1": "res://assets/tracks/road_template_v1.json",
	}
	return load_json(str(mapped.get(layout_id, "res://assets/tracks/riverside_short.json")))


func validate(bundle: Dictionary) -> PackedStringArray:
	var errors := PackedStringArray()
	if bundle.is_empty():
		errors.append("bundle missing")
		return errors
	if str(bundle.get("viewer_contract_version", "")) != VIEWER_CONTRACT:
		errors.append("bad contract")
	if int(bundle.get("duration_ms", 0)) <= 0:
		errors.append("bad duration")
	if str(bundle.get("bundle_hash", "")) == "":
		errors.append("missing hash")
	var entries: Array = bundle.get("entries", [])
	var known := {}
	for row in entries:
		if typeof(row) == TYPE_DICTIONARY:
			known[str(row.get("entry_id", ""))] = true
	if known.is_empty():
		errors.append("no entries")
	for frame in bundle.get("keyframes", []):
		if typeof(frame) != TYPE_DICTIONARY:
			continue
		var entry_id := str(frame.get("entry_id", ""))
		if not known.has(entry_id):
			errors.append("unknown keyframe entry")
			break
		if int(frame.get("source_event_seq", 0)) < 1:
			errors.append("keyframe missing provenance")
			break
	return errors
