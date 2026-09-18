#!/usr/bin/env python3
"""Run the Era 6 writable-book playtest (Days 123, 124, 126)."""

import io
import sys
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import run_season as rs
from game.aero_playtest import run_era6_playtest


def _print_errors(label, errors):
    print("%s_OK=%s" % (label, 0 if errors else 1))
    if errors:
        for item in errors:
            print("%s_ERROR=%s" % (label, item))


def main():
    log = io.StringIO()
    try:
        with redirect_stdout(log):
            report = run_era6_playtest(rs)
    except Exception as error:
        print("PLAYTEST_OK=0")
        print("PLAYTEST_ERROR=%s" % error)
        return 1
    loop = report.get("loop") or []
    save_load = report.get("save_load") or []
    rewind = report.get("rewind") or []
    tester = report.get("tester") or {}
    tester_errors = tester.get("errors") or []
    _print_errors("LOOP", loop)
    _print_errors("SAVE_LOAD", save_load)
    _print_errors("REWIND", rewind)
    _print_errors("TESTER", tester_errors)
    print("TESTER_WEEKS=%s" % tester.get("weeks", 0))
    print("TESTER_RACES=%s" % tester.get("races", 0))
    print("TESTER_SUPERBIRD=%s" % tester.get("superbird", ""))
    print("TESTER_PLATES=%s" % tester.get("plates"))
    meters = tester.get("meters") or {}
    print("TESTER_INTEGRITY=%s" % meters.get("integrity", ""))
    print("TESTER_FANS=%s" % meters.get("fan_interest", ""))
    print("TESTER_CONTROVERSY=%s" % meters.get("controversy", ""))
    print("PLAYTEST_OK=%s" % (1 if report.get("ok") else 0))
    status = rs.aero_desk_status()
    print("AERO_HARBOR=%s" % status.get("harbor", ""))
    print("AERO_VALIANT=%s" % int(bool(status.get("valiant"))))
    return 0 if report.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
