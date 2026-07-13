import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from season_data import drivers, teams, tracks


POINTS_BY_POSITION = [40, 35, 32, 30, 28, 26]
PRIZE_PERCENTAGES = [0.30, 0.22, 0.17, 0.13, 0.10, 0.08]

league = {
    "integrity": 70,
    "fan_interest": 65,
    "controversy": 20,
    "fines_collected": 0,
}


def get_team(team_name):
    """Return the team matching the supplied team name."""

    for team in teams:
        if team["name"] == team_name:
            return team

    raise ValueError(f"Team not found: {team_name}")


def clamp(value, minimum=0, maximum=100):
    """Keep a numerical rating inside the allowed range."""

    return max(minimum, min(value, maximum))


def calculate_crash_chance(driver, track):
    """Calculate a driver's likelihood of crashing."""

    aggression_effect = driver["aggression"] // 10
    consistency_effect = driver["consistency"] // 15

    crash_chance = (
        track["incident_risk"]
        + aggression_effect
        - consistency_effect
    )

    return clamp(crash_chance, 3, 40)


def check_for_crash(driver, track):
    """Return True if the driver crashes."""

    crash_chance = calculate_crash_chance(driver, track)

    return random.randint(1, 100) <= crash_chance


def check_for_mechanical_failure(driver):
    """Return True if the car experiences a mechanical failure."""

    team = get_team(driver["team"])
    failure_chance = max(2, 100 - team["reliability"])

    return random.randint(1, 100) <= failure_chance


def calculate_race_score(driver):
    """Calculate the driver's performance score."""

    team = get_team(driver["team"])
    random_factor = random.randint(-25, 25)

    return (
        driver["speed"]
        + driver["consistency"]
        + team["car_rating"]
        + team["crew_rating"]
        + random_factor
    )


def determine_crash_cause(driver):
    """
    Determine whether a crash appears accidental or potentially reckless.

    Aggressive drivers are more likely to trigger a reviewable incident.
    """

    reckless_chance = clamp(driver["aggression"] - 35, 10, 65)

    if random.randint(1, 100) <= reckless_chance:
        return "Reckless Driving"

    return "Racing Incident"


