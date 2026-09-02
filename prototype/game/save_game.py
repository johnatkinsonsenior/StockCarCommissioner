"""Save and load career progress for the commissioner sim."""

import json
from datetime import datetime
from pathlib import Path

from game.models import Driver, Owner, Team, Track

SAVE_VERSION = "0.0.9"
SUPPORTED_SAVE_VERSIONS = {
    "0.0.3",
    "0.0.4",
    "0.0.5",
    "0.0.6",
    "0.0.7",
    "0.0.8",
    "0.0.9",
}
GAME_NAME = "Stock Car Commissioner"


def get_saves_folder():
    """Return the folder where career saves are stored."""

    project_root = Path(__file__).resolve().parent.parent.parent
    saves_folder = project_root / "saves"
    saves_folder.mkdir(exist_ok=True)

    return saves_folder


def driver_to_dict(driver):
    """Serialize a driver to a dictionary."""

    return {
        "name": driver.name,
        "team_name": driver.team_name,
        "age": driver.age,
        "speed": driver.speed,
        "consistency": driver.consistency,
        "aggression": driver.aggression,
        "personality": driver.personality,
        "rival": driver.rival,
        "rivalry_intensity": driver.rivalry_intensity,
        "ally": driver.ally,
        "friendship_strength": driver.friendship_strength,
        "teammate_bond": driver.teammate_bond,
        "friendships": dict(driver.friendships),
        "feuds": list(driver.feuds),
        "short_track": driver.short_track,
        "road_course": driver.road_course,
        "intermediate": driver.intermediate,
        "superspeedway": driver.superspeedway,
        "temperament": driver.temperament,
        "loyalty": driver.loyalty,
        "ambition": driver.ambition,
        "media_skill": driver.media_skill,
        "risk_tolerance": driver.risk_tolerance,
        "reputation": driver.reputation,
        "credibility": driver.credibility,
        "team_satisfaction": driver.team_satisfaction,
        "contract_satisfaction": driver.contract_satisfaction,
        "competitive_frustration": driver.competitive_frustration,
        "popularity": driver.popularity,
        "salary": driver.salary,
        "contract_years": driver.contract_years,
        "is_rookie": driver.is_rookie,
        "previous_team": driver.previous_team,
        "is_free_agent": driver.is_free_agent,
        "morale": driver.morale,
        "commissioner_trust": driver.commissioner_trust,
        "is_retired": driver.is_retired,
        "career_starts": driver.career_starts,
        "career_finishes": driver.career_finishes,
        "career_wins": driver.career_wins,
        "career_dnfs": driver.career_dnfs,
        "career_points": driver.career_points,
        "career_earnings": driver.career_earnings,
        "championships": driver.championships,
        "seasons_completed": driver.seasons_completed,
        "points": driver.points,
        "earnings": driver.earnings,
        "starts": driver.starts,
        "finishes": driver.finishes,
        "wins": driver.wins,
        "dnfs": driver.dnfs,
        "warnings": driver.warnings,
        "fines": driver.fines,
        "points_penalties": driver.points_penalties,
        "suspensions": driver.suspensions,
        "suspension_races": driver.suspension_races,
        "endorsement": driver.endorsement,
    }


def driver_from_dict(data):
    """Restore a driver from a saved dictionary."""

    driver = Driver(
        name=data["name"],
        team_name=data["team_name"],
        age=data["age"],
        speed=data["speed"],
        consistency=data["consistency"],
        aggression=data["aggression"],
        personality=data["personality"],
        rival=data["rival"],
        popularity=data["popularity"],
        salary=data["salary"],
        contract_years=data["contract_years"],
        is_rookie=data.get("is_rookie", False),
        temperament=data.get("temperament"),
        loyalty=data.get("loyalty"),
        ambition=data.get("ambition"),
        media_skill=data.get("media_skill"),
        risk_tolerance=data.get("risk_tolerance"),
        rivalry_intensity=data.get("rivalry_intensity"),
        ally=data.get("ally"),
        friendship_strength=data.get("friendship_strength", 0),
        teammate_bond=data.get("teammate_bond", 55),
        reputation=data.get("reputation"),
        credibility=data.get("credibility"),
        team_satisfaction=data.get("team_satisfaction", 65),
        contract_satisfaction=data.get("contract_satisfaction", 65),
        competitive_frustration=data.get("competitive_frustration", 30),
        feuds=data.get("feuds") or [],
        friendships=data.get("friendships") or {},
        short_track=data.get("short_track"),
        road_course=data.get("road_course"),
        intermediate=data.get("intermediate"),
        superspeedway=data.get("superspeedway"),
    )

    driver.previous_team = data.get("previous_team")
    driver.is_free_agent = data.get("is_free_agent", False)
    driver.morale = data["morale"]
    driver.commissioner_trust = data["commissioner_trust"]
    driver.is_retired = data.get("is_retired", False)

    driver.career_starts = data["career_starts"]
    driver.career_finishes = data["career_finishes"]
    driver.career_wins = data["career_wins"]
    driver.career_dnfs = data["career_dnfs"]
    driver.career_points = data["career_points"]
    driver.career_earnings = data["career_earnings"]
    driver.championships = data["championships"]
    driver.seasons_completed = data["seasons_completed"]

    driver.points = data["points"]
    driver.earnings = data["earnings"]
    driver.starts = data["starts"]
    driver.finishes = data["finishes"]
    driver.wins = data["wins"]
    driver.dnfs = data["dnfs"]
    driver.warnings = data["warnings"]
    driver.fines = data["fines"]
    driver.points_penalties = data["points_penalties"]
    driver.suspensions = data["suspensions"]
    driver.suspension_races = data["suspension_races"]
    driver.endorsement = data.get("endorsement")

    return driver


