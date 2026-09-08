"""Aero Wars: homologated coupes and manufacturer track maps.

Day 113 replaces the single `aero_bias` tick that only fired on road
courses and superspeedways. Each factory fields a named two-door coupe
with a four-number map (short track, intermediate, superspeedway, road).
Race pace mixes that map with driver track skill. Day 114 lets the
commissioner rewrite the winter book and the per-track kit.
"""

from game.settings import (
    ERA_1970S,
    ERA_1980S,
    ERA_BEYOND,
    ERA_PINNACLE,
    current_settings,
)

FAMILY_FORD = "Ford"
FAMILY_GM = "GM"
FAMILY_CHRYSLER = "Chrysler"
FAMILY_INDEPENDENT = "Independent"

MAKER_FAMILY = {
    "Apex": FAMILY_FORD,
    "Vanguard": FAMILY_GM,
    "Falcon": FAMILY_GM,
    "Valiant": FAMILY_CHRYSLER,
    "Independent": FAMILY_INDEPENDENT,
}

TYPE_KEYS = {
    "Short Track": "short_track",
    "Intermediate": "intermediate",
    "Superspeedway": "superspeedway",
    "Road Course": "road_course",
}

# Driver skill leads on short tracks and roads. Aero leads on plates.
SKILL_WEIGHT = {
    "Short Track": 0.75,
    "Intermediate": 0.50,
    "Superspeedway": 0.25,
    "Road Course": 0.70,
}
AERO_WEIGHT = {
    "Short Track": 0.25,
    "Intermediate": 0.50,
    "Superspeedway": 0.75,
    "Road Course": 0.30,
}

# Daytona / Talladega analogues. Pinnacle plates start here (1988 book).
PLATE_TRACKS = ("Atlantic Speedway", "Coastal Superspeedway")

SPECIALS_BANNED = "banned"
SPECIALS_LEGAL = "legal"
SPECIALS_HOMOLOGATE = "homologate"

_LIVE = {"book": None, "packages": None}


def _era():
    key = str((current_settings or {}).get("era_book") or ERA_PINNACLE)
    if key in (ERA_1970S, ERA_1980S, ERA_PINNACLE, ERA_BEYOND):
        return key
    return ERA_PINNACLE


def _bound(value, lo=0, hi=100):
    return max(lo, min(hi, int(value)))


def family_for(maker_name):
    """Return the Detroit family a factory name stands in for."""

    return MAKER_FAMILY.get(str(maker_name or ""), FAMILY_INDEPENDENT)


def default_aero_book(era_book=None):
    """Return the inherited winter book for an era."""

    era = era_book or _era()
    book = {
        "homologation": 200,
        "wheelbase": 110,
        "coupe_only": True,
        "aero_specials": SPECIALS_BANNED,
        "aerocoupes": False,
        "template": "identity",
        "chrysler": False,
        "plates": False,
        "plate_tracks": list(PLATE_TRACKS),
        "short_equalize": False,
        "spoiler": "identity",
        "body_picks": {},
    }
    if era == ERA_1970S:
        book["homologation"] = 500
        book["wheelbase"] = 115
        book["chrysler"] = True
        book["aero_specials"] = SPECIALS_BANNED
    elif era == ERA_1980S:
        book["homologation"] = "per-dealer"
        book["wheelbase"] = 110
        book["chrysler"] = True
        book["aero_specials"] = SPECIALS_BANNED
    elif era == ERA_PINNACLE:
        book["homologation"] = 200
        book["aerocoupes"] = True
        book["plates"] = True
        book["chrysler"] = False
    else:
        book["homologation"] = 200
        book["aerocoupes"] = True
        book["plates"] = True
        book["chrysler"] = True
        book["template"] = "identity"
    return book


def default_packages():
    """Return per-track-type kits the commissioner can later rewrite."""

    return {
        "Superspeedway": {
            "plates": "era",
            "spoiler": "stock",
            "radiator": "stock",
        },
        "Intermediate": {
            "spoiler": "identity",
            "air_dam": "stock",
        },
        "Short Track": {
            "aero": "mechanical",
            "equalize": False,
        },
        "Road Course": {
            "downforce": "stock",
            "brakes": "stock",
        },
        "venues": {},
    }


