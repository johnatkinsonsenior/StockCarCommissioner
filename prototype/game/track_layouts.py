"""Presentation-only track layouts for the V2 race viewer."""

from __future__ import annotations

import math


LAYOUT_VERSION = 1
CANVAS_WIDTH = 1400
CANVAS_HEIGHT = 800


def _closed_oval(cx, cy, rx, ry, count=56):
    points = []
    for index in range(count):
        angle = (2.0 * math.pi * index) / count
        x = int(round(cx + rx * math.sin(angle)))
        y = int(round(cy + ry * math.cos(angle)))
        points.append([x, y])
    return points


def _open_pit(cx, cy, rx, ry, count=12):
    points = []
    for index in range(count):
        # Inner line along the frontstretch, then slightly into the apron.
        t = index / float(count - 1)
        angle = -0.42 + 0.84 * t
        x = int(round(cx + (rx - 38) * math.sin(angle)))
        y = int(round(cy + (ry - 46) * math.cos(angle)))
        points.append([x, y])
    return points


def _ranges_for_path(segments, path):
    chosen = [row for row in segments if str(row.get("path")) == path]
    total = sum(int(row["length_mm"]) for row in chosen) or 1
    acc = 0
    ranges = []
    for offset, row in enumerate(chosen):
        start = acc * 1_000_000 // total
        acc += int(row["length_mm"])
        end = 1_000_000 if offset == len(chosen) - 1 else acc * 1_000_000 // total
        ranges.append(
            {
                "end_ppm": end,
                "length_mm": int(row["length_mm"]),
                "path": path,
                "segment_index": int(row["segment_index"]),
                "start_ppm": start,
            }
        )
    return ranges


def layout_from_polylines(track, layout_id, racing, pit, track_type):
    """Build a presentation layout that covers every canonical segment."""

    segments = list((track or {}).get("segments") or [])
    ranges = _ranges_for_path(segments, "RACING") + _ranges_for_path(segments, "PIT")
    return {
        "camera_bounds": {
            "height": CANVAS_HEIGHT,
            "width": CANVAS_WIDTH,
            "x": 0,
            "y": 0,
        },
        "canvas_height": CANVAS_HEIGHT,
        "canvas_width": CANVAS_WIDTH,
        "lane_offset_px": 9,
        "pit_polyline": pit,
        "racing_polyline": racing,
        "segment_ranges": ranges,
        "start_finish_ppm": 0,
        "track_layout_id": layout_id,
        "track_type": track_type,
        "version": LAYOUT_VERSION,
    }


def oval_template_layout(track, layout_id="oval_template_v1"):
    racing = _closed_oval(700, 400, 470, 250)
    pit = _open_pit(700, 400, 470, 250)
    return layout_from_polylines(
        track,
        layout_id,
        racing,
        pit,
        str((track or {}).get("track_type") or "SHORT"),
    )


def intermediate_template_layout(track):
    racing = _closed_oval(700, 400, 500, 230)
    pit = _open_pit(700, 400, 500, 230)
    return layout_from_polylines(track, "intermediate_template_v1", racing, pit, "INTERMEDIATE")


def superspeedway_template_layout(track):
    racing = _closed_oval(700, 400, 540, 210)
    pit = _open_pit(700, 400, 540, 210)
    return layout_from_polylines(track, "superspeedway_template_v1", racing, pit, "SUPERSPEEDWAY")


def road_template_layout(track):
    racing = [
        [260, 620],
        [430, 650],
        [690, 640],
        [930, 600],
        [1120, 520],
        [1180, 390],
        [1100, 250],
        [900, 190],
        [680, 210],
        [500, 170],
        [330, 220],
        [220, 340],
        [210, 480],
        [240, 580],
    ]
    pit = [
        [250, 590],
        [360, 605],
        [500, 615],
        [640, 612],
        [760, 600],
    ]
    return layout_from_polylines(track, "road_template_v1", racing, pit, "ROAD")


def riverside_short_layout(track):
    """Authored short-track presentation for the Riverside 200 fixture."""

    return oval_template_layout(track, layout_id="riverside_short_v1")


def layout_for_track(track):
    """Return the authored venue layout or a typed template fallback."""

    track_id = str((track or {}).get("track_id") or "")
    track_type = str((track or {}).get("track_type") or "SHORT")
    if track_id in {"trk_riverside_short", "trk_riverside_200"}:
        return riverside_short_layout(track)
    if track_type == "INTERMEDIATE":
        return intermediate_template_layout(track)
    if track_type == "SUPERSPEEDWAY":
        return superspeedway_template_layout(track)
    if track_type == "ROAD":
        return road_template_layout(track)
    return oval_template_layout(track)


def all_template_builders():
    return {
        "riverside_short_v1": riverside_short_layout,
        "oval_template_v1": oval_template_layout,
        "intermediate_template_v1": intermediate_template_layout,
        "superspeedway_template_v1": superspeedway_template_layout,
        "road_template_v1": road_template_layout,
    }
