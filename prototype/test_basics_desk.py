#!/usr/bin/env python3
"""Assert the commissioner-basics desk: Cup roster, winter book, no politics."""

import io
import sys
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import run_season as rs
from game.ui_bridge import (
    BASICS_HEARING_CATEGORIES,
    DESK_MODE,
    ERA_START_BOOKS,
    UI_VERSION,
    clamp_era_book,
    compose_ui_snapshot,
)


HIDDEN_NAV = {
    "prospects",
    "hearings",
    "treasury",
    "television",
    "sponsors",
    "hof",
    "board",
    "councils",
}


def _fail(errors, message):
    errors.append(message)


def main():
    errors = []
    log = io.StringIO()
    with redirect_stdout(log):
        rs.start_office_career(
            {
                "difficulty": "normal",
                "career_seasons": 3,
                "autosave": "off",
                "era_book": "pinnacle",
            }
        )
        snapshot = rs.build_ui_snapshot()
        beyond = rs.start_office_career(
            {
                "difficulty": "normal",
                "career_seasons": 3,
                "autosave": "off",
                "era_book": "beyond",
            }
        )
        seventies = rs.start_office_career(
            {
                "difficulty": "normal",
                "career_seasons": 3,
                "autosave": "off",
                "era_book": "1970s",
            }
        )
        seventies_snap = rs.build_ui_snapshot()

    if DESK_MODE != "basics":
        _fail(errors, "DESK_MODE is %s" % DESK_MODE)
    if UI_VERSION != "2.6":
        _fail(errors, "UI_VERSION is %s" % UI_VERSION)
    if snapshot.get("desk_mode") != "basics":
        _fail(errors, "snapshot desk_mode is %s" % snapshot.get("desk_mode"))

    nav_ids = [item.get("id") for item in (snapshot.get("office") or {}).get("nav") or []]
    for hidden in sorted(HIDDEN_NAV):
        if hidden in nav_ids:
            _fail(errors, "nav still shows %s" % hidden)
    for required in ("dashboard", "mail", "standings", "schedule", "teams", "drivers", "rulebook", "history", "settings"):
        if required not in nav_ids:
            _fail(errors, "nav missing %s" % required)

    if snapshot.get("prospects"):
        _fail(errors, "prospects still on the desk: %s" % len(snapshot.get("prospects") or []))

    for hearing in snapshot.get("hearings") or []:
        category = str(hearing.get("category") or "")
        if category not in BASICS_HEARING_CATEGORIES:
            _fail(errors, "parked hearing on desk: %s" % category)

    inbox = (snapshot.get("office") or {}).get("inbox") or []
    for letter in inbox:
        kind = str(letter.get("kind") or "")
        category = str(letter.get("category") or "")
        if kind == "hearing" and category not in BASICS_HEARING_CATEGORIES:
            _fail(errors, "inbox hearing %s" % category)
        subject = str(letter.get("subject") or "").lower()
        if "prospect" in subject or "owner council" in subject or "driver council" in subject:
            _fail(errors, "parked memo in inbox: %s" % letter.get("subject"))

    welcome = next((item for item in inbox if item.get("id") == "welcome"), {})
    body = str(welcome.get("body") or "")
    if "board wants" in body.lower():
        _fail(errors, "welcome letter still talks about the board")
    if "do not own a shop" not in body.lower():
        _fail(errors, "welcome letter missing commissioner-only line")

    dash = snapshot.get("dashboard") or {}
    if dash.get("approval"):
        _fail(errors, "dashboard still shows approval")
    if dash.get("board"):
        _fail(errors, "dashboard still shows board")
    if dash.get("prospects"):
        _fail(errors, "dashboard still shows prospects")

    era_ids = [row.get("id") for row in (snapshot.get("settings") or {}).get("era_books") or []]
    if "beyond" in era_ids:
        _fail(errors, "Beyond still in era picker")
    if list(era_ids) != list(ERA_START_BOOKS):
        _fail(errors, "era books are %s" % era_ids)

    if beyond.get("era_book") != "pinnacle":
        _fail(errors, "beyond new career was not clamped: %s" % beyond.get("era_book"))
    if clamp_era_book("beyond") != "pinnacle":
        _fail(errors, "clamp_era_book(beyond) failed")

    if seventies.get("era_book") != "1970s":
        _fail(errors, "1970s new career lost: %s" % seventies.get("era_book"))
    if (seventies_snap.get("settings") or {}).get("era_book") != "1970s":
        _fail(errors, "1970s snapshot era is %s" % (seventies_snap.get("settings") or {}).get("era_book"))

    rulebook = snapshot.get("rulebook") or {}
    if not isinstance(rulebook, dict) or not rulebook.get("bodies"):
        # 1970s snapshot still has bodies
        rulebook = seventies_snap.get("rulebook") or {}
    if isinstance(rulebook, dict) and not rulebook.get("bodies"):
        _fail(errors, "rulebook lost homologated bodies")

    composed = compose_ui_snapshot(
        {
            "hearings": [
                {"id": "a", "category": "factory-lobby", "title": "Detroit"},
                {"id": "b", "category": "rule-change", "title": "Points"},
            ],
            "alerts": ["A prospect is ready for a call-up", "Fan interest is sliding."],
            "prospects": [{"name": "hidden"}],
            "dashboard": {"alerts": ["The board is watching"], "approval": "nope"},
        }
    )
    cats = [item.get("category") for item in composed.get("hearings") or []]
    if cats != ["rule-change"]:
        _fail(errors, "compose filter hearings: %s" % cats)
    if composed.get("prospects"):
        _fail(errors, "compose left prospects")
    dash_alerts = (composed.get("dashboard") or {}).get("alerts") or []
    if dash_alerts:
        _fail(errors, "compose left board alert: %s" % dash_alerts)

    print("BASICS_OK=%s" % (1 if not errors else 0))
    print("DESK_MODE=%s" % DESK_MODE)
    print("NAV=%s" % ",".join(str(item) for item in nav_ids))
    print("HEARINGS=%s" % len(snapshot.get("hearings") or []))
    print("PROSPECTS=%s" % len(snapshot.get("prospects") or []))
    print("ERA_BOOKS=%s" % ",".join(str(item) for item in era_ids))
    print("CLAMP_BEYOND=%s" % beyond.get("era_book"))
    print("ERA_1970S=%s" % seventies.get("era_book"))
    print("TEAMS=%s" % len(snapshot.get("teams") or []))
    print("DRIVERS=%s" % len(seventies_snap.get("drivers") or []))
    for item in errors:
        print("BASICS_ERROR=%s" % item)
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
