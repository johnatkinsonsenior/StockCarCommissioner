"""Reusable race simulation calculations."""

import random

from data import drivers, teams
from game.policies import (
    current_policies,
    get_crash_modifier,
    get_stage_points_by_position,
    uses_heat_races,
    uses_stage_racing,
)

PRIZE_PERCENTAGES = [0.30, 0.22, 0.17, 0.13, 0.10, 0.08]

WEATHER_CONDITIONS = (
    "Clear",
    "Hot",
    "Cloudy",
    "Windy",
    "Light rain",
)


def clamp(value, minimum=0, maximum=100):
    return max(minimum, min(value, maximum))


def get_team(team_name):
    """Return the team matching the supplied name."""

    for team in teams:
        if team.name == team_name:
            return team

    raise ValueError(f"Team not found: {team_name}")


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


def calculate_crash_chance(driver, track, weather=None):
    aggression_effect = driver.aggression // 10
    consistency_effect = driver.consistency // 15
    weather_mod = (weather or {}).get("incident_mod", 0)
    tire_pressure = (track.tire_wear - 50) // 25
    surface_tax = 2 if track.surface == "concrete" else 0
    banking_tax = (track.banking - 18) // 15

    crash_chance = (
        track.incident_risk
        + aggression_effect
        - consistency_effect
        + get_crash_modifier()
        + (getattr(driver, "risk_tolerance", 50) - 50) // 25
        + weather_mod
        + tire_pressure
        + surface_tax
        + banking_tax
    )

    return clamp(crash_chance, 3, 45)


def check_for_crash(driver, track, weather=None):
    crash_chance = calculate_crash_chance(driver, track, weather)

    return random.randint(1, 100) <= crash_chance


def check_for_mechanical_failure(team, track=None):
    engineering_help = getattr(team, "engineering", 0) // 20
    length_tax = 0

    if track is not None and track.length >= 2.0:
        length_tax = 2

    failure_chance = max(2, 100 - team.reliability - engineering_help + length_tax)

    return random.randint(1, 100) <= failure_chance


def check_for_pit_mistake(team, strategy="two-stop"):
    """Return whether the team's pit crew makes a costly stop."""

    mistake_chance = max(3, 22 - team.crew_rating // 5)

    if strategy == "three-stop":
        mistake_chance += 4
    elif strategy == "wet-tires":
        mistake_chance += 3
    elif strategy == "short-run":
        mistake_chance += 2

    return random.randint(1, 100) <= mistake_chance


def choose_pit_strategy(driver, team, track, weather, start_position):
    """Pick a race-outcome pit plan from tires, weather, and grid."""

    tire_load = clamp(track.tire_wear + weather.get("tire_mod", 0))

    if weather["condition"] == "Light rain":
        return "wet-tires"

    if tire_load >= 70 and team.crew_rating >= 72:
        return "three-stop"

    if start_position <= 2 and track.passing_difficulty >= 60:
        return "short-run"

    if start_position >= 5 and driver.consistency >= 80:
        return "fuel-save"

    return "two-stop"


def pit_strategy_score(strategy, team, track, weather, cautions):
    """Return a race-score adjustment for the chosen pit plan."""

    tire_load = track.tire_wear + weather.get("tire_mod", 0)
    crew = team.crew_rating // 20

    if strategy == "two-stop":
        bonus = crew
        if cautions >= 2:
            bonus += 6
        return bonus

    if strategy == "three-stop":
        bonus = 4 + crew
        if tire_load >= 70 and cautions <= 1:
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
        + grid_bonus
        + weather_mod
        + pit_bonus
        + track.banking // 10
        + random.randint(-25, 25)
    )


def determine_crash_cause(driver):
    """Determine whether a crash requires commissioner review."""

    reckless_chance = clamp(driver.aggression - 35, 10, 65)

    if random.randint(1, 100) <= reckless_chance:
        return "Reckless Driving"

    return "Racing Incident"


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

    if check_for_crash(driver, track, weather):
        return {
            "driver": driver,
            "status": "Crash",
            "cause": determine_crash_cause(driver),
            "score": random.randint(1, 50),
            "pit_mistake": False,
            "start": start_position,
            "strategy": strategy,
        }

    if check_for_mechanical_failure(team, track):
        return {
            "driver": driver,
            "status": "Mechanical Failure",
            "cause": None,
            "score": random.randint(51, 100),
            "pit_mistake": False,
            "start": start_position,
            "strategy": strategy,
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
    )
    pit_mistake = check_for_pit_mistake(team, strategy)

    if pit_mistake:
        team.record_pit_mistake()
        score -= random.randint(8, 18)

    return {
        "driver": driver,
        "status": "Running",
        "cause": None,
        "score": score,
        "pit_mistake": pit_mistake,
        "start": start_position,
        "strategy": strategy,
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


def generate_cautions(track, weather, crash_count):
    """Return a race-outcome caution count. Not a lap-by-lap wreck chain."""

    base = max(0, track.incident_risk // 10)
    extra = 1 if weather.get("incident_mod", 0) >= 4 else 0
    yellows = base + extra + crash_count

    return min(yellows, 5)


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
        track.incident_risk // 10
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

    crash_count = sum(
        1
        for result in results
        if result["status"] == "Crash"
    )
    cautions = generate_cautions(track, weather, crash_count)
    apply_caution_compression(results, cautions, track)
    results = sort_race_results(results)

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
        "stage_results": stage_results,
        "stage_points": stage_points,
        "results": results,
    }
