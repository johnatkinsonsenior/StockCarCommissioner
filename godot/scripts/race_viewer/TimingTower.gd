extends RefCounted

var hide_final := true


func lines(bundle: Dictionary, timing: Dictionary, finished: bool) -> PackedStringArray:
	var entries := {}
	for row in bundle.get("entries", []):
		if typeof(row) == TYPE_DICTIONARY:
			entries[str(row.get("entry_id", ""))] = row
	var classification := {}
	for row in bundle.get("classification", []):
		if typeof(row) == TYPE_DICTIONARY:
			classification[str(row.get("entry_id", ""))] = row
	var rows := PackedStringArray()
	var order: Array = timing.get("order", [])
	if hide_final and not finished:
		for index in range(mini(order.size(), 12)):
			var entry_id := str(order[index])
			var entry: Dictionary = entries.get(entry_id, {})
			rows.append("%02d  #%s  %s" % [
				index + 1,
				str(entry.get("car_number", "")),
				str(entry.get("driver_name", entry_id)),
			])
		return rows
	var source: Array = bundle.get("classification", []) if finished else []
	if source.is_empty():
		for entry_id in order:
			source.append({"entry_id": entry_id})
	for row in source:
		if typeof(row) != TYPE_DICTIONARY:
			continue
		var entry_id := str(row.get("entry_id", ""))
		var entry: Dictionary = entries.get(entry_id, {})
		rows.append("%02d  #%s  %s  %s" % [
			int(row.get("position", rows.size() + 1)),
			str(entry.get("car_number", "")),
			str(entry.get("driver_name", entry_id)),
			str(row.get("status", "")),
		])
	return rows
