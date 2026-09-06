"""Godot UI helpers: snapshot JSON, office layout, and engine launch."""

import json
import os
import shutil
import subprocess
from pathlib import Path

UI_VERSION = "0.3"
GODOT_MAJOR = 4
OFFICE_LAYOUT = "commissioner-desk"

HEARING_SENDERS = {
    "rule-change": "Competition Committee",
    "safety": "Safety Committee",
    "owner-complaint": "Owner's Office",
    "driver-complaint": "Garage Steward",
    "rivalry": "Competition Committee",
    "press-conference": "Media Relations",
    "media-controversy": "Communications",
    "owner-council": "Owner Council",
    "driver-council": "Driver Council",
    "rule-proposal": "Rules Docket",
    "rule-vote": "Owner Council",
    "lobbying": "Paddock Lobby",
    "board-confidence": "Board of Directors",
    "team-entry": "Charter Office",
    "team-closure": "Charter Office",
    "manufacturer-switch": "Factory Desk",
}

OFFICE_NAV = (
    {"id": "dashboard", "label": "Dashboard", "group": ""},
    {"id": "mail", "label": "Mail", "group": ""},
    {"id": "standings", "label": "Standings", "group": "Competition"},
    {"id": "schedule", "label": "Schedule", "group": "Competition"},
    {"id": "hearings", "label": "Hearings", "group": "Competition"},
    {"id": "teams", "label": "Teams", "group": "Paddock"},
    {"id": "drivers", "label": "Drivers", "group": "Paddock"},
    {"id": "prospects", "label": "Prospects", "group": "Paddock"},
    {"id": "treasury", "label": "Treasury", "group": "Business"},
    {"id": "television", "label": "Television", "group": "Business"},
    {"id": "sponsors", "label": "Sponsors", "group": "Business"},
    {"id": "rulebook", "label": "Rulebook", "group": "League"},
    {"id": "board", "label": "Board", "group": "League"},
    {"id": "settings", "label": "Settings", "group": ""},
    {"id": "quit", "label": "Quit", "group": ""},
)

OFFICE_CHECKLIST = (
    {"id": "dashboard", "label": "Review the dashboard", "section": "dashboard"},
    {"id": "standings", "label": "View standings", "section": "standings"},
    {"id": "teams", "label": "Review teams", "section": "teams"},
    {"id": "television", "label": "Check television and naming rights", "section": "television"},
    {"id": "drivers", "label": "Review the grid", "section": "drivers"},
    {"id": "rulebook", "label": "Open the rulebook", "section": "rulebook"},
    {"id": "board", "label": "Check the board", "section": "board"},
    {"id": "mail", "label": "Read series mail", "section": "mail"},
)


def hearing_sender(category=None):
    """Return the desk that files a hearing letter."""

    return HEARING_SENDERS.get(category or "", "Series Office")


def make_letter(
    letter_id,
    kind,
    from_name,
    subject,
    body,
    category="",
    hearing_id="",
    prompt="",
    choices=None,
):
    """Return one inbox letter dictionary."""

    return {
        "id": letter_id,
        "kind": kind or "letter",
        "from": from_name or "Series Office",
        "subject": subject or "Mail",
        "body": body or "",
        "unread": True,
        "category": category or "",
        "hearing_id": hearing_id or "",
        "prompt": prompt or "",
        "choices": list(choices or []),
    }


def hearing_letter(decision):
    """Turn a queued decision event into an inbox hearing."""

    decision = decision or {}
    hearing_id = str(decision.get("id") or "hearing")
    category = str(decision.get("category") or "")
    title = str(decision.get("title") or "Hearing")
    prompt = str(decision.get("prompt") or "")
    choices = [
        {"id": str(choice.get("id", "")), "label": str(choice.get("label", ""))}
        for choice in decision.get("choices") or []
        if isinstance(choice, dict)
    ]
    body = prompt or ("The %s asks for a ruling." % hearing_sender(category))
    return make_letter(
        letter_id="hearing-%s" % hearing_id,
        kind="hearing",
        from_name=hearing_sender(category),
        subject=title,
        body=body,
        category=category,
        hearing_id=hearing_id,
        prompt=prompt,
        choices=choices,
    )


def alert_letter(index, alert):
    """Turn a dashboard alert into a league-office memo."""

    text = str(alert)
    return make_letter(
        letter_id="alert-%s" % index,
        kind="alert",
        from_name="League Office",
        subject=text,
        body=(
            "Commissioner,\n\n"
            "%s\n\n"
            "This sits on the dashboard until the situation changes. "
            "Read it, then Advance when the inbox is clear enough to work."
            % text
        ),
    )


def press_letter(index, story):
    """Turn a media story into a press clipping."""

    if not isinstance(story, dict):
        story = {"headline": str(story), "body": str(story)}
    headline = str(story.get("headline") or "Press clipping")
    body = str(story.get("body") or headline)
    outlet = str(story.get("outlet") or "Beat desk")
    return make_letter(
        letter_id="press-%s" % index,
        kind="press",
        from_name=outlet,
        subject=headline,
        body=body,
    )


