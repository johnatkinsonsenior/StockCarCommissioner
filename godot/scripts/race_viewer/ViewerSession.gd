extends Node

var bundle_path := "res://data/races/riverside_200_viewer.json"
var layout_path := ""
var return_scene := "res://scenes/Main.tscn"
var spoiler_free := true
var watched_races := {}


func configure(path: String, hide_result: bool = true) -> void:
	bundle_path = path
	spoiler_free = hide_result


func mark_watched(race_id: String) -> void:
	watched_races[race_id] = true


func has_watched(race_id: String) -> bool:
	return bool(watched_races.get(race_id, false))
