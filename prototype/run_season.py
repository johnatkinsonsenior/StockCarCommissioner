import json
import random
from datetime import datetime
from pathlib import Path

from data import (
    create_initial_drivers,
    create_initial_teams,
    create_initial_tracks,
    drivers,
    teams,
    tracks,
)
from game.calendar import (
    LeagueCalendar,
    OFFSEASON,
    POSTSEASON,
    PRESEASON,
    REGULAR_SEASON,
)
from game.event_catalog import (
    offseason_events,
    postseason_events,
    preseason_events,
    regular_season_events,
)
from game.events import resolve_event_choice
from game.models import Driver, Team
from game.policies import (
    current_policies,
    get_penalty_fine_amount,
    get_penalty_points_amount,
    get_points_by_position,
    get_policy_operating_cost,
    load_policies,
    policy_label,
    reset_policies,
)
from game.save_game import (
    build_save_data,
    get_saves_folder,
    list_save_files,
    load_from_file,
    save_to_file,
)
from game.race import (
    PART_LABELS,
    PRIZE_PERCENTAGES,
    clamp,
    get_driver,
    get_team,
    simulate_race_weekend,
    tire_load,
    weather_label,
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

ROOKIE_FIRST_NAMES = [
    "Evan",
    "Logan",
    "Caleb",
    "Noah",
    "Carter",
    "Blake",
    "Trevor",
    "Jordan",
    "Cameron",
    "Wyatt",
]

ROOKIE_LAST_NAMES = [
    "Hayes",
    "Mercer",
    "Dawson",
    "Bishop",
    "Carver",
    "Stone",
    "Ramsey",
    "Foster",
    "Barrett",
    "Wheeler",
]

ROOKIE_PERSONALITIES = [
    "Professional",
    "Temperamental",
    "Rookie",
    "Aggressive",
    "Popular",
]

league = {
    "integrity": 70,
    "fan_interest": 65,
    "controversy": 20,
    "fines_collected": 0,
    "owner_pressure": 25,
    "driver_sentiment": 60,
}

race_history = []
career_history = []
retired_drivers = []
decision_log = []
events_resolved = []

current_season = 1
championship_awarded = False
career_seasons_total = 3
season_in_progress = False
calendar = LeagueCalendar()

BASE_OPERATING_EXPENSE = 350_000
FACILITY_MAINTENANCE_PER_LEVEL = 75_000
BASE_SPONSORSHIP = 800_000
PERFORMANCE_INVESTMENT_UNIT = 250_000


def sync_calendar_aliases():
    """Keep Day 14 season fields aligned with the league calendar."""

    global current_season, career_seasons_total, season_in_progress

    current_season = calendar.current_season
    career_seasons_total = calendar.career_seasons_total
    season_in_progress = calendar.season_in_progress()


def display_calendar_banner():
    """Display the current league calendar phase."""

    print("\n" + "-" * 90)
    print(f"LEAGUE CALENDAR — {calendar.description()}")
    print("-" * 90)


def reset_career_state():
    """Restore league data for a brand-new career."""

    global championship_awarded

    race_history.clear()
    career_history.clear()
    retired_drivers.clear()
    decision_log.clear()
    events_resolved.clear()

    drivers.clear()
    drivers.extend(create_initial_drivers())

    teams.clear()
    teams.extend(create_initial_teams())

    tracks.clear()
    tracks.extend(create_initial_tracks())

    league["integrity"] = 70
    league["fan_interest"] = 65
    league["controversy"] = 20
    league["fines_collected"] = 0
    league["owner_pressure"] = 25
    league["driver_sentiment"] = 60

    reset_policies()

    championship_awarded = False
    calendar.current_season = 1
    calendar.career_seasons_total = 3
    calendar.enter_preseason()
    sync_calendar_aliases()


def is_season_mid_progress():
    """Return whether the active season still has races remaining."""

    return (
        calendar.phase == REGULAR_SEASON
        and len(race_history) < len(tracks)
    )


def apply_loaded_state(restored_state):
    """Replace live game state with data from a save file."""

    global championship_awarded

    race_history.clear()
    race_history.extend(restored_state["race_history"])

    career_history.clear()
    career_history.extend(restored_state["career_history"])

    retired_drivers.clear()
    retired_drivers.extend(restored_state["retired_drivers"])

    decision_log.clear()
    decision_log.extend(restored_state.get("decision_log") or [])

    events_resolved.clear()
    events_resolved.extend(restored_state.get("events_resolved") or [])

    drivers.clear()
    drivers.extend(restored_state["drivers"])

    teams.clear()
    teams.extend(restored_state["teams"])

    if restored_state.get("tracks"):
        tracks.clear()
        tracks.extend(restored_state["tracks"])

    league.clear()
    league.update(restored_state["league"])
    league.setdefault("owner_pressure", 25)
    league.setdefault("driver_sentiment", 60)

    load_policies(restored_state.get("policies"))

    championship_awarded = restored_state["championship_awarded"]

    restored_calendar = LeagueCalendar.from_save_data(
        restored_state,
        track_count=len(tracks),
    )
    calendar.current_season = restored_calendar.current_season
    calendar.career_seasons_total = restored_calendar.career_seasons_total
    calendar.phase = restored_calendar.phase
    sync_calendar_aliases()


def save_career(save_name=None):
    """Save the current career progress to disk."""

    sync_calendar_aliases()

    save_data = build_save_data(
        league=league,
        race_history=race_history,
        career_history=career_history,
        retired_drivers=retired_drivers,
        drivers=drivers,
        teams=teams,
        current_season=calendar.current_season,
        championship_awarded=championship_awarded,
        career_seasons_total=calendar.career_seasons_total,
        season_in_progress=calendar.season_in_progress(),
        calendar_phase=calendar.phase,
        policies=current_policies,
        decision_log=decision_log,
        events_resolved=events_resolved,
        tracks=tracks,
    )

    save_path = save_to_file(save_data, save_name)

    print("\nCareer saved:")
    print(save_path)

    return save_path


def choose_save_file():
    """Prompt the player to choose a save file."""

    save_files = list_save_files()

    if not save_files:
        print("\nNo save files found in:")
        print(get_saves_folder())
        return None

    print("\nAvailable Saves")
    print("-" * 75)

    for index, save_path in enumerate(save_files, start=1):
        print(f"{index}. {save_path.name}")

    while True:
        choice = input(
            "\nChoose a save number (or press Enter to cancel): "
        ).strip()

        if not choice:
            return None

        if choice.isdigit():
            choice_index = int(choice)

            if 1 <= choice_index <= len(save_files):
                return save_files[choice_index - 1]

        print("Please enter a valid save number.")


def load_career(save_path=None):
    """Load a saved career from disk."""

    if save_path is None:
        save_path = choose_save_file()

    if save_path is None:
        return False

    restored_state = load_from_file(save_path)
    apply_loaded_state(restored_state)

    print("\nCareer loaded:")
    print(save_path)
    print(calendar.description())

    return True


def prompt_save_career():
    """Offer to save the current career progress."""

    choice = input("\nSave career progress? (y/n): ").strip().lower()

    if choice != "y":
        return

    save_name = input(
        "Save name (press Enter for timestamp): "
    ).strip()

    save_career(save_name or None)


def relationship_label(trust):
    """Return a short relationship label from commissioner trust."""

    if trust >= 80:
        return "Strong Supporter"
    if trust >= 65:
        return "Supportive"
    if trust >= 50:
        return "Neutral"
    if trust >= 35:
        return "Distrustful"

    return "Openly Hostile"


def collect_commissioner_alerts():
    """Build key alerts for the commissioner dashboard."""

    alerts = []

    if league["integrity"] < 55:
        alerts.append("League integrity is under pressure.")

    if league["fan_interest"] < 50:
        alerts.append("Fan interest is sliding.")

    if league["controversy"] >= 50:
        alerts.append("Controversy is running hot.")

    if league["owner_pressure"] >= 55:
        alerts.append("Owner pressure is elevated.")

    impatient_owners = [
        team
        for team in teams
        if team.owner.patience < 40 or team.owner.pressure >= 60
    ]

    if impatient_owners:
        names = ", ".join(
            f"{team.owner.name} ({team.name})"
            for team in impatient_owners
        )
        alerts.append(f"Impatient owners: {names}")

    if league["driver_sentiment"] < 45:
        alerts.append("Driver sentiment is poor.")

    struggling_teams = [
        team
        for team in teams
        if team.financial_distress_level >= 2
    ]

    if struggling_teams:
        names = ", ".join(
            f"{team.name} ({team.financial_status_label()})"
            for team in struggling_teams
        )
        alerts.append(f"Financial health: {names}")

    unhappy_drivers = [
        driver
        for driver in drivers
        if driver.morale < 40 or driver.commissioner_trust < 35
    ]

    if unhappy_drivers:
        names = ", ".join(driver.name for driver in unhappy_drivers)
        alerts.append(f"Relationship risk: {names}")

    hot_feuds = []
    seen_feuds = set()

    for driver in drivers:
        feud = driver.hottest_feud()

        if (
            feud
            and feud.get("status") == "active"
            and feud.get("intensity", 0) >= 70
        ):
            pair = tuple(sorted((driver.name, feud["opponent"])))

            if pair in seen_feuds:
                continue

            seen_feuds.add(pair)
            hot_feuds.append(
                f"{pair[0]}/{pair[1]} ({feud['intensity']})"
            )

    if hot_feuds:
        alerts.append("Hot feuds: " + ", ".join(hot_feuds[:3]))

    credibility_risks = [
        driver
        for driver in drivers
        if driver.credibility < 40
    ]

    if credibility_risks:
        names = ", ".join(driver.name for driver in credibility_risks)
        alerts.append(f"Credibility watch: {names}")

    return alerts


def display_league_dashboard():
    """Display league health, finances, relationships, and alerts."""

    score, grade = calculate_commissioner_grade()
    average_trust = round(
        sum(driver.commissioner_trust for driver in drivers) / len(drivers)
    )
    average_morale = round(
        sum(driver.morale for driver in drivers) / len(drivers)
    )
    lowest_trust = min(drivers, key=lambda driver: driver.commissioner_trust)
    richest_team = max(teams, key=lambda team: team.budget)
    poorest_team = min(teams, key=lambda team: team.budget)
    alerts = collect_commissioner_alerts()

    print("\nCommissioner Dashboard")
    print("-" * 90)
    print(calendar.description())
    print(
        f"Integrity {league['integrity']}/100 | "
        f"Fan interest {league['fan_interest']}/100 | "
        f"Controversy {league['controversy']}/100"
    )
    print(
        f"Owner pressure {league['owner_pressure']}/100 | "
        f"Driver sentiment {league['driver_sentiment']}/100 | "
        f"Grade {grade} ({score}/100)"
    )
    print(f"Fines collected: ${league['fines_collected']:,}")
    print(
        "Policies — "
        f"{policy_label('points_system')}; "
        f"{policy_label('race_format')}; "
        f"{policy_label('penalty_standard')}; "
        f"{policy_label('technical_rules')}; "
        f"{policy_label('safety_standard')}"
    )
    print(
        "Finances — "
        f"{richest_team.name} ${richest_team.budget:,} / "
        f"{poorest_team.name} ${poorest_team.budget:,}"
    )
    print(
        "Relationships — "
        f"avg trust {average_trust}, avg morale {average_morale}; "
        f"watch {lowest_trust.name} "
        f"({relationship_label(lowest_trust.commissioner_trust)})"
    )

    print("Locker room")

    for driver in drivers:
        rival_text = (
            f"{driver.rival} ({driver.rivalry_intensity})"
            if driver.rival
            else "none"
        )
        ally_text = driver.ally or "none"
        feud = driver.hottest_feud()
        feud_text = (
            f"{feud['opponent']} {feud['intensity']} {feud['status']}"
            if feud
            else "none"
        )
        print(
            f"- {driver.name}: {driver.happiness_label()} "
            f"{driver.morale} | "
            f"Rep {driver.reputation}/Cred {driver.credibility} | "
            f"Rival {rival_text} | Ally {ally_text} | "
            f"Teammate bond {driver.teammate_bond} | "
            f"Feud {feud_text}"
        )

    print("Organizations")

    for team in teams:
        owner = team.owner
        print(
            f"- {team.name}: {owner.description()} | "
            f"{team.financial_status_label()} | "
            f"Prestige {team.prestige} | "
            f"{team.performance_trend_label()} | "
            f"Shop {team.facility_rating()} "
            f"(Lv {team.facility_level}) | "
            f"Eng {team.engineering} | "
            f"Crew {team.crew_rating}"
        )

    next_index = len(race_history)

    if next_index < len(tracks):
        next_track = tracks[next_index]
        print(
            f"Next weekend: {next_track.name} ({next_track.type}) — "
            f"{next_track.description()} | purse ${next_track.purse:,}"
        )

    if race_history:
        last_race = race_history[-1]
        weather_text = last_race.get("weather")
        last_weather = (
            f"{weather_text}, {last_race.get('temperature')}°"
            if weather_text
            else "weather n/a"
        )
        last_cautions = last_race.get("cautions", 0) or 0
        yellow_word = "yellow" if last_cautions == 1 else "yellows"
        print(
            f"Last weekend: {last_race['track']} — {last_weather} | "
            f"{last_cautions} {yellow_word} | "
            f"pole {last_race.get('pole') or 'n/a'} | "
            f"{last_race.get('format', 'single-feature')}"
        )
        wrecks = last_race.get("wrecks") or []
        investigations = last_race.get("investigations") or []
        if wrecks:
            biggest = max(wrecks, key=lambda wreck: wreck.get("size", 0))
            print(
                f"Last wrecks: {len(wrecks)} "
                f"(biggest {biggest['size']}-car, "
                f"started by {biggest.get('initiator', 'n/a')})"
            )
        if investigations:
            packet = investigations[0]
            print(
                f"Last investigation: blame {packet.get('blame')} "
                f"({packet.get('confidence')} confidence)"
            )

    print("Alerts")

    if alerts:
        for alert in alerts:
            print(f"- {alert}")
    else:
        print("- No critical alerts.")


def build_event_context(event):
    """Attach live subjects to a decision event."""

    subject_driver = None
    subject_team = None
    subject_other_driver = None
    driver_name = event.get("subject_driver_name")
    team_name = event.get("subject_team_name")
    other_name = event.get("subject_other_driver_name")

    if driver_name:
        subject_driver = get_driver(driver_name)
        subject_team = get_team(subject_driver.team_name)

    if team_name:
        subject_team = get_team(team_name)

    if other_name:
        subject_other_driver = get_driver(other_name)

    return {
        "league": league,
        "policies": current_policies,
        "drivers": drivers,
        "teams": teams,
        "subject_driver": subject_driver,
        "subject_team": subject_team,
        "subject_other_driver": subject_other_driver,
        "season": calendar.current_season,
    }


def get_numbered_choice(choice_count):
    """Ask the player for a numbered choice."""

    valid = {str(number) for number in range(1, choice_count + 1)}

    while True:
        choice = input(
            f"\nCommissioner decision (1-{choice_count}): "
        ).strip()

        if choice in valid:
            return choice

        print(f"Please enter a number from 1 through {choice_count}.")


def present_decision_event(event):
    """Present one commissioner event and apply the chosen outcome."""

    if event["id"] in events_resolved:
        return None

    print("\n" + "=" * 90)
    print(f"COMMISSIONER DECISION — {event['title']}")
    print(f"Category: {event['category']}")
    print("=" * 90)
    print(event["prompt"])
    print()

    for choice in event["choices"]:
        print(f"{choice['id']}. {choice['label']}")

    choice_id = get_numbered_choice(len(event["choices"]))
    context = build_event_context(event)
    result = resolve_event_choice(event, choice_id, context)

    events_resolved.append(event["id"])
    decision_log.append(
        {
            "season": calendar.current_season,
            **result,
        }
    )

    print(f"\nDecision: {result['choice_label']}")
    print(f"Outcome: {result['outcome']}")
    print(
        f"Integrity {league['integrity']} | "
        f"Fans {league['fan_interest']} | "
        f"Controversy {league['controversy']} | "
        f"Owners {league['owner_pressure']} | "
        f"Drivers {league['driver_sentiment']}"
    )

    return result


def present_events(event_list):
    """Present each unresolved event in order."""

    for event in event_list:
        present_decision_event(event)


def generate_unique_rookie_name():
    """Generate a driver name that is not currently in use."""

    existing_names = {
        driver.name
        for driver in drivers
    }

    existing_names.update(
        driver.name
        for driver in retired_drivers
    )

    for _ in range(100):
        first_name = random.choice(ROOKIE_FIRST_NAMES)
        last_name = random.choice(ROOKIE_LAST_NAMES)
        name = f"{first_name} {last_name}"

        if name not in existing_names:
            return name

    raise RuntimeError("Unable to generate a unique rookie name.")


def generate_rookie(team_name):
    """Create a new rookie driver for an available team seat."""

    rookie = Driver(
        name=generate_unique_rookie_name(),
        team_name=team_name,
        age=random.randint(19, 23),
        speed=random.randint(66, 78),
        consistency=random.randint(64, 80),
        aggression=random.randint(55, 82),
        personality=random.choice(ROOKIE_PERSONALITIES),
        rival=None,
        popularity=random.randint(45, 65),
        salary=0,
        contract_years=random.randint(1, 3),
        is_rookie=True,
    )
    rookie.salary = rookie.calculate_market_value()

    return rookie


def assign_rookie_rival(rookie):
    """Assign an active driver as the rookie's first rival."""

    possible_rivals = [
        driver
        for driver in drivers
        if (
            driver.name != rookie.name
            and driver.team_name != rookie.team_name
        )
    ]

    if possible_rivals:
        rival = random.choice(possible_rivals)
        intensity = 35 + rookie.ambition // 10
        rookie.set_rival(rival.name, intensity)


def apply_driver_development(driver):
    """Apply age-based offseason improvement or decline."""

    old_speed = driver.speed
    old_consistency = driver.consistency
    old_aggression = driver.aggression

    if driver.age <= 23:
        speed_change = random.randint(1, 4)
        consistency_change = random.randint(1, 3)
        aggression_change = random.randint(-2, 1)

        development_stage = "Young Prospect Development"

    elif driver.age <= 29:
        speed_change = random.randint(0, 2)
        consistency_change = random.randint(0, 2)
        aggression_change = random.randint(-1, 1)

        development_stage = "Prime Development"

    elif driver.age <= 34:
        speed_change = random.randint(-1, 1)
        consistency_change = random.randint(0, 2)
        aggression_change = random.randint(-2, 0)

        development_stage = "Veteran Refinement"

    elif driver.age <= 38:
        speed_change = random.randint(-3, 0)
        consistency_change = random.randint(-1, 1)
        aggression_change = random.randint(-2, 0)

        development_stage = "Veteran Decline"

    else:
        speed_change = random.randint(-5, -1)
        consistency_change = random.randint(-3, 0)
        aggression_change = random.randint(-3, 0)

        development_stage = "Late-Career Decline"

    driver.speed = clamp(driver.speed + speed_change, 40, 99)
    driver.consistency = clamp(
        driver.consistency + consistency_change,
        40,
        99,
    )
    driver.aggression = clamp(
        driver.aggression + aggression_change,
        20,
        95,
    )

    return {
        "stage": development_stage,
        "speed_change": driver.speed - old_speed,
        "consistency_change": (
            driver.consistency - old_consistency
        ),
        "aggression_change": (
            driver.aggression - old_aggression
        ),
    }


def calculate_retirement_chance(driver):
    """Return a driver's retirement probability."""

    if driver.age < 35:
        chance = 0

    elif driver.age <= 37:
        chance = 5

    elif driver.age <= 39:
        chance = 15

    elif driver.age <= 41:
        chance = 30

    elif driver.age <= 43:
        chance = 50

    else:
        chance = 75

    if driver.championships > 0:
        chance += 5

    if driver.morale < 40:
        chance += 10

    if driver.commissioner_trust < 35:
        chance += 5

    return clamp(chance, 0, 95)


def should_driver_retire(driver):
    """Determine whether a driver retires during the offseason."""

    retirement_chance = calculate_retirement_chance(driver)
    retirement_roll = random.randint(1, 100)

    return retirement_roll <= retirement_chance


def clear_retired_rivalries(retired_driver_name):
    """Remove references to a driver who has retired."""

    for driver in drivers:
        driver.clear_relationship_with(retired_driver_name)


def retire_driver(driver):
    """Move a driver from the active roster to retirement history."""

    driver.is_retired = True
    retired_drivers.append(driver)

    drivers.remove(driver)
    clear_retired_rivalries(driver.name)

    print(
        f"{driver.name} has retired at age {driver.age}. "
        f"Career: {driver.career_wins} wins, "
        f"{driver.championships} championships."
    )


def replace_retired_driver(retired_driver):
    """Create a rookie to fill a retired driver's team seat."""

    rookie = generate_rookie(retired_driver.team_name)
    drivers.append(rookie)
    assign_rookie_rival(rookie)

    print(
        f"{rookie.name}, age {rookie.age}, joins "
        f"{rookie.team_name} as a rookie."
    )

    print(
        f"Ratings — Speed: {rookie.speed}, "
        f"Consistency: {rookie.consistency}, "
        f"Aggression: {rookie.aggression}, "
        f"ST {rookie.short_track}/RC {rookie.road_course}/"
        f"Int {rookie.intermediate}/SS {rookie.superspeedway}, "
        f"{rookie.personality}, "
        f"Rival: {rookie.rival or 'none'}"
    )

    return rookie


def get_team_drivers(team_name):
    """Return all active drivers on a team."""

    return [
        driver
        for driver in drivers
        if driver.team_name == team_name
    ]


def get_team_season_wins(team_name):
    """Return the number of race wins earned by a team this season."""

    return sum(
        driver.wins
        for driver in get_team_drivers(team_name)
    )


def refresh_driver_happiness(driver):
    """Update satisfaction components and blend them into morale."""

    team = get_team(driver.team_name)
    market = max(1, driver.calculate_market_value())
    ratio = driver.salary / market

    if driver.is_free_agent:
        contract = 40
    elif ratio >= 1.05:
        contract = 82
    elif ratio >= 0.90:
        contract = 68
    elif ratio >= 0.75:
        contract = 50
    else:
        contract = 35

    driver.contract_satisfaction = contract

    health_penalty = team.financial_distress_level * 8
    team_sat = round(
        team.prestige * 0.30
        + team.facility_rating() * 0.15
        + driver.teammate_bond * 0.40
        + 25
        - health_penalty
    )
    driver.team_satisfaction = clamp(team_sat)

    standings = get_driver_standings()
    position = 1

    for index, ranked in enumerate(standings, start=1):
        if ranked.name == driver.name:
            position = index
            break

    rank_frustration = (position - 1) * 8
    dnf_frustration = driver.dnfs * 6
    win_relief = driver.wins * 10
    ambition_heat = (position - 1) * 2 if driver.ambition >= 75 else 0

    driver.competitive_frustration = clamp(
        20 + rank_frustration + dnf_frustration + ambition_heat - win_relief
    )
    driver.sync_morale_from_happiness()


def refresh_all_driver_happiness():
    """Refresh happiness for every active driver."""

    for driver in drivers:
        refresh_driver_happiness(driver)


def update_paddock_after_race(results):
    """Escalate rivalries, bonds, reputation, and happiness after a race."""

    results_by_name = {
        result["driver"].name: result
        for result in results
    }

    for result in results:
        driver = result["driver"]

        if result["status"] != "Running":
            driver.competitive_frustration = clamp(
                driver.competitive_frustration + 5
            )

            if result.get("cause") == "Reckless Driving":
                driver.credibility = clamp(driver.credibility - 3)
                driver.reputation = clamp(driver.reputation - 1)
                driver.adjust_rivalry(8)
            else:
                driver.adjust_rivalry(4)

            if driver.rival:
                driver.record_feud(
                    driver.rival,
                    calendar.current_season,
                    6,
                    f"race incident ({result['status']})",
                )
                try:
                    rival = get_driver(driver.rival)
                    rival.record_feud(
                        driver.name,
                        calendar.current_season,
                        4,
                        f"race incident ({result['status']})",
                    )
                except ValueError:
                    pass
        else:
            driver.competitive_frustration = clamp(
                driver.competitive_frustration - 2
            )
            driver.credibility = clamp(driver.credibility + 1)

        for teammate in get_team_drivers(driver.team_name):
            if teammate.name == driver.name:
                continue

            teammate_result = results_by_name.get(teammate.name)

            if teammate_result is None:
                continue

            if (
                result["status"] == "Running"
                and teammate_result["status"] == "Running"
            ):
                driver.teammate_bond = clamp(driver.teammate_bond + 1)
                driver.adjust_friendship(teammate.name, 2)
            elif teammate_result["status"] != "Running":
                driver.teammate_bond = clamp(driver.teammate_bond - 1)

    winner = None

    for result in results:
        if result["status"] == "Running":
            winner = result["driver"]
            break

    if winner:
        winner.reputation = clamp(winner.reputation + 2)
        winner.competitive_frustration = clamp(
            winner.competitive_frustration - 8
        )

        if winner.ally:
            try:
                ally = get_driver(winner.ally)
                ally.morale = clamp(ally.morale + 2)
                ally.adjust_friendship(winner.name, 2)
            except ValueError:
                winner.ally = None

    refresh_all_driver_happiness()


def process_paddock_relationships():
    """Decay rivalries, cool feuds, and settle teammate bonds in the offseason."""

    print("\nPaddock Relationships")
    print("-" * 90)

    for driver in drivers:
        feud = driver.hottest_feud()
        decay = 3 if feud and feud.get("status") == "active" else 8
        driver.decay_rivalry(decay)
        driver.cool_feuds()

        for teammate in get_team_drivers(driver.team_name):
            if teammate.name == driver.name:
                continue

            driver.teammate_bond = clamp(driver.teammate_bond + 2)
            driver.adjust_friendship(teammate.name, 1)

            if driver.ally is None and driver.teammate_bond >= 70:
                driver.set_ally(teammate.name, driver.teammate_bond)

        refresh_driver_happiness(driver)

        rival_text = (
            f"{driver.rival} ({driver.rivalry_intensity})"
            if driver.rival
            else "none"
        )
        feud = driver.hottest_feud()
        feud_text = (
            f"{feud['opponent']} {feud['intensity']} ({feud['status']})"
            if feud
            else "none"
        )
        print(
            f"{driver.name} — {driver.happiness_label()} "
            f"{driver.morale} | Rep {driver.reputation} | "
            f"Cred {driver.credibility} | Rival {rival_text} | "
            f"Ally {driver.ally or 'none'} | Feud {feud_text}"
        )


def calculate_sponsorship_income(team):
    """Calculate offseason sponsorship revenue for a team."""

    team_drivers = get_team_drivers(team.name)

    average_popularity = (
        sum(driver.popularity for driver in team_drivers)
        / len(team_drivers)
    )

    income = BASE_SPONSORSHIP
    income += team.facility_level * 100_000
    income += team.championships * 300_000
    income += get_team_season_wins(team.name) * 75_000
    income += int(average_popularity * 2_500)
    income += team.sponsor_appeal() * 2_000

    if team.financial_status_label() == "Insolvent":
        income = int(income * 0.75)
    elif team.financial_status_label() == "Struggling":
        income = int(income * 0.90)

    return income


def calculate_operating_expenses(team):
    """Calculate seasonal operating expenses for a team."""

    expenses = (
        BASE_OPERATING_EXPENSE
        + team.facility_level * FACILITY_MAINTENANCE_PER_LEVEL
        + get_policy_operating_cost()
    )

    if team.financial_distress_level >= 2:
        expenses = int(expenses * 0.90)

    return expenses


def pay_team_driver_salaries(team):
    """Pay annual salaries for every driver on the team."""

    total_paid = 0

    for driver in get_team_drivers(team.name):
        if driver.is_free_agent:
            continue

        team.pay_driver_salary(driver.salary)
        total_paid += driver.salary
        driver.advance_contract()

    return total_paid


def apply_financial_distress_effects(team):
    """Apply performance and morale penalties for teams in distress."""

    team_drivers = get_team_drivers(team.name)

    if team.financial_distress_level == 1:
        for driver in team_drivers:
            driver.morale = clamp(driver.morale - 2)

    elif team.financial_distress_level == 2:
        team.car_rating = clamp(team.car_rating - 2)
        team.crew_rating = clamp(team.crew_rating - 2)
        team.reliability = clamp(team.reliability - 3)
        team.prestige = clamp(team.prestige - 2)
        team.engineering = clamp(team.engineering - 1)

        for driver in team_drivers:
            driver.morale = clamp(driver.morale - 5)

    elif team.financial_distress_level == 3:
        team.car_rating = clamp(team.car_rating - 5)
        team.crew_rating = clamp(team.crew_rating - 5)
        team.reliability = clamp(team.reliability - 5)
        team.prestige = clamp(team.prestige - 5)
        team.engineering = clamp(team.engineering - 3)

        for driver in team_drivers:
            driver.morale = clamp(driver.morale - 10)


def team_offseason_investment_decisions(team):
    """Make automated facility and performance investments."""

    actions = []

    if team.financial_distress_level >= 2:
        return actions

    upgrade_cost = team.facility_upgrade_cost()

    if (
        upgrade_cost is not None
        and team.can_afford(upgrade_cost)
        and (
            team.championships > 0
            or team.budget >= 3_000_000
        )
    ):
        old_level = team.facility_level

        if team.upgrade_facility():
            actions.append(
                f"Upgraded facility to level {team.facility_level} "
                f"(from level {old_level}) for ${upgrade_cost:,}"
            )

    investment_amount = PERFORMANCE_INVESTMENT_UNIT

    if (
        team.financial_distress_level == 0
        and team.can_afford(investment_amount)
    ):
        if team.budget >= 4_000_000:
            investment_amount = PERFORMANCE_INVESTMENT_UNIT * 2

        result = team.invest_in_performance(investment_amount)

        if result["spent"] > 0:
            actions.append(
                "Performance investment "
                f"${result['spent']:,} "
                f"(Car +{result['car_gain']}, "
                f"Crew +{result['crew_gain']}, "
                f"Eng +{result['engineering_gain']})"
            )

    if team.financial_distress_level <= 1:
        crew_gain = team.train_pit_crew()

        if crew_gain:
            actions.append(
                f"Pit crew training +{crew_gain} "
                f"(now {team.crew_rating})"
            )

    return actions


def process_team_offseason_finances(team):
    """Process one team's complete offseason financial cycle."""

    team.update_financial_distress()

    salaries_paid = pay_team_driver_salaries(team)
    sponsorship = calculate_sponsorship_income(team)
    team.add_sponsorship(sponsorship)

    operating_expenses = calculate_operating_expenses(team)
    team.pay_operating_expense(operating_expenses)

    investment_actions = team_offseason_investment_decisions(team)

    team.apply_trend_effects()
    team.update_financial_distress()
    apply_financial_distress_effects(team)
    team.apply_owner_financial_mood()

    return {
        "salaries_paid": salaries_paid,
        "sponsorship": sponsorship,
        "operating_expenses": operating_expenses,
        "investment_actions": investment_actions,
        "financial_status": team.financial_status_label(),
    }


def run_offseason_finances():
    """Collect sponsorship, pay expenses, and process team investments."""

    print("\nOffseason Financial Review")
    print("-" * 90)

    for team in teams:
        summary = process_team_offseason_finances(team)

        print(f"\n{team.name}")
        print(f"  Salaries paid: ${summary['salaries_paid']:,}")
        print(f"  Sponsorship revenue: ${summary['sponsorship']:,}")
        print(
            f"  Operating expenses: "
            f"${summary['operating_expenses']:,}"
        )

        if summary["investment_actions"]:
            for action in summary["investment_actions"]:
                print(f"  Investment: {action}")
        else:
            print("  Investment: No major spending this offseason")

        print(
            f"  Ending budget: ${team.budget:,} "
            f"- Owner: {team.owner.name} "
            f"- Prestige {team.prestige} "
            f"- {team.performance_trend_label()} "
            f"- Shop {team.facility_rating()} "
            f"(Lv {team.facility_level}) "
            f"- Eng {team.engineering} "
            f"- Crew {team.crew_rating} "
            f"- Status: {summary['financial_status']}"
        )

        if team.season_pit_mistakes:
            print(
                f"  Pit mistakes last season: {team.season_pit_mistakes}"
            )

        if team.financial_distress_level == 3:
            print(
                "  Entry status: Insolvent — remains on the grid"
            )


def run_offseason(completed_season):
    """Age drivers, update abilities, and process retirements."""

    print("\n" + "=" * 90)
    print(f"OFFSEASON AFTER SEASON {completed_season}")
    print("=" * 90)
    display_league_dashboard()

    retirement_candidates = []

    print("\nDriver Development")
    print("-" * 90)

    for driver in list(drivers):
        driver.age += 1
        development = apply_driver_development(driver)

        print(
            f"{driver.name}, age {driver.age} "
            f"- {development['stage']} "
            f"- Speed {development['speed_change']:+d} "
            f"- Consistency {development['consistency_change']:+d} "
            f"- Aggression {development['aggression_change']:+d} "
            f"- Overall {driver.overall_rating()}"
        )

        if should_driver_retire(driver):
            retirement_candidates.append(driver)

    print("\nRetirement Announcements")
    print("-" * 90)

    if not retirement_candidates:
        print("No drivers retired this offseason.")
    else:
        for retiring_driver in retirement_candidates:
            team_name = retiring_driver.team_name

            retire_driver(retiring_driver)

            rookie = generate_rookie(team_name)
            drivers.append(rookie)
            assign_rookie_rival(rookie)

            print(
                f"{rookie.name}, age {rookie.age}, replaces "
                f"{retiring_driver.name} at {team_name}."
            )

    run_offseason_finances()
    process_paddock_relationships()
    present_events(
        offseason_events(current_policies, events_resolved)
    )


def serve_suspensions():
    """Reduce active suspension lengths."""

    for driver in drivers:
        if driver.suspension_races > 0:
            driver.suspension_races -= 1


def result_strategy_text(result):
    """Return pit plan plus fuel call for reports."""

    strategy = (result.get("strategy") or "two-stop").replace("-", " ")
    fuel_call = result.get("fuel_call")

    if fuel_call and fuel_call != "window":
        return f"{strategy}, {fuel_call}"

    return strategy


def result_status_display(result):
    """Return a finish/DNF label including parts, wrecks, and pit penalties."""

    status = result["status"]

    if status == "Running":
        bits = []

        if result.get("contact") == "spin":
            bits.append("spin")
        elif result.get("contact") == "minor contact":
            bits.append("contact")

        if result.get("pit_mistake"):
            mistake = result.get("pit_mistake_type") or "pit mistake"
            penalty = result.get("pit_penalty")
            if penalty:
                bits.append(f"{mistake}, {penalty}")
            else:
                bits.append(mistake)

        if bits:
            return "Finished (" + "; ".join(bits) + ")"

        return "Finished"

    if status == "Mechanical Failure":
        part = PART_LABELS.get(result.get("component"), "Mechanical")
        return f"DNF: {part}"

    if status == "Crash":
        wreck = result.get("wreck")
        if wreck:
            role = wreck.get("role", "collected")
            return f"DNF: Crash ({wreck['size']}-car wreck, {role})"
        if result.get("contact") == "spin":
            return "DNF: Spin"
        return "DNF: Crash"

    return f"DNF: {status}"


def print_strategy_report(weekend, track):
    """Print tire wear and the field's pit/fuel plans."""

    weather = weekend["weather"]
    load = tire_load(track, weather)
    print(
        f"\nTire/fuel: wear {load} "
        f"(track {track.tire_wear}, weather {weather.get('tire_mod', 0):+d})"
    )

    for result in weekend["results"]:
        driver = result["driver"]
        print(
            f"- {driver.name}: {result_strategy_text(result)}"
        )


def record_race_history(track, race_number, results, weekend):
    """Save the results of a completed race."""

    pole = None

    for entry in weekend["grid"]:
        if entry.get("qualifying_position") == 1:
            pole = entry["driver"].name
            break

    weather = weekend["weather"]
    race_record = {
        "race_number": race_number,
        "track": track.name,
        "track_type": track.type,
        "weather": weather["condition"],
        "temperature": weather["temperature"],
        "format": weekend["format"],
        "cautions": weekend["cautions"],
        "pole": pole,
        "heat_results": list(weekend["heat_results"]),
        "stage_results": list(weekend["stage_results"]),
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
                "pit_mistake": result.get("pit_mistake", False),
                "start": result.get("start"),
                "strategy": result.get("strategy"),
                "stage_points": weekend["stage_points"].get(driver.name, 0),
                "qualifying_position": result.get("qualifying_position"),
                "grid_penalty": result.get("grid_penalty", 0),
                "fuel_call": result.get("fuel_call"),
                "pit_mistake_type": result.get("pit_mistake_type"),
                "pit_penalty": result.get("pit_penalty"),
                "component": result.get("component"),
                "contact": result.get("contact"),
                "wreck": result.get("wreck"),
            }
        )

    race_record["wrecks"] = list(weekend.get("wrecks") or [])
    race_record["investigations"] = list(weekend.get("investigations") or [])
    race_history.append(race_record)


