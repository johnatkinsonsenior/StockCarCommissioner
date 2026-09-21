extends RefCounted

signal changed

var time_ms := 0
var duration_ms := 1
var playing := true
var speed := 1.0
const SPEEDS := [0.5, 1.0, 2.0, 4.0, 8.0]


func configure(length_ms: int) -> void:
	duration_ms = max(1, length_ms)
	time_ms = 0
	playing = true
	speed = 1.0


func tick(delta: float) -> void:
	if not playing:
		return
	seek(time_ms + int(round(delta * speed * 1000.0)))


func pause_toggle() -> void:
	playing = not playing
	changed.emit()


func set_speed(value: float) -> void:
	speed = value
	playing = true
	changed.emit()


func cycle_speed() -> void:
	var index := SPEEDS.find(speed)
	set_speed(SPEEDS[(index + 1) % SPEEDS.size()] if index >= 0 else 1.0)


func seek(value: int) -> void:
	var next_time: int = clampi(value, 0, duration_ms)
	if next_time == time_ms:
		return
	time_ms = next_time
	if time_ms >= duration_ms:
		playing = false
	changed.emit()


func jump_finish() -> void:
	playing = false
	seek(duration_ms)