def determine_driver_result(driver, track):
    """Determine whether a driver finishes, crashes, or has a failure."""

    if check_for_crash(driver, track):
        crash_cause = determine_crash_cause(driver)

        return {
            "driver": driver,
            "status": "Crash",
            "cause": crash_cause,
            "score": random.randint(1, 50),
        }

    if check_for_mechanical_failure(driver):
        return {
            "driver": driver,
            "status": "Mechanical Failure",
            "cause": None,
            "score": random.randint(51, 100),
        }

    return {
        "driver": driver,
        "status": "Running",
        "cause": None,
        "score": calculate_race_score(driver),
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
    """Return drivers who are eligible to compete in the current race."""

    return [
        driver
        for driver in drivers
        if driver["suspension_races"] == 0
    ]


def run_race(track, race_number):
    """Run one race and update season statistics."""

    results = []
    active_drivers = get_active_drivers()

    print(f"\n{'=' * 75}")
    print(f"Race {race_number}: {track['name']}")
    print(f"Track type: {track['type']}")
    print(f"Incident risk: {track['incident_risk']}%")
    print(f"Purse: ${track['purse']:,}")
    print("=" * 75)

    suspended_drivers = [
        driver
        for driver in drivers
        if driver["suspension_races"] > 0
    ]

    if suspended_drivers:
        print("\nSuspended from this race:")

        for driver in suspended_drivers:
            print(f"- {driver['name']} ({driver['team']})")

    for driver in active_drivers:
        result = determine_driver_result(driver, track)
        results.append(result)

    results = sort_race_results(results)

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
    review_race_incidents(results)

    for driver in suspended_drivers:
        driver["suspension_races"] -= 1

    display_league_dashboard()


def display_incident_report(results):
    """Display crashes and mechanical failures."""

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

        if incident["status"] == "Crash":
            print(
                f"{driver['name']}: Crash "
                f"— Initial finding: {incident['cause']}"
            )
        else:
            print(f"{driver['name']}: Mechanical Failure")


def review_race_incidents(results):
    """Allow the commissioner to review potentially reckless crashes."""

    reviewable_incidents = [
        result
        for result in results
        if (
            result["status"] == "Crash"
            and result["cause"] == "Reckless Driving"
        )
    ]

    if not reviewable_incidents:
        print("\nCommissioner Review")
        print("-" * 75)
        print("No incidents require commissioner action.")
        return

    print("\nCommissioner Review")
    print("-" * 75)

    for incident in reviewable_incidents:
        review_single_incident(incident)


def review_single_incident(incident):
    """Present disciplinary options for one incident."""

    driver = incident["driver"]
    team = get_team(driver["team"])

    print(
        f"\nRace control has referred {driver['name']} "
        f"of {driver['team']} for possible reckless driving."
    )

    print(f"Driver aggression rating: {driver['aggression']}")
    print(f"Current morale: {driver['morale']}")
    print(f"Current championship points: {driver['points']}")
    print(f"Team budget: ${team['budget']:,}")

    print("\nChoose a ruling:")
    print("1. No action")
    print("2. Official warning")
    print("3. $50,000 fine")
    print("4. Deduct 10 championship points")
    print("5. Suspend for the next race")

    choice = get_valid_choice()

    apply_commissioner_ruling(choice, driver, team)


def get_valid_choice():
    """Ask the player for a valid disciplinary choice."""

    while True:
        choice = input("\nCommissioner decision (1-5): ").strip()

        if choice in {"1", "2", "3", "4", "5"}:
            return choice

        print("Please enter a number from 1 through 5.")


def apply_commissioner_ruling(choice, driver, team):
    """Apply the selected commissioner ruling."""

    if choice == "1":
        league["integrity"] -= 4
        league["fan_interest"] += 2
        league["controversy"] += 8
        driver["morale"] += 3

        decision = "No action taken"

    elif choice == "2":
        league["integrity"] += 1
        league["controversy"] += 2
        driver["warnings"] += 1
        driver["morale"] -= 1

        decision = "Official warning issued"

    elif choice == "3":
        fine_amount = 50_000

        team["budget"] -= fine_amount
        league["fines_collected"] += fine_amount
        league["integrity"] += 3
        league["controversy"] += 1
        driver["fines"] += fine_amount
        driver["morale"] -= 4

        decision = f"${fine_amount:,} fine issued"

    elif choice == "4":
        points_penalty = 10

        driver["points"] = max(0, driver["points"] - points_penalty)
        league["integrity"] += 5
        league["fan_interest"] -= 1
        driver["points_penalties"] += points_penalty
        driver["morale"] -= 6

        decision = f"{points_penalty}-point penalty issued"

    else:
        driver["suspension_races"] = 1
        driver["suspensions"] += 1
        driver["morale"] -= 10
        league["integrity"] += 7
        league["fan_interest"] -= 3
        league["controversy"] += 5

        decision = "Driver suspended for the next race"

    league["integrity"] = clamp(league["integrity"])
    league["fan_interest"] = clamp(league["fan_interest"])
    league["controversy"] = clamp(league["controversy"])
    driver["morale"] = clamp(driver["morale"])

    print(f"\nRuling: {decision}")
    print(f"{driver['name']} morale: {driver['morale']}")
    print(f"League integrity: {league['integrity']}")
    print(f"Fan interest: {league['fan_interest']}")
    print(f"Controversy: {league['controversy']}")


def display_league_dashboard():
    """Display the league's current health after each race."""

    print("\nLeague Dashboard")
    print("-" * 75)
    print(f"Integrity: {league['integrity']}/100")
    print(f"Fan interest: {league['fan_interest']}/100")
    print(f"Controversy: {league['controversy']}/100")
    print(f"Fines collected: ${league['fines_collected']:,}")


def display_driver_standings():
    """Display the final driver championship standings."""

    standings = sorted(
        drivers,
        key=lambda driver: driver["points"],
        reverse=True,
    )

    print("\nFinal Driver Standings")
    print("-" * 90)

    for position, driver in enumerate(standings, start=1):
        print(
            f"{position}. {driver['name']} "
            f"({driver['team']}) "
            f"- {driver['points']} pts "
            f"- {driver['wins']} wins "
            f"- {driver['dnfs']} DNFs "
            f"- {driver['suspensions']} suspensions "
            f"- Morale: {driver['morale']} "
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


def display_commissioner_report():
    """Display the commissioner's end-of-season performance."""

    print("\nCommissioner Season Report")
    print("-" * 75)
    print(f"League integrity: {league['integrity']}/100")
    print(f"Fan interest: {league['fan_interest']}/100")
    print(f"Controversy: {league['controversy']}/100")
    print(f"Fines collected: ${league['fines_collected']:,}")

    if league["integrity"] >= 80:
        rating = "Highly Respected Commissioner"
    elif league["integrity"] >= 60:
        rating = "Effective Commissioner"
    elif league["integrity"] >= 40:
        rating = "Controversial Commissioner"
    else:
        rating = "Commissioner Under Pressure"

    print(f"Performance rating: {rating}")


def initialize_season():
    """Reset driver and league season statistics."""

    for driver in drivers:
        driver["points"] = 0
        driver["earnings"] = 0
        driver["starts"] = 0
        driver["finishes"] = 0
        driver["wins"] = 0
        driver["dnfs"] = 0
        driver["morale"] = 70
        driver["warnings"] = 0
        driver["fines"] = 0
        driver["points_penalties"] = 0
        driver["suspensions"] = 0
        driver["suspension_races"] = 0


def run_season():
    """Run the complete racing season."""

    initialize_season()

    for race_number, track in enumerate(tracks, start=1):
        run_race(track, race_number)

    display_driver_standings()
    display_team_finances()
    display_commissioner_report()


if __name__ == "__main__":
    run_season()
