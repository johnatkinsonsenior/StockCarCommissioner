"""Era books: rewind the same commissioner model into a start decade.

Day 100 stored the book as a label. Day 112 changes who sits on the
opening grid, which factories badge the field, and how fat the TV
check is. It is not the Aero Wars coupe rewrite (Days 113–114).
"""

from data.cup_grid import (
    BEYOND_DRIVER_COUNT,
    BEYOND_TEAM_COUNT,
    PINNACLE_DRIVER_COUNT,
    PINNACLE_TEAM_COUNT,
    premier_drivers,
    premier_teams,
    waiting_applicants,
)
from game.models import Manufacturer
from game.settings import (
    ERA_1970S,
    ERA_1980S,
    ERA_BEYOND,
    ERA_PINNACLE,
    VALID_ERA_BOOKS,
)

# Chrysler analogue. Present in the 1970s, fading in the 1980s, gone
# from the pinnacle charter unless a later book invites them back.
VALIANT = Manufacturer(
    name="Valiant",
    identity="Torque",
    speed_bias=62,
    reliability_bias=58,
    aero_bias=44,
    prestige=60,
    factory_support=64,
)


ERA_FIELD = {
    ERA_1970S: 8,
    ERA_1980S: 9,
    ERA_PINNACLE: PINNACLE_TEAM_COUNT,
    ERA_BEYOND: BEYOND_TEAM_COUNT,
}

# Who badges which shop in each book. Missing names keep the pinnacle badge.
ERA_BADGES = {
    ERA_1970S: {
        "Harbor Racing": "Valiant",
        "Ironwood Motorsports": "Valiant",
        "Redline Racing": "Apex",
        "Coastal Speed": "Falcon",
        "Midland Racing": "Vanguard",
        "Crown Motorsports": "Apex",
        "Blue Ridge Racing": "Falcon",
    },
    ERA_1980S: {
        "Harbor Racing": "Valiant",
        "Ironwood Motorsports": "Apex",
    },
    ERA_PINNACLE: {},
    ERA_BEYOND: {
        "Silver Creek Racing": "Apex",
        "Lakeside Motorsports": "Falcon",
        "Harbor Racing": "Valiant",
    },
}

ERA_WORLD = {
    ERA_1970S: {
        "fan_delta": -8,
        "tv_value_scale": 0.55,
        "treasury_bonus": 0,
        "shop_bonus": 0,
        "valiant_support": 70,
    },
    ERA_1980S: {
        "fan_delta": -3,
        "tv_value_scale": 0.80,
        "treasury_bonus": 0,
        "shop_bonus": 0,
        "valiant_support": 38,
    },
    ERA_PINNACLE: {
        "fan_delta": 0,
        "tv_value_scale": 1.0,
        "treasury_bonus": 0,
        "shop_bonus": 0,
        "valiant_support": 0,
    },
    ERA_BEYOND: {
        "fan_delta": 6,
        "tv_value_scale": 1.15,
        "treasury_bonus": 400_000,
        "shop_bonus": 200_000,
        "valiant_support": 52,
    },
}


def normalize_era_book(era_book):
    """Return a valid era key, defaulting to pinnacle."""

    key = str(era_book or ERA_PINNACLE).strip()
    if key in VALID_ERA_BOOKS:
        return key
    return ERA_PINNACLE


def era_team_count(era_book):
    """Return how many shops open this book."""

    return int(ERA_FIELD.get(normalize_era_book(era_book), PINNACLE_TEAM_COUNT))


def era_driver_count(era_book):
    """Return how many Cup seats open this book."""

    return era_team_count(era_book) * 2


def uses_valiant(era_book):
    """Return whether Valiant badges a shop on the opening grid."""

    badges = ERA_BADGES.get(normalize_era_book(era_book)) or {}
    return "Valiant" in list(badges.values())


def _bound(value, lo=0, hi=100):
    return max(lo, min(hi, int(value)))