def welcome_letter(payload=None):
    """Return the series-office briefing that opens a career."""

    payload = payload or {}
    series = payload.get("series") or "the series"
    mail = payload.get("mail") or {}
    return make_letter(
        letter_id="welcome",
        kind="letter",
        from_name=mail.get("from") or "Series Office — Preseason",
        subject=mail.get("title") or ("Welcome to %s" % series),
        body=mail.get("body") or default_welcome_body(series),
    )


def normalize_letter(item, index=0):
    """Fill missing inbox fields on a letter dict."""

    item = dict(item or {})
    kind = item.get("kind") or "letter"
    letter_id = item.get("id") or ("%s-%s" % (kind, index))
    return make_letter(
        letter_id=letter_id,
        kind=kind,
        from_name=item.get("from") or "Series Office",
        subject=item.get("subject") or item.get("title") or "Mail",
        body=item.get("body") or item.get("prompt") or "",
        category=item.get("category") or "",
        hearing_id=item.get("hearing_id") or "",
        prompt=item.get("prompt") or "",
        choices=item.get("choices") or [],
    )


def build_office_inbox(payload=None):
    """Build the live inbox: hearings, memos, press, and series letters."""

    payload = payload or {}
    if payload.get("inbox"):
        return [
            normalize_letter(item, index)
            for index, item in enumerate(payload.get("inbox") or [])
        ]
    letters = []
    decision = payload.get("decision")
    if decision:
        letters.append(hearing_letter(decision))
    alerts = payload.get("alerts")
    if alerts is None:
        alerts = (payload.get("dashboard") or {}).get("alerts") or []
    for index, alert in enumerate(alerts):
        letters.append(alert_letter(index, alert))
    headlines = payload.get("headlines") or payload.get("media") or []
    for index, story in enumerate(headlines):
        letters.append(press_letter(index, story))
    letters.append(welcome_letter(payload))
    return letters


def selected_mail_id(inbox, requested=None):
    """Return the letter that should be open: a hearing first, else the top row."""

    inbox = list(inbox or [])
    if requested:
        for letter in inbox:
            if letter.get("id") == requested:
                return requested
    for letter in inbox:
        if letter.get("kind") == "hearing":
            return letter.get("id")
    if inbox:
        return inbox[0].get("id")
    return ""


def mail_view(letter):
    """Return the compact mail card the desk used before the inbox."""

    if not letter:
        return {
            "id": "",
            "kind": "letter",
            "title": "Mail",
            "from": "Series Office",
            "body": "",
        }
    return {
        "id": letter.get("id") or "",
        "kind": letter.get("kind") or "letter",
        "title": letter.get("subject") or letter.get("title") or "Mail",
        "from": letter.get("from") or "Series Office",
        "body": letter.get("body") or letter.get("prompt") or "",
    }


def letter_by_id(inbox, letter_id):
    """Return the inbox row matching letter_id."""

    for letter in inbox or []:
        if letter.get("id") == letter_id:
            return letter
    return None


def project_root():
    """Return the repository root (parent of prototype/)."""

    return Path(__file__).resolve().parent.parent.parent


def godot_project_dir():
    """Return the Godot 4 project folder."""

    return project_root() / "godot"


def default_snapshot_path():
    """Return the snapshot file the Godot project reads at runtime."""

    return godot_project_dir() / "data" / "ui_snapshot.json"


def default_office(payload=None):
    """Return the Football Commissioner-style office payload."""

    payload = payload or {}
    dashboard = payload.get("dashboard") or {}
    treasury = dashboard.get("treasury") or 0
    fans = dashboard.get("fan_interest") or 0
    calendar = payload.get("calendar") or dashboard.get("calendar") or "Preseason"
    checklist = payload.get("checklist") or [dict(item) for item in OFFICE_CHECKLIST]
    nav = payload.get("nav") or [dict(item) for item in OFFICE_NAV]
    inbox = build_office_inbox(payload)
    selected = selected_mail_id(inbox, payload.get("selected_mail_id"))
    opened = letter_by_id(inbox, selected)
    view = mail_view(opened)
    return {
        "layout": OFFICE_LAYOUT,
        "advance_label": payload.get("advance_label") or "Advance",
        "advance_hint": payload.get("advance_hint")
        or "Visit each section to unlock the first weekend.",
        "header": {
            "calendar": calendar,
            "treasury": treasury,
            "fans": fans,
            "status_line": payload.get("status_line")
            or "%s — $%s — %s fans" % (calendar, _comma(treasury), fans),
        },
        "mail": view,
        "inbox": inbox,
        "selected_mail_id": selected,
        "unread_count": len(inbox),
        "checklist": list(checklist),
        "nav": list(nav),
    }


