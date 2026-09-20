shader_type canvas_item;

uniform float density : hint_range(80.0, 520.0) = 200.0;
uniform float strength : hint_range(0.0, 0.35) = 0.18;

void fragment() {
	float line = step(0.55, fract(SCREEN_UV.y * density));
	COLOR = vec4(0.0, 0.0, 0.0, line * strength);
}
