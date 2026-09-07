#!/usr/bin/env python3
"""Save the office career into a named slot and rewrite the Godot snapshot."""

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
        with redirect_stdout(log):
            if rs.office_save_path().is_file():
                rs.restore_office_career()
            else:
                rs.reset_career_state()
            path = rs.save_office_slot(save_name or None)
    except Exception as error:
        print("SAVE_OK=0")
        print("SAVE_ERROR=%s" % error)
        return 1
    print("SAVE_OK=1")
    print("SAVE_PATH=%s" % path)
    print("SAVE_NAME=%s" % (path.stem if path is not None else save_name))
    print("SAVE_COUNT=%s" % len(rs.office_save_catalog()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