def owner_to_dict(owner):
    """Serialize an owner to a dictionary."""

    if owner is None:
        return None

    return {
        "name": owner.name,
        "personality": owner.personality,
        "wealth": owner.wealth,
        "patience": owner.patience,
        "priority": owner.priority,
        "pressure": owner.pressure,
    }


def owner_from_dict(data, team_name):
    """Restore an owner, or create a default if an older save has none."""

    if not data:
        return Owner.default_for_team(team_name)

    owner = Owner(
        name=data["name"],
        personality=data.get("personality", "Hands-On"),
        wealth=data.get("wealth", 50),
        patience=data.get("patience", 50),
        priority=data.get("priority", "stability"),
    )
    owner.pressure = data.get("pressure", 25)

    return owner


def team_to_dict(team):
    """Serialize a team to a dictionary."""

    return {
        "name": team.name,
        "manufacturer": team.manufacturer,
        "car_rating": team.car_rating,
        "crew_rating": team.crew_rating,
        "reliability": team.reliability,
        "starting_budget": team.starting_budget,
        "budget": team.budget,
        "career_prize_money": team.career_prize_money,
        "championships": team.championships,
        "organization_titles": team.organization_titles,
        "career_wins": team.career_wins,
        "current_payroll": team.current_payroll,
        "career_salary_expenses": team.career_salary_expenses,
        "facility_level": team.facility_level,
        "season_sponsorship": team.season_sponsorship,
        "season_operating_expenses": team.season_operating_expenses,
        "career_sponsorship_income": team.career_sponsorship_income,
        "career_operating_expenses": team.career_operating_expenses,
        "career_facility_investment": team.career_facility_investment,
        "career_performance_investment": team.career_performance_investment,
        "career_crew_training": team.career_crew_training,
        "financial_distress_level": team.financial_distress_level,
        "owner": owner_to_dict(team.owner),
        "prestige": team.prestige,
        "engineering": team.engineering,
        "season_points_history": list(team.season_points_history),
        "performance_trend": team.performance_trend,
        "season_pit_mistakes": team.season_pit_mistakes,
    }


def team_from_dict(data):
    """Restore a team from a saved dictionary."""

    team = Team(
        name=data["name"],
        car_rating=data["car_rating"],
        crew_rating=data["crew_rating"],
        reliability=data["reliability"],
        starting_budget=data["starting_budget"],
        owner=owner_from_dict(data.get("owner"), data["name"]),
        prestige=data.get("prestige"),
        engineering=data.get("engineering"),
        manufacturer=data.get("manufacturer"),
    )

    team.budget = data["budget"]
    team.career_prize_money = data["career_prize_money"]
    team.championships = data["championships"]
    team.organization_titles = data.get("organization_titles", 0)
    team.career_wins = data["career_wins"]
    team.current_payroll = data["current_payroll"]
    team.career_salary_expenses = data["career_salary_expenses"]
    team.facility_level = data["facility_level"]
    team.season_sponsorship = data["season_sponsorship"]
    team.season_operating_expenses = data["season_operating_expenses"]
    team.career_sponsorship_income = data["career_sponsorship_income"]
    team.career_operating_expenses = data["career_operating_expenses"]
    team.career_facility_investment = data["career_facility_investment"]
    team.career_performance_investment = data["career_performance_investment"]
    team.career_crew_training = data.get("career_crew_training", 0)
    team.financial_distress_level = data["financial_distress_level"]
    team.season_points_history = list(data.get("season_points_history") or [])
    team.performance_trend = data.get("performance_trend", 0)
    team.season_pit_mistakes = data.get("season_pit_mistakes", 0)

    return team