def print_qualifying_report(weekend):
    """Print starting grid, penalties, heats, stages, and cautions."""

    print("\nQualifying / Starting Grid")
    print("-" * 75)

    for entry in weekend["grid"]:
        penalty = entry.get("penalty", 0)
        penalty_text = ""

        if penalty:
            penalty_text = (
                f" — {entry['penalty_reason']} "
                f"(+{penalty} spot{'s' if penalty != 1 else ''})"
            )

        print(
            f"{entry['grid']}. {entry['driver'].name} "
            f"({entry['driver'].team_name}) "
            f"qualified {entry['qualifying_position']}"
            f"{penalty_text}"
        )

    if weekend["heat_results"]:
        print("\nHeat Results (feature grid)")
        print("-" * 75)

        for heat in weekend["heat_results"]:
            print(
                f"{heat['position']}. {heat['driver']} "
                f"({heat['team']})"
            )

    if weekend["stage_results"]:
        print("\nStage Results")
        print("-" * 75)

        for stage in weekend["stage_results"]:
            if not stage:
                continue

            print(f"Stage {stage[0]['stage']}")

            for row in stage[:3]:
                print(
                    f"  {row['position']}. {row['driver']} "
                    f"- {row['points']} stage pts"
                )

    print(
        f"\nCautions: {weekend['cautions']} yellow"
        f"{'' if weekend['cautions'] == 1 else 's'} "
        "(restarts compressed the field)"
        if weekend["cautions"]
        else "\nCautions: none (green-flag race)"
    )