def ensure_aero_book(league, era_book=None):
    """Fill missing Aero Wars slots without wiping a custom book."""

    era = era_book or _era()
    defaults = default_aero_book(era)
    current = league.get("aero_book") if league is not None else None
    if not isinstance(current, dict) or not current:
        if league is not None:
            league["aero_book"] = dict(defaults)
        current = dict(defaults)
    else:
        for key, value in defaults.items():
            if key not in current:
                current[key] = value
        if league is not None:
            league["aero_book"] = current
    packages = league.get("track_packages") if league is not None else None
    if not isinstance(packages, dict) or not packages:
        packages = default_packages()
        if league is not None:
            league["track_packages"] = packages
    else:
        stock = default_packages()
        for key, value in stock.items():
            if key not in packages:
                packages[key] = value
        if league is not None:
            league["track_packages"] = packages
    bind_live(current, packages)
    return current


def bind_live(book, packages=None):
    """Point race-pace helpers at the live winter book."""

    _LIVE["book"] = dict(book or {})
    _LIVE["packages"] = dict(packages or default_packages())


def live_book():
    """Return the bound winter book, or the era default."""

    book = _LIVE.get("book")
    if isinstance(book, dict) and book:
        return book
    return default_aero_book()


def live_packages():
    packages = _LIVE.get("packages")
    if isinstance(packages, dict) and packages:
        return packages
    return default_packages()


def _truthy(value):
    return str(value).lower() in ("1", "true", "on", "yes")


def apply_aero_rule(league, key, value):
    """Rewrite one winter-book or package slot. Day 114 desk writer."""

    book = ensure_aero_book(league)
    packages = None
    if league is not None:
        packages = league.get("track_packages")
    if not isinstance(packages, dict) or not packages:
        packages = default_packages()
        if league is not None:
            league["track_packages"] = packages
    key = str(key or "").strip()
    if key == "aero_specials":
        if value in (SPECIALS_BANNED, SPECIALS_LEGAL, SPECIALS_HOMOLOGATE):
            book["aero_specials"] = value
            if value == SPECIALS_LEGAL:
                book["aerocoupes"] = True
    elif key == "aerocoupes":
        book["aerocoupes"] = _truthy(value)
    elif key == "template":
        if value in ("identity", "spec"):
            book["template"] = value
    elif key == "plates":
        book["plates"] = _truthy(value)
    elif key == "chrysler":
        book["chrysler"] = _truthy(value)
    elif key == "wheelbase":
        try:
            book["wheelbase"] = int(value)
        except (TypeError, ValueError):
            pass
    elif key == "homologation":
        book["homologation"] = value
    elif key in ("short_equalize", "st_equalize"):
        on = _truthy(value)
        book["short_equalize"] = on
        kit = dict(packages.get("Short Track") or {})
        kit["equalize"] = on
        packages["Short Track"] = kit
    elif key == "spoiler":
        if value in ("identity", "flatten", "stock"):
            book["spoiler"] = value
    elif key in ("ss_plates", "package_ss_plates"):
        token = str(value).lower()
        if token in ("on", "off", "era"):
            kit = dict(packages.get("Superspeedway") or {})
            kit["plates"] = token
            packages["Superspeedway"] = kit
    elif key == "int_spoiler":
        if value in ("identity", "flatten", "stock"):
            kit = dict(packages.get("Intermediate") or {})
            kit["spoiler"] = value
            packages["Intermediate"] = kit
            book["spoiler"] = value
    elif key == "plate_track":
        tracks = list(book.get("plate_tracks") or [])
        name = str(value or "")
        if name and name not in tracks:
            tracks.append(name)
            book["plate_tracks"] = tracks
    elif key == "body_pick":
        maker, body_id = _parse_body_pick(value)
        if maker and body_id:
            picks = dict(book.get("body_picks") or {})
            entry = body_by_id(body_id) or body_by_name(maker, body_id)
            if (
                entry is not None
                and entry.get("maker") == maker
                and _body_legal(entry, book)
            ):
                picks[maker] = entry["id"]
                book["body_picks"] = picks
    if league is not None:
        league["aero_book"] = book
        league["track_packages"] = packages
    bind_live(book, packages)
    return book


def _map(short_track, intermediate, superspeedway, road_course):
    return {
        "short_track": _bound(short_track),
        "intermediate": _bound(intermediate),
        "superspeedway": _bound(superspeedway),
        "road_course": _bound(road_course),
    }


def _parse_body_pick(value):
    text = str(value or "").strip()
    if ":" not in text:
        return "", ""
    maker, body_id = text.split(":", 1)
    return maker.strip(), body_id.strip()


