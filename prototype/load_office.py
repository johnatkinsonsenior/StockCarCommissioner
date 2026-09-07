#!/usr/bin/env python3
"""Load a career slot onto the office desk and rewrite the Godot snapshot."""

import io
import sys
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import run_season as rs


def main():
    save_name = ""
    if len(sys.argv) >= 2:
        save_name = str(sys.argv[1] or "").strip()
    log = io.StringIO()
    path = None
    try:
        if not save_name:
            raise ValueError("save name is required")
        with redirect_stdout(log):
            path = rs.load_office_slot(save_name)
    except Exception as error:
        print("LOAD_OK=0")
        print("LOAD_ERROR=%s" % error)
        return 1
    print("LOAD_OK=1")
    print("LOAD_PATH=%s" % path)
    print("LOAD_NAME=%s" % (path.stem if path is not None else save_name))
    print("CALENDAR=%s" % rs.calendar.description())
    return 0


if __name__ == "__main__":
    sys.exit(main())
