"""Reusable race simulation calculations."""

import random

from data import drivers, manufacturers, teams
from game.policies import (
    current_policies,
    get_crash_modifier,
    get_stage_points_by_position,
    pit_road_enforcement,
    uses_heat_races,
    uses_stage_racing,
)

from game.settings import incident_risk_mod

PRIZE_PERCENTAGES = [0.30, 0.22, 0.17, 0.13, 0.10, 0.08]

WEATHER_CONDITIONS = (
    "Clear",
    "Hot",
    "Cloudy",
    "Windy",
    "Light rain",
)

MECHANICAL_PARTS = ("engine", "transmission", "brakes")
PART_LABELS = {
    "engine": "Engine",
    "transmission": "Transmission",
    "brakes": "Brakes",
}


def clamp(value, minimum=0, maximum=100):
    return max(minimum, min(value, maximum))


def weekend_incident_risk(track):
    """Return track incident risk after the live difficulty modifier."""

    return clamp(int(track.incident_risk) + int(incident_risk_mod()))


def get_team(team_name):
    """Return the team matching the supplied name."""

    for team in teams:
        if team.name == team_name:
            return team

    raise ValueError(f"Team not found: {team_name}")


def get_manufacturer(name):
    """Return the automaker matching the supplied name."""

    for maker in manufacturers:
        if maker.name == name:
            return maker
    return None


def manufacturer_for_team(team):
    """Return the automaker badging a team, if any."""

    if team is None:
        return None
    return get_manufacturer(getattr(team, "manufacturer", None))


def manufacturer_pace_mod(team, track=None):
    """Return the factory pace tick for a team at this venue."""

    maker = manufacturer_for_team(team)
    if maker is None:
        return 0
    bonus = maker.pace_bonus()
    if track is not None:
        bonus += maker.aero_bonus(track.type)
    return bonus


def manufacturer_reliability_mod(team):
    """Return the factory durability tick for a team."""

    maker = manufacturer_for_team(team)
    if maker is None:
        return 0
    return maker.reliability_bonus()


def get_driver(driver_name):
    """Return the driver matching the supplied name."""

    for driver in drivers:
        if driver.name == driver_name:
            return driver

    raise ValueError(f"Driver not found: {driver_name}")


def generate_weather(track):
    """Generate race-day conditions for qualifying and the race."""

    if track.type == "Road Course":
        weights = (35, 15, 20, 10, 20)
    elif track.type == "Superspeedway":
        weights = (40, 25, 15, 18, 2)
    elif track.type == "Short Track":
        weights = (40, 20, 25, 10, 5)
    else:
        weights = (45, 20, 20, 10, 5)

    condition = random.choices(WEATHER_CONDITIONS, weights=weights, k=1)[0]

    if condition == "Clear":
        temp = random.randint(68, 84)
        return {
            "condition": condition,
            "temperature": temp,
            "qualifying_mod": 0,
            "race_mod": 0,
            "incident_mod": 0,
            "tire_mod": 0,
        }

    if condition == "Hot":
        temp = random.randint(88, 98)
        return {
            "condition": condition,
            "temperature": temp,
            "qualifying_mod": -3,
            "race_mod": -2,
            "incident_mod": 2,
            "tire_mod": 12,
        }

    if condition == "Cloudy":
        temp = random.randint(60, 74)
        return {
            "condition": condition,
            "temperature": temp,
            "qualifying_mod": 0,
            "race_mod": 0,
            "incident_mod": 0,
            "tire_mod": -4,
        }

    if condition == "Windy":
        temp = random.randint(62, 80)
        return {
            "condition": condition,
            "temperature": temp,
            "qualifying_mod": -6,
            "race_mod": -4,
            "incident_mod": 4,
            "tire_mod": 2,
        }

    temp = random.randint(52, 66)
    return {
        "condition": condition,
        "temperature": temp,
        "qualifying_mod": -10,
        "race_mod": -8,
        "incident_mod": 8,
        "tire_mod": -15,
    }


