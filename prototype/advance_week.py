#!/usr/bin/env python3
"""Advance the office career one week and rewrite the Godot snapshot."""

import io
import sys
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import run_season as rs


def main():
    log = io.StringIO()
    recap = {}
    try:
        with redirect_stdout(log):
            if rs.office_save_path().is_file():
                rs.restore_office_career()
            else:
                rs.reset_career_state()
            recap = rs.advance_office_week()
            rs.persist_office_career()
            rs.write_ui_snapshot()
    except Exception as error:
        print("WEEK_OK=0")
        print("WEEK_ERROR=%s" % error)
        return 1
    print("WEEK_OK=1")
    print("WEEK_KIND=%s" % recap.get("kind", ""))
    print("WEEK_TITLE=%s" % recap.get("title", ""))
    print("WEEK_RACE=%s" % recap.get("race_number", ""))
    print("WEEK_TRACK=%s" % recap.get("track", ""))
    print("WEEK_WINNER=%s" % recap.get("winner", ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
