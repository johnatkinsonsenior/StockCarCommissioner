import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from season_data import drivers, teams, tracks


POINTS_BY_POSITION = [40, 35, 32, 30, 28, 26]
PRIZE_PERCENTAGES = [0.30, 0.22, 0.17, 0.13, 0.10, 0.08]


def get_team(team_name):
    """Return the team matching the supplied team name."""

    for team in teams:
        if team["name"] == team_name:
            return team

    raise ValueError(f"Team not found: {team_name}")


def calculate_crash_chance(driver, track):
    """
    Calculate a driver's crash chance.

    Aggressive drivers have a higher crash chance.
    Consistent drivers have a lower crash chance.
    Dangerous tracks increase the chance.
    """

    aggression_effect = driver["aggression"] // 10
    consistency_effect = driver["consistency"] // 15

    crash_chance = (
        track["incident_risk"]
        + aggression_effect
        - consistency_effect
    )

    return max(3, min(crash_chance, 40))


def check_for_crash(driver, track):
    """Return True when the driver crashes."""

    crash_chance = calculate_crash_chance(driver, track)
    roll = random.randint(1, 100)

    return roll <= crash_chance


def check_for_mechanical_failure(driver):
    """Return True when the driver's car suffers a mechanical failure."""

    team = get_team(driver["team"])

    failure_chance = max(2, 100 - team["reliability"])
    roll = random.randint(1, 100)

    return roll <= failure_chance


def calculate_race_score(driver):
    """Calculate the driver's performance score for the race."""

    team = get_team(driver["team"])
    random_factor = random.randint(-25, 25)

    return (
        driver["speed"]
        + driver["consistency"]
        + team["car_rating"]
        + team["crew_rating"]
        + random_factor
    )


def determine_driver_result(driver, track):
    """Determine whether a driver finishes, crashes, or has a failure."""

    if check_for_crash(driver, track):
        return {
            "driver": driver,
            "status": "Crash",
            "score": random.randint(1, 50),
        }

    if check_for_mechanical_failure(driver):
        return {
            "driver": driver,
            "status": "Mechanical Failure",
            "score": random.randint(51, 100),
        }

    return {
        "driver": driver,
        "status": "Running",
        "score": calculate_race_score(driver),
    }


def sort_race_results(results):
    """
    Running cars finish ahead of cars that did not finish.

    Among each group, the higher score finishes ahead.
    """

    return sorted(
        results,
        key=lambda result: (
            result["status"] == "Running",
            result["score"],
        ),
        reverse=True,
    )


def run_race(track, race_number):
    """Run one race and update season statistics."""

    results = []

    for driver in drivers:
        result = determine_driver_result(driver, track)
        results.append(result)

    results = sort_race_results(results)

    print(f"\nRace {race_number}: {track['name']}")
    print(f"Track type: {track['type']}")
    print(f"Incident risk: {track['incident_risk']}%")
    print(f"Purse: ${track['purse']:,}")
    print("-" * 75)

    for position, result in enumerate(results, start=1):
        driver = result["driver"]
        status = result["status"]

        points_earned = POINTS_BY_POSITION[position - 1]
        prize_money = int(
            track["purse"] * PRIZE_PERCENTAGES[position - 1]
        )

        driver["points"] += points_earned
        driver["earnings"] += prize_money
        driver["starts"] += 1

        team = get_team(driver["team"])
        team["budget"] += prize_money

        if status == "Running":
            driver["finishes"] += 1

            if position == 1:
                driver["wins"] += 1

            status_display = "Finished"

        else:
            driver["dnfs"] += 1
            status_display = f"DNF: {status}"

        print(
            f"{position}. {driver['name']} "
            f"({driver['team']}) "
            f"- {status_display} "
            f"- {points_earned} pts "
            f"- ${prize_money:,}"
        )

    display_incident_report(results)


def display_incident_report(results):
    """Display crashes and mechanical failures from the race."""

    incidents = [
        result
        for result in results
        if result["status"] != "Running"
    ]

    print("\nIncident Report")
    print("-" * 75)

    if not incidents:
        print("No major incidents occurred.")

        return

    for incident in incidents:
        driver = incident["driver"]
        print(f"{driver['name']}: {incident['status']}")


def display_driver_standings():
    """Display the final driver championship standings."""

    standings = sorted(
        drivers,
        key=lambda driver: driver["points"],
        reverse=True,
    )

    print("\nFinal Driver Standings")
    print("-" * 75)

    for position, driver in enumerate(standings, start=1):
        print(
            f"{position}. {driver['name']} "
            f"({driver['team']}) "
            f"- {driver['points']} pts "
            f"- {driver['wins']} wins "
            f"- {driver['dnfs']} DNFs "
            f"- ${driver['earnings']:,}"
        )


def display_team_finances():
    """Display team budgets after the season."""

    financial_ranking = sorted(
        teams,
        key=lambda team: team["budget"],
        reverse=True,
    )

    print("\nFinal Team Finances")
    print("-" * 75)

    for team in financial_ranking:
        print(
            f"{team['name']} "
            f"- Budget: ${team['budget']:,} "
            f"- Reliability: {team['reliability']}"
        )


def initialize_season():
    """Reset driver season statistics."""

    for driver in drivers:
        driver["points"] = 0
        driver["earnings"] = 0
        driver["starts"] = 0
        driver["finishes"] = 0
        driver["wins"] = 0
        driver["dnfs"] = 0


def run_season():
    """Run the complete racing season."""

    initialize_season()

    for race_number, track in enumerate(tracks, start=1):
        run_race(track, race_number)

    display_driver_standings()
    display_team_finances()


if __name__ == "__main__":
    run_season()
