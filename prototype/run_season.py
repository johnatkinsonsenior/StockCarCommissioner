import json
from datetime import datetime
from pathlib import Path

from data import drivers, teams, tracks
from game.race import (
    POINTS_BY_POSITION,
    PRIZE_PERCENTAGES,
    clamp,
    determine_driver_result,
    get_active_drivers,
    get_driver,
    get_team,
    sort_race_results,
)

PERSONALITY_REACTIONS = {
    "Professional": {
        "1": -4,
        "2": 1,
        "3": 2,
        "4": 3,
        "5": 1,
    },
    "Veteran": {
        "1": -1,
        "2": 2,
        "3": 1,
        "4": 0,
        "5": -3,
    },
    "Temperamental": {
        "1": 4,
        "2": -2,
        "3": -6,
        "4": -8,
        "5": -12,
    },
    "Rookie": {
        "1": 2,
        "2": 0,
        "3": -3,
        "4": -5,
        "5": -7,
    },
    "Aggressive": {
        "1": 5,
        "2": 1,
        "3": -3,
        "4": -6,
        "5": -10,
    },
    "Popular": {
        "1": 3,
        "2": 1,
        "3": -4,
        "4": -5,
        "5": -8,
    },
}

league = {
    "integrity": 70,
    "fan_interest": 65,
    "controversy": 20,
    "fines_collected": 0,
}

race_history = []
career_history = []
current_season = 1
championship_awarded = False


def serve_suspensions():
    """Reduce active suspension lengths."""

    for driver in drivers:
        if driver.suspension_races > 0:
            driver.suspension_races -= 1


def record_race_history(track, race_number, results):
    """Save the results of a completed race."""

    race_record = {
        "race_number": race_number,
        "track": track["name"],
        "track_type": track["type"],
        "results": [],
    }

    for position, result in enumerate(results, start=1):
        driver = result["driver"]

        race_record["results"].append(
            {
                "position": position,
                "driver": driver.name,
                "team": driver.team_name,
                "status": result["status"],
                "cause": result["cause"],
            }
        )

    race_history.append(race_record)


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
        if driver.is_suspended()
    ]

    if suspended_drivers:
        print("\nSuspended from this race:")

        for driver in suspended_drivers:
            print(f"- {driver.name} ({driver.team_name})")

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

        driver.add_points(points_earned)
        driver.add_earnings(prize_money)
        driver.starts += 1

        team = get_team(driver.team_name)
        team.add_prize_money(prize_money)

        if status == "Running":
            driver.finishes += 1

            if position == 1:
                driver.wins += 1
                driver.popularity = clamp(driver.popularity + 4)

                winning_team = get_team(driver.team_name)
                winning_team.record_win()
            elif position <= 3:
                driver.popularity = clamp(driver.popularity + 2)

            status_display = "Finished"

        else:
            driver.dnfs += 1

            if status == "Crash":
                driver.popularity = clamp(driver.popularity + 1)
            else:
                driver.popularity = clamp(driver.popularity - 1)

            status_display = f"DNF: {status}"

        print(
            f"{position}. {driver.name} "
            f"({driver.team_name}) "
            f"- {status_display} "
            f"- {points_earned} pts "
            f"- ${prize_money:,}"
        )

    display_incident_report(results)
    review_race_incidents(results)
    record_race_history(track, race_number, results)
    serve_suspensions()
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
                f"{driver.name}: Crash "
                f"— Initial finding: {incident['cause']}"
            )
        else:
            print(f"{driver.name}: Mechanical Failure")


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
    team = get_team(driver.team_name)

    print(
        f"\nRace control has referred {driver.name} "
        f"of {driver.team_name} for possible reckless driving."
    )

    print(f"Personality: {driver.personality}")
    print(f"Known rival: {driver.rival}")
    print(f"Driver aggression rating: {driver.aggression}")
    print(f"Current morale: {driver.morale}")
    print(f"Commissioner trust: {driver.commissioner_trust}")
    print(f"Current championship points: {driver.points}")
    print(f"Team budget: ${team.budget:,}")

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


