"""Aero Wars: homologated coupes and manufacturer track maps.

Day 113 replaces the single `aero_bias` tick that only fired on road
courses and superspeedways. Each factory fields a named two-door coupe
with a four-number map (short track, intermediate, superspeedway, road).
Race pace mixes that map with driver track skill. Day 114 lets the
commissioner rewrite the winter book and the per-track kit. Day 116
lets a named venue break from its type kit — plate this oval, not
every superspeedway. Day 117 puts homologation count and wheelbase
class on the Rulebook desk as first-class winter-book levers. Day 118
makes homologate-to-run a real aero-specials choice. Days 119–122
give that book stakeholders: Detroit mail, kit lobby, victory-lane
hearings, and Win-on-Sunday on the desk.
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

HOMOLOGATION_200 = 200
HOMOLOGATION_500 = 500
HOMOLOGATION_PER_DEALER = "per-dealer"

WHEELBASE_110 = 110
WHEELBASE_115 = 115
WHEELBASE_MIXED = "mixed"

HOMOLOGATION_OPTIONS = (
    {
        "value": HOMOLOGATION_200,
        "label": "200 street units",
        "blurb": "A short street run. Detroit can homologate wilder coupes.",
    },
    {
        "value": HOMOLOGATION_500,
        "label": "500 street units",
        "blurb": "The late-sixties count. A real production line, not a handful.",
    },
    {
        "value": HOMOLOGATION_PER_DEALER,
        "label": "Per-dealership count",
        "blurb": "Each dealer takes one. Superbird-era paperwork.",
    },
)

WHEELBASE_OPTIONS = (
    {
        "value": WHEELBASE_110,
        "label": "110-inch downsized",
        "blurb": "The 1981 cut. Aero owns the big tracks.",
    },
    {
        "value": WHEELBASE_115,
        "label": "115-inch intermediates",
        "blurb": "Grand National wheelbase. Mechanical grip, less aero war.",
    },
    {
        "value": WHEELBASE_MIXED,
        "label": "Mixed class",
        "blurb": "Shops may run 110 or 115. Packing gets messy.",
    },
)

SPECIALS_OPTIONS = (
    {
        "value": SPECIALS_BANNED,
        "label": "Aero specials banned",
        "blurb": "No Superbirds, no long-nose warriors. The 1971 kneecap holds.",
    },
    {
        "value": SPECIALS_HOMOLOGATE,
        "label": "Homologate-to-run",
        "blurb": "Specials are legal only if Detroit sells the street count.",
    },
    {
        "value": SPECIALS_LEGAL,
        "label": "Aero specials legal",
        "blurb": "Wings and long noses run if a factory will badge them.",
    },
)

_LIVE = {"book": None, "packages": None}


def _era():
    key = str((current_settings or {}).get("era_book") or ERA_PINNACLE)
    if key in (ERA_1970S, ERA_1980S, ERA_PINNACLE, ERA_BEYOND):
        return key
    return ERA_PINNACLE


def _bound(value, lo=0, hi=100):
    return max(lo, min(hi, int(value)))


def normalize_homologation(value):
    """Return 200, 500, or per-dealer, else None."""

    if value in (HOMOLOGATION_200, HOMOLOGATION_500):
        return int(value)
    token = str(value or "").strip().lower().replace("_", "-")
    token = token.replace(" ", "-")
    if token in ("200", "200-units", "200-street-units"):
        return HOMOLOGATION_200
    if token in ("500", "500-units", "500-street-units"):
        return HOMOLOGATION_500
    if token in (
        "per-dealer",
        "per-dealership",
        "dealer",
        "dealership",
        "perdealer",
    ):
        return HOMOLOGATION_PER_DEALER
    try:
        count = int(value)
    except (TypeError, ValueError):
        return None
    if count in (HOMOLOGATION_200, HOMOLOGATION_500):
        return count
    return None


def normalize_wheelbase(value):
    """Return 110, 115, or mixed, else None."""

    if value in (WHEELBASE_110, WHEELBASE_115):
        return int(value)
    token = str(value or "").strip().lower().replace("_", "-")
    token = token.replace(" ", "-")
    if token in ("110", "110-inch", "downsized", "downsize"):
        return WHEELBASE_110
    if token in ("115", "115-inch", "intermediate", "intermediates"):
        return WHEELBASE_115
    if token in ("mixed", "mix", "both"):
        return WHEELBASE_MIXED
    try:
        inches = int(float(token))
    except (TypeError, ValueError):
        return None
    if inches in (WHEELBASE_110, WHEELBASE_115):
        return inches
    return None


def homologation_label(value):
    """Return the winter-book line for a homologation count."""

    token = normalize_homologation(value)
    if token == HOMOLOGATION_PER_DEALER:
        return "Per-dealership homologation"
    if token == HOMOLOGATION_500:
        return "500 street units"
    return "200 street units"


def wheelbase_label(value):
    """Return the winter-book line for a wheelbase class."""

    token = normalize_wheelbase(value)
    if token == WHEELBASE_MIXED:
        return "Mixed wheelbase class (110 and 115)"
    if token == WHEELBASE_115:
        return "115-inch intermediates"
    return "110-inch downsized"


def normalize_specials(value):
    """Return banned, legal, or homologate, else None."""

    if value in (SPECIALS_BANNED, SPECIALS_LEGAL, SPECIALS_HOMOLOGATE):
        return value
    token = str(value or "").strip().lower().replace("_", "-")
    token = token.replace(" ", "-")
    if token in ("legal", "legalize", "allowed", "on"):
        return SPECIALS_LEGAL
    if token in (
        "homologate",
        "homologate-to-run",
        "homologation",
        "to-run",
    ):
        return SPECIALS_HOMOLOGATE
    if token in ("banned", "ban", "off", "illegal"):
        return SPECIALS_BANNED
    return None


def specials_label(value):
    """Return the winter-book line for aero specials."""

    token = normalize_specials(value) or SPECIALS_BANNED
    if token == SPECIALS_LEGAL:
        return "Aero specials legal"
    if token == SPECIALS_HOMOLOGATE:
        return "Homologate-to-run"
    return "Aero specials banned"


def homologation_operating_cost(book=None):
    """Return extra per-shop cost from the live homologation count."""

    token = normalize_homologation((book or live_book()).get("homologation"))
    if token == HOMOLOGATION_500:
        return 25_000
    if token == HOMOLOGATION_PER_DEALER:
        return 75_000
    return 0


def specials_operating_cost(book=None):
    """Return extra per-shop cost when specials must be homologated to run."""

    token = normalize_specials((book or live_book()).get("aero_specials"))
    if token == SPECIALS_HOMOLOGATE:
        return 40_000
    return 0


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
    """Fill missing Aero Wars slots without wiping a custom book.

    Present keys stay as the commissioner wrote them. New career must
    clear `aero_book` first so an era rewind does not keep Superbirds
    or pulled plates from the previous desk.
    """

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
        homo = normalize_homologation(current.get("homologation"))
        current["homologation"] = (
            homo if homo is not None else defaults["homologation"]
        )
        wheel = normalize_wheelbase(current.get("wheelbase"))
        current["wheelbase"] = (
            wheel if wheel is not None else defaults["wheelbase"]
        )
        specials = normalize_specials(current.get("aero_specials"))
        current["aero_specials"] = (
            specials if specials is not None else defaults["aero_specials"]
        )
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


def package_show_modifiers(book=None):
    """Return how the live winter book moves TV, gate, and wreck risk."""

    book = book if isinstance(book, dict) and book else live_book() or {}
    specials = normalize_specials(book.get("aero_specials"))
    plates = bool(book.get("plates"))
    tv = 0
    gate = 0
    wrecks = 0
    notes = []
    if specials == SPECIALS_LEGAL:
        tv += 6
        gate += 4
        wrecks += 3
        notes.append("Legal aero specials sell the show and raise wreck risk.")
    elif specials == SPECIALS_HOMOLOGATE:
        tv += 3
        gate += 2
        wrecks += 1
        notes.append(
            "Homologate-to-run specials add a little product without opening the barn door."
        )
    else:
        notes.append("Banned specials keep the field even and the houses quieter.")
    if plates:
        tv -= 2
        wrecks -= 2
        notes.append("Restrictor plates pack the superspeedways and cap the show.")
    else:
        tv += 4
        gate += 2
        wrecks += 2
        notes.append("Open superspeedways lift ratings and the wreck book.")
    return {
        "tv": tv,
        "gate": gate,
        "wrecks": wrecks,
        "notes": notes,
        "specials": specials or "banned",
        "plates": plates,
    }


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
        specials = normalize_specials(value)
        if specials is not None:
            book["aero_specials"] = specials
            if specials in (SPECIALS_LEGAL, SPECIALS_HOMOLOGATE):
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
        wheel = normalize_wheelbase(value)
        if wheel is not None:
            book["wheelbase"] = wheel
    elif key == "homologation":
        homo = normalize_homologation(value)
        if homo is not None:
            book["homologation"] = homo
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
    elif key in ("venue_plates", "venue_kit"):
        name, token = _parse_venue_token(value)
        set_venue_plates(packages, name, token)
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


def _parse_venue_token(value):
    """Split 'Atlantic Speedway:on' into (name, plates token)."""

    text = str(value or "").strip()
    if ":" not in text:
        return text, ""
    name, token = text.rsplit(":", 1)
    return name.strip(), token.strip().lower()


def _plates_token(value):
    """Normalize a plates override to on, off, or era (inherit)."""

    token = str(value).strip().lower()
    if token in ("on", "true", "1", "yes", "plate", "plated"):
        return "on"
    if token in ("off", "false", "0", "no", "open"):
        return "off"
    if token in ("era", "follow", "inherit", "type", "kit", ""):
        return "era"
    return ""


def venue_plate_mode(name, packages=None):
    """Return on, off, or era for this named venue's kit override."""

    packages = packages or live_packages()
    venues = packages.get("venues") if isinstance(packages, dict) else None
    if not isinstance(venues, dict):
        return "era"
    kit = venues.get(name) or {}
    plates = kit.get("plates") if isinstance(kit, dict) else None
    if plates is True or plates == "on":
        return "on"
    if plates is False or plates == "off":
        return "off"
    return "era"