def weather_label(weather):
    """Return a short weather line."""

    return f"{weather['condition']}, {weather['temperature']}°"


def tire_load(track, weather):
    """Return combined tire stress from the track and race-day weather."""

    return clamp(track.tire_wear + (weather or {}).get("tire_mod", 0))


def blank_result_fields(start_position, strategy, fuel_call="window"):
    """Return the shared incident/strategy keys for a race result."""

    return {
        "start": start_position,
        "strategy": strategy,
        "fuel_call": fuel_call,
        "pit_mistake": False,
        "pit_mistake_type": None,
        "pit_penalty": None,
        "component": None,
        "contact": None,
        "wreck": None,
    }


def calculate_crash_chance(driver, track, weather=None):
    aggression_effect = driver.aggression // 10
    consistency_effect = driver.consistency // 15
    weather_mod = (weather or {}).get("incident_mod", 0)
    tire_pressure = (tire_load(track, weather) - 50) // 20
    surface_tax = 2 if track.surface == "concrete" else 0
    banking_tax = (track.banking - 18) // 15
    rivalry_heat = getattr(driver, "rivalry_intensity", 0) // 30

    crash_chance = (
        weekend_incident_risk(track)
        + aggression_effect
        - consistency_effect
        + get_crash_modifier()
        + (getattr(driver, "risk_tolerance", 50) - 50) // 25
        + weather_mod
        + tire_pressure
        + surface_tax
        + banking_tax
        + rivalry_heat
    )

    return clamp(crash_chance, 3, 45)


def check_for_crash(driver, track, weather=None):
    crash_chance = calculate_crash_chance(driver, track, weather)

    return random.randint(1, 100) <= crash_chance


def check_for_mechanical_failure(team, track=None, weather=None, strategy="two-stop"):
    """Return a failed part name, or None if the car holds together."""

    engineering_help = getattr(team, "engineering", 0) // 20
    length_tax = 0

    if track is not None and track.length >= 2.0:
        length_tax = 2

    if weather and weather.get("condition") == "Hot":
        length_tax += 1

    failure_chance = max(
        2,
        100
        - team.reliability
        - engineering_help
        + length_tax
        - manufacturer_reliability_mod(team),
    )

    if random.randint(1, 100) > failure_chance:
        return None

    return choose_failed_component(track, weather, strategy)


def choose_failed_component(track, weather=None, strategy="two-stop"):
    """Pick which part failed. Durability still comes from the team."""

    weights = [40, 30, 30]

    if track is not None:
        if track.length >= 2.0 or track.type == "Superspeedway":
            weights[0] += 18
        if track.type in ("Short Track", "Road Course"):
            weights[2] += 14
        if track.type == "Road Course":
            weights[1] += 10

    if weather and weather.get("condition") == "Hot":
        weights[0] += 10

    if strategy == "short-run":
        weights[2] += 10
    elif strategy == "fuel-save":
        weights[0] += 6

    return random.choices(MECHANICAL_PARTS, weights=weights, k=1)[0]


