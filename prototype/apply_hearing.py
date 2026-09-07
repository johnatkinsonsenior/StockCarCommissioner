#!/usr/bin/env python3
"""Apply a commissioner hearing choice from the office and rewrite the snapshot."""

import io
import sys
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import run_season as rs


def main():
    hearing_id = ""
    choice_id = ""
    if len(sys.argv) >= 3:
        hearing_id = str(sys.argv[1] or "")
        choice_id = str(sys.argv[2] or "")
    log = io.StringIO()
    result = {}
    try:
        if not hearing_id or not choice_id:
            raise ValueError("hearing-id and choice-id are required")
        with redirect_stdout(log):
            if rs.office_save_path().is_file():
                rs.restore_office_career()
            else:
                rs.reset_career_state()
            result = rs.apply_office_hearing(hearing_id, choice_id)
            rs.persist_office_career()
            rs.write_ui_snapshot()
    except Exception as error:
        print("HEARING_OK=0")
        print("HEARING_ERROR=%s" % error)
        return 1
    print("HEARING_OK=1")
    print("HEARING_ID=%s" % result.get("event_id", hearing_id))
    print("HEARING_CHOICE=%s" % result.get("choice_id", choice_id))
    print("HEARING_LABEL=%s" % result.get("choice_label", ""))
    print("HEARING_OUTCOME=%s" % result.get("outcome", ""))
    print("HEARING_TITLE=%s" % result.get("event_title", ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
