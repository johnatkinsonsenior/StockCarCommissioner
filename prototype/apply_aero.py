#!/usr/bin/env python3
"""Rewrite one Aero Wars winter-book or package slot from the office.

Day 117 prints homologation count and wheelbase class so the Rulebook
desk can round-trip those levers.
"""

import io
import sys
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import run_season as rs
from game.aero_wars import venue_plate_mode


def main():
    key = ""
    value = ""
    if len(sys.argv) >= 3:
        key = str(sys.argv[1] or "").strip()
        value = str(sys.argv[2] or "").strip()
    log = io.StringIO()
    try:
        if not key:
            raise ValueError("aero-key is required")
        with redirect_stdout(log):
            if rs.office_save_path().is_file():
                rs.restore_office_career()
            else:
                rs.reset_career_state()
            book = rs.apply_office_aero(key, value)
            rs.persist_office_career()
            rs.write_ui_snapshot()
    except Exception as error:
        print("AERO_OK=0")
        print("AERO_ERROR=%s" % error)
        return 1
    print("AERO_OK=1")
    print("AERO_KEY=%s" % key)
    print("AERO_VALUE=%s" % value)
    print("AERO_SPECIALS=%s" % (book.get("aero_specials") if book else ""))
    print("AERO_TEMPLATE=%s" % (book.get("template") if book else ""))
    print("AERO_PLATES=%s" % (book.get("plates") if book else ""))
    print("AERO_CHRYSLER=%s" % (book.get("chrysler") if book else ""))
    print("AERO_HOMOLOGATION=%s" % (book.get("homologation") if book else ""))
    print("AERO_WHEELBASE=%s" % (book.get("wheelbase") if book else ""))
    picks = (book.get("body_picks") if book else None) or {}
    print("AERO_BODY_PICKS=%s" % ",".join("%s:%s" % item for item in sorted(picks.items())))
    packages = rs.league.get("track_packages") if rs.league else None
    venues = (packages or {}).get("venues") or {}
    bits = []
    for name in sorted(venues):
        bits.append("%s:%s" % (name, venue_plate_mode(name, packages)))
    print("AERO_VENUES=%s" % ",".join(bits))
    return 0


if __name__ == "__main__":
    sys.exit(main())