def run_race(track, race_number):
    """Run one race weekend and update season statistics."""

    print(f"\n{'=' * 75}")
    print(f"Race {race_number}: {track.name}")
    print(f"Track type: {track.type}")
    print(f"Layout: {track.description()}")
    print(f"Incident risk: {track.incident_risk}%")
    print(f"Purse: ${track.purse:,}")
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

    weekend = simulate_race_weekend(track)
    results = weekend["results"]

    print(f"Weather: {weather_label(weekend['weather'])}")
    print(f"Format: {policy_label('race_format')}")
    print_qualifying_report(weekend)
    print_strategy_report(weekend, track)

    print("\nFeature Results")
    print("-" * 75)

    for position, result in enumerate(results, start=1):
        driver = result["driver"]
        status = result["status"]
        finish_points = get_points_by_position()[position - 1]
        stage_points = weekend["stage_points"].get(driver.name, 0)
        points_earned = finish_points + stage_points
        prize_money = int(
            track.purse * PRIZE_PERCENTAGES[position - 1]
        )
        start_position = result.get("start", position)
        strategy = result_strategy_text(result)

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

            status_display = result_status_display(result)

        else:
            driver.dnfs += 1

            if status == "Crash":
                driver.popularity = clamp(driver.popularity + 1)
            else:
                driver.popularity = clamp(driver.popularity - 1)

            status_display = result_status_display(result)

        points_text = f"{points_earned} pts"

        if stage_points:
            points_text = (
                f"{points_earned} pts "
                f"(finish {finish_points} + stage {stage_points})"
            )

        print(
            f"{position}. {driver.name} "
            f"({driver.team_name}) "
            f"- start P{start_position}, {strategy} "
            f"- {status_display} "
            f"- {points_text} "
            f"- ${prize_money:,}"
        )

    display_incident_report(results, weekend)
    review_race_incidents(results, weekend)
    update_paddock_after_race(results)
    record_race_history(track, race_number, results, weekend)
    serve_suspensions()
    display_league_dashboard()


