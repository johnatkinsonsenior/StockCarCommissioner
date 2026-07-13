import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from season_data import drivers, teams, tracks


POINTS_BY_POSITION = [40, 35, 32, 30, 28, 26]
PRIZE_PERCENTAGES = [0.30, 0.22, 0.17, 0.13, 0.10, 0.08]


def get_team(team_name):
    for team in teams:
        if team["name"] == team_name:
            return team

    raise ValueError(f"Team not found: {team_name}")


def calculate_race_score(driver):
    team = get_team(driver["team"])

    random_factor = random.randint(-25, 25)

    return (
        driver["speed"]
        + driver["consistency"]
        + team["car_rating"]
        + team["crew_rating"]
        + random_factor
    )


def run_race(track, race_number):
    results = []

    for driver in drivers:
        score = calculate_race_score(driver)
        results.append({"driver": driver, "score": score})

    results.sort(key=lambda result: result["score"], reverse=True)

    print(f"\nRace {race_number}: {track['name']}")
    print(f"Track type: {track['type']}")
    print(f"Purse: ${track['purse']:,}")
    print("-" * 55)

    for position, result in enumerate(results, start=1):
        driver = result["driver"]
        points_earned = POINTS_BY_POSITION[position - 1]
        prize_money = int(track["purse"] * PRIZE_PERCENTAGES[position - 1])

        driver["points"] += points_earned
        driver["earnings"] += prize_money

        team = get_team(driver["team"])
        team["budget"] += prize_money

        print(
            f"{position}. {driver['name']} "
            f"({driver['team']}) "
            f"- Score: {result['score']} "
            f"- {points_earned} pts "
            f"- ${prize_money:,}"
        )


def display_driver_standings():
    standings = sorted(
        drivers,
        key=lambda driver: driver["points"],
        reverse=True,
    )

    print("\nFinal Driver Standings")
    print("-" * 55)

    for position, driver in enumerate(standings, start=1):
        print(
            f"{position}. {driver['name']} "
            f"({driver['team']}) "
            f"- {driver['points']} pts "
            f"- ${driver['earnings']:,}"
        )


def display_team_finances():
    standings = sorted(
        teams,
        key=lambda team: team["budget"],
        reverse=True,
    )

    print("\nFinal Team Finances")
    print("-" * 55)

    for team in standings:
        print(f"{team['name']}: ${team['budget']:,}")


def initialize_season():
    for driver in drivers:
        driver["points"] = 0
        driver["earnings"] = 0


def run_season():
    initialize_season()

    for race_number, track in enumerate(tracks, start=1):
        run_race(track, race_number)

    display_driver_standings()
    display_team_finances()


if __name__ == "__main__":
    run_season()