def check_for_pit_mistake(team, strategy="two-stop", driver=None):
    """Return a typed pit-road mistake, or None if the stop is clean."""

    mistake_chance = max(3, 22 - team.crew_rating // 5)

    if strategy == "three-stop":
        mistake_chance += 4
    elif strategy == "wet-tires":
        mistake_chance += 3
    elif strategy == "short-run":
        mistake_chance += 2
    elif strategy == "fuel-save":
        mistake_chance += 1

    if random.randint(1, 100) > mistake_chance:
        return None

    speeding_chance = 32 + pit_road_enforcement() * 8

    if driver is not None:
        speeding_chance += max(0, getattr(driver, "risk_tolerance", 50) - 55) // 3

    if strategy in ("three-stop", "short-run"):
        speeding_chance += 8

    if random.randint(1, 100) <= clamp(speeding_chance, 20, 70):
        mistake_type = "speeding"
        if pit_road_enforcement() >= 2:
            penalty = "stop-and-go"
        elif pit_road_enforcement() == 0 and random.randint(1, 100) <= 40:
            penalty = "drive-through"
        else:
            penalty = "drive-through" if random.randint(1, 100) <= 70 else "stop-and-go"
    else:
        mistake_type = "crew error"
        penalty = "stop-and-go" if team.crew_rating < 68 else "drive-through"

    return {
        "type": mistake_type,
        "penalty": penalty,
    }


def pit_mistake_score_drop(mistake):
    """Return the race-score cost of a typed pit-road penalty."""

    if not mistake:
        return 0

    if mistake["penalty"] == "stop-and-go":
        return random.randint(20, 32)

    if mistake["type"] == "speeding":
        return random.randint(12, 22)

    return random.randint(8, 18)


def choose_pit_strategy(driver, team, track, weather, start_position):
    """Pick a race-outcome pit plan from tires, weather, and grid."""

    load = tire_load(track, weather)

    if weather["condition"] == "Light rain":
        return "wet-tires"

    if load >= 70:
        return "three-stop"

    if start_position <= 2 and track.passing_difficulty >= 60:
        return "short-run"

    if start_position >= 5 and (driver.consistency >= 76 or load <= 45):
        return "fuel-save"

    return "two-stop"


def choose_fuel_call(driver, strategy, cautions):
    """Describe how the pit plan treats fuel. Not a second fuel model."""

    if strategy != "fuel-save":
        return "window"

    if cautions <= 1 and (
        driver.aggression >= 70
        or getattr(driver, "risk_tolerance", 50) >= 72
    ):
        return "late gamble"

    return "conservation"


def late_gamble_fails(fuel_call, cautions):
    """Return whether a stretch call runs the car dry."""

    if fuel_call != "late gamble":
        return False

    chance = 16 + (2 - min(cautions, 2)) * 10

    return random.randint(1, 100) <= chance


def tire_degradation(strategy, track, weather):
    """Return the pace cost of tire wear for the chosen pit plan."""

    load = tire_load(track, weather)

    if strategy == "three-stop":
        return -load // 12
    if strategy == "short-run":
        return -load // 5
    if strategy == "fuel-save":
        return -load // 6
    if strategy == "wet-tires":
        if weather["condition"] == "Light rain":
            return 4
        return -8

    return -load // 8


def fuel_call_score(fuel_call, cautions):
    """Return the pace adjustment from the fuel window on this pit plan."""

    if fuel_call == "conservation":
        return 8 if cautions >= 2 else 1
    if fuel_call == "late gamble":
        return 14 if cautions <= 1 else 6

    if cautions >= 3:
        return 3

    return 0


def pit_strategy_score(strategy, team, track, weather, cautions):
    """Return a race-score adjustment for the chosen pit plan."""

    tire_load_value = tire_load(track, weather)
    crew = team.crew_rating // 20

    if strategy == "two-stop":
        bonus = crew
        if cautions >= 2:
            bonus += 6
        if tire_load_value >= 70:
            bonus -= 4
        return bonus

    if strategy == "three-stop":
        bonus = 4 + crew
        if tire_load_value >= 70 and cautions <= 1:
            bonus += 8
        if cautions >= 3:
            bonus -= 8
        return bonus

    if strategy == "fuel-save":
        bonus = 2
        if cautions >= 3:
            bonus += 8
        elif cautions <= 1:
            bonus -= 6
        return bonus

    if strategy == "short-run":
        bonus = 3
        if track.passing_difficulty >= 60:
            bonus += 5
        return bonus

    if strategy == "wet-tires":
        if weather["condition"] == "Light rain":
            return 10 + crew
        return -18

    return 0


def calculate_qualifying_score(driver, team, track, weather):
    """Return a qualifying speed used to set the grid."""

    skill = driver.track_skill_for(track.type)
    engineering = getattr(team, "engineering", 0)

    return (
        driver.speed
        + skill // 2
        + team.car_rating // 2
        + engineering // 8
        + manufacturer_pace_mod(team, track)
        + weather.get("qualifying_mod", 0)
        + random.randint(-12, 12)
    )


def run_qualifying(active_drivers, track, weather):
    """Set a qualifying order and any grid penalties."""

    entries = []

    for driver in active_drivers:
        team = get_team(driver.team_name)
        score = calculate_qualifying_score(driver, team, track, weather)
        entries.append(
            {
                "driver": driver,
                "score": score,
                "penalty": 0,
                "penalty_reason": None,
            }
        )

    entries.sort(key=lambda entry: entry["score"], reverse=True)

    inspection_heavy = current_policies["technical_rules"] == "inspection-heavy"

    for entry in entries:
        chance = 8
        if inspection_heavy:
            chance += 10

        if random.randint(1, 100) <= chance:
            spots = random.randint(1, 2)
            entry["penalty"] = spots
            entry["penalty_reason"] = "inspection infraction"

    penalized = sorted(
        entries,
        key=lambda entry: (
            entries.index(entry) + entry["penalty"],
            -entry["score"],
        ),
    )

    for position, entry in enumerate(penalized, start=1):
        entry["grid"] = position
        entry["qualifying_position"] = entries.index(entry) + 1

    return penalized


def calculate_race_score(
    driver,
    team,
    track,
    weather,
    start_position,
    field_size,
    cautions,
    strategy,
    fuel_call="window",
):
    engineering = getattr(team, "engineering", 0)
    skill = driver.track_skill_for(track.type)
    grid_weight = 2 + track.passing_difficulty // 20
    grid_bonus = (field_size - start_position) * grid_weight
    weather_mod = weather.get("race_mod", 0)
    pit_bonus = pit_strategy_score(strategy, team, track, weather, cautions)

    return (
        driver.speed
        + driver.consistency
        + team.car_rating
        + team.crew_rating
        + engineering // 5
        + skill // 3
        + manufacturer_pace_mod(team, track)
        + grid_bonus
        + weather_mod
        + pit_bonus
        + track.banking // 10
        + tire_degradation(strategy, track, weather)
        + fuel_call_score(fuel_call, cautions)
        + random.randint(-25, 25)
    )


def determine_crash_cause(driver, contact="crash"):
    """Determine whether a crash requires commissioner review."""

    reckless_chance = clamp(driver.aggression - 35, 10, 65)

    if contact == "minor contact":
        reckless_chance -= 20
    elif contact == "spin":
        reckless_chance -= 8

    if getattr(driver, "rivalry_intensity", 0) >= 70:
        reckless_chance += 8

    if random.randint(1, 100) <= clamp(reckless_chance, 5, 75):
        return "Reckless Driving"

    return "Racing Incident"


def resolve_contact(driver, track, weather):
    """Turn crash chance into minor contact, a spin, or a crash."""

    crashed = check_for_crash(driver, track, weather)

    if not crashed:
        minor_chance = (
            weekend_incident_risk(track) // 4
            + driver.aggression // 20
            + getattr(driver, "rivalry_intensity", 0) // 25
        )

        if random.randint(1, 100) <= clamp(minor_chance, 4, 28):
            return {
                "contact": "minor contact",
                "status": "Running",
                "cause": determine_crash_cause(driver, "minor contact"),
                "score_delta": -random.randint(3, 9),
            }

        return None

    spin_chance = (
        38
        + driver.consistency // 5
        - driver.aggression // 10
        + get_crash_modifier()
    )

    if random.randint(1, 100) <= clamp(spin_chance, 15, 72):
        if random.randint(1, 100) <= 58:
            return {
                "contact": "spin",
                "status": "Running",
                "cause": determine_crash_cause(driver, "spin"),
                "score_delta": -random.randint(10, 22),
            }

        return {
            "contact": "spin",
            "status": "Crash",
            "cause": determine_crash_cause(driver, "spin"),
            "score_delta": 0,
        }

    return {
        "contact": "crash",
        "status": "Crash",
        "cause": determine_crash_cause(driver, "crash"),
        "score_delta": 0,
    }


def determine_driver_result(
    driver,
    track,
    weather=None,
    start_position=1,
    field_size=6,
    cautions=0,
    strategy="two-stop",
):
    """Determine the result for one driver."""

    team = get_team(driver.team_name)
    weather = weather or {
        "condition": "Clear",
        "temperature": 75,
        "qualifying_mod": 0,
        "race_mod": 0,
        "incident_mod": 0,
        "tire_mod": 0,
    }
    fuel_call = choose_fuel_call(driver, strategy, cautions)
    extras = blank_result_fields(start_position, strategy, fuel_call)
    contact = resolve_contact(driver, track, weather)

    if contact and contact["status"] == "Crash":
        return {
            "driver": driver,
            **extras,
            "status": "Crash",
            "cause": contact["cause"],
            "score": random.randint(1, 50),
            "contact": contact["contact"],
        }

    contact_delta = 0

    if contact:
        extras["contact"] = contact["contact"]
        extras["cause"] = contact["cause"]
        contact_delta = contact.get("score_delta", 0)

    failed_part = check_for_mechanical_failure(
        team,
        track,
        weather,
        strategy,
    )

    if failed_part:
        return {
            "driver": driver,
            **extras,
            "status": "Mechanical Failure",
            "cause": None,
            "score": random.randint(51, 100),
            "component": failed_part,
        }

    if late_gamble_fails(fuel_call, cautions):
        return {
            "driver": driver,
            **extras,
            "status": "Out of Fuel",
            "cause": None,
            "score": random.randint(40, 90),
        }

    score = calculate_race_score(
        driver,
        team,
        track,
        weather,
        start_position,
        field_size,
        cautions,
        strategy,
        fuel_call=fuel_call,
    )
    score += contact_delta
    mistake = check_for_pit_mistake(team, strategy, driver)

    if mistake:
        team.record_pit_mistake()
        extras["pit_mistake"] = True
        extras["pit_mistake_type"] = mistake["type"]
        extras["pit_penalty"] = mistake["penalty"]
        score -= pit_mistake_score_drop(mistake)

    cause = extras.pop("cause", None)

    return {
        "driver": driver,
        **extras,
        "status": "Running",
        "cause": cause,
        "score": score,
    }


def sort_race_results(results):
    """Place running cars ahead of cars that did not finish."""

    return sorted(
        results,
        key=lambda result: (
            result["status"] == "Running",
            result["score"],
        ),
        reverse=True,
    )


def get_active_drivers():
    """Return drivers who may participate in the race."""

    return [
        driver
        for driver in drivers
        if not driver.is_suspended()
    ]


def generate_cautions(track, weather, crash_count, wrecks=None):
    """Return a race-outcome caution count. Not a lap-by-lap wreck chain."""

    base = max(0, weekend_incident_risk(track) // 10)
    extra = 1 if weather.get("incident_mod", 0) >= 4 else 0
    major = sum(1 for wreck in (wrecks or []) if wreck.get("major"))
    yellows = base + extra + crash_count + major

    return min(yellows, 6)


def apply_caution_compression(results, cautions, track):
    """Bunch running cars after yellows and give restart variance."""

    if cautions <= 0:
        return

    running = [
        result
        for result in results
        if result["status"] == "Running"
    ]

    for result in running:
        driver = result["driver"]
        bunch = cautions * random.randint(-3, 7)
        restart = cautions * ((driver.aggression - 60) // 20)
        result["score"] += bunch + restart


def simulate_stage_results(running_results, stage_number):
    """Order running cars for one stage without a second physics model."""

    staged = []

    for result in running_results:
        staged.append(
            {
                "driver": result["driver"],
                "score": result["score"] + random.randint(-16, 16),
            }
        )

    staged.sort(key=lambda item: item["score"], reverse=True)

    table = get_stage_points_by_position()
    awarded = []

    for position, item in enumerate(staged, start=1):
        points = table[position - 1] if position <= len(table) else 0
        awarded.append(
            {
                "stage": stage_number,
                "position": position,
                "driver": item["driver"].name,
                "team": item["driver"].team_name,
                "points": points,
            }
        )

    return awarded


def simulate_heat(grid, track, weather):
    """Run a qualifying heat that reshuffles the feature grid."""

    heated = []

    for entry in grid:
        driver = entry["driver"]
        skill = driver.track_skill_for(track.type)
        heated.append(
            {
                "driver": driver,
                "score": (
                    entry["score"]
                    + skill // 4
                    + weather.get("race_mod", 0)
                    + random.randint(-14, 14)
                ),
                "penalty": entry.get("penalty", 0),
                "penalty_reason": entry.get("penalty_reason"),
                "qualifying_position": entry["qualifying_position"],
            }
        )

    heated.sort(key=lambda item: item["score"], reverse=True)

    for position, entry in enumerate(heated, start=1):
        entry["grid"] = position

    return heated


def apply_multi_car_wrecks(results, track):
    """Collect nearby cars into chain-reaction wrecks at outcome level."""

    crashers = [
        result
        for result in results
        if result["status"] == "Crash" and result.get("contact") == "crash"
    ]
    wrecks = []

    for initiator in crashers:
        if initiator.get("wreck"):
            continue

        start = initiator.get("start", 3)
        collected = []

        for other in results:
            if other is initiator or other.get("wreck"):
                continue

            if other["status"] in ("Out of Fuel", "Mechanical Failure"):
                continue

            distance = abs(other.get("start", 0) - start)
            collect_chance = (
                16
                + weekend_incident_risk(track) // 2
                - distance * 7
            )

            if track.type == "Superspeedway":
                collect_chance += 12
            elif track.type == "Short Track":
                collect_chance += 6

            if other.get("contact") in ("spin", "minor contact"):
                collect_chance += 14

            if other["status"] == "Crash":
                collect_chance += 10

            if random.randint(1, 100) <= clamp(collect_chance, 4, 52):
                collected.append(other)

        involved = [initiator] + collected

        if len(involved) < 2:
            continue

        cars = [result["driver"].name for result in involved]
        major = len(involved) >= 3

        for result in involved:
            result["wreck"] = {
                "role": "initiator" if result is initiator else "collected",
                "size": len(involved),
                "cars": cars,
                "major": major,
            }

            if result is not initiator:
                result["contact"] = result.get("contact") or "crash"
                result["status"] = "Crash"
                if not result.get("cause"):
                    result["cause"] = "Racing Incident"
                result["score"] = min(
                    result.get("score", 40),
                    random.randint(1, 45),
                )

        wrecks.append(
            {
                "initiator": initiator["driver"].name,
                "team": initiator["driver"].team_name,
                "cars": cars,
                "size": len(involved),
                "major": major,
            }
        )

    return wrecks


def build_investigation(incident, wrecks):
    """Assemble evidence and blame for the existing commissioner review."""

    driver = incident["driver"]
    wreck = incident.get("wreck")
    evidence = []
    confidence = "moderate"
    blame = driver.name

    if incident.get("cause") == "Reckless Driving":
        evidence.append("onboard shows a late move into the corner")
        evidence.append(f"aggression rating {driver.aggression}")
        confidence = "strong" if driver.aggression >= 75 else "moderate"

    if incident.get("contact") == "spin":
        evidence.append("the car rotated after side-to-side contact")
    elif incident.get("contact") == "crash":
        evidence.append("heavy contact ended the car's race")

    if wreck:
        evidence.append(
            f"{wreck['size']}-car incident involving {', '.join(wreck['cars'])}"
        )
        if wreck.get("role") == "initiator":
            evidence.append("replay shows first contact from this car")
        evidence.append("spotters report a chain reaction after the initial hit")
        if wreck.get("major"):
            confidence = "strong"

    if getattr(driver, "rival", None):
        evidence.append(
            f"history with {driver.rival} "
            f"(rivalry {driver.rivalry_intensity})"
        )

    matching = [
        wreck_row
        for wreck_row in wrecks
        if wreck_row["initiator"] == driver.name
    ]

    if matching and not wreck:
        evidence.append(
            f"race control lists {driver.name} as the first car in the pileup"
        )

    if not evidence:
        evidence.append("stewards have video and spotter audio to review")

    return {
        "driver": driver.name,
        "team": driver.team_name,
        "blame": blame,
        "confidence": confidence,
        "cause": incident.get("cause"),
        "contact": incident.get("contact"),
        "evidence": evidence,
        "involved": wreck["cars"] if wreck else [driver.name],
        "major": bool(wreck and wreck.get("major")),
    }


def collect_investigations(results, wrecks):
    """Return review packets for reckless crashes and wreck initiators."""

    investigations = []
    seen = set()

    for result in results:
        driver_name = result["driver"].name

        if driver_name in seen:
            continue

        wreck = result.get("wreck")
        reviewable = result["status"] == "Crash" and (
            result.get("cause") == "Reckless Driving"
            or (wreck and wreck.get("role") == "initiator")
        )

        if not reviewable:
            continue

        seen.add(driver_name)
        investigations.append(build_investigation(result, wrecks))

    return investigations


def simulate_race_weekend(track):
    """Run qualifying, optional stages/heats, and the feature race."""

    weather = generate_weather(track)
    active_drivers = get_active_drivers()
    grid = run_qualifying(active_drivers, track, weather)
    heat_results = []

    if uses_heat_races() and grid:
        grid = simulate_heat(grid, track, weather)
        heat_results = [
            {
                "position": entry["grid"],
                "driver": entry["driver"].name,
                "team": entry["driver"].team_name,
            }
            for entry in grid
        ]

    field_size = max(1, len(grid))
    preview_cautions = max(
        0,
        weekend_incident_risk(track) // 10
        + (1 if weather.get("incident_mod", 0) >= 4 else 0),
    )

    results = []

    for entry in grid:
        driver = entry["driver"]
        team = get_team(driver.team_name)
        start_position = entry["grid"]
        strategy = choose_pit_strategy(
            driver,
            team,
            track,
            weather,
            start_position,
        )
        result = determine_driver_result(
            driver,
            track,
            weather=weather,
            start_position=start_position,
            field_size=field_size,
            cautions=preview_cautions,
            strategy=strategy,
        )
        result["qualifying_position"] = entry["qualifying_position"]
        result["grid_penalty"] = entry["penalty"]
        result["grid_penalty_reason"] = entry["penalty_reason"]
        results.append(result)

    wrecks = apply_multi_car_wrecks(results, track)
    crash_count = sum(
        1
        for result in results
        if result["status"] == "Crash"
    )
    cautions = generate_cautions(track, weather, crash_count, wrecks)
    apply_caution_compression(results, cautions, track)
    results = sort_race_results(results)
    investigations = collect_investigations(results, wrecks)

    stage_results = []
    stage_points = {driver.name: 0 for driver in active_drivers}

    if uses_stage_racing():
        running = [
            result
            for result in results
            if result["status"] == "Running"
        ]

        for stage_number in (1, 2):
            stage = simulate_stage_results(running, stage_number)
            stage_results.append(stage)

            for row in stage:
                stage_points[row["driver"]] += row["points"]

    return {
        "weather": weather,
        "format": current_policies["race_format"],
        "grid": grid,
        "heat_results": heat_results,
        "cautions": cautions,
        "wrecks": wrecks,
        "investigations": investigations,
        "stage_results": stage_results,
        "stage_points": stage_points,
        "results": results,
    }