def display_incident_report(results, weekend=None):
    """Display crashes, parts, contact, wrecks, and pit-road mistakes."""

    weekend = weekend or {}
    incidents = [
        result
        for result in results
        if result["status"] != "Running"
    ]
    contacts = [
        result
        for result in results
        if result.get("contact") and result["status"] == "Running"
    ]
    pit_mistakes = [
        result
        for result in results
        if result.get("pit_mistake")
    ]
    wrecks = weekend.get("wrecks") or []

    print("\nIncident Report")
    print("-" * 75)

    if not incidents and not contacts:
        print("No major incidents occurred.")
    else:
        for incident in incidents:
            driver = incident["driver"]

            if incident["status"] == "Crash":
                wreck = incident.get("wreck")
                wreck_text = ""
                if wreck:
                    wreck_text = f" — {wreck['size']}-car wreck ({wreck['role']})"
                print(
                    f"{driver.name}: Crash"
                    f"{wreck_text} "
                    f"— Initial finding: {incident.get('cause') or 'Racing Incident'}"
                )
            elif incident["status"] == "Mechanical Failure":
                part = PART_LABELS.get(incident.get("component"), "Mechanical")
                print(f"{driver.name}: {part} failure")
            else:
                print(f"{driver.name}: {incident['status']}")

        for result in contacts:
            driver = result["driver"]
            print(
                f"{driver.name}: {result['contact']} "
                f"— continued (finding: {result.get('cause') or 'Racing Incident'})"
            )

    if wrecks:
        print("\nMulti-car Wrecks")
        print("-" * 75)

        for wreck in wrecks:
            label = "Major" if wreck.get("major") else "Chain"
            print(
                f"{label} {wreck['size']}-car: "
                f"{', '.join(wreck['cars'])} "
                f"(started by {wreck['initiator']})"
            )

    if pit_mistakes:
        print("\nPit Crew Report")
        print("-" * 75)

        for result in pit_mistakes:
            driver = result["driver"]
            mistake = result.get("pit_mistake_type") or "crew error"
            penalty = result.get("pit_penalty")
            penalty_text = f", {penalty} penalty" if penalty else ""
            print(
                f"{driver.name} ({driver.team_name}): "
                f"{mistake}{penalty_text}"
            )