def apply_personality_reaction(choice, driver):
    """Change commissioner trust based on the driver's personality."""

    personality = driver.personality
    reaction_table = PERSONALITY_REACTIONS.get(personality, {})
    trust_change = reaction_table.get(choice, 0)

    driver.commissioner_trust = clamp(
        driver.commissioner_trust + trust_change
    )

    if trust_change > 0:
        reaction = "responded positively"
    elif trust_change < 0:
        reaction = "responded negatively"
    else:
        reaction = "had a neutral reaction"

    print(
        f"{driver.name} ({personality}) {reaction}. "
        f"Commissioner trust changed by {trust_change:+d}."
    )


def apply_rival_reaction(choice, penalized_driver):
    """Allow a rival to react to the commissioner's ruling."""

    rival_name = penalized_driver.rival

    if not rival_name:
        return

    rival = get_driver(rival_name)

    severe_decisions = {"3", "4", "5"}
    lenient_decisions = {"1", "2"}

    if choice in severe_decisions:
        trust_change = 3
        morale_change = 2
        reaction = "approved of the punishment"
    elif choice in lenient_decisions:
        trust_change = -2
        morale_change = -1
        reaction = "believed the punishment was too lenient"
    else:
        trust_change = 0
        morale_change = 0
        reaction = "had no reaction"

    rival.commissioner_trust = clamp(
        rival.commissioner_trust + trust_change
    )

    rival.morale = clamp(
        rival.morale + morale_change
    )

    print(
        f"{rival.name}, a rival of {penalized_driver.name}, "
        f"{reaction}."
    )

    print(
        f"{rival.name} commissioner trust: "
        f"{rival.commissioner_trust}"
    )


def apply_commissioner_ruling(choice, driver, team):
    """Apply the selected commissioner ruling."""

    if choice == "1":
        league["integrity"] -= 4
        league["fan_interest"] += 2
        league["controversy"] += 8

        decision = "No action taken"

    elif choice == "2":
        league["integrity"] += 1
        league["controversy"] += 2
        driver.warnings += 1

        decision = "Official warning issued"

    elif choice == "3":
        fine_amount = 50_000

        team.pay_fine(fine_amount)
        league["fines_collected"] += fine_amount
        league["integrity"] += 3
        league["controversy"] += 1
        driver.fines += fine_amount

        decision = f"${fine_amount:,} fine issued"

    elif choice == "4":
        points_penalty = 10

        driver.deduct_points(points_penalty)
        league["integrity"] += 5
        league["fan_interest"] -= 1

        decision = f"{points_penalty}-point penalty issued"

    else:
        driver.suspension_races = 2
        driver.suspensions += 1
        driver.morale -= 10
        league["integrity"] += 7
        league["fan_interest"] -= 3
        league["controversy"] += 5

        decision = "Driver suspended for the next race"

    apply_personality_reaction(choice, driver)
    apply_rival_reaction(choice, driver)

    league["integrity"] = clamp(league["integrity"])
    league["fan_interest"] = clamp(league["fan_interest"])
    league["controversy"] = clamp(league["controversy"])
    driver.morale = clamp(driver.morale)

    print(f"\nRuling: {decision}")
    print(f"League integrity: {league['integrity']}")
    print(f"Fan interest: {league['fan_interest']}")
    print(f"Controversy: {league['controversy']}")
    print(f"{driver.name} morale: {driver.morale}")


def display_league_dashboard():
    """Display the league's current health after each race."""

    print("\nLeague Dashboard")
    print("-" * 75)
    print(f"Integrity: {league['integrity']}/100")
    print(f"Fan interest: {league['fan_interest']}/100")
    print(f"Controversy: {league['controversy']}/100")
    print(f"Fines collected: ${league['fines_collected']:,}")


def get_driver_standings():
    """Return drivers ranked by points and race victories."""

    return sorted(
        drivers,
        key=lambda driver: (
            driver.points,
            driver.wins,
        ),
        reverse=True,
    )