def default_welcome_body(series=None):
    """Return the opening letter on the commissioner desk."""

    series = series or "the series"
    return (
        "Commissioner,\n\n"
        "You run %s. You do not drive.\n\n"
        "Revenue comes from television, naming rights, the gate, and fines. "
        "Owners want wins and cheaper shops. Drivers want a fair garage. "
        "Fans want a show. The board wants a league that still exists next year.\n\n"
        "Use the left rail to inspect standings, teams, television, and the "
        "rulebook. Mail is your inbox. When the checklist on the right is "
        "done, Advance unlocks the next weekend.\n\n"
        "The Python sim still runs the races. This office is where you sit."
        % series
    )


def _comma(value):
    try:
        number = int(value)
    except (TypeError, ValueError):
        return "0"
    sign = "-" if number < 0 else ""
    digits = str(abs(number))
    parts = []
    while len(digits) > 3:
        parts.insert(0, digits[-3:])
        digits = digits[:-3]
    parts.insert(0, digits or "0")
    return sign + ",".join(parts)


def compose_ui_snapshot(payload):
    """Build the JSON document the Godot office renders."""

    payload = payload or {}
    dashboard = payload.get("dashboard") or {}
    settings = payload.get("settings") or {}
    menu_items = payload.get("menu_items") or []
    office = default_office(payload)
    if payload.get("office"):
        incoming = payload.get("office") or {}
        office.update(incoming)
        if incoming.get("header"):
            office["header"] = dict(office.get("header") or {})
            office["header"].update(incoming.get("header") or {})
        if incoming.get("inbox"):
            office["inbox"] = [
                normalize_letter(item, index)
                for index, item in enumerate(incoming.get("inbox") or [])
            ]
        elif incoming.get("mail") and not office.get("inbox"):
            office["inbox"] = build_office_inbox({"mail": incoming.get("mail")})
        if incoming.get("mail") and not incoming.get("inbox"):
            office["mail"] = dict(office.get("mail") or {})
            office["mail"].update(incoming.get("mail") or {})
        selected = selected_mail_id(
            office.get("inbox") or [],
            incoming.get("selected_mail_id") or office.get("selected_mail_id"),
        )
        office["selected_mail_id"] = selected
        opened = letter_by_id(office.get("inbox") or [], selected)
        if opened:
            office["mail"] = mail_view(opened)
        office["unread_count"] = len(office.get("inbox") or [])
    return {
        "game": "Stock Car Commissioner",
        "ui_version": UI_VERSION,
        "engine": "godot-4",
        "layout": OFFICE_LAYOUT,
        "screen": payload.get("screen") or "mail",
        "series": payload.get("series") or "Stock Car Series",
        "settings_line": payload.get("settings_line") or "",
        "calendar": payload.get("calendar") or "",
        "menu_items": list(menu_items),
        "settings": {
            "difficulty": settings.get("difficulty") or "normal",
            "difficulty_label": settings.get("difficulty_label") or "Normal",
            "career_seasons": settings.get("career_seasons") or 3,
            "autosave": settings.get("autosave") or "off",
            "autosave_label": settings.get("autosave_label") or "Off",
        },
        "dashboard": dashboard,
        "decision": payload.get("decision"),
        "drivers": list(payload.get("drivers") or []),
        "schedule": list(payload.get("schedule") or []),
        "office": office,
    }


def write_ui_snapshot_file(snapshot, path=None):
    """Write a UI snapshot JSON file for Godot to load."""

    path = Path(path) if path else default_snapshot_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(snapshot, handle, indent=4)
    return path


def find_godot_binary():
    """Return a Godot 4 editor binary if one is on disk or PATH."""

    env_bin = os.environ.get("GODOT_BIN")
    candidates = []
    if env_bin:
        candidates.append(Path(env_bin))
    for name in ("godot", "godot4", "Godot_v4.4-stable_linux.x86_64"):
        found = shutil.which(name)
        if found:
            candidates.append(Path(found))
    candidates.extend(
        [
            Path("/tmp/godot-engine/Godot_v4.4-stable_linux.x86_64"),
            Path("/usr/local/bin/godot"),
            Path("/usr/bin/godot"),
        ]
    )
    for candidate in candidates:
        if candidate and candidate.is_file() and os.access(candidate, os.X_OK):
            return candidate
    return None


def launch_godot_process(snapshot_path=None, headless=None, extra_args=None):
    """Spawn Godot against the UI project. Returns a result dict."""

    binary = find_godot_binary()
    project = godot_project_dir()
    if headless is None:
        headless = not (
            os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY")
        )
    result = {
        "binary": str(binary) if binary else None,
        "project": str(project),
        "snapshot": str(snapshot_path) if snapshot_path else None,
        "headless": bool(headless),
        "returncode": None,
        "output": "",
    }
    if binary is None:
        result["output"] = (
            "Godot 4 was not found. Install Godot 4.4+ and open godot/project.godot, "
            "or set GODOT_BIN."
        )
        return result
    command = [str(binary), "--path", str(project)]
    if headless:
        command.extend(["--headless", "--quit-after", "3"])
    if extra_args:
        command.extend(list(extra_args))
    completed = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
    )
    result["returncode"] = completed.returncode
    result["output"] = (completed.stdout or "") + (completed.stderr or "")
    return result