def body_catalog():
    """Return every homologated coupe the commissioner can field."""

    return [
        {
            "id": "torino",
            "maker": "Apex",
            "name": "Torino",
            "family": FAMILY_FORD,
            "map": _map(46, 56, 70, 48),
            "needs": None,
        },
        {
            "id": "thunderbird",
            "maker": "Apex",
            "name": "Thunderbird",
            "family": FAMILY_FORD,
            "map": _map(42, 60, 74, 52),
            "needs": None,
        },
        {
            "id": "chevelle",
            "maker": "Vanguard",
            "name": "Chevelle",
            "family": FAMILY_GM,
            "map": _map(66, 54, 46, 50),
            "needs": None,
        },
        {
            "id": "monte_carlo",
            "maker": "Vanguard",
            "name": "Monte Carlo",
            "family": FAMILY_GM,
            "map": _map(64, 54, 44, 50),
            "needs": None,
        },
        {
            "id": "monte_carlo_aerocoupe",
            "maker": "Vanguard",
            "name": "Monte Carlo Aerocoupe",
            "family": FAMILY_GM,
            "map": _map(56, 56, 66, 48),
            "needs": "aerocoupes",
        },
        {
            "id": "grand_prix",
            "maker": "Falcon",
            "name": "Grand Prix",
            "family": FAMILY_GM,
            "map": _map(58, 56, 52, 54),
            "needs": None,
        },
        {
            "id": "grand_prix_22",
            "maker": "Falcon",
            "name": "Grand Prix 2+2",
            "family": FAMILY_GM,
            "map": _map(54, 56, 64, 50),
            "needs": "aerocoupes",
        },
        {
            "id": "charger",
            "maker": "Valiant",
            "name": "Charger",
            "family": FAMILY_CHRYSLER,
            "map": _map(50, 52, 54, 46),
            "needs": None,
        },
        {
            "id": "superbird",
            "maker": "Valiant",
            "name": "Superbird",
            "family": FAMILY_CHRYSLER,
            "map": _map(38, 50, 88, 36),
            "needs": "specials",
        },
        {
            "id": "mirada",
            "maker": "Valiant",
            "name": "Mirada",
            "family": FAMILY_CHRYSLER,
            "map": _map(52, 50, 48, 48),
            "needs": None,
        },
        {
            "id": "magnum",
            "maker": "Valiant",
            "name": "Magnum",
            "family": FAMILY_CHRYSLER,
            "map": _map(50, 52, 56, 48),
            "needs": None,
        },
        {
            "id": "generic_coupe",
            "maker": "Independent",
            "name": "Generic coupe",
            "family": FAMILY_INDEPENDENT,
            "map": _map(48, 48, 48, 48),
            "needs": None,
        },
    ]


def body_by_id(body_id):
    token = str(body_id or "").strip()
    for entry in body_catalog():
        if entry["id"] == token:
            return entry
    return None


def body_by_name(maker, name):
    maker = str(maker or "")
    name = str(name or "").strip()
    slug = name.lower().replace(" ", "_").replace("+", "")
    for entry in body_catalog():
        if entry["maker"] != maker:
            continue
        if entry["name"] == name or entry["id"] == slug:
            return entry
    return None


def _body_legal(entry, book):
    if entry is None:
        return False
    needs = entry.get("needs")
    specials = (book or {}).get("aero_specials") or SPECIALS_BANNED
    winged = specials in (SPECIALS_LEGAL, SPECIALS_HOMOLOGATE)
    aero = bool((book or {}).get("aerocoupes")) or winged
    if needs == "specials":
        return winged
    if needs == "aerocoupes":
        return aero
    return True


def default_body_id(maker_name, era_book=None, book=None):
    """Return the inherited coupe id for this factory and era."""

    era = era_book or _era()
    book = book or live_book()
    maker = str(maker_name or "Independent")
    specials = book.get("aero_specials") or SPECIALS_BANNED
    winged = specials in (SPECIALS_LEGAL, SPECIALS_HOMOLOGATE)
    aero = bool(book.get("aerocoupes")) or winged
    if maker == "Apex":
        return "torino" if era == ERA_1970S else "thunderbird"
    if maker == "Vanguard":
        if era == ERA_1970S:
            return "chevelle"
        return "monte_carlo_aerocoupe" if aero else "monte_carlo"
    if maker == "Falcon":
        if era == ERA_1970S:
            return "grand_prix"
        return "grand_prix_22" if aero else "grand_prix"
    if maker == "Valiant":
        if winged:
            return "superbird"
        if era == ERA_1970S:
            return "charger"
        if era == ERA_1980S:
            return "mirada"
        return "magnum"
    return "generic_coupe"