def display_driver_standings():
    """Display the final driver championship standings."""

    standings = get_driver_standings()

    print("\nFinal Driver Standings")
    print("-" * 90)

    for position, driver in enumerate(standings, start=1):
        print(
            f"{position}. {driver.name} "
            f"({driver.team_name}) "
            f"- {driver.points} pts "
            f"- {driver.wins} wins "
            f"- {driver.dnfs} DNFs "
            f"- {driver.suspensions} suspensions "
            f"- Morale: {driver.morale} "
            f"- Trust: {driver.commissioner_trust} "
            f"- ${driver.earnings:,}"
        )


def display_team_finances():
    """Display team budgets after the season."""

    financial_ranking = sorted(
        teams,
        key=lambda team: team.budget,
        reverse=True,
    )

    print("\nFinal Team Finances")
    print("-" * 75)

    for team in financial_ranking:
        print(
            f"{team.name} "
            f"- Budget: ${team.budget:,} "
            f"- Reliability: {team.reliability}"
        )


def get_driver_champion():
    return get_driver_standings()[0]


def get_most_wins_driver():
    return max(
        drivers,
        key=lambda driver: (
            driver.wins,
            driver.points,
        ),
    )


def get_most_popular_driver():
    return max(
        drivers,
        key=lambda driver: driver.popularity,
    )


def get_most_reliable_team():
    return max(
        teams,
        key=lambda team: team.reliability,
    )


def calculate_commissioner_grade():
    """Calculate an overall commissioner performance grade."""

    score = (
        league["integrity"] * 0.45
        + league["fan_interest"] * 0.35
        + (100 - league["controversy"]) * 0.20
    )

    if score >= 90:
        grade = "A+"
    elif score >= 85:
        grade = "A"
    elif score >= 80:
        grade = "A-"
    elif score >= 75:
        grade = "B+"
    elif score >= 70:
        grade = "B"
    elif score >= 65:
        grade = "B-"
    elif score >= 60:
        grade = "C"
    elif score >= 50:
        grade = "D"
    else:
        grade = "F"

    return round(score, 1), grade


def display_driver_relationship_report():
    """Display each driver's relationship with the commissioner."""

    relationship_ranking = sorted(
        drivers,
        key=lambda driver: driver.commissioner_trust,
        reverse=True,
    )

    print("\nDriver Relationship Report")
    print("-" * 90)

    for driver in relationship_ranking:
        trust = driver.commissioner_trust

        if trust >= 80:
            relationship = "Strong Supporter"
        elif trust >= 65:
            relationship = "Supportive"
        elif trust >= 50:
            relationship = "Neutral"
        elif trust >= 35:
            relationship = "Distrustful"
        else:
            relationship = "Openly Hostile"

        print(
            f"{driver.name} "
            f"({driver.personality}) "
            f"- Trust: {trust}/100 "
            f"- {relationship} "
            f"- Rival: {driver.rival}"
        )


def display_race_history():
    """Display the winner and incidents from every race."""

    print("\nSeason Race History")
    print("-" * 90)

    for race in race_history:
        winner = race["results"][0]

        incidents = [
            result
            for result in race["results"]
            if result["status"] != "Running"
        ]

        print(
            f"Race {race['race_number']}: {race['track']} "
            f"- Winner: {winner['driver']} "
            f"({winner['team']}) "
            f"- Incidents: {len(incidents)}"
        )


def display_season_awards():
    """Display championship and end-of-season awards."""

    champion = get_driver_champion()
    most_wins = get_most_wins_driver()
    most_popular = get_most_popular_driver()
    reliable_team = get_most_reliable_team()
    commissioner_score, commissioner_grade = calculate_commissioner_grade()

    print("\nSeason Awards")
    print("-" * 90)

    print(
        f"Series Champion: {champion.name} "
        f"({champion.team_name}) "
        f"- {champion.points} points"
    )

    print(
        f"Most Race Wins: {most_wins.name} "
        f"- {most_wins.wins} wins"
    )

    print(
        f"Most Popular Driver: {most_popular.name} "
        f"- Popularity {most_popular.popularity}/100"
    )

    print(
        f"Reliability Award: {reliable_team.name} "
        f"- Reliability {reliable_team.reliability}/100"
    )

    print(
        f"Commissioner Grade: {commissioner_grade} "
        f"({commissioner_score}/100)"
    )


