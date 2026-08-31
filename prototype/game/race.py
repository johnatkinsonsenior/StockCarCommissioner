"""Reusable race simulation calculations."""

import random

from data import drivers, teams
from game.policies import get_crash_modifier

POINTS_BY_POSITION = [40, 35, 32, 30, 28, 26]
PRIZE_PERCENTAGES = [0.30, 0.22, 0.17, 0.13, 0.10, 0.08]


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


def calculate_crash_chance(driver, track):
    aggression_effect = driver.aggression // 10
    consistency_effect = driver.consistency // 15

    crash_chance = (
        track["incident_risk"]
        + aggression_effect
        - consistency_effect
        + get_crash_modifier()
    )

    return clamp(crash_chance, 3, 40)


def check_for_crash(driver, track):
    crash_chance = calculate_crash_chance(driver, track)

    return random.randint(1, 100) <= crash_chance


def check_for_mechanical_failure(team):
    engineering_help = getattr(team, "engineering", 0) // 20
    failure_chance = max(2, 100 - team.reliability - engineering_help)

    return random.randint(1, 100) <= failure_chance


def check_for_pit_mistake(team):
    """Return whether the team's pit crew makes a costly stop."""

    mistake_chance = max(3, 22 - team.crew_rating // 5)

    return random.randint(1, 100) <= mistake_chance


def calculate_race_score(driver, team):
    engineering = getattr(team, "engineering", 0)

    return (
        driver.speed
        + driver.consistency
        + team.car_rating
        + team.crew_rating
        + engineering // 5
        + random.randint(-25, 25)
    )


def determine_crash_cause(driver):
    """Determine whether a crash requires commissioner review."""

    reckless_chance = clamp(driver.aggression - 35, 10, 65)

    if random.randint(1, 100) <= reckless_chance:
        return "Reckless Driving"

    return "Racing Incident"


def determine_driver_result(driver, track):
    """Determine the result for one driver."""

    team = get_team(driver.team_name)

    if check_for_crash(driver, track):
        return {
            "driver": driver,
            "status": "Crash",
            "cause": determine_crash_cause(driver),
            "score": random.randint(1, 50),
            "pit_mistake": False,
        }

    if check_for_mechanical_failure(team):
        return {
            "driver": driver,
            "status": "Mechanical Failure",
            "cause": None,
            "score": random.randint(51, 100),
            "pit_mistake": False,
        }

    score = calculate_race_score(driver, team)
    pit_mistake = check_for_pit_mistake(team)

    if pit_mistake:
        team.record_pit_mistake()
        score -= random.randint(8, 18)

    return {
        "driver": driver,
        "status": "Running",
        "cause": None,
        "score": score,
        "pit_mistake": pit_mistake,
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