def legal_bodies(maker_name, era_book=None, book=None):
    """Return legal coupe cards this factory may field this year."""

    maker = str(maker_name or "Independent")
    book = book or live_book()
    rows = []
    for entry in body_catalog():
        if entry["maker"] != maker:
            continue
        if not _body_legal(entry, book):
            continue
        rows.append(dict(entry))
    return rows


def _spec_from_entry(entry):
    return {
        "id": entry.get("id"),
        "name": entry.get("name"),
        "family": entry.get("family"),
        "map": dict(entry.get("map") or _map(50, 50, 50, 50)),
        "portrait": entry.get("id"),
    }


def coupe_spec(maker_name, era_book=None, book=None):
    """Return the named homologated body this factory fields right now."""

    era = era_book or _era()
    book = book or live_book()
    maker = str(maker_name or "Independent")
    picks = book.get("body_picks") if isinstance(book.get("body_picks"), dict) else {}
    picked = picks.get(maker)
    entry = body_by_id(picked) or body_by_name(maker, picked)
    if (
        entry is not None
        and entry.get("maker") == maker
        and _body_legal(entry, book)
    ):
        return _spec_from_entry(entry)
    fallback = body_by_id(default_body_id(maker, era, book))
    if fallback is not None:
        return _spec_from_entry(fallback)
    return {
        "id": "generic_coupe",
        "name": "Generic coupe",
        "family": FAMILY_INDEPENDENT,
        "map": _map(48, 48, 48, 48),
        "portrait": "generic_coupe",
    }


def _flatten(raw_map, pull, toward=50):
    out = {}
    for key, value in (raw_map or {}).items():
        out[key] = _bound(int(round(toward + (int(value) - toward) * pull)))
    return out


def is_plate_track(track, book=None):
    """Return whether this venue runs a restrictor this week."""

    book = book or live_book()
    if track is None:
        return False
    if isinstance(track, dict):
        name = track.get("name")
        track_type = track.get("type")
    else:
        name = getattr(track, "name", None)
        track_type = getattr(track, "type", None)
    packages = live_packages()
    venues = packages.get("venues") or {}
    override = venues.get(name) or {}
    if override.get("plates") is True:
        return True
    if override.get("plates") is False:
        return False
    ss = packages.get("Superspeedway") or {}
    if ss.get("plates") == "off":
        return False
    if ss.get("plates") == "on" and track_type == "Superspeedway":
        return True
    if not book.get("plates"):
        return False
    plates = list(book.get("plate_tracks") or PLATE_TRACKS)
    if name in plates:
        return True
    return False


def body_map_for(maker_name, track=None, era_book=None, book=None):
    """Return the four-number map after template, plates, and kits."""

    book = book or live_book()
    spec = coupe_spec(maker_name, era_book, book)
    raw = dict(spec.get("map") or _map(50, 50, 50, 50))
    if book.get("template") == "spec":
        raw = _flatten(raw, 0.30, 50)
    track_type = None
    if isinstance(track, dict):
        track_type = track.get("type")
    elif track is not None:
        track_type = getattr(track, "type", None)
    packages = live_packages()
    if track_type == "Short Track":
        kit = packages.get("Short Track") or {}
        if book.get("short_equalize") or kit.get("equalize"):
            raw = _flatten(raw, 0.20, 50)
    if track_type == "Intermediate":
        spoiler = book.get("spoiler") or (packages.get("Intermediate") or {}).get("spoiler")
        if spoiler == "flatten":
            raw = _flatten(raw, 0.45, 52)
    if track is not None and is_plate_track(track, book):
        raw["superspeedway"] = _bound(
            int(round(58 + (raw.get("superspeedway", 50) - 58) * 0.35))
        )
    return raw


def body_rating(maker_name, track, era_book=None, book=None):
    """Return this factory's map number at this venue."""

    track_type = getattr(track, "type", None) if track is not None else None
    if track_type is None and isinstance(track, dict):
        track_type = track.get("type")
    key = TYPE_KEYS.get(track_type, "intermediate")
    return int(body_map_for(maker_name, track, era_book, book).get(key) or 50)