def display_commissioner_report():
    """Display the commissioner's end-of-season performance."""

    print("\nCommissioner Season Report")
    print("-" * 75)
    print(f"League integrity: {league['integrity']}/100")
    print(f"Fan interest: {league['fan_interest']}/100")
    print(f"Controversy: {league['controversy']}/100")
    print(f"Fines collected: ${league['fines_collected']:,}")


def save_season_report(season_number):
    """Save the completed season to a JSON file."""

    champion = get_driver_champion()
    most_wins = get_most_wins_driver()
    most_popular = get_most_popular_driver()
    reliable_team = get_most_reliable_team()
    commissioner_score, commissioner_grade = calculate_commissioner_grade()

    report = {
        "game": "Stock Car Commissioner",
        "version": "0.0.2",
        "season": season_number,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "league": {
            "integrity": league["integrity"],
            "fan_interest": league["fan_interest"],
            "controversy": league["controversy"],
            "fines_collected": league["fines_collected"],
        },
        "commissioner": {
            "score": commissioner_score,
            "grade": commissioner_grade,
        },
        "awards": {
            "champion": champion.name,
            "champion_team": champion.team_name,
            "champion_points": champion.points,
            "most_wins_driver": most_wins.name,
            "most_wins": most_wins.wins,
            "most_popular_driver": most_popular.name,
            "most_popular_rating": most_popular.popularity,
            "most_reliable_team": reliable_team.name,
            "most_reliable_team_rating": reliable_team.reliability,
        },
        "driver_standings": [],
        "team_finances": [],
        "race_history": list(race_history),
    }

    standings = get_driver_standings()

    for position, driver in enumerate(standings, start=1):
        report["driver_standings"].append(
            {
                "position": position,
                "name": driver.name,
                "team": driver.team_name,
                "points": driver.points,
                "wins": driver.wins,
                "dnfs": driver.dnfs,
                "earnings": driver.earnings,
                "morale": driver.morale,
                "popularity": driver.popularity,
                "commissioner_trust": driver.commissioner_trust,
                "warnings": driver.warnings,
                "fines": driver.fines,
                "points_penalties": driver.points_penalties,
                "suspensions": driver.suspensions,
                "career_starts": driver.career_starts + driver.starts,
                "career_wins": driver.career_wins + driver.wins,
                "career_points": driver.career_points + driver.points,
                "career_earnings": driver.career_earnings + driver.earnings,
                "championships": driver.championships,
            }
        )

    for team in teams:
        report["team_finances"].append(
            {
                "name": team.name,
                "budget": team.budget,
                "reliability": team.reliability,
                "car_rating": team.car_rating,
                "crew_rating": team.crew_rating,
            }
        )

    project_root = Path(__file__).resolve().parent.parent
    report_folder = project_root / "season_reports"
    report_folder.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    report_path = (
        report_folder
        / f"season_{season_number}_report_{timestamp}.json"
    )

    with report_path.open("w", encoding="utf-8") as report_file:
        json.dump(report, report_file, indent=4)

    print("\nSeason report saved:")
    print(report_path)


def initialize_season(season_number):
    """Prepare league, drivers, teams, and history for a new season."""

    global championship_awarded

    race_history.clear()
    championship_awarded = False

    league["integrity"] = 70
    league["fan_interest"] = 65
    league["controversy"] = 20
    league["fines_collected"] = 0

    for team in teams:
        team.start_new_season()

    for driver in drivers:
        driver.reset_season()

        # Small recovery between seasons
        driver.morale = clamp(driver.morale + 5)

    print("\n" + "=" * 90)
    print(f"STOCK CAR COMMISSIONER — SEASON {season_number}")
    print("=" * 90)


