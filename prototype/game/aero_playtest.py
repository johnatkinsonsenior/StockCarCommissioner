"""Era 6 playtest: writable book, save/load, era rewind, tester career.

Days 123–126. A playtester can legalize specials, pull plates, invite
Chrysler, and plate one oval — then save, rewind the era, and load the
custom Winston Cup back. Harbor stays Vanguard when Chrysler is invited
on the pinnacle book. Superbirds need specials on and Valiant in the
factory list.
"""

from game.aero_wars import coupe_spec, live_book, venue_plate_mode

CUSTOM_SLOT = "era6-custom"
MID_SLOT = "era6-mid"
LOOP_WEEKS = 12


def _fail(errors, cond, message):
    if not cond:
        errors.append(message)
    return cond


def _harbor(rs):
    for team in rs.teams:
        if team.name == "Harbor Racing":
            return str(team.manufacturer or "")
    return ""


def _makers(rs):
    return [maker.name for maker in rs.manufacturers]


def _venues(rs):
    packages = rs.league.get("track_packages") or {}
    names = (packages.get("venues") or {})
    return {
        name: venue_plate_mode(name, packages) for name in names
    }


def _meters(rs):
    league = rs.league
    return {
        "integrity": int(league.get("integrity") or 0),
        "fan_interest": int(league.get("fan_interest") or 0),
        "controversy": int(league.get("controversy") or 0),
        "owner_pressure": int(league.get("owner_pressure") or 0),
        "driver_sentiment": int(league.get("driver_sentiment") or 0),
    }


def _open_pinnacle(rs):
    rs.apply_game_settings(
        {
            "era_book": "pinnacle",
            "difficulty": "normal",
            "career_seasons": 3,
            "autosave": "off",
        }
    )
    rs.reset_career_state(keep_settings=True)


def write_custom_book(rs):
    """Legalize specials, pull plates, invite Chrysler, plate Thunder Valley."""

    rs.apply_office_aero("aero_specials", "legal")
    rs.apply_office_aero("plates", "off")
    rs.apply_office_aero("chrysler", "on")
    rs.apply_office_aero("venue_plates", "Thunder Valley:on")
    rs.apply_office_aero("body_pick", "Apex:torino")
    return rs.league.get("aero_book") or {}


def assert_custom_book(rs, errors, prefix="custom"):
    """Check the writable-book loop landed."""

    book = rs.league.get("aero_book") or {}
    _fail(
        errors,
        book.get("aero_specials") == "legal",
        "%s specials should be legal, got %s" % (prefix, book.get("aero_specials")),
    )
    _fail(
        errors,
        book.get("plates") is False,
        "%s plates should be pulled, got %s" % (prefix, book.get("plates")),
    )
    _fail(
        errors,
        book.get("chrysler") is True,
        "%s Chrysler should be invited" % prefix,
    )
    _fail(
        errors,
        _harbor(rs) == "Vanguard",
        "%s Harbor should stay Vanguard, got %s" % (prefix, _harbor(rs)),
    )
    _fail(
        errors,
        "Valiant" in _makers(rs),
        "%s Valiant should sit on the factory list" % prefix,
    )
    _fail(
        errors,
        _venues(rs).get("Thunder Valley") == "on",
        "%s Thunder Valley should be plated" % prefix,
    )
    _fail(
        errors,
        (book.get("body_picks") or {}).get("Apex") == "torino",
        "%s Apex should field the Torino" % prefix,
    )
    spec = coupe_spec("Valiant")
    _fail(
        errors,
        (spec or {}).get("id") == "superbird",
        "%s Valiant should field Superbirds, got %s" % (prefix, (spec or {}).get("id")),
    )
    bound = live_book() or {}
    _fail(
        errors,
        bound.get("aero_specials") == "legal",
        "%s live book should keep legal specials after bind_live" % prefix,
    )
    _fail(
        errors,
        bound.get("plates") is False,
        "%s live book should keep plates pulled" % prefix,
    )
    return book


def assert_era_default(rs, errors, era, prefix="era"):
    """Check a New career rewound to the inherited book, not a custom one."""

    book = rs.league.get("aero_book") or {}
    settings_era = rs.current_settings.get("era_book")
    _fail(
        errors,
        settings_era == era,
        "%s era_book should be %s, got %s" % (prefix, era, settings_era),
    )
    if era == "1970s":
        _fail(
            errors,
            book.get("aero_specials") == "banned",
            "%s 1970s specials should be banned, got %s"
            % (prefix, book.get("aero_specials")),
        )
        _fail(
            errors,
            book.get("chrysler") is True,
            "%s 1970s Chrysler should already be in the book" % prefix,
        )
        _fail(
            errors,
            book.get("plates") is False,
            "%s 1970s plates should be off" % prefix,
        )
        _fail(
            errors,
            _harbor(rs) == "Valiant",
            "%s 1970s Harbor should badge Valiant, got %s" % (prefix, _harbor(rs)),
        )
        _fail(
            errors,
            not (book.get("body_picks") or {}),
            "%s 1970s should not keep a custom Apex Torino pick" % prefix,
        )
        _fail(
            errors,
            "Thunder Valley" not in _venues(rs),
            "%s 1970s should not keep the Thunder Valley override" % prefix,
        )
    return book


