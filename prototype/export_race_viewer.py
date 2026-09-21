#!/usr/bin/env python3
"""Export Riverside viewer fixtures, layouts, and the top-down car sprite."""

from __future__ import annotations

import argparse
import json
import struct
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from game.race_fixtures import build_riverside_fixture
from game.race_playback import (
    project_race_viewer_bundle,
    validate_bundle,
    write_bundle,
)
from game.track_layouts import all_template_builders


def _repo_root():
    return ROOT.parent


def write_png(path, width, height, rgba):
    def chunk(tag, data):
        return (
            struct.pack(">I", len(data))
            + tag
            + data
            + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        )

    raw = b""
    for y in range(height):
        raw += b"\x00"
        start = y * width * 4
        raw += bytes(rgba[start : start + width * 4])
    payload = b"\x89PNG\r\n\x1a\n"
    payload += chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))
    payload += chunk(b"IDAT", zlib.compress(raw, 9))
    payload += chunk(b"IEND", b"")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)
    return path


def write_car_sprite(path):
    """Write an original top-down stock-car sprite that Godot can tint."""

    width, height = 48, 24
    pixels = bytearray(width * height * 4)
    for y in range(height):
        for x in range(width):
            idx = (y * width + x) * 4
            body = 18 <= x <= 44 and 5 <= y <= 18
            nose = 6 <= x <= 17 and 8 <= y <= 15
            cabin = 22 <= x <= 34 and 7 <= y <= 16
            wheel = (x in (12, 13, 38, 39) and y in (3, 4, 19, 20))
            if wheel:
                pixels[idx : idx + 4] = bytes((18, 18, 18, 255))
            elif cabin:
                pixels[idx : idx + 4] = bytes((210, 220, 230, 255))
            elif nose or body:
                pixels[idx : idx + 4] = bytes((236, 236, 236, 255))
            else:
                pixels[idx : idx + 4] = bytes((0, 0, 0, 0))
    return write_png(path, width, height, pixels)


def write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return path


def export_fixture(field_size, dest_root, laps=None):
    fixture = build_riverside_fixture(field_size=field_size, scheduled_laps=laps)
    bundle = project_race_viewer_bundle(
        fixture["input"], fixture["result"], fixture["layout"]
    )
    validate_bundle(bundle, fixture["layout"])
    label = "riverside_200" if field_size == 8 else "riverside_200_%s" % field_size
    if laps and laps != 20:
        label = "%s_%sl" % (label, laps)
    races = dest_root / "godot" / "data" / "races"
    proto = dest_root / "prototype" / "data" / "races"
    write_json(proto / ("%s_input.json" % label), fixture["input"])
    write_json(proto / ("%s_result.json" % label), fixture["result"])
    write_bundle(bundle, races / ("%s_viewer.json" % label))
    write_json(dest_root / "godot" / "assets" / "tracks" / "riverside_short.json", fixture["layout"])
    return bundle, fixture


def export_templates(dest_root, sample_track):
    folder = dest_root / "godot" / "assets" / "tracks"
    for layout_id, builder in all_template_builders().items():
        if layout_id == "riverside_short_v1":
            continue
        write_json(folder / ("%s.json" % layout_id), builder(sample_track))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=str(_repo_root()))
    args = parser.parse_args(argv)
    root = Path(args.root)
    eight, fixture = export_fixture(8, root)
    forty, _ = export_fixture(40, root)
    export_templates(root, fixture["input"]["track"])
    write_car_sprite(root / "godot" / "assets" / "cars" / "stock_car_topdown.png")
    print("VIEWER_EXPORT_8=%s" % eight["race_id"])
    print("VIEWER_EXPORT_8_HASH=%s" % eight["bundle_hash"])
    print("VIEWER_EXPORT_8_FRAMES=%s" % len(eight["keyframes"]))
    print("VIEWER_EXPORT_40=%s" % forty["race_id"])
    print("VIEWER_EXPORT_40_HASH=%s" % forty["bundle_hash"])
    print("VIEWER_EXPORT_40_CARS=%s" % len(forty["entries"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