def award_championship():
    """Award the season championship to the top driver and team."""

    global championship_awarded

    champion = get_driver_champion()

    if championship_awarded:
        return champion

    championship_awarded = True
    champion_team = get_team(champion.team_name)

    champion.record_championship()
    champion_team.record_championship()

    print("\nChampionship Awarded")
    print("-" * 90)
    print(
        f"{champion.name} wins the championship "
        f"for {champion.team_name}."
    )

    print(
        f"Career championships: {champion.championships}"
    )

    return champion


def record_completed_season(season_number, champion):
    """Store a permanent summary of a completed season."""

    commissioner_score, commissioner_grade = calculate_commissioner_grade()
    standings = get_driver_standings()

    season_record = {
        "season": season_number,
        "champion": champion.name,
        "champion_team": champion.team_name,
        "champion_points": champion.points,
        "champion_wins": champion.wins,
        "commissioner_score": commissioner_score,
        "commissioner_grade": commissioner_grade,
        "league_integrity": league["integrity"],
        "fan_interest": league["fan_interest"],
        "controversy": league["controversy"],
        "standings": [],
        "race_history": list(race_history),
    }

    for position, driver in enumerate(standings, start=1):
        season_record["standings"].append(
            {
                "position": position,
                "driver": driver.name,
                "team": driver.team_name,
                "points": driver.points,
                "wins": driver.wins,
                "dnfs": driver.dnfs,
                "earnings": driver.earnings,
            }
        )

    career_history.append(season_record)


def finalize_driver_career_totals():
    """Move current season results into driver career statistics."""

    for driver in drivers:
        driver.complete_season()


def run_single_season(season_number):
    """Run one complete championship season."""

    initialize_season(season_number)

    for race_number, track in enumerate(tracks, start=1):
        run_race(track, race_number)

    display_driver_standings()
    display_team_finances()
    display_commissioner_report()
    display_driver_relationship_report()
    display_race_history()
    display_season_awards()

    champion = award_championship()

    record_completed_season(
        season_number,
        champion,
    )

    save_season_report(season_number)
    finalize_driver_career_totals()


def display_career_report():
    """Display career statistics after all seasons are completed."""

    print("\n" + "=" * 100)
    print("CAREER REPORT")
    print("=" * 100)

    print("\nChampionship History")
    print("-" * 100)

    for season in career_history:
        print(
            f"Season {season['season']}: "
            f"{season['champion']} "
            f"({season['champion_team']}) "
            f"- {season['champion_points']} points "
            f"- {season['champion_wins']} wins"
        )

    career_ranking = sorted(
        drivers,
        key=lambda driver: (
            driver.championships,
            driver.career_wins,
            driver.career_points,
        ),
        reverse=True,
    )

    print("\nDriver Career Statistics")
    print("-" * 100)

    for driver in career_ranking:
        print(
            f"{driver.name} "
            f"({driver.team_name}) "
            f"- Championships: {driver.championships} "
            f"- Wins: {driver.career_wins} "
            f"- Starts: {driver.career_starts} "
            f"- DNFs: {driver.career_dnfs} "
            f"- Points: {driver.career_points} "
            f"- Earnings: ${driver.career_earnings:,}"
        )

    team_ranking = sorted(
        teams,
        key=lambda team: (
            team.championships,
            team.career_wins,
        ),
        reverse=True,
    )

    print("\nTeam Career Statistics")
    print("-" * 100)

    for team in team_ranking:
        print(
            f"{team.name} "
            f"- Championships: {team.championships} "
            f"- Wins: {team.career_wins} "
            f"- Career prize money: ${team.career_prize_money:,} "
            f"- Current budget: ${team.budget:,}"
        )


def run_career(number_of_seasons=3):
    """Run several consecutive seasons."""

    career_history.clear()

    for season_number in range(1, number_of_seasons + 1):
        run_single_season(season_number)

        if season_number < number_of_seasons:
            input(
                "\nPress Enter to begin the next season..."
            )

    display_career_report()


def run_season():
    """Run the complete racing season."""

    global current_season

    run_single_season(current_season)
    current_season += 1


if __name__ == "__main__":
    run_career(number_of_seasons=3)