def writable_book_loop(rs):
    """Day 123: specials, plates, Chrysler, venue kits."""

    errors = []
    _open_pinnacle(rs)
    book = rs.league.get("aero_book") or {}
    _fail(
        errors,
        book.get("aero_specials") == "banned",
        "pinnacle specials start banned",
    )
    _fail(errors, book.get("plates") is True, "pinnacle plates start on")
    _fail(errors, book.get("chrysler") is False, "pinnacle Chrysler starts out")
    _fail(errors, _harbor(rs) == "Vanguard", "pinnacle Harbor is Vanguard")
    _fail(
        errors,
        "Valiant" not in _makers(rs),
        "pinnacle Valiant sits out until invited",
    )
    write_custom_book(rs)
    assert_custom_book(rs, errors, "loop")
    return errors


def save_load_book_pass(rs):
    """Day 124: custom book round-trips; Chrysler roster comes back."""

    errors = []
    _open_pinnacle(rs)
    write_custom_book(rs)
    rs.save_career(save_name=CUSTOM_SLOT)
    rs.start_office_career({"era_book": "1970s"})
    assert_era_default(rs, errors, "1970s", "after-save-rewind")
    path = rs.resolve_office_save_path(CUSTOM_SLOT)
    if not rs.load_career(path):
        errors.append("could not load %s" % CUSTOM_SLOT)
        return errors
    assert_custom_book(rs, errors, "loaded")
    _fail(
        errors,
        rs.current_settings.get("era_book") == "pinnacle",
        "loaded career should restore the pinnacle era book",
    )
    return errors


def era_rewind_vs_custom(rs):
    """Day 124: New career rewinds; Load restores the custom book."""

    errors = []
    _open_pinnacle(rs)
    write_custom_book(rs)
    rs.save_career(save_name=CUSTOM_SLOT)
    rs.start_office_career({"era_book": "1970s"})
    assert_era_default(rs, errors, "1970s", "new-1970s")
    bound = live_book() or {}
    _fail(
        errors,
        bound.get("aero_specials") == "banned",
        "live book after era rewind should be banned specials, not Superbirds",
    )
    path = rs.resolve_office_save_path(CUSTOM_SLOT)
    if not rs.load_career(path):
        errors.append("could not load custom book after era rewind")
        return errors
    assert_custom_book(rs, errors, "restored-after-rewind")
    return errors


def tester_career_pass(rs, weeks=LOOP_WEEKS):
    """Day 126: meters, Superbirds, and plates hold for a short career."""

    errors = []
    _open_pinnacle(rs)
    write_custom_book(rs)
    seen = []
    for _ in range(int(weeks)):
        rs.advance_office_week()
        meters = _meters(rs)
        seen.append(meters)
        for key, value in meters.items():
            _fail(
                errors,
                0 <= value <= 100,
                "meter %s out of range at week %s: %s"
                % (key, len(seen), value),
            )
        spec = coupe_spec("Valiant")
        _fail(
            errors,
            (spec or {}).get("id") == "superbird",
            "Superbirds dropped off at week %s" % len(seen),
        )
        book = rs.league.get("aero_book") or {}
        _fail(
            errors,
            book.get("plates") is False,
            "plates came back at week %s" % len(seen),
        )
        _fail(
            errors,
            _harbor(rs) == "Vanguard",
            "Harbor rebadged at week %s: %s" % (len(seen), _harbor(rs)),
        )
    rs.save_career(save_name=MID_SLOT)
    rs.start_office_career({"era_book": "1970s"})
    path = rs.resolve_office_save_path(MID_SLOT)
    if not rs.load_career(path):
        errors.append("could not reload the tester career")
        return {"errors": errors, "weeks": len(seen), "meters": seen}
    assert_custom_book(rs, errors, "tester-reload")
    last = seen[-1] if seen else _meters(rs)
    return {
        "errors": errors,
        "weeks": len(seen),
        "meters": last,
        "races": len(rs.race_history),
        "superbird": (coupe_spec("Valiant") or {}).get("id"),
        "plates": bool((rs.league.get("aero_book") or {}).get("plates")),
    }


def cleanup_playtest_saves(rs):
    folder = rs.get_saves_folder()
    for name in (CUSTOM_SLOT, MID_SLOT):
        path = folder / ("%s.json" % name)
        if path.is_file():
            path.unlink()


def run_era6_playtest(rs):
    """Run Days 123, 124, and 126 and return a report dict."""

    report = {
        "loop": [],
        "save_load": [],
        "rewind": [],
        "tester": {},
    }
    try:
        report["loop"] = writable_book_loop(rs)
        report["save_load"] = save_load_book_pass(rs)
        report["rewind"] = era_rewind_vs_custom(rs)
        report["tester"] = tester_career_pass(rs)
    finally:
        cleanup_playtest_saves(rs)
    tester_errors = (report.get("tester") or {}).get("errors") or []
    report["ok"] = not (
        report["loop"] or report["save_load"] or report["rewind"] or tester_errors
    )
    return report
