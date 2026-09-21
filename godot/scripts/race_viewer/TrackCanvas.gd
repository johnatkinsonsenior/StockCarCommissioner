extends Control

const CarInterpolator := preload("res://scripts/race_viewer/CarInterpolator.gd")
const CarPool := preload("res://scripts/race_viewer/CarPool.gd")
const CameraDirector := preload("res://scripts/race_viewer/CameraDirector.gd")

var layout := {}
var interpolator := CarInterpolator.new()
var director := CameraDirector.new()
var world: Node2D
var track_draw: Node2D
var pool: Node2D
var camera: Camera2D
var viewport: SubViewport


func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	var host := SubViewportContainer.new()
	host.stretch = false
	host.set_anchors_preset(Control.PRESET_FULL_RECT)
	host.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	host.size_flags_vertical = Control.SIZE_EXPAND_FILL
	add_child(host)
	viewport = SubViewport.new()
	viewport.transparent_bg = false
	viewport.handle_input_locally = true
	viewport.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	viewport.size = Vector2i(1100, 640)
	host.add_child(viewport)
	world = Node2D.new()
	world.name = "World"
	viewport.add_child(world)
	track_draw = Node2D.new()
	track_draw.name = "TrackDraw"
	track_draw.set_script(preload("res://scripts/race_viewer/TrackDraw.gd"))
	world.add_child(track_draw)
	pool = CarPool.new()
	pool.name = "Cars"
	world.add_child(pool)
	camera = Camera2D.new()
	camera.enabled = true
	world.add_child(camera)


func configure(next_layout: Dictionary, entries: Array) -> void:
	layout = next_layout
	if track_draw:
		track_draw.set("layout", layout)
		track_draw.queue_redraw()
	if pool:
		pool.bind_entries(entries)
	if viewport:
		viewport.size = Vector2i(max(1, int(size.x)), max(1, int(size.y)))


func apply(states: Dictionary, timing: Dictionary) -> void:
	if pool:
		pool.apply_states(states, interpolator, layout, director.selected_entry_id)
	if camera:
		director.apply(camera, layout, timing, pool)


func set_camera_mode(mode: String) -> void:
	director.set_mode(mode)


func select_entry(entry_id: String) -> void:
	director.select(entry_id)


func pooled_cars() -> int:
	return pool.spawned_count() if pool else 0


func _notification(what: int) -> void:
	if what == NOTIFICATION_RESIZED and viewport:
		viewport.size = Vector2i(max(1, int(size.x)), max(1, int(size.y)))