def review_race_incidents(results, weekend=None):
    """Allow the commissioner to review reckless crashes and wreck blame."""

    weekend = weekend or {}
    investigations = weekend.get("investigations") or []
    by_name = {packet["driver"]: packet for packet in investigations}

    reviewable_incidents = [
        result
        for result in results
        if result["driver"].name in by_name
    ]

    if not reviewable_incidents:
        reviewable_incidents = [
            result
            for result in results
            if (
                result["status"] == "Crash"
                and result.get("cause") == "Reckless Driving"
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
        packet = by_name.get(incident["driver"].name)
        review_single_incident(incident, packet)


def review_single_incident(incident, investigation=None):
    """Present disciplinary options for one incident."""

    driver = incident["driver"]
    team = get_team(driver.team_name)

    print(
        f"\nRace control has referred {driver.name} "
        f"of {driver.team_name} for possible reckless driving."
    )

    if investigation:
        involved = ", ".join(investigation.get("involved") or [driver.name])
        print("\nInvestigation")
        print(
            f"Assigned blame: {investigation.get('blame')} "
            f"({investigation.get('confidence')} confidence)"
        )
        print(f"Contact: {investigation.get('contact') or 'crash'}")
        print(f"Involved: {involved}")
        print("Evidence:")

        for line in investigation.get("evidence") or []:
            print(f"- {line}")

    print(f"Personality: {driver.personality}")
    print(
        f"Traits — temperament {driver.temperament}, "
        f"loyalty {driver.loyalty}, ambition {driver.ambition}, "
        f"media {driver.media_skill}, risk {driver.risk_tolerance}"
    )
    print(
        f"Known rival: {driver.rival} "
        f"(intensity {driver.rivalry_intensity})"
    )
    print(f"Ally: {driver.ally or 'none'}")
    print(
        f"Reputation {driver.reputation} | "
        f"Credibility {driver.credibility} | "
        f"Popularity {driver.popularity}"
    )
    print(
        f"Happiness: {driver.happiness_label()} "
        f"(morale {driver.morale})"
    )
    print(f"Commissioner trust: {driver.commissioner_trust}")
    print(f"Current championship points: {driver.points}")
    print(f"Team budget: ${team.budget:,}")

    print("\nChoose a ruling:")
    print("1. No action")
    print("2. Official warning")
    print("3. Financial fine")
    print("4. Championship points penalty")
    print("5. Suspend for the next race")

    choice = get_valid_choice()

    apply_commissioner_ruling(choice, driver, team)

    if investigation:
        decision_log.append(
            {
                "season": calendar.current_season,
                "id": "post-race-investigation",
                "title": "Post-race investigation",
                "choice_id": choice,
                "choice_label": f"Disciplinary ruling on {driver.name}",
                "outcome": (
                    f"Blame assigned to {investigation.get('blame')} "
                    f"({investigation.get('confidence')} confidence). "
                    "Evidence: "
                    + "; ".join(investigation.get("evidence") or [])
                ),
            }
        )


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

    if trust_change < 0 and driver.temperament < 40:
        trust_change -= 1

    if choice in {"3", "4", "5"} and driver.loyalty >= 75:
        trust_change -= 1

    if choice == "1" and driver.ambition >= 75:
        trust_change += 1

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
    """Allow a rival to react to a commissioner ruling."""

    rival_name = penalized_driver.rival

    if not rival_name:
        return

    try:
        rival = get_driver(rival_name)
    except ValueError:
        penalized_driver.rival = None
        return

    severe_decisions = {"3", "4", "5"}
    lenient_decisions = {"1", "2"}
    heat = 1 if penalized_driver.rivalry_intensity >= 60 else 0

    if choice in severe_decisions:
        trust_change = 3 + heat
        morale_change = 2 + heat
        reaction = "approved of the punishment"
        penalized_driver.adjust_rivalry(-4)

        if rival.rival == penalized_driver.name:
            rival.adjust_rivalry(-4)
    elif choice in lenient_decisions:
        trust_change = -2 - heat
        morale_change = -1 - heat
        reaction = "believed the punishment was too lenient"
        penalized_driver.adjust_rivalry(6)
        penalized_driver.record_feud(
            rival.name,
            calendar.current_season,
            6,
            "lenient ruling",
        )
        rival.record_feud(
            penalized_driver.name,
            calendar.current_season,
            6,
            "lenient ruling",
        )
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


def apply_ally_reaction(choice, penalized_driver):
    """Let a driver's ally react to a commissioner ruling."""

    ally_name = penalized_driver.ally

    if not ally_name:
        return

    try:
        ally = get_driver(ally_name)
    except ValueError:
        penalized_driver.ally = None
        return

    if choice in {"4", "5"}:
        trust_change = -3 if penalized_driver.loyalty >= 70 else -2
        bond_change = -4
        reaction = "thought the ruling was hard on a friend"
    elif choice == "1":
        trust_change = 2
        bond_change = 2
        reaction = "appreciated the break given to a friend"
    else:
        trust_change = 0
        bond_change = 0
        reaction = None

    if reaction is None:
        return

    ally.commissioner_trust = clamp(ally.commissioner_trust + trust_change)
    ally.adjust_friendship(penalized_driver.name, bond_change)
    penalized_driver.adjust_friendship(ally.name, bond_change)

    print(
        f"{ally.name}, an ally of {penalized_driver.name}, "
        f"{reaction}."
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
        fine_amount = get_penalty_fine_amount()

        team.pay_fine(fine_amount)
        league["fines_collected"] += fine_amount
        league["integrity"] += 3
        league["controversy"] += 1
        driver.fines += fine_amount

        decision = f"${fine_amount:,} fine issued"

    elif choice == "4":
        points_penalty = get_penalty_points_amount()

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
    apply_ally_reaction(choice, driver)

    league["integrity"] = clamp(league["integrity"])
    league["fan_interest"] = clamp(league["fan_interest"])
    league["controversy"] = clamp(league["controversy"])
    driver.morale = clamp(driver.morale)

    print(f"\nRuling: {decision}")
    print(f"League integrity: {league['integrity']}")
    print(f"Fan interest: {league['fan_interest']}")
    print(f"Controversy: {league['controversy']}")
    print(f"{driver.name} morale: {driver.morale}")


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
            f"- Age {driver.age} "
            f"- Overall {driver.overall_rating()} "
            f"- {driver.points} pts "
            f"- {driver.wins} wins "
            f"- {driver.dnfs} DNFs "
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
    print("-" * 90)

    for team in financial_ranking:
        print(
            f"{team.name} "
            f"- Owner: {team.owner.name} "
            f"- Budget: ${team.budget:,} "
            f"- {team.financial_status_label()} "
            f"- Prestige {team.prestige} "
            f"- {team.performance_trend_label()} "
            f"- Shop {team.facility_rating()} "
            f"(Lv {team.facility_level}) "
            f"- Eng {team.engineering} "
            f"- Crew {team.crew_rating} "
            f"- Rel {team.reliability}"
        )


def record_team_season_trends():
    """Store each team's season points and update performance trends."""

    for team in teams:
        if len(team.season_points_history) >= calendar.current_season:
            continue

        points = sum(
            driver.points
            for driver in get_team_drivers(team.name)
        )
        team.record_season_performance(points)


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

        print(
            f"{driver.name} "
            f"({driver.personality}) "
            f"- {driver.happiness_label()} {driver.morale} "
            f"- Trust: {trust}/100 "
            f"- {relationship_label(trust)} "
            f"- Rep {driver.reputation}/Cred {driver.credibility} "
            f"- Rival: {driver.rival or 'none'} "
            f"({driver.rivalry_intensity}) "
            f"- Ally: {driver.ally or 'none'} "
            f"- Bond {driver.teammate_bond}"
        )

        feud = driver.hottest_feud()

        if feud:
            print(
                f"    Feud: {feud['opponent']} "
                f"{feud['intensity']} ({feud['status']}) "
                f"since season {feud.get('started_season', '?')} "
                f"— {feud.get('last_incident', '')}"
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

        weather = race.get("weather", "n/a")
        cautions = race.get("cautions")
        if cautions is None:
            caution_text = ""
        elif cautions == 1:
            caution_text = ", 1 yellow"
        else:
            caution_text = f", {cautions} yellows"

        wrecks = race.get("wrecks") or []
        wreck_text = f", {len(wrecks)} wrecks" if wrecks else ""

        print(
            f"Race {race['race_number']}: {race['track']} "
            f"- Winner: {winner['driver']} "
            f"({winner['team']}) "
            f"- {weather}{caution_text}{wreck_text} "
            f"- Pole: {race.get('pole') or 'n/a'} "
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
    print(f"Owner pressure: {league['owner_pressure']}/100")
    print(f"Driver sentiment: {league['driver_sentiment']}/100")


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
            "owner_pressure": league["owner_pressure"],
            "driver_sentiment": league["driver_sentiment"],
        },
        "policies": dict(current_policies),
        "decisions": [
            record
            for record in decision_log
            if record.get("season") == season_number
        ],
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
                "age": driver.age,
                "overall_rating": driver.overall_rating(),
                "is_rookie": driver.is_rookie,
                "speed": driver.speed,
                "consistency": driver.consistency,
                "aggression": driver.aggression,
                "short_track": driver.short_track,
                "road_course": driver.road_course,
                "intermediate": driver.intermediate,
                "superspeedway": driver.superspeedway,
                "points": driver.points,
                "wins": driver.wins,
                "dnfs": driver.dnfs,
                "earnings": driver.earnings,
                "morale": driver.morale,
                "happiness": driver.happiness_label(),
                "popularity": driver.popularity,
                "reputation": driver.reputation,
                "credibility": driver.credibility,
                "commissioner_trust": driver.commissioner_trust,
                "temperament": driver.temperament,
                "loyalty": driver.loyalty,
                "ambition": driver.ambition,
                "media_skill": driver.media_skill,
                "risk_tolerance": driver.risk_tolerance,
                "rival": driver.rival,
                "rivalry_intensity": driver.rivalry_intensity,
                "ally": driver.ally,
                "teammate_bond": driver.teammate_bond,
                "feuds": list(driver.feuds),
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
                "owner": team.owner.name,
                "owner_personality": team.owner.personality,
                "owner_priority": team.owner.priority,
                "budget": team.budget,
                "facility_level": team.facility_level,
                "facility_rating": team.facility_rating(),
                "financial_status": team.financial_status_label(),
                "prestige": team.prestige,
                "attractiveness": team.attractiveness(),
                "sponsor_appeal": team.sponsor_appeal(),
                "performance_trend": team.performance_trend_label(),
                "engineering": team.engineering,
                "season_pit_mistakes": team.season_pit_mistakes,
                "season_sponsorship": team.season_sponsorship,
                "season_operating_expenses": (
                    team.season_operating_expenses
                ),
                "current_payroll": team.current_payroll,
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
    events_resolved.clear()

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

    refresh_all_driver_happiness()

    print("\n" + "=" * 90)
    print(f"STOCK CAR COMMISSIONER — SEASON {season_number}")
    print("=" * 90)
    display_league_dashboard()
    present_events(
        preseason_events(current_policies, season_number)
    )


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


def run_preseason(season_number):
    """Open the season and prepare teams and drivers."""

    calendar.current_season = season_number
    calendar.enter_preseason()
    sync_calendar_aliases()
    display_calendar_banner()
    initialize_season(season_number)
    calendar.enter_regular_season()
    sync_calendar_aliases()


def run_regular_season():
    """Run remaining regular-season races."""

    calendar.enter_regular_season()
    sync_calendar_aliases()
    display_calendar_banner()

    start_race = len(race_history) + 1

    print(
        f"Next race: {start_race} of {len(tracks)}"
        if start_race <= len(tracks)
        else "All regular-season races are complete."
    )
    display_league_dashboard()

    for race_number, track in enumerate(
        tracks[start_race - 1:],
        start=start_race,
    ):
        run_race(track, race_number)
        present_events(
            regular_season_events(
                race_number,
                teams,
                drivers,
                events_resolved,
            )
        )

    calendar.enter_postseason()
    sync_calendar_aliases()


def run_postseason(season_number):
    """Close the season with standings, awards, and records."""

    global championship_awarded

    calendar.enter_postseason()
    sync_calendar_aliases()
    display_calendar_banner()
    display_league_dashboard()

    display_driver_standings()
    record_team_season_trends()
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

    championship_awarded = False
    present_events(
        postseason_events(teams, drivers, events_resolved)
    )


def run_single_season(season_number, resume=False):
    """Run one complete championship season through postseason."""

    calendar.current_season = season_number

    if not resume or calendar.phase == PRESEASON:
        run_preseason(season_number)

    if calendar.phase == REGULAR_SEASON:
        run_regular_season()

    if calendar.phase == POSTSEASON:
        run_postseason(season_number)


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
            f"- Age: {driver.age} "
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
            f"- Owner: {team.owner.name} "
            f"- Championships: {team.championships} "
            f"- Wins: {team.career_wins} "
            f"- Prestige: {team.prestige} "
            f"- {team.performance_trend_label()} "
            f"- Shop: {team.facility_rating()} "
            f"(Lv {team.facility_level}) "
            f"- Eng: {team.engineering} "
            f"- Crew: {team.crew_rating} "
            f"- Career prize money: ${team.career_prize_money:,} "
            f"- Sponsorship income: ${team.career_sponsorship_income:,} "
            f"- Current budget: ${team.budget:,} "
            f"- Status: {team.financial_status_label()}"
        )


def display_retirement_report():
    """Display all retired drivers from the career."""

    print("\nRetired Drivers")
    print("-" * 100)

    if not retired_drivers:
        print("No drivers retired during this career.")
        return

    retirement_ranking = sorted(
        retired_drivers,
        key=lambda driver: (
            driver.championships,
            driver.career_wins,
            driver.career_points,
        ),
        reverse=True,
    )

    for driver in retirement_ranking:
        print(
            f"{driver.name} "
            f"- Retired age: {driver.age} "
            f"- Seasons: {driver.seasons_completed} "
            f"- Championships: {driver.championships} "
            f"- Wins: {driver.career_wins} "
            f"- Starts: {driver.career_starts} "
            f"- Career points: {driver.career_points} "
            f"- Career earnings: ${driver.career_earnings:,}"
        )


def process_offseason_and_advance():
    """Run the offseason, then move the calendar into the next preseason."""

    calendar.enter_offseason()
    sync_calendar_aliases()
    display_calendar_banner()
    run_offseason(calendar.current_season)
    calendar.advance_to_next_season()
    sync_calendar_aliases()
    prompt_save_career()

    input(
        "\nPress Enter to begin the next season..."
    )


def run_career(number_of_seasons=3, start_season=1, resume=False):
    """Run several consecutive seasons through the league calendar."""

    calendar.career_seasons_total = number_of_seasons

    if not resume:
        calendar.current_season = start_season
        calendar.enter_preseason()

    sync_calendar_aliases()

    while calendar.current_season <= calendar.career_seasons_total:
        if calendar.phase == OFFSEASON:
            if calendar.has_more_seasons():
                display_calendar_banner()
                run_offseason(calendar.current_season)
                calendar.advance_to_next_season()
                sync_calendar_aliases()
                prompt_save_career()

                input(
                    "\nPress Enter to begin the next season..."
                )
                continue

            break

        resume_season = calendar.phase in {
            REGULAR_SEASON,
            POSTSEASON,
        }
        run_single_season(
            calendar.current_season,
            resume=resume_season,
        )

        if calendar.has_more_seasons():
            process_offseason_and_advance()
        else:
            break

    display_career_report()
    display_retirement_report()


def continue_loaded_career():
    """Continue a career that was loaded from a save file."""

    run_career(
        number_of_seasons=calendar.career_seasons_total,
        start_season=calendar.current_season,
        resume=True,
    )


def display_main_menu():
    """Display the main menu."""

    print("\n" + "=" * 75)
    print("STOCK CAR COMMISSIONER")
    print("=" * 75)
    print("1. Start new career (3 seasons)")
    print("2. Load saved career")
    print("3. Save current career")
    print("4. Run one quick season")
    print("5. Exit")


def get_main_menu_choice():
    """Return a valid main menu choice."""

    while True:
        choice = input("\nChoose an option (1-5): ").strip()

        if choice in {"1", "2", "3", "4", "5"}:
            return choice

        print("Please enter a number from 1 to 5.")


def main():
    """Run the commissioner sim main menu."""

    while True:
        display_main_menu()
        choice = get_main_menu_choice()

        if choice == "1":
            reset_career_state()
            run_career(number_of_seasons=3)

        elif choice == "2":
            if load_career():
                continue_loaded_career()

        elif choice == "3":
            if drivers:
                save_career()
            else:
                print("\nNo active career to save.")

        elif choice == "4":
            run_season()

        elif choice == "5":
            print("\nGoodbye.")
            break


def run_season():
    """Run the complete racing season."""

    run_single_season(calendar.current_season)
    calendar.advance_to_next_season()
    sync_calendar_aliases()


if __name__ == "__main__":
    main()
