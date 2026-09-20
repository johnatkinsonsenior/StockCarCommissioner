shader_type canvas_item;

uniform float density : hint_range(80.0, 520.0) = 260.0;
uniform float strength : hint_range(0.0, 0.35) = 0.12;

void fragment() {
	float scan = sin(SCREEN_UV.y * density * 3.14159);
	float dark = (scan * 0.5 + 0.5) * strength;
	COLOR = vec4(0.0, 0.0, 0.0, dark);
}