def track_to_dict(track):
    """Serialize a track to a dictionary."""

    return {
        "name": track.name,
        "type": track.type,
        "purse": track.purse,
        "incident_risk": track.incident_risk,
        "length": track.length,
        "banking": track.banking,
        "surface": track.surface,
        "tire_wear": track.tire_wear,
        "passing_difficulty": track.passing_difficulty,
    }


def track_from_dict(data):
    """Restore a track from a saved dictionary."""

    return Track(
        name=data["name"],
        track_type=data.get("type", "Intermediate"),
        purse=data["purse"],
        incident_risk=data["incident_risk"],
        length=data.get("length", 1.5),
        banking=data.get("banking", 18),
        surface=data.get("surface", "asphalt"),
        tire_wear=data.get("tire_wear", 55),
        passing_difficulty=data.get("passing_difficulty", 50),
    )


def build_save_data(
    league,
    race_history,
    career_history,
    retired_drivers,
    drivers,
    teams,
    current_season,
    championship_awarded,
    career_seasons_total,
    season_in_progress,
    calendar_phase,
    policies,
    decision_log,
    events_resolved,
    tracks=None,
):
    """Build a save file dictionary from live game state."""

    save_data = {
        "game": GAME_NAME,
        "version": SAVE_VERSION,
        "save_type": "career",
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "current_season": current_season,
        "championship_awarded": championship_awarded,
        "career_seasons_total": career_seasons_total,
        "season_in_progress": season_in_progress,
        "calendar_phase": calendar_phase,
        "policies": dict(policies),
        "decision_log": list(decision_log),
        "events_resolved": list(events_resolved),
        "league": dict(league),
        "race_history": list(race_history),
        "career_history": list(career_history),
        "drivers": [driver_to_dict(driver) for driver in drivers],
        "teams": [team_to_dict(team) for team in teams],
        "retired_drivers": [
            driver_to_dict(driver)
            for driver in retired_drivers
        ],
    }

    if tracks is not None:
        save_data["tracks"] = [track_to_dict(track) for track in tracks]

    return save_data


def validate_save_data(save_data):
    """Raise ValueError if the save file is not compatible."""

    if save_data.get("game") != GAME_NAME:
        raise ValueError("This file is not a Stock Car Commissioner save.")

    if save_data.get("version") not in SUPPORTED_SAVE_VERSIONS:
        raise ValueError(
            "Unsupported save version: "
            f"{save_data.get('version')}"
        )


def parse_save_data(save_data):
    """Convert a save dictionary into restored game objects."""

    validate_save_data(save_data)

    restored_drivers = [
        driver_from_dict(driver_data)
        for driver_data in save_data["drivers"]
    ]

    restored_teams = [
        team_from_dict(team_data)
        for team_data in save_data["teams"]
    ]

    restored_retired = [
        driver_from_dict(driver_data)
        for driver_data in save_data["retired_drivers"]
    ]

    restored_tracks = None

    if save_data.get("tracks"):
        restored_tracks = [
            track_from_dict(track_data)
            for track_data in save_data["tracks"]
        ]

    return {
        "league": dict(save_data["league"]),
        "race_history": list(save_data["race_history"]),
        "career_history": list(save_data["career_history"]),
        "drivers": restored_drivers,
        "teams": restored_teams,
        "retired_drivers": restored_retired,
        "tracks": restored_tracks,
        "current_season": save_data["current_season"],
        "championship_awarded": save_data["championship_awarded"],
        "career_seasons_total": save_data["career_seasons_total"],
        "season_in_progress": save_data["season_in_progress"],
        "calendar_phase": save_data.get("calendar_phase"),
        "policies": dict(save_data.get("policies") or {}),
        "decision_log": list(save_data.get("decision_log") or []),
        "events_resolved": list(save_data.get("events_resolved") or []),
    }


def save_to_file(save_data, save_name=None):
    """Write a save dictionary to the saves folder."""

    saves_folder = get_saves_folder()

    if save_name:
        filename = save_name
        if not filename.endswith(".json"):
            filename = f"{filename}.json"
    else:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"career_save_{timestamp}.json"

    save_path = saves_folder / filename

    with save_path.open("w", encoding="utf-8") as save_file:
        json.dump(save_data, save_file, indent=4)

    return save_path


def load_from_file(save_path):
    """Read and validate a save file from disk."""

    save_path = Path(save_path)

    with save_path.open("r", encoding="utf-8") as save_file:
        save_data = json.load(save_file)

    return parse_save_data(save_data)


def list_save_files():
    """Return available career save files, newest first."""

    saves_folder = get_saves_folder()

    return sorted(
        saves_folder.glob("*.json"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