def skill_pace_tick(driver, track):
    """Return the driver-skill half of race pace at this venue."""

    if driver is None or track is None:
        return 0
    track_type = getattr(track, "type", "Intermediate")
    skill = int(driver.track_skill_for(track_type) or 50)
    weight = float(SKILL_WEIGHT.get(track_type, 0.50))
    return int(round((skill // 4) * (weight / 0.50)))


def body_pace_tick(team, track, era_book=None, book=None):
    """Return the body-aero half of race pace at this venue."""

    if team is None or track is None:
        return 0
    maker = getattr(team, "manufacturer", None) or "Independent"
    rating = body_rating(maker, track, era_book, book)
    track_type = getattr(track, "type", "Intermediate")
    weight = float(AERO_WEIGHT.get(track_type, 0.50))
    return int(round((rating - 50) * weight / 1.5))


def pack_heat(track, team=None):
    """Return extra wreck heat from plates or a loose superspeedway body."""

    extra = 0
    if track is None:
        return extra
    track_type = getattr(track, "type", "")
    if is_plate_track(track):
        extra += 4
    if team is not None and track_type == "Superspeedway":
        rating = body_rating(getattr(team, "manufacturer", None), track)
        if rating < 46:
            extra += 3
    return extra


def mechanical_heat(team, track):
    """Return extra failure chance for a brick cooking behind a spoiler kit."""

    if team is None or track is None:
        return 0
    track_type = getattr(track, "type", "")
    rating = body_rating(getattr(team, "manufacturer", None), track)
    extra = 0
    if track_type == "Superspeedway" and rating >= 64:
        extra += 1
    if track_type == "Superspeedway" and is_plate_track(track) and rating >= 60:
        extra += 1
    if track_type == "Road Course" and rating <= 42:
        extra += 2
    return extra


def office_bodies_book(makers=None, era_book=None, book=None):
    """Return factory coupe cards for the office Rulebook and Teams."""

    era = era_book or _era()
    book = book or live_book()
    rows = []
    seen = []
    for maker in makers or []:
        name = maker.name if hasattr(maker, "name") else str(maker)
        if name in seen:
            continue
        seen.append(name)
        spec = coupe_spec(name, era, book)
        body_map = body_map_for(name, None, era, book)
        choices = []
        for entry in legal_bodies(name, era, book):
            choices.append(
                {
                    "id": entry.get("id"),
                    "name": entry.get("name"),
                    "portrait": entry.get("id"),
                    "selected": entry.get("id") == spec.get("id"),
                    "short_track": int((entry.get("map") or {}).get("short_track") or 50),
                    "intermediate": int((entry.get("map") or {}).get("intermediate") or 50),
                    "superspeedway": int((entry.get("map") or {}).get("superspeedway") or 50),
                    "road_course": int((entry.get("map") or {}).get("road_course") or 50),
                }
            )
        rows.append(
            {
                "maker": name,
                "family": spec.get("family"),
                "coupe": spec.get("name"),
                "portrait": spec.get("portrait") or spec.get("id"),
                "choices": choices,
                "short_track": int(body_map.get("short_track") or 50),
                "intermediate": int(body_map.get("intermediate") or 50),
                "superspeedway": int(body_map.get("superspeedway") or 50),
                "road_course": int(body_map.get("road_course") or 50),
            }
        )
    return rows


def package_lines(packages=None, book=None):
    """Return per-track kit lines for the desk."""

    packages = packages or live_packages()
    book = book or live_book()
    ss = packages.get("Superspeedway") or {}
    inter = packages.get("Intermediate") or {}
    short = packages.get("Short Track") or {}
    road = packages.get("Road Course") or {}
    plates = ss.get("plates") or "era"
    if plates == "on":
        plate_line = "plates on every superspeedway"
    elif plates == "off":
        plate_line = "no plates"
    else:
        plate_line = "plates follow the winter book"
    spoiler = inter.get("spoiler") or book.get("spoiler") or "identity"
    equalized = bool(book.get("short_equalize") or short.get("equalize"))
    return [
        "Superspeedway: %s" % plate_line,
        "Intermediate: spoiler %s" % spoiler,
        "Short Track: %s" % ("aero equalized" if equalized else "mechanical"),
        "Road Course: downforce %s" % (road.get("downforce") or "stock"),
    ]


def office_aero_actions(book=None, packages=None):
    """Return Rulebook rewrite buttons for the winter book and kits."""

    book = book or live_book()
    packages = packages or live_packages()
    specials = book.get("aero_specials") or SPECIALS_BANNED
    actions = []
    if specials != SPECIALS_LEGAL:
        actions.append(
            {
                "key": "aero_specials",
                "value": SPECIALS_LEGAL,
                "label": "Legalize aero specials",
            }
        )
    else:
        actions.append(
            {
                "key": "aero_specials",
                "value": SPECIALS_BANNED,
                "label": "Ban aero specials",
            }
        )
    if book.get("template") != "spec":
        actions.append(
            {
                "key": "template",
                "value": "spec",
                "label": "Adopt a spec silhouette",
            }
        )
    else:
        actions.append(
            {
                "key": "template",
                "value": "identity",
                "label": "Restore manufacturer identity",
            }
        )
    if book.get("plates"):
        actions.append(
            {
                "key": "plates",
                "value": "off",
                "label": "Pull restrictor plates",
            }
        )
    else:
        actions.append(
            {
                "key": "plates",
                "value": "on",
                "label": "Plate the two biggest ovals",
            }
        )
    if book.get("chrysler"):
        actions.append(
            {
                "key": "chrysler",
                "value": "off",
                "label": "Close the book to Chrysler",
            }
        )
    else:
        actions.append(
            {
                "key": "chrysler",
                "value": "on",
                "label": "Invite Chrysler",
            }
        )
    if book.get("short_equalize"):
        actions.append(
            {
                "key": "short_equalize",
                "value": "off",
                "label": "Let short tracks stay mechanical",
            }
        )
    else:
        actions.append(
            {
                "key": "short_equalize",
                "value": "on",
                "label": "Equalize short-track aero",
            }
        )
    ss = packages.get("Superspeedway") or {}
    if ss.get("plates") != "off":
        actions.append(
            {
                "key": "ss_plates",
                "value": "off",
                "label": "Superspeedway kit: no plates",
            }
        )
    else:
        actions.append(
            {
                "key": "ss_plates",
                "value": "era",
                "label": "Superspeedway kit: follow the era book",
            }
        )
    inter = packages.get("Intermediate") or {}
    spoiler = inter.get("spoiler") or book.get("spoiler") or "identity"
    if spoiler != "flatten":
        actions.append(
            {
                "key": "int_spoiler",
                "value": "flatten",
                "label": "Intermediate kit: flatten spoilers",
            }
        )
    else:
        actions.append(
            {
                "key": "int_spoiler",
                "value": "identity",
                "label": "Intermediate kit: restore identity",
            }
        )
    return actions


def book_lines(book=None):
    """Return short winter-book lines for the desk."""

    book = book or live_book()
    specials = book.get("aero_specials") or SPECIALS_BANNED
    template = book.get("template") or "identity"
    homologation = book.get("homologation")
    if homologation == "per-dealer":
        homo_line = "Per-dealership homologation"
    else:
        homo_line = "%s street units" % homologation
    plates = "Plates on the two biggest ovals" if book.get("plates") else "No restrictor plates"
    chrysler = "Chrysler invited" if book.get("chrysler") else "Chrysler out of the book"
    aero = "Aerocoupes legal" if book.get("aerocoupes") else "Aerocoupes parked"
    return [
        "Two-door coupes required" if book.get("coupe_only") else "Open body class",
        "%s-inch wheelbase" % book.get("wheelbase"),
        homo_line,
        "Aero specials %s" % specials,
        aero,
        "Template: %s" % ("manufacturer identity" if template == "identity" else "spec silhouette"),
        plates,
        chrysler,
    ]


def one_make_runaway(race_history, teams_by_name=None, window=3):
    """Return a family name when the last few winners wear the same badge."""

    if not race_history or window < 2:
        return None
    families = []
    for record in list(race_history)[-window:]:
        winner = None
        results = record.get("results") or record.get("feature") or []
        if results:
            first = results[0] if isinstance(results[0], dict) else None
            if first:
                winner = first.get("team") or first.get("team_name")
        if not winner:
            winner = record.get("winner_team") or record.get("team")
        maker = None
        if teams_by_name and winner:
            team = teams_by_name.get(winner)
            if team is not None:
                maker = getattr(team, "manufacturer", None)
        if not maker:
            maker = record.get("manufacturer")
        family = family_for(maker)
        if family == FAMILY_INDEPENDENT:
            return None
        families.append(family)
    if len(families) < window:
        return None
    if all(item == families[0] for item in families):
        return families[0]
    return None