def _base_manufacturers():
    return [
        Manufacturer(
            name="Vanguard",
            identity="Durability",
            speed_bias=48,
            reliability_bias=78,
            aero_bias=58,
            prestige=72,
            factory_support=70,
        ),
        Manufacturer(
            name="Apex",
            identity="Speed",
            speed_bias=82,
            reliability_bias=46,
            aero_bias=64,
            prestige=76,
            factory_support=74,
        ),
        Manufacturer(
            name="Falcon",
            identity="Balance",
            speed_bias=56,
            reliability_bias=70,
            aero_bias=62,
            prestige=64,
            factory_support=58,
        ),
        Manufacturer(
            name="Independent",
            identity="Unaligned",
            speed_bias=50,
            reliability_bias=50,
            aero_bias=50,
            prestige=40,
            factory_support=0,
        ),
    ]


def create_manufacturers_for_era(era_book):
    """Return factories for this book. Valiant sits out the pinnacle grid."""

    makers = _base_manufacturers()
    era = normalize_era_book(era_book)
    if not uses_valiant(era):
        return makers
    valiant = Manufacturer(
        name=VALIANT.name,
        identity=VALIANT.identity,
        speed_bias=VALIANT.speed_bias,
        reliability_bias=VALIANT.reliability_bias,
        aero_bias=VALIANT.aero_bias,
        prestige=VALIANT.prestige,
        factory_support=int(
            (ERA_WORLD.get(era) or {}).get("valiant_support") or 50
        ),
    )
    return makers[:-1] + [valiant, makers[-1]]


def create_teams_for_era(era_book):
    """Return the opening charter for this era book."""

    era = normalize_era_book(era_book)
    count = era_team_count(era)
    shops = premier_teams()[:count]
    badges = ERA_BADGES.get(era) or {}
    for team in shops:
        if team.name in badges:
            team.manufacturer = badges[team.name]
    return shops


def create_drivers_for_era(era_book):
    """Return the opening grid that sits on this era's charter."""

    count = era_driver_count(era_book)
    if count >= BEYOND_DRIVER_COUNT:
        return premier_drivers()[:BEYOND_DRIVER_COUNT]
    if count >= PINNACLE_DRIVER_COUNT:
        return premier_drivers()[:PINNACLE_DRIVER_COUNT]
    names = {team.name for team in create_teams_for_era(era_book)}
    return [
        driver
        for driver in premier_drivers()
        if driver.team_name in names
    ]


def create_applicants_for_era(era_book):
    """Return owners still outside the charter for this book."""

    seated = {team.name for team in create_teams_for_era(era_book)}
    rows = []
    for applicant in waiting_applicants():
        if applicant.get("team_name") in seated:
            continue
        rows.append(dict(applicant))
    return rows


def apply_era_flavor(league, teams, era_book):
    """Overlay TV/treasury/fan flavor after the opening book is built."""

    era = normalize_era_book(era_book)
    flavor = ERA_WORLD.get(era) or ERA_WORLD[ERA_PINNACLE]
    fan_delta = int(flavor.get("fan_delta") or 0)
    if fan_delta:
        league["fan_interest"] = _bound(
            int(league.get("fan_interest") or 65) + fan_delta
        )
    bonus = int(flavor.get("treasury_bonus") or 0)
    if bonus:
        league["treasury"] = max(0, int(league.get("treasury") or 0) + bonus)
    shop_bonus = int(flavor.get("shop_bonus") or 0)
    if shop_bonus:
        for team in teams or []:
            team.budget = max(100_000, int(team.budget) + shop_bonus)
    scale = float(flavor.get("tv_value_scale") or 1.0)
    deal = league.get("tv_rights")
    if deal and scale != 1.0 and deal.get("value"):
        deal["value"] = int(deal["value"] * scale)
    naming = league.get("naming_rights")
    if naming and scale < 1.0 and naming.get("value"):
        naming["value"] = int(naming["value"] * scale)
    return era
