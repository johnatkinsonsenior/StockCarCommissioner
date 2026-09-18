#!/usr/bin/env python3
"""Write a live career snapshot and open the Godot 4 UI prototype."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import run_season as rs


def main():
    continued = rs.boot_office_session()
    print("OFFICE_CONTINUE=%s" % (1 if continued else 0))
    result = rs.launch_godot_ui()
    if not result.get("binary"):
        print(result.get("output") or "Godot 4.4 was not found.")
        print("Install Godot 4.4 from https://godotengine.org/download")
        print("or set GODOT_BIN to the editor .exe / binary.")
        sys.exit(2)
    if result.get("returncode") not in (0, None):
        sys.exit(result.get("returncode") or 1)


if __name__ == "__main__":
    main()
