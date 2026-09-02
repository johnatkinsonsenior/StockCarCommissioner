"""Personal driver endorsement deals.

Matches sponsors (see :mod:`game.models.Sponsor`) to drivers based on how well
a driver's profile fits what the sponsor values, then builds an endorsement
deal with an annual value and an obligation the driver is expected to uphold.

An endorsement is stored on a driver as a plain dict so it serializes cleanly
into save files:

    {
        "sponsor": str,            # sponsor company name
        "industry": str,
        "annual_value": int,       # paid to the driver each season
        "years_remaining": int,
        "priority": str,           # sponsor's top value (drives the obligation)
        "obligation": str,         # human-readable obligation
        "obligation_attr": str,    # driver attribute the obligation checks
        "obligation_target": int,  # threshold that attribute must reach
    }
"""

import random

# For each sponsor priority: (obligation text, driver attribute, target value).
OBLIGATIONS = {
    "wins": ("Win at least 2 races", "wins", 2),
    "popularity": ("Keep popularity at or above 60", "popularity", 60),
    "exposure": ("Keep reputation at or above 60", "reputation", 60),
    "clean_image": ("Keep credibility at or above 60", "credibility", 60),
}


def _driver_qualities(driver):
    """Map sponsor value keys to the driver stat that represents them."""

    return {
        "wins": driver.overall_rating(),
        "popularity": driver.popularity,
        "exposure": driver.reputation,
        "clean_image": driver.credibility,
    }


def fit_score(sponsor, driver):
    """Return how well a driver matches a sponsor's preferences."""

    qualities = _driver_qualities(driver)

    return sum(
        weight * qualities[key]
        for key, weight in sponsor.preferences.items()
    )


def deal_value(sponsor, driver):
    """Return the annual endorsement value, scaled by the driver's popularity."""

    base = sponsor.budget * 0.10
    multiplier = 0.75 + driver.popularity / 200.0

    return int(round(base * multiplier, -4))


def build_endorsement(sponsor, driver, years_remaining):
    """Build an endorsement deal dict for a sponsor/driver pairing."""

    priority = sponsor.top_priority()
    obligation, attribute, target = OBLIGATIONS[priority]

    return {
        "sponsor": sponsor.name,
        "industry": sponsor.industry,
        "annual_value": deal_value(sponsor, driver),
        "years_remaining": years_remaining,
        "priority": priority,
        "obligation": obligation,
        "obligation_attr": attribute,
        "obligation_target": target,
    }


def obligation_met(driver):
    """Return True/False if the driver has a deal, else None."""

    endorsement = getattr(driver, "endorsement", None)

    if not endorsement:
        return None

    value = getattr(driver, endorsement["obligation_attr"], 0)

    return value >= endorsement["obligation_target"]


def assign_endorsements(drivers, sponsors, rng=None):
    """Assign a best-fit available sponsor to each driver who lacks a deal.

    Sponsors already under contract are skipped so each backs one driver. Higher
    rated drivers get first pick. Returns the list of newly signed drivers.
    """

    rng = rng or random

    taken = {
        driver.endorsement["sponsor"]
        for driver in drivers
        if driver.endorsement
    }
    available = [sponsor for sponsor in sponsors if sponsor.name not in taken]

    needing = sorted(
        (driver for driver in drivers if not driver.endorsement),
        key=lambda driver: driver.overall_rating(),
        reverse=True,
    )

    signed = []

    for driver in needing:
        if not available:
            break

        best = max(available, key=lambda sponsor: fit_score(sponsor, driver))
        available.remove(best)
        driver.endorsement = build_endorsement(
            best,
            driver,
            rng.randint(1, 3),
        )
        signed.append(driver)

    return signed


def age_endorsements(drivers):
    """Decrement deal length by one season and expire finished deals.

    Returns the list of (driver, expired_sponsor_name) for expired deals.
    """

    expired = []

    for driver in drivers:
        endorsement = driver.endorsement

        if not endorsement:
            continue

        endorsement["years_remaining"] -= 1

        if endorsement["years_remaining"] <= 0:
            expired.append((driver, endorsement["sponsor"]))
            driver.endorsement = None

    return expired
