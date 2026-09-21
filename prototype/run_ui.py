#!/usr/bin/env python3
"""Write a live career snapshot and open the Godot 4 UI prototype."""

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import run_season as rs
from game.desktop_runtime import ensure_godot_binary


def main():
    continued = rs.boot_office_session()
    print("OFFICE_CONTINUE=%s" % (1 if continued else 0))
    try:
        godot = ensure_godot_binary()
    except Exception as error:
        print("Could not fetch Godot 4.4: %s" % error)
        godot = None
    if godot:
        os.environ.setdefault("GODOT_BIN", str(godot))
        print("GODOT_BIN=%s" % godot)
    result = rs.launch_godot_ui()
    if not result.get("binary"):
        print(result.get("output") or "Godot 4.4 was not found.")
        print("Double-click \"Double-click to play.bat\" with internet once.")
        print("It downloads Godot 4.4 into tools\\godot.")
        sys.exit(2)
    if result.get("returncode") not in (0, None):
        sys.exit(result.get("returncode") or 1)


if __name__ == "__main__":
    main()
