#!/usr/bin/env python3
"""Start a new commissioner career on the office desk."""

import io
import sys
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import run_season as rs


def main():
    difficulty = ""
    seasons = ""
    autosave = ""
    era_book = ""
    if len(sys.argv) >= 2:
        difficulty = str(sys.argv[1] or "").strip()
    if len(sys.argv) >= 3:
        seasons = str(sys.argv[2] or "").strip()
    if len(sys.argv) >= 4:
        autosave = str(sys.argv[3] or "").strip()
    if len(sys.argv) >= 5:
        era_book = str(sys.argv[4] or "").strip()
    log = io.StringIO()
    settings = {}
    try:
        data = {}
        if difficulty:
            data["difficulty"] = difficulty
        if seasons:
            data["career_seasons"] = int(seasons)
        if autosave:
            data["autosave"] = autosave
        if era_book:
            data["era_book"] = era_book
        with redirect_stdout(log):
            settings = rs.start_office_career(data)
    except Exception as error:
        print("NEW_OK=0")
        print("NEW_ERROR=%s" % error)
        return 1
    print("NEW_OK=1")
    print("ERA_BOOK=%s" % settings.get("era_book", ""))
    print("DIFFICULTY=%s" % settings.get("difficulty", ""))
    print("CAREER_SEASONS=%s" % settings.get("career_seasons", ""))
    print("CALENDAR=%s" % rs.calendar.description())
    return 0


if __name__ == "__main__":
    sys.exit(main())
