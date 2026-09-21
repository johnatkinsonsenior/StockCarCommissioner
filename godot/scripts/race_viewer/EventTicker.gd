extends RefCounted

const LABELS := {
	"START": "Green flag",
	"LEAD_CHANGE": "Lead change",
	"PASS": "Pass completed",
	"PIT": "Pit stop",
	"MECHANICAL": "Mechanical trouble",
	"CONTACT": "Contact",
	"CAUTION": "Caution",
	"RESTART": "Restart",
	"CONDITION": "Conditions change",
	"RETIREMENT": "Retirement",
	"FINISH": "Checkered flag",
}


func visible_lines(markers: Array, entries: Array) -> PackedStringArray:
	var names := {}
	for row in entries:
		if typeof(row) == TYPE_DICTIONARY:
			names[str(row.get("entry_id", ""))] = str(row.get("driver_name", row.get("entry_id", "")))
	var lines := PackedStringArray()
	var start := maxi(0, markers.size() - 6)
	for index in range(start, markers.size()):
		var marker: Dictionary = markers[index]
		var people: Array = []
		for entry_id in marker.get("entry_ids", []):
			people.append(str(names.get(str(entry_id), entry_id)))
		var who := ", ".join(people)
		var label := str(LABELS.get(str(marker.get("kind", "")), marker.get("kind", "")))
		if who != "":
			lines.append("%s — %s" % [label, who])
		else:
			lines.append(label)
	return lines