def set_venue_plates(packages, name, token):
    """Write or clear a named-venue plates override. Returns the venues map."""

    packages = packages if isinstance(packages, dict) else default_packages()
    venues = dict(packages.get("venues") or {})
    name = str(name or "").strip()
    mode = _plates_token(token)
    if not name or mode == "":
        packages["venues"] = venues
        return venues
    if mode == "era":
        venues.pop(name, None)
    else:
        kit = dict(venues.get(name) or {})
        kit["plates"] = mode == "on"
        venues[name] = kit
    packages["venues"] = venues
    return venues


def _body(body_id, maker, name, year, family, body_map, needs=None, years=None, street=None):
    """Build one homologated coupe card with its street-release year."""

    years = years or (year, year)
    return {
        "id": body_id,
        "maker": maker,
        "name": name,
        "year": int(year),
        "years": "%s–%s" % (years[0], years[1]),
        "street": street or name,
        "family": family,
        "map": body_map,
        "needs": needs,
        "label": "%s %s" % (year, name),
        "portrait": body_id,
    }


def body_catalog():
    """Return every homologated coupe the commissioner can field.

    Each card is a street-release year. The 16-bit portrait must match
    that year's silhouette — 1980 Monte Carlo is the box G-body with the
    opera window, not the 1983 downsized SS or the 1986 Aerocoupe.
    """

    return [
        _body("torino", "Apex", "Torino", 1971, FAMILY_FORD, _map(46, 56, 70, 48), years=(1970, 1976)),
        _body("thunderbird", "Apex", "Thunderbird", 1983, FAMILY_FORD, _map(42, 60, 74, 52), years=(1983, 1988)),
        _body("thunderbird_aero", "Apex", "Thunderbird", 1989, FAMILY_FORD, _map(40, 62, 78, 54), years=(1989, 1997)),
        _body("chevelle", "Vanguard", "Chevelle", 1970, FAMILY_GM, _map(66, 54, 46, 50), years=(1970, 1972)),
        _body("monte_carlo", "Vanguard", "Monte Carlo", 1980, FAMILY_GM, _map(64, 54, 44, 50), years=(1978, 1980)),
        _body("monte_carlo_gbody", "Vanguard", "Monte Carlo SS", 1983, FAMILY_GM, _map(60, 56, 50, 50), years=(1981, 1985)),
        _body(
            "monte_carlo_aerocoupe",
            "Vanguard",
            "Monte Carlo Aerocoupe",
            1986,
            FAMILY_GM,
            _map(56, 56, 66, 48),
            needs="aerocoupes",
            years=(1986, 1988),
        ),
        _body("lumina", "Vanguard", "Lumina", 1989, FAMILY_GM, _map(52, 60, 70, 52), years=(1989, 1994)),
        _body("grand_prix", "Falcon", "Grand Prix", 1981, FAMILY_GM, _map(58, 56, 52, 54), years=(1981, 1987)),
        _body(
            "grand_prix_22",
            "Falcon",
            "Grand Prix 2+2",
            1986,
            FAMILY_GM,
            _map(54, 56, 64, 50),
            needs="aerocoupes",
            years=(1986, 1987),
        ),
        _body("charger", "Valiant", "Charger", 1971, FAMILY_CHRYSLER, _map(50, 52, 54, 46), years=(1971, 1974)),
        _body(
            "superbird",
            "Valiant",
            "Superbird",
            1970,
            FAMILY_CHRYSLER,
            _map(38, 50, 88, 36),
            needs="specials",
            years=(1970, 1970),
        ),
        _body("magnum", "Valiant", "Magnum", 1978, FAMILY_CHRYSLER, _map(50, 52, 56, 48), years=(1978, 1979)),
        _body("mirada", "Valiant", "Mirada", 1980, FAMILY_CHRYSLER, _map(52, 50, 48, 48), years=(1980, 1983)),
        _body(
            "generic_coupe",
            "Independent",
            "Generic coupe",
            1984,
            FAMILY_INDEPENDENT,
            _map(48, 48, 48, 48),
            years=(1981, 1988),
        ),
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
    specials = normalize_specials((book or {}).get("aero_specials")) or SPECIALS_BANNED
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
    specials = normalize_specials(book.get("aero_specials")) or SPECIALS_BANNED
    winged = specials in (SPECIALS_LEGAL, SPECIALS_HOMOLOGATE)
    aero = bool(book.get("aerocoupes")) or winged
    if maker == "Apex":
        if era == ERA_1970S:
            return "torino"
        if era == ERA_1980S:
            return "thunderbird"
        return "thunderbird_aero"
    if maker == "Vanguard":
        if era == ERA_1970S:
            return "chevelle"
        if era == ERA_1980S:
            return "monte_carlo_aerocoupe" if aero else "monte_carlo_gbody"
        return "monte_carlo_aerocoupe" if aero else "lumina"
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
    year = int(entry.get("year") or 0)
    name = str(entry.get("name") or "")
    label = str(entry.get("label") or (("%s %s" % (year, name)).strip() if year else name))
    return {
        "id": entry.get("id"),
        "name": name,
        "label": label,
        "year": year,
        "years": entry.get("years") or "",
        "street": entry.get("street") or name,
        "family": entry.get("family"),
        "map": dict(entry.get("map") or _map(50, 50, 50, 50)),
        "portrait": entry.get("portrait") or entry.get("id"),
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
        "label": "1984 Generic coupe",
        "year": 1984,
        "years": "1981–1988",
        "street": "Generic coupe",
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
    mode = venue_plate_mode(name, packages)
    if mode == "on":
        return True
    if mode == "off":
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
    homo = normalize_homologation(book.get("homologation"))
    if homo == HOMOLOGATION_500:
        raw = _flatten(raw, 0.88, 50)
    elif homo == HOMOLOGATION_PER_DEALER:
        raw = _flatten(raw, 0.72, 50)
    wheel = normalize_wheelbase(book.get("wheelbase"))
    if wheel == WHEELBASE_115:
        raw["short_track"] = _bound(int(raw.get("short_track", 50)) + 4)
        raw["road_course"] = _bound(int(raw.get("road_course", 50)) + 2)
        raw["superspeedway"] = _bound(
            int(round(54 + (int(raw.get("superspeedway", 50)) - 54) * 0.72))
        )
    elif wheel == WHEELBASE_MIXED:
        raw = _flatten(raw, 0.84, 50)
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
    if normalize_wheelbase(live_book().get("wheelbase")) == WHEELBASE_MIXED:
        if track_type in ("Superspeedway", "Intermediate"):
            extra += 2
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
                    "name": entry.get("label") or entry.get("name"),
                    "year": int(entry.get("year") or 0),
                    "years": entry.get("years") or "",
                    "portrait": entry.get("portrait") or entry.get("id"),
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
                "coupe": spec.get("label") or spec.get("name"),
                "year": int(spec.get("year") or 0),
                "years": spec.get("years") or "",
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
    lines = [
        "Superspeedway: %s" % plate_line,
        "Intermediate: spoiler %s" % spoiler,
        "Short Track: %s" % ("aero equalized" if equalized else "mechanical"),
        "Road Course: downforce %s" % (road.get("downforce") or "stock"),
    ]
    venues = packages.get("venues") or {}
    for venue_name in sorted(venues):
        kit = venues.get(venue_name) or {}
        plates_on = kit.get("plates")
        if plates_on is True or plates_on == "on":
            lines.append("%s: plates (named venue)" % venue_name)
        elif plates_on is False or plates_on == "off":
            lines.append("%s: open (named venue)" % venue_name)
    return lines


def office_aero_actions(book=None, packages=None):
    """Return Rulebook rewrite buttons for the winter book and kits."""

    book = book or live_book()
    packages = packages or live_packages()
    actions = []
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


def office_venue_kits(schedule=None, pool=None, book=None, packages=None):
    """Return superspeedway cards so one oval can break from the type kit."""

    book = book or live_book()
    packages = packages or live_packages()
    if pool is None:
        try:
            from data.season_data import create_track_pool

            pool = create_track_pool()
        except Exception:
            pool = []
    rows = []
    seen = set()
    calendar_names = set()
    for track in schedule or []:
        name = getattr(track, "name", None) or (
            track.get("name") if isinstance(track, dict) else None
        )
        if name:
            calendar_names.add(name)
    for source in (schedule, pool):
        for track in source or []:
            if isinstance(track, dict):
                name = track.get("name")
                track_type = track.get("type")
            else:
                name = getattr(track, "name", None)
                track_type = getattr(track, "type", None)
            if not name or name in seen:
                continue
            if track_type != "Superspeedway":
                continue
            seen.add(name)
            mode = venue_plate_mode(name, packages)
            plated = is_plate_track(track, book)
            if plated:
                status = "plates this week"
            else:
                status = "open this week"
            if mode == "on":
                override = "named venue: plates"
            elif mode == "off":
                override = "named venue: open"
            else:
                override = "follows the type kit"
            actions = []
            if mode != "on":
                actions.append(
                    {
                        "key": "venue_plates",
                        "value": "%s:on" % name,
                        "label": "Plate this oval",
                    }
                )
            if mode != "off":
                actions.append(
                    {
                        "key": "venue_plates",
                        "value": "%s:off" % name,
                        "label": "Run this oval open",
                    }
                )
            if mode != "era":
                actions.append(
                    {
                        "key": "venue_plates",
                        "value": "%s:era" % name,
                        "label": "Follow the type kit",
                    }
                )
            rows.append(
                {
                    "name": name,
                    "type": track_type,
                    "mode": mode,
                    "plated": plated,
                    "on_calendar": name in calendar_names,
                    "status": status,
                    "override": override,
                    "actions": actions,
                }
            )
    return rows


def office_homologation_desk(book=None):
    """Return the Rulebook homologation-count card."""

    book = book or live_book()
    current = normalize_homologation(book.get("homologation"))
    if current is None:
        current = HOMOLOGATION_200
    choices = []
    for option in HOMOLOGATION_OPTIONS:
        choices.append(
            {
                "key": "homologation",
                "value": str(option["value"]),
                "label": option["label"],
                "blurb": option["blurb"],
                "selected": current == option["value"],
            }
        )
    return {
        "value": current,
        "label": homologation_label(current),
        "blurb": (
            "Detroit must sell this many street coupes before the race body "
            "is legal."
        ),
        "choices": choices,
    }


def office_wheelbase_desk(book=None):
    """Return the Rulebook wheelbase-class card."""

    book = book or live_book()
    current = normalize_wheelbase(book.get("wheelbase"))
    if current is None:
        current = WHEELBASE_110
    choices = []
    for option in WHEELBASE_OPTIONS:
        choices.append(
            {
                "key": "wheelbase",
                "value": str(option["value"]),
                "label": option["label"],
                "blurb": option["blurb"],
                "selected": current == option["value"],
            }
        )
    return {
        "value": current,
        "label": wheelbase_label(current),
        "blurb": (
            "The Cup car's wheelbase. Downsizing in 1981 made aero the war."
        ),
        "choices": choices,
    }


def office_specials_desk(book=None):
    """Return the Rulebook aero-specials card, including homologate-to-run."""

    book = book or live_book()
    current = normalize_specials(book.get("aero_specials"))
    if current is None:
        current = SPECIALS_BANNED
    choices = []
    for option in SPECIALS_OPTIONS:
        choices.append(
            {
                "key": "aero_specials",
                "value": str(option["value"]),
                "label": option["label"],
                "blurb": option["blurb"],
                "selected": current == option["value"],
            }
        )
    return {
        "value": current,
        "label": specials_label(current),
        "blurb": (
            "Winged cars and long noses. Homologate-to-run lets Detroit "
            "field them only after the street count is sold."
        ),
        "choices": choices,
    }


def book_lines(book=None):
    """Return short winter-book lines for the desk."""

    book = book or live_book()
    template = book.get("template") or "identity"
    plates = "Plates on the two biggest ovals" if book.get("plates") else "No restrictor plates"
    chrysler = "Chrysler invited" if book.get("chrysler") else "Chrysler out of the book"
    aero = "Aerocoupes legal" if book.get("aerocoupes") else "Aerocoupes parked"
    return [
        "Two-door coupes required" if book.get("coupe_only") else "Open body class",
        wheelbase_label(book.get("wheelbase")),
        homologation_label(book.get("homologation")),
        specials_label(book.get("aero_specials")),
        aero,
        "Template: %s" % ("manufacturer identity" if template == "identity" else "spec silhouette"),
        plates,
        chrysler,
    ]


def _winner_family(record, teams_by_name=None):
    """Return the Detroit family that took victory lane in this race."""

    record = record or {}
    winner = None
    maker = None
    results = record.get("results") or record.get("feature") or []
    if results:
        first = results[0] if isinstance(results[0], dict) else None
        if first:
            winner = first.get("team") or first.get("team_name")
            maker = first.get("manufacturer")
    if not winner:
        winner = record.get("winner_team") or record.get("team")
    if teams_by_name and winner:
        team = teams_by_name.get(winner)
        if team is not None:
            maker = getattr(team, "manufacturer", None) or maker
    if not maker:
        maker = record.get("manufacturer")
    return family_for(maker)


def one_make_runaway(race_history, teams_by_name=None, window=3):
    """Return a family name when the last few winners wear the same badge."""

    if not race_history or window < 2:
        return None
    families = []
    for record in list(race_history)[-window:]:
        family = _winner_family(record, teams_by_name)
        if family == FAMILY_INDEPENDENT:
            return None
        families.append(family)
    if len(families) < window:
        return None
    if all(item == families[0] for item in families):
        return families[0]
    return None


def win_on_sunday(race_history, teams_by_name=None, window=6):
    """Return the Win-on-Sunday health line from recent victory lanes."""

    families = []
    for record in list(race_history or [])[-window:]:
        family = _winner_family(record, teams_by_name)
        if family and family != FAMILY_INDEPENDENT:
            families.append(family)
    unique = []
    for family in families:
        if family not in unique:
            unique.append(family)
    runaway = one_make_runaway(race_history, teams_by_name)
    if not families:
        return {
            "line": "Win on Sunday: no feature yet this year",
            "health": "pending",
            "families": [],
            "runaway": None,
        }
    if runaway:
        line = "Win on Sunday: %s monopoly — board is restless" % runaway
        health = "poor"
    elif len(unique) >= 3:
        line = "Win on Sunday: %s families in victory lane" % len(unique)
        health = "strong"
    elif len(unique) == 2:
        line = "Win on Sunday: two families splitting the lane"
        health = "fair"
    else:
        line = "Win on Sunday: one-make Sundays — Detroit is restless"
        health = "poor"
    return {
        "line": line,
        "health": health,
        "families": unique,
        "runaway": runaway,
    }


def plate_pack_kind(race_record, book=None):
    """Return wreckfest, single-file, or None for a plate-track feature."""

    if not race_record:
        return None
    track = {
        "name": race_record.get("track") or race_record.get("name"),
        "type": race_record.get("track_type") or race_record.get("type"),
    }
    if not is_plate_track(track, book):
        return None
    cautions = int(race_record.get("cautions") or 0)
    wrecks = race_record.get("wrecks") or []
    wreck_size = 0
    for wreck in wrecks:
        if isinstance(wreck, dict):
            wreck_size = max(
                wreck_size,
                int(wreck.get("cars") or wreck.get("size") or 0),
                len(wreck.get("drivers") or []),
            )
        elif isinstance(wreck, (list, tuple)):
            wreck_size = max(wreck_size, len(wreck))
    if cautions >= 6 or wreck_size >= 6:
        return "wreckfest"
    if cautions <= 1:
        return "single-file"
    return None
