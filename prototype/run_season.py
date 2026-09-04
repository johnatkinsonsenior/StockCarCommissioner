import json
import random
from datetime import datetime
from pathlib import Path

from data import (
    create_initial_drivers,
    create_initial_networks,
    create_initial_sponsors,
    create_sponsor_prospects,
    create_initial_teams,
    create_initial_tracks,
    generate_season_schedule,
    drivers,
    networks,
    sponsors,
    sponsor_prospects,
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
    APPROVAL_SLIP_FLOOR,
    BOARD_CONFIDENCE_TILT,
    BOARD_DISMISSAL_FLOOR,
    DRIVER_COUNCIL_TILT,
    LOBBY_OPPOSITION_TILT,
    LOBBY_SWING_DELTA,
    OWNER_COUNCIL_TILT,
    RULE_VOTE_TILT,
    approval_ratings,
    board_confidence_events,
    board_confidence_label,
    job_security_ratings,
    media_controversy_events,
    offseason_events,
    driver_council_chair,
    driver_council_mood,
    driver_council_seats,
    driver_council_tally,
    lobbying_events,
    owner_coalitions,
    owner_council_chair,
    owner_council_mood,
    owner_council_seats,
    owner_council_tally,
    coalition_label,
    postseason_events,
    preseason_events,
    proposal_coalitions,
    regular_season_events,
    rule_proposal_events,
    rule_vote_events,
    rule_vote_swing_seat,
    rule_vote_tally,
)
from game.events import resolve_event_choice
from game.models import (
    Driver,
    Team,
    SPONSOR_RENEWAL_MIN_SATISFACTION,
    TREND_HISTORY_SEASONS,
    TREND_LABELS,
    apply_controversy_shock,
    apply_objective_review,
    sponsor_pay_multiplier,
    sponsor_satisfaction_label,
)
from game.records import build_record_book
from game.policies import (
    current_policies,
    get_penalty_fine_amount,
    get_penalty_points_amount,
    get_manufacturer_points_by_position,
    get_playoff_field_size,
    get_playoff_race_count,
    get_points_by_position,
    get_points_speeding_penalty,
    get_policy_operating_cost,
    get_scoring_bonuses,
    load_policies,
    policy_label,
    reset_policies,
    uses_playoff,
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
    "sponsor_conflicts": [],
    "sponsor_walk_blocks": [],
    "treasury": 0,
    "naming_rights": None,
    "official_partners": [],
    "season_commercial_income": 0,
    "career_commercial_income": 0,
    "sponsor_market_log": [],
    "tv_rights": None,
    "season_tv_income": 0,
    "career_tv_income": 0,
    "season_tv_ratings": [],
    "season_tv_viewers": [],
    "last_tv_rating": None,
    "last_tv_viewers": None,
    "tv_rating_history": [],
    "tv_rating_trend": 0,
    "season_gate_attendance": [],
    "season_gate_fill": [],
    "last_gate_attendance": None,
    "last_gate_capacity": None,
    "last_gate_fill": None,
    "last_gate_draw": None,
    "gate_history": [],
    "gate_trend": 0,
    "season_media_stories": [],
    "last_media_stories": [],
    "season_press_conferences": [],
    "last_press_conference": None,
    "season_media_controversies": [],
    "last_media_controversy": None,
    "season_owner_councils": [],
    "last_owner_council": None,
    "season_driver_councils": [],
    "last_driver_council": None,
    "season_rule_proposals": [],
    "last_rule_proposal": None,
    "rule_docket": [],
    "season_rule_votes": [],
    "last_rule_vote": None,
    "season_lobbying": [],
    "last_lobbying": None,
    "approval": None,
    "approval_history": [],
    "job_security": None,
    "season_board_reviews": [],
    "last_board_review": None,
    "board_history": [],
    "dismissed": False,
    "dismissal": None,
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
ENDORSEMENT_MIN_INTEREST = 40
TEAM_SPONSOR_MIN_INTEREST = 48
UNSPONSORED_STIPEND_FACTOR = 0.35
LEAGUE_NAMING_MIN_INTEREST = 55
LEAGUE_PARTNER_MIN_INTEREST = 48
OFFICIAL_PARTNER_SLOTS = 2
SERIES_NAME_BASE = "Stock Car Series"
SPONSOR_MARKET_MIN = 8
SPONSOR_MARKET_MAX = 14
TV_RIGHTS_MIN_INTEREST = 55
TRACK_TYPE_TV_DRAW = {
    "Superspeedway": 8,
    "Short Track": 5,
    "Intermediate": 4,
    "Road Course": 3,
}
TRACK_TYPE_GATE_DRAW = {
    "Superspeedway": 3,
    "Intermediate": 5,
    "Short Track": 8,
    "Road Course": 2,
}
TRACK_TYPE_FILL_BIAS = {
    "Superspeedway": 0.90,
    "Intermediate": 1.00,
    "Short Track": 1.14,
    "Road Course": 0.86,
}
MEDIA_STORY_MAX = 3
SPONSOR_CONFLICT_CONDUCT_FLOOR = 40
SPONSOR_CONFLICT_SATISFACTION_FLOOR = 48
RULING_SPONSOR_SEVERITY = {
    "1": 10,
    "2": 3,
    "3": 1,
    "4": 2,
    "5": 12,
}


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

    sponsors.clear()
    sponsors.extend(create_initial_sponsors())

    sponsor_prospects.clear()
    sponsor_prospects.extend(create_sponsor_prospects())

    networks.clear()
    networks.extend(create_initial_networks())

    league["integrity"] = 70
    league["fan_interest"] = 65
    league["controversy"] = 20
    league["fines_collected"] = 0
    league["owner_pressure"] = 25
    league["driver_sentiment"] = 60
    league["sponsor_conflicts"] = []
    league["sponsor_walk_blocks"] = []
    league["treasury"] = 0
    league["naming_rights"] = None
    league["official_partners"] = []
    league["season_commercial_income"] = 0
    league["career_commercial_income"] = 0
    league["sponsor_market_log"] = []
    league["tv_rights"] = None
    league["season_tv_income"] = 0
    league["career_tv_income"] = 0
    league["season_tv_ratings"] = []
    league["season_tv_viewers"] = []
    league["last_tv_rating"] = None
    league["last_tv_viewers"] = None
    league["tv_rating_history"] = []
    league["tv_rating_trend"] = 0
    league["season_gate_attendance"] = []
    league["season_gate_fill"] = []
    league["last_gate_attendance"] = None
    league["last_gate_capacity"] = None
    league["last_gate_fill"] = None
    league["last_gate_draw"] = None
    league["gate_history"] = []
    league["gate_trend"] = 0
    league["season_media_stories"] = []
    league["last_media_stories"] = []
    league["season_press_conferences"] = []
    league["last_press_conference"] = None
    league["season_media_controversies"] = []
    league["last_media_controversy"] = None
    league["season_owner_councils"] = []
    league["last_owner_council"] = None
    league["season_driver_councils"] = []
    league["last_driver_council"] = None
    league["season_rule_proposals"] = []
    league["last_rule_proposal"] = None
    league["rule_docket"] = []
    league["season_rule_votes"] = []
    league["last_rule_vote"] = None
    league["season_lobbying"] = []
    league["last_lobbying"] = None
    league["approval"] = None
    league["approval_history"] = []
    league["job_security"] = None
    league["season_board_reviews"] = []
    league["last_board_review"] = None
    league["board_history"] = []
    league["dismissed"] = False
    league["dismissal"] = None

    reset_policies()

    championship_awarded = False
    calendar.current_season = 1
    calendar.career_seasons_total = 3
    calendar.enter_preseason()
    sync_calendar_aliases()
    assign_endorsement_deals(
        season=calendar.current_season,
        apply_signing_boost=False,
    )
    assign_team_sponsor_deals(
        season=calendar.current_season,
        apply_signing_boost=False,
    )
    assign_league_deals(
        season=calendar.current_season,
        apply_signing_boost=False,
    )
    assign_tv_rights(
        season=calendar.current_season,
        apply_signing_boost=False,
    )


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

    sponsors.clear()

    if restored_state.get("sponsors"):
        sponsors.extend(restored_state["sponsors"])
    else:
        sponsors.extend(create_initial_sponsors())

    sponsor_prospects.clear()
    if restored_state.get("sponsor_prospects") is not None:
        sponsor_prospects.extend(restored_state["sponsor_prospects"])
    else:
        sponsor_prospects.extend(create_sponsor_prospects())

    networks.clear()
    if restored_state.get("networks") is not None:
        networks.extend(restored_state["networks"])
    else:
        networks.extend(create_initial_networks())

    league.clear()
    league.update(restored_state["league"])
    league.setdefault("owner_pressure", 25)
    league.setdefault("driver_sentiment", 60)
    league.setdefault("sponsor_conflicts", [])
    league.setdefault("sponsor_walk_blocks", [])
    league.setdefault("treasury", 0)
    league.setdefault("official_partners", [])
    league.setdefault("season_commercial_income", 0)
    league.setdefault("career_commercial_income", 0)
    league.setdefault("sponsor_market_log", [])
    league.setdefault("season_tv_income", 0)
    league.setdefault("career_tv_income", 0)
    if not isinstance(league.get("season_tv_ratings"), list):
        league["season_tv_ratings"] = []
    if not isinstance(league.get("season_tv_viewers"), list):
        league["season_tv_viewers"] = []
    league.setdefault("last_tv_rating", None)
    league.setdefault("last_tv_viewers", None)
    if not isinstance(league.get("tv_rating_history"), list):
        league["tv_rating_history"] = []
    league.setdefault("tv_rating_trend", 0)
    if not isinstance(league.get("season_gate_attendance"), list):
        league["season_gate_attendance"] = []
    if not isinstance(league.get("season_gate_fill"), list):
        league["season_gate_fill"] = []
    league.setdefault("last_gate_attendance", None)
    league.setdefault("last_gate_capacity", None)
    league.setdefault("last_gate_fill", None)
    league.setdefault("last_gate_draw", None)
    if not isinstance(league.get("gate_history"), list):
        league["gate_history"] = []
    league.setdefault("gate_trend", 0)
    if not isinstance(league.get("season_media_stories"), list):
        league["season_media_stories"] = []
    if not isinstance(league.get("last_media_stories"), list):
        league["last_media_stories"] = []
    if not isinstance(league.get("season_press_conferences"), list):
        league["season_press_conferences"] = []
    league.setdefault("last_press_conference", None)
    if not isinstance(league.get("season_media_controversies"), list):
        league["season_media_controversies"] = []
    league.setdefault("last_media_controversy", None)
    if not isinstance(league.get("season_owner_councils"), list):
        league["season_owner_councils"] = []
    league.setdefault("last_owner_council", None)
    if not isinstance(league.get("season_driver_councils"), list):
        league["season_driver_councils"] = []
    league.setdefault("last_driver_council", None)
    if not isinstance(league.get("season_rule_proposals"), list):
        league["season_rule_proposals"] = []
    league.setdefault("last_rule_proposal", None)
    if not isinstance(league.get("rule_docket"), list):
        league["rule_docket"] = []
    if not isinstance(league.get("season_rule_votes"), list):
        league["season_rule_votes"] = []
    league.setdefault("last_rule_vote", None)
    if not isinstance(league.get("season_lobbying"), list):
        league["season_lobbying"] = []
    league.setdefault("last_lobbying", None)
    league.setdefault("approval", None)
    if not isinstance(league.get("approval_history"), list):
        league["approval_history"] = []
    league.setdefault("job_security", None)
    if not isinstance(league.get("season_board_reviews"), list):
        league["season_board_reviews"] = []
    league.setdefault("last_board_review", None)
    if not isinstance(league.get("board_history"), list):
        league["board_history"] = []
    league.setdefault("dismissed", False)
    league.setdefault("dismissal", None)
    had_naming = "naming_rights" in restored_state["league"]
    league.setdefault("naming_rights", None)
    had_tv = "tv_rights" in restored_state["league"]
    league.setdefault("tv_rights", None)

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

    if not any(driver.has_endorsement() for driver in drivers):
        assign_endorsement_deals(
            season=calendar.current_season,
            apply_signing_boost=False,
        )

    if not any(team.has_primary_sponsor() for team in teams):
        assign_team_sponsor_deals(
            season=calendar.current_season,
            apply_signing_boost=False,
        )

    if not had_naming:
        assign_league_deals(
            season=calendar.current_season,
            apply_signing_boost=False,
        )

    if not had_tv:
        assign_tv_rights(
            season=calendar.current_season,
            apply_signing_boost=False,
        )


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
        sponsors=sponsors,
        sponsor_prospects=sponsor_prospects,
        networks=networks,
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

    approval = refresh_approval_ratings()
    if approval["overall"] < APPROVAL_SLIP_FLOOR:
        alerts.append("Approval is slipping")

    security = refresh_job_security()
    if security["threatened"]:
        alerts.append("Dismissal risk is high")
    elif security["review"]:
        alerts.append("The board is watching")

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

    unsponsored_teams = [
        team for team in teams if not team.has_primary_sponsor()
    ]

    if unsponsored_teams:
        names = ", ".join(team.name for team in unsponsored_teams)
        alerts.append(f"No main sponsor: {names}")

    restless_titles = [
        team
        for team in teams
        if (
            team.has_primary_sponsor()
            and team.primary_sponsor.get("satisfaction", 55) < 50
        )
    ]

    if restless_titles:
        names = ", ".join(
            f"{team.primary_sponsor['sponsor']} ({team.name})"
            for team in restless_titles
        )
        alerts.append(f"Restless title sponsors: {names}")

    restless_deals = [
        driver
        for driver in drivers
        if (
            driver.has_endorsement()
            and driver.endorsement.get("satisfaction", 55) < 50
        )
    ]

    if restless_deals:
        names = ", ".join(
            f"{driver.endorsement['sponsor']} ({driver.name})"
            for driver in restless_deals
        )
        alerts.append(f"Restless endorsements: {names}")

    walked = [
        item
        for item in league.get("sponsor_conflicts") or []
        if item.get("season") == calendar.current_season
    ]

    if walked:
        names = ", ".join(
            f"{item['sponsor']} left {item['party']}"
            for item in walked
        )
        alerts.append(f"Sponsor walked: {names}")

    if not has_naming_rights():
        alerts.append("No series sponsor")

    naming = league.get("naming_rights") or {}
    if naming.get("sponsor") and naming.get("satisfaction", 55) < 50:
        alerts.append(
            f"Restless series sponsor: {naming['sponsor']}"
        )

    if not has_tv_rights():
        alerts.append("No TV deal")

    tv_deal = league.get("tv_rights") or {}
    if tv_deal.get("network") and tv_deal.get("satisfaction", 55) < 50:
        alerts.append(
            f"Restless TV partner: {tv_deal['network']}"
        )

    last_rating = league.get("last_tv_rating")
    if last_rating is not None and last_rating < 42:
        alerts.append("TV ratings are soft")

    if league.get("tv_rating_trend", 0) <= -1:
        alerts.append("TV ratings are sliding")

    if league.get("last_media_controversy"):
        alerts.append("Media scandal is active")

    last_council = league.get("last_owner_council") or {}
    if last_council.get("passed"):
        alerts.append("Owner council issued a rebuke")
    elif owner_council_mood(teams, league.get("owner_pressure", 0)) == "restless":
        alerts.append("Owner council is restless")

    last_garage = league.get("last_driver_council") or {}
    if last_garage.get("protested"):
        alerts.append("Driver council filed a protest")
    elif driver_council_mood(drivers, league.get("driver_sentiment", 60)) == "restless":
        alerts.append("Driver council is restless")

    if league.get("rule_docket"):
        alerts.append("Rule proposal on the docket")

    last_fill = league.get("last_gate_fill")
    if last_fill is not None and last_fill < 55:
        alerts.append("The gate is soft")

    if league.get("gate_trend", 0) <= -1:
        alerts.append("Attendance is sliding")

    if len(sponsors) <= SPONSOR_MARKET_MIN:
        alerts.append("Sponsor market is thin")

    season_moves = [
        item
        for item in league.get("sponsor_market_log") or []
        if item.get("season") == calendar.current_season
    ]
    left = [item["name"] for item in season_moves if item.get("action") == "left"]
    entered = [
        item["name"] for item in season_moves if item.get("action") == "entered"
    ]
    if left or entered:
        parts = []
        if left:
            parts.append("left " + ", ".join(left))
        if entered:
            parts.append("entered " + ", ".join(entered))
        alerts.append("Sponsor market: " + "; ".join(parts))

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


def ranked_sponsor_interest(team):
    """Return (score, sponsor) pairs for a team, strongest first."""

    team_drivers = get_team_drivers(team.name)
    season_wins = get_team_season_wins(team.name)

    ranked = [
        (
            sponsor.interest_in_team(team, team_drivers, season_wins),
            sponsor,
        )
        for sponsor in sponsors
    ]
    ranked.sort(key=lambda item: (-item[0], item[1].name))
    return ranked


def top_sponsors_for_team(team, count=3):
    """Return the brands most interested in a team."""

    return ranked_sponsor_interest(team)[:count]


def market_interest_multiplier(team):
    """Scale sponsorship by how well the team matches the market."""

    ranked = ranked_sponsor_interest(team)

    if not ranked:
        return 1.0

    top_scores = [score for score, _sponsor in ranked[:3]]
    average = sum(top_scores) / len(top_scores)
    return 0.72 + (average / 100.0) * 0.56


def best_team_for_sponsor(sponsor):
    """Return (team, score) for the team this brand likes most."""

    if not teams:
        return None, 0

    scored = [
        (
            sponsor.interest_in_team(
                team,
                get_team_drivers(team.name),
                get_team_season_wins(team.name),
            ),
            team,
        )
        for team in teams
    ]
    scored.sort(key=lambda item: (-item[0], item[1].name))
    score, team = scored[0]
    return team, score


def driver_backed_by(sponsor):
    """Return the active driver this brand personally sponsors, if any."""

    for driver in drivers:
        if (
            driver.has_endorsement()
            and driver.endorsement["sponsor"] == sponsor.name
        ):
            return driver

    return None


def taken_endorsement_sponsors():
    """Return sponsor names already on an active driver deal."""

    return {
        driver.endorsement["sponsor"]
        for driver in drivers
        if driver.has_endorsement()
    }


def endorsement_deal_terms(sponsor, driver):
    """Return (interest, annual value, years) for a personal deal."""

    interest = sponsor.interest_in_driver(driver)
    share = 0.08 + (interest / 100.0) * 0.12
    value = int(round(sponsor.spending_power() * share / 1_000) * 1_000)
    value = max(50_000, value)

    if interest >= 72:
        years = 3
    elif interest >= 60:
        years = 2
    else:
        years = 1

    if driver.is_rookie:
        value = max(50_000, int(round(value * 0.75 / 1_000) * 1_000))
        years = min(years, 2)

    return interest, value, years


def assign_endorsement_deals(season, apply_signing_boost=True, blocked=None):
    """Match free brands to unsigned drivers, stars picking first."""

    signed = []
    taken = taken_endorsement_sponsors()
    blocked = blocked or set()
    available = {
        sponsor.name: sponsor
        for sponsor in sponsors
        if sponsor.name not in taken
    }
    unsigned = [
        driver for driver in drivers if not driver.has_endorsement()
    ]
    unsigned.sort(
        key=lambda driver: (
            driver.popularity,
            driver.overall_rating(),
            driver.career_wins,
        ),
        reverse=True,
    )

    for driver in unsigned:
        best_sponsor = None
        best_score = ENDORSEMENT_MIN_INTEREST - 1

        for sponsor in available.values():
            if (sponsor.name, driver.name) in blocked:
                continue

            score = sponsor.interest_in_driver(driver)

            if score < ENDORSEMENT_MIN_INTEREST:
                continue

            if best_sponsor is None or score > best_score:
                best_sponsor = sponsor
                best_score = score
            elif score == best_score and sponsor.name < best_sponsor.name:
                best_sponsor = sponsor

        if best_sponsor is None:
            continue

        interest, value, years = endorsement_deal_terms(best_sponsor, driver)
        driver.sign_endorsement(best_sponsor.name, value, years, season)

        if apply_signing_boost:
            driver.morale = clamp(driver.morale + 3)
            driver.contract_satisfaction = clamp(
                driver.contract_satisfaction + 4
            )
            popularity_gain = (
                2 if best_sponsor.popularity_preference >= 70 else 1
            )
            driver.popularity = clamp(driver.popularity + popularity_gain)

        del available[best_sponsor.name]
        signed.append(
            {
                "driver": driver,
                "sponsor": best_sponsor,
                "interest": interest,
                "value": value,
                "years": years,
            }
        )

    return signed


def get_sponsor(name):
    """Return a sponsor company by name, or None."""

    for sponsor in sponsors:
        if sponsor.name == name:
            return sponsor

    return None


def get_network(name):
    """Return a television network by name, or None."""

    for network in networks:
        if network.name == name:
            return network

    return None


def ensure_league_commercial_state():
    """Make sure league naming-rights, partner, TV, gate, media, press, scandal, and council slots exist."""

    if not isinstance(league.get("official_partners"), list):
        league["official_partners"] = []
    if "naming_rights" not in league:
        league["naming_rights"] = None
    league.setdefault("treasury", 0)
    league.setdefault("season_commercial_income", 0)
    league.setdefault("career_commercial_income", 0)
    if not isinstance(league.get("sponsor_market_log"), list):
        league["sponsor_market_log"] = []
    if "tv_rights" not in league:
        league["tv_rights"] = None
    league.setdefault("season_tv_income", 0)
    league.setdefault("career_tv_income", 0)
    if not isinstance(league.get("season_tv_ratings"), list):
        league["season_tv_ratings"] = []
    if not isinstance(league.get("season_tv_viewers"), list):
        league["season_tv_viewers"] = []
    league.setdefault("last_tv_rating", None)
    league.setdefault("last_tv_viewers", None)
    if not isinstance(league.get("tv_rating_history"), list):
        league["tv_rating_history"] = []
    league.setdefault("tv_rating_trend", 0)
    if not isinstance(league.get("season_gate_attendance"), list):
        league["season_gate_attendance"] = []
    if not isinstance(league.get("season_gate_fill"), list):
        league["season_gate_fill"] = []
    league.setdefault("last_gate_attendance", None)
    league.setdefault("last_gate_capacity", None)
    league.setdefault("last_gate_fill", None)
    league.setdefault("last_gate_draw", None)
    if not isinstance(league.get("gate_history"), list):
        league["gate_history"] = []
    league.setdefault("gate_trend", 0)
    if not isinstance(league.get("season_media_stories"), list):
        league["season_media_stories"] = []
    if not isinstance(league.get("last_media_stories"), list):
        league["last_media_stories"] = []
    if not isinstance(league.get("season_press_conferences"), list):
        league["season_press_conferences"] = []
    league.setdefault("last_press_conference", None)
    if not isinstance(league.get("season_media_controversies"), list):
        league["season_media_controversies"] = []
    league.setdefault("last_media_controversy", None)
    if not isinstance(league.get("season_owner_councils"), list):
        league["season_owner_councils"] = []
    league.setdefault("last_owner_council", None)
    if not isinstance(league.get("season_driver_councils"), list):
        league["season_driver_councils"] = []
    league.setdefault("last_driver_council", None)
    if not isinstance(league.get("season_rule_proposals"), list):
        league["season_rule_proposals"] = []
    league.setdefault("last_rule_proposal", None)
    if not isinstance(league.get("rule_docket"), list):
        league["rule_docket"] = []
    if not isinstance(league.get("season_rule_votes"), list):
        league["season_rule_votes"] = []
    league.setdefault("last_rule_vote", None)
    if not isinstance(league.get("season_lobbying"), list):
        league["season_lobbying"] = []
    league.setdefault("last_lobbying", None)
    league.setdefault("approval", None)
    if not isinstance(league.get("approval_history"), list):
        league["approval_history"] = []
    league.setdefault("job_security", None)
    if not isinstance(league.get("season_board_reviews"), list):
        league["season_board_reviews"] = []
    league.setdefault("last_board_review", None)
    if not isinstance(league.get("board_history"), list):
        league["board_history"] = []
    league.setdefault("dismissed", False)
    league.setdefault("dismissal", None)


def has_naming_rights():
    """Return whether the series currently has a naming-rights partner."""

    deal = league.get("naming_rights") or {}
    return bool(deal.get("sponsor"))


def series_name():
    """Return the series name, including naming rights when signed."""

    if has_naming_rights():
        return f"{league['naming_rights']['sponsor']} {SERIES_NAME_BASE}"

    return SERIES_NAME_BASE


def league_deal_label(deal):
    """Return a readable naming-rights or official-partner line."""

    if not deal or not deal.get("sponsor"):
        return "unsponsored"

    year_word = "yr" if deal["years"] == 1 else "yrs"
    mood = sponsor_satisfaction_label(deal.get("satisfaction", 55))
    extra = f", {deal['category']}" if deal.get("category") else ""
    return (
        f"{deal['sponsor']}{extra} "
        f"(${deal['value']:,}/yr, {deal['years']} {year_word}) "
        f"— {mood}"
    )


def live_league_deals():
    """Return (party, deal, kind) tuples for signed league commercial deals."""

    ensure_league_commercial_state()
    deals = []

    if has_naming_rights():
        deals.append(("the series", league["naming_rights"], "league"))

    for partner in league["official_partners"]:
        if partner and partner.get("sponsor"):
            category = partner.get("category") or "partner"
            deals.append(
                (f"official {category}", partner, "league")
            )

    return deals


def league_objective_signals():
    """Return performance, exposure, and conduct signals for the series."""

    fan = league.get("fan_interest", 65)
    integrity = league.get("integrity", 70)
    controversy = league.get("controversy", 20)
    performance = clamp(fan)
    exposure = clamp(fan * 0.70 + (100 - controversy) * 0.30)
    conduct = clamp((integrity + (100 - controversy)) / 2)
    return round(performance), round(exposure), round(conduct)


def team_objective_signals(team):
    """Return performance, exposure, and conduct signals for a team."""

    team_drivers = get_team_drivers(team.name)
    wins = get_team_season_wins(team.name)
    org_champ = get_team_champion()
    champ_bonus = 10 if org_champ is not None and org_champ.name == team.name else 0

    performance = clamp(
        38
        + wins * 9
        + champ_bonus
        + team.performance_trend * 6
        + (team.car_rating - 80)
    )

    if team_drivers:
        popularity = sum(d.popularity for d in team_drivers) / len(team_drivers)
        reputation = sum(d.reputation for d in team_drivers) / len(team_drivers)
        credibility = sum(d.credibility for d in team_drivers) / len(team_drivers)
        warnings = sum(d.warnings for d in team_drivers)
        suspensions = sum(d.suspensions for d in team_drivers)
        dnfs = sum(d.dnfs for d in team_drivers)
    else:
        popularity = 55
        reputation = 55
        credibility = 55
        warnings = 0
        suspensions = 0
        dnfs = 0

    exposure = clamp(popularity)
    conduct = clamp(
        (reputation + credibility) / 2
        - warnings * 3
        - suspensions * 8
        - dnfs * 1.5
    )
    return (
        round(performance),
        round(exposure),
        round(conduct),
    )


def driver_objective_signals(driver):
    """Return performance, exposure, and conduct signals for a driver."""

    performance = clamp(
        36
        + driver.wins * 11
        + min(driver.points // 18, 28)
    )
    exposure = clamp(driver.popularity * 0.70 + driver.media_skill * 0.30)
    conduct = clamp(
        (driver.reputation + driver.credibility) / 2
        - driver.warnings * 5
        - driver.suspensions * 10
        - (4 if driver.aggression >= 80 else 0)
    )
    return round(performance), round(exposure), round(conduct)


def review_one_deal(party_name, deal, kind):
    """Score one signed deal and update satisfaction. Return a report dict."""

    sponsor = get_sponsor(deal["sponsor"])

    if sponsor is None:
        return None

    if kind == "team":
        team = get_team(party_name)
        performance, exposure, conduct = team_objective_signals(team)
    elif kind == "league":
        performance, exposure, conduct = league_objective_signals()
    else:
        driver = get_driver(party_name)
        performance, exposure, conduct = driver_objective_signals(driver)

    breakdown = {
        "performance": performance,
        "exposure": exposure,
        "conduct": conduct,
    }
    delivery = sponsor.score_objectives(performance, exposure, conduct)
    previous, current, delta = apply_objective_review(deal, delivery, breakdown)
    return {
        "party": party_name,
        "kind": kind,
        "sponsor": sponsor,
        "focus": sponsor.primary_objective(),
        "delivery": delivery,
        "previous": previous,
        "satisfaction": current,
        "delta": delta,
        "breakdown": breakdown,
        "mood": sponsor_satisfaction_label(current),
        "multiplier": sponsor_pay_multiplier(current),
    }


def review_sponsor_objectives():
    """Grade signed brands on the season just completed."""

    print("\nSponsor Objectives")
    print("-" * 90)

    reports = []

    for team in teams:
        if team.has_primary_sponsor():
            report = review_one_deal(
                team.name,
                team.primary_sponsor,
                "team",
            )
            if report:
                reports.append(report)

    for driver in drivers:
        if driver.has_endorsement():
            report = review_one_deal(
                driver.name,
                driver.endorsement,
                "driver",
            )
            if report:
                reports.append(report)

    for party_name, deal, kind in live_league_deals():
        report = review_one_deal(party_name, deal, kind)
        if report:
            reports.append(report)

    if not reports:
        print("No signed sponsors to review.")
        return reports

    for report in reports:
        focus = report["focus"]
        breakdown = report["breakdown"]
        delta = report["delta"]
        sign = f"{delta:+d}" if delta else "0"
        bonus = int(round((report["multiplier"] - 1.0) * 100))
        if bonus > 0:
            pay_text = f"check {bonus:+d}%"
        elif bonus < 0:
            pay_text = f"check {bonus}%"
        else:
            pay_text = "check unchanged"
        print(
            f"- {report['sponsor'].name} / {report['party']}: "
            f"{report['mood']} ({report['satisfaction']}, {sign}) | "
            f"wants {focus} | "
            f"perf {breakdown['performance']}, "
            f"exposure {breakdown['exposure']}, "
            f"conduct {breakdown['conduct']} | "
            f"{pay_text}"
        )

    return reports


def ensure_sponsor_conflict_state():
    """Make sure career league state has conflict lists."""

    if not isinstance(league.get("sponsor_conflicts"), list):
        league["sponsor_conflicts"] = []
    if not isinstance(league.get("sponsor_walk_blocks"), list):
        league["sponsor_walk_blocks"] = []


def walk_block_set():
    """Return (sponsor, party) pairs that will not rematch this offseason."""

    ensure_sponsor_conflict_state()
    return {
        (item[0], item[1])
        for item in league["sponsor_walk_blocks"]
        if item and len(item) >= 2
    }


def add_walk_block(sponsor_name, party_name):
    """Remember that this brand walked on this team or driver."""

    ensure_sponsor_conflict_state()
    pair = [sponsor_name, party_name]
    if pair not in league["sponsor_walk_blocks"]:
        league["sponsor_walk_blocks"].append(pair)


def record_sponsor_conflict(record):
    """Append a withdrawal to the career conflict log."""

    ensure_sponsor_conflict_state()
    league["sponsor_conflicts"].append(record)


def current_season_conflicts():
    """Return withdrawals recorded during the active season."""

    ensure_sponsor_conflict_state()
    season = calendar.current_season
    return [
        item
        for item in league["sponsor_conflicts"]
        if item.get("season") == season
    ]


def deal_conflict_signals(kind, party_name):
    """Return satisfaction, conduct, and scandal extras for a signed deal."""

    if kind == "team":
        team = get_team(party_name)
        deal = team.primary_sponsor or {}
        team_drivers = get_team_drivers(team.name)
        last = deal.get("last_objectives") or {}
        conduct = last.get("conduct")
        if conduct is None:
            _, _, conduct = team_objective_signals(team)
        return {
            "satisfaction": deal.get("satisfaction", 55),
            "conduct": conduct,
            "warnings": sum(driver.warnings for driver in team_drivers),
            "suspensions": sum(driver.suspensions for driver in team_drivers),
            "distress": team.financial_distress_level,
            "years": deal.get("years", 0),
            "sponsor_name": deal.get("sponsor"),
            "value": deal.get("value", 0),
        }

    driver = get_driver(party_name)
    deal = driver.endorsement or {}
    last = deal.get("last_objectives") or {}
    conduct = last.get("conduct")
    if conduct is None:
        _, _, conduct = driver_objective_signals(driver)
    return {
        "satisfaction": deal.get("satisfaction", 55),
        "conduct": conduct,
        "warnings": driver.warnings,
        "suspensions": driver.suspensions,
        "distress": 0,
        "years": deal.get("years", 0),
        "sponsor_name": deal.get("sponsor"),
        "value": deal.get("value", 0),
    }


def sponsor_conflict_heat(sponsor, signals, severity=0):
    """Score how badly a live deal is on fire for this brand."""

    heat = 0
    heat += max(0, SPONSOR_CONFLICT_SATISFACTION_FLOOR - signals["satisfaction"])
    heat += max(0, SPONSOR_CONFLICT_CONDUCT_FLOOR - signals["conduct"])
    heat += signals.get("warnings", 0)
    heat += signals.get("suspensions", 0) * 6
    heat += max(0, league.get("controversy", 0) - 50) // 4
    if signals.get("distress", 0) >= 3:
        heat += 6
    heat += max(0, int(severity))
    return round(heat * (0.50 + sponsor.controversy_sensitivity()))


def should_sponsor_withdraw(sponsor, signals, severity=0, immediate=False):
    """Return (walks, heat, threshold) for a live deal."""

    heat = sponsor_conflict_heat(sponsor, signals, severity)
    threshold = sponsor.conflict_walk_threshold()

    if heat < threshold:
        return False, heat, threshold

    if immediate:
        walks = severity >= 8 or signals["satisfaction"] < 40
    else:
        walks = signals["satisfaction"] < 50 or signals["conduct"] < 30

    return walks, heat, threshold


def withdraw_team_sponsor(team, reason, heat, threshold):
    """Pull a title deal mid-contract and log the walk."""

    deal = team.primary_sponsor
    sponsor_name = deal["sponsor"]
    record = {
        "season": calendar.current_season,
        "kind": "team",
        "sponsor": sponsor_name,
        "party": team.name,
        "reason": reason,
        "heat": heat,
        "threshold": threshold,
        "years_left": deal.get("years", 0),
        "satisfaction": deal.get("satisfaction", 55),
        "value": deal.get("value", 0),
    }
    add_walk_block(sponsor_name, team.name)
    record_sponsor_conflict(record)
    team.clear_primary_sponsor(penalize=True)
    league["controversy"] = clamp(league["controversy"] + 4)
    league["fan_interest"] = clamp(league["fan_interest"] - 2)
    league["owner_pressure"] = clamp(league.get("owner_pressure", 25) + 4)
    return record


def withdraw_driver_endorsement(driver, reason, heat, threshold):
    """Pull a personal deal mid-contract and log the walk."""

    deal = driver.endorsement
    sponsor_name = deal["sponsor"]
    record = {
        "season": calendar.current_season,
        "kind": "driver",
        "sponsor": sponsor_name,
        "party": driver.name,
        "reason": reason,
        "heat": heat,
        "threshold": threshold,
        "years_left": deal.get("years", 0),
        "satisfaction": deal.get("satisfaction", 55),
        "value": deal.get("value", 0),
    }
    add_walk_block(sponsor_name, driver.name)
    record_sponsor_conflict(record)
    driver.clear_endorsement()
    driver.morale = clamp(driver.morale - 6)
    driver.popularity = clamp(driver.popularity - 2)
    driver.contract_satisfaction = clamp(driver.contract_satisfaction - 5)
    league["controversy"] = clamp(league["controversy"] + 2)
    return record


def maybe_withdraw_deal(kind, party_name, reason, severity=0, immediate=False):
    """Withdraw one deal if conflict heat clears the brand's threshold."""

    if kind == "team":
        team = get_team(party_name)
        if not team.has_primary_sponsor():
            return None
        sponsor = get_sponsor(team.primary_sponsor["sponsor"])
    else:
        driver = get_driver(party_name)
        if not driver.has_endorsement():
            return None
        sponsor = get_sponsor(driver.endorsement["sponsor"])

    if sponsor is None:
        return None

    signals = deal_conflict_signals(kind, party_name)
    walks, heat, threshold = should_sponsor_withdraw(
        sponsor,
        signals,
        severity=severity,
        immediate=immediate,
    )

    if not walks:
        return None

    if kind == "team":
        return withdraw_team_sponsor(team, reason, heat, threshold)

    return withdraw_driver_endorsement(driver, reason, heat, threshold)


def apply_ruling_sponsor_fallout(choice, driver, team):
    """Let signed brands react to a commissioner incident ruling."""

    severity = RULING_SPONSOR_SEVERITY.get(choice, 0)

    if severity <= 0:
        return

    reasons = {
        "1": "unpunished incident",
        "2": "official warning",
        "3": "on-track fine",
        "4": "points penalty",
        "5": "race suspension",
    }
    reason = reasons.get(choice, "incident")

    candidates = []

    if driver.has_endorsement():
        candidates.append(("driver", driver.name, driver.endorsement))
    if team.has_primary_sponsor():
        candidates.append(("team", team.name, team.primary_sponsor))

    for kind, party_name, deal in candidates:
        sponsor = get_sponsor(deal["sponsor"])
        if sponsor is None:
            continue

        shock = max(1, round(severity * sponsor.controversy_sensitivity()))
        previous, current, delta = apply_controversy_shock(deal, shock)
        print(
            f"{sponsor.name} ({sponsor.risk_posture()}) took the {reason} "
            f"hard: {sponsor_satisfaction_label(previous)} "
            f"{previous} → {sponsor_satisfaction_label(current)} "
            f"{current} ({delta:+d})."
        )

        if severity >= 8:
            if kind == "team" and deal.get("satisfaction", 55) >= 40:
                continue
            record = maybe_withdraw_deal(
                kind,
                party_name,
                reason,
                severity=severity,
                immediate=True,
            )
            if record:
                year_word = "year" if record["years_left"] == 1 else "years"
                print(
                    f"{record['sponsor']} withdrew from {record['party']} "
                    f"with {record['years_left']} {year_word} left "
                    f"(heat {record['heat']}/{record['threshold']})."
                )


def resolve_sponsor_conflicts():
    """Let scandalized brands pull live deals after the season review."""

    print("\nSponsor Conflicts")
    print("-" * 90)

    withdrawals = []

    for team in list(teams):
        if team.has_primary_sponsor():
            record = maybe_withdraw_deal(
                "team",
                team.name,
                "season controversy",
            )
            if record:
                withdrawals.append(record)

    for driver in list(drivers):
        if driver.has_endorsement():
            record = maybe_withdraw_deal(
                "driver",
                driver.name,
                "season controversy",
            )
            if record:
                withdrawals.append(record)

    for party_name, deal, _kind in live_league_deals():
        record = maybe_withdraw_league_deal(
            party_name,
            deal,
            "season controversy",
        )
        if record:
            withdrawals.append(record)

    if not withdrawals:
        print("No signed sponsors walked away.")
        return withdrawals

    for record in withdrawals:
        year_word = "year" if record["years_left"] == 1 else "years"
        print(
            f"- {record['sponsor']} withdrew from {record['party']} "
            f"({record['kind']}, {record['reason']}, "
            f"{record['years_left']} {year_word} left, "
            f"heat {record['heat']}/{record['threshold']})"
        )

    return withdrawals


def team_titled_by(sponsor):
    """Return the team this brand holds as main sponsor, if any."""

    for team in teams:
        if (
            team.has_primary_sponsor()
            and team.primary_sponsor["sponsor"] == sponsor.name
        ):
            return team

    return None


def taken_team_sponsors():
    """Return sponsor names already on a team main-sponsor contract."""

    return {
        team.primary_sponsor["sponsor"]
        for team in teams
        if team.has_primary_sponsor()
    }


def team_sponsor_interest(sponsor, team):
    """Score a brand's interest in a team, with distress penalties."""

    score = sponsor.interest_in_team(
        team,
        get_team_drivers(team.name),
        get_team_season_wins(team.name),
    )

    if team.financial_distress_level >= 3:
        score -= 12
    elif team.financial_distress_level >= 2:
        score -= 6

    return clamp(score)


def team_sponsor_deal_terms(sponsor, team):
    """Return (interest, annual value, years) for a main-sponsor contract."""

    interest = team_sponsor_interest(sponsor, team)
    share = 0.75 + (interest / 100.0) * 0.55
    value = int(round(sponsor.spending_power() * share / 1_000) * 1_000)
    value = max(250_000, value)

    if team.financial_distress_level >= 3:
        value = int(value * 0.75)
    elif team.financial_distress_level >= 2:
        value = int(value * 0.90)

    if interest >= 70:
        years = 4
    elif interest >= 58:
        years = 3
    else:
        years = 2

    return interest, value, years


def assign_team_sponsor_deals(season, apply_signing_boost=True, blocked=None):
    """Match free brands to teams without a main sponsor, prestige first."""

    signed = []
    taken = taken_team_sponsors()
    blocked = blocked or set()
    available = {
        sponsor.name: sponsor
        for sponsor in sponsors
        if sponsor.name not in taken
    }
    unsigned = [
        team for team in teams if not team.has_primary_sponsor()
    ]
    unsigned.sort(
        key=lambda team: (
            team.prestige,
            team.sponsor_appeal(),
            team.championships,
        ),
        reverse=True,
    )

    for team in unsigned:
        best_sponsor = None
        best_score = TEAM_SPONSOR_MIN_INTEREST - 1

        for sponsor in available.values():
            if (sponsor.name, team.name) in blocked:
                continue

            score = team_sponsor_interest(sponsor, team)

            if score < TEAM_SPONSOR_MIN_INTEREST:
                continue

            if best_sponsor is None or score > best_score:
                best_sponsor = sponsor
                best_score = score
            elif score == best_score and sponsor.name < best_sponsor.name:
                best_sponsor = sponsor

        if best_sponsor is None:
            continue

        interest, value, years = team_sponsor_deal_terms(best_sponsor, team)
        team.sign_primary_sponsor(best_sponsor.name, value, years, season)

        if apply_signing_boost:
            team.prestige = clamp(team.prestige + 2)
            team.owner.patience = clamp(team.owner.patience + 2)
            team.owner.pressure = clamp(team.owner.pressure - 3)

        del available[best_sponsor.name]
        signed.append(
            {
                "team": team,
                "sponsor": best_sponsor,
                "interest": interest,
                "value": value,
                "years": years,
            }
        )

    return signed


def taken_league_sponsors():
    """Return sponsor names already on a league commercial deal."""

    ensure_league_commercial_state()
    names = set()

    if has_naming_rights():
        names.add(league["naming_rights"]["sponsor"])

    for partner in league["official_partners"]:
        if partner and partner.get("sponsor"):
            names.add(partner["sponsor"])

    return names


def league_naming_terms(sponsor):
    """Return (interest, annual value, years) for series naming rights."""

    interest = sponsor.interest_in_league(league)
    share = 1.35 + (interest / 100.0) * 0.70
    value = int(round(sponsor.spending_power() * share / 1_000) * 1_000)
    value = max(750_000, value)

    if interest >= 75:
        years = 5
    elif interest >= 62:
        years = 4
    else:
        years = 3

    return interest, value, years


def league_partner_terms(sponsor):
    """Return (interest, annual value, years) for an official series partner."""

    interest = sponsor.interest_in_league(league)
    share = 0.22 + (interest / 100.0) * 0.20
    value = int(round(sponsor.spending_power() * share / 1_000) * 1_000)
    value = max(150_000, value)

    if interest >= 70:
        years = 4
    elif interest >= 58:
        years = 3
    else:
        years = 2

    return interest, value, years


def make_league_deal(sponsor, value, years, season, role, category=None):
    """Build a naming-rights or official-partner contract dict."""

    deal = {
        "sponsor": sponsor.name,
        "role": role,
        "value": int(value),
        "years": int(years),
        "signed_season": season,
        "satisfaction": 55,
    }

    if category:
        deal["category"] = category

    return deal


def pick_league_sponsor(min_interest, blocked, taken, used_industries=None):
    """Return the best free brand for a league commercial slot."""

    used_industries = used_industries or set()
    best_sponsor = None
    best_score = min_interest - 1

    for sponsor in sponsors:
        if sponsor.name in taken:
            continue
        if (sponsor.name, "the series") in blocked:
            continue
        if (sponsor.name, "official partner") in blocked:
            continue
        if sponsor.industry in used_industries:
            continue

        score = sponsor.interest_in_league(league)

        if score < min_interest:
            continue

        if best_sponsor is None or score > best_score:
            best_sponsor = sponsor
            best_score = score
        elif score == best_score and sponsor.name < best_sponsor.name:
            best_sponsor = sponsor

    return best_sponsor, best_score


def assign_league_deals(season, apply_signing_boost=True, blocked=None):
    """Fill empty naming-rights and official-partner slots."""

    ensure_league_commercial_state()
    blocked = blocked or set()
    signed = []
    taken = taken_league_sponsors()

    if not has_naming_rights():
        sponsor, interest = pick_league_sponsor(
            LEAGUE_NAMING_MIN_INTEREST,
            blocked,
            taken,
        )
        if sponsor is not None:
            interest, value, years = league_naming_terms(sponsor)
            league["naming_rights"] = make_league_deal(
                sponsor,
                value,
                years,
                season,
                "naming",
            )
            taken.add(sponsor.name)
            if apply_signing_boost:
                league["fan_interest"] = clamp(league["fan_interest"] + 3)
            signed.append(
                {
                    "role": "naming",
                    "sponsor": sponsor,
                    "interest": interest,
                    "value": value,
                    "years": years,
                }
            )

    used_industries = {
        partner.get("category")
        for partner in league["official_partners"]
        if partner and partner.get("category")
    }

    while len(league["official_partners"]) < OFFICIAL_PARTNER_SLOTS:
        sponsor, interest = pick_league_sponsor(
            LEAGUE_PARTNER_MIN_INTEREST,
            blocked,
            taken,
            used_industries,
        )
        if sponsor is None:
            sponsor, interest = pick_league_sponsor(
                LEAGUE_PARTNER_MIN_INTEREST,
                blocked,
                taken,
            )
        if sponsor is None:
            break

        interest, value, years = league_partner_terms(sponsor)
        deal = make_league_deal(
            sponsor,
            value,
            years,
            season,
            "official",
            category=sponsor.industry,
        )
        league["official_partners"].append(deal)
        taken.add(sponsor.name)
        used_industries.add(sponsor.industry)
        signed.append(
            {
                "role": "official",
                "sponsor": sponsor,
                "interest": interest,
                "value": value,
                "years": years,
                "category": sponsor.industry,
            }
        )

    return signed


def league_deal_signals(deal):
    """Return satisfaction and scandal extras for a league commercial deal."""

    last = deal.get("last_objectives") or {}
    conduct = last.get("conduct")
    if conduct is None:
        _, _, conduct = league_objective_signals()

    return {
        "satisfaction": deal.get("satisfaction", 55),
        "conduct": conduct,
        "warnings": 0,
        "suspensions": 0,
        "distress": 3 if league.get("controversy", 0) >= 55 else 0,
        "years": deal.get("years", 0),
        "sponsor_name": deal.get("sponsor"),
        "value": deal.get("value", 0),
    }


def drop_league_deal(deal):
    """Remove a naming-rights or official-partner contract."""

    ensure_league_commercial_state()

    if has_naming_rights() and league["naming_rights"] is deal:
        league["naming_rights"] = None
        return

    league["official_partners"] = [
        item
        for item in league["official_partners"]
        if item is not deal
    ]


def withdraw_league_deal(party_name, deal, reason, heat, threshold):
    """Pull a series commercial deal mid-contract and log the walk."""

    sponsor_name = deal["sponsor"]
    record = {
        "season": calendar.current_season,
        "kind": "league",
        "sponsor": sponsor_name,
        "party": party_name,
        "reason": reason,
        "heat": heat,
        "threshold": threshold,
        "years_left": deal.get("years", 0),
        "satisfaction": deal.get("satisfaction", 55),
        "value": deal.get("value", 0),
    }
    add_walk_block(sponsor_name, "the series")
    add_walk_block(sponsor_name, "official partner")
    record_sponsor_conflict(record)
    drop_league_deal(deal)

    if deal.get("role") == "naming":
        league["controversy"] = clamp(league["controversy"] + 5)
        league["fan_interest"] = clamp(league["fan_interest"] - 4)
    else:
        league["controversy"] = clamp(league["controversy"] + 2)
        league["fan_interest"] = clamp(league["fan_interest"] - 1)

    return record


def maybe_withdraw_league_deal(party_name, deal, reason, severity=0):
    """Withdraw a league deal if conflict heat clears the brand's threshold."""

    sponsor = get_sponsor(deal.get("sponsor"))

    if sponsor is None:
        return None

    signals = league_deal_signals(deal)
    walks, heat, threshold = should_sponsor_withdraw(
        sponsor,
        signals,
        severity=severity,
        immediate=False,
    )

    if not walks:
        return None

    return withdraw_league_deal(party_name, deal, reason, heat, threshold)


def collect_league_deal_pay(deal):
    """Pay one league commercial check into the treasury."""

    amount = int(
        deal["value"]
        * sponsor_pay_multiplier(deal.get("satisfaction", 55))
    )
    league["treasury"] += amount
    league["season_commercial_income"] += amount
    league["career_commercial_income"] += amount
    return amount


def advance_league_deal_years(deal):
    """Tick one year off a league deal. Return True if it expired."""

    deal["years"] -= 1
    return deal["years"] <= 0


def series_named_by(sponsor):
    """Return True if this brand holds series naming rights."""

    return (
        has_naming_rights()
        and league["naming_rights"]["sponsor"] == sponsor.name
    )


def official_partner_named(sponsor):
    """Return the official-partner deal for this brand, if any."""

    ensure_league_commercial_state()
    for partner in league["official_partners"]:
        if partner and partner.get("sponsor") == sponsor.name:
            return partner

    return None


def display_league_sponsors():
    """Display series naming rights and official partners."""

    ensure_league_commercial_state()
    print("\nLeague Sponsors")
    print("-" * 90)
    print(f"Series: {series_name()}")
    naming = league.get("naming_rights")
    print(f"Naming rights: {league_deal_label(naming)}")
    if naming and naming.get("last_objectives"):
        obj = naming["last_objectives"]
        print(
            f"    Last review: perf {obj['performance']}, "
            f"exposure {obj['exposure']}, "
            f"conduct {obj['conduct']} "
            f"(delivery {naming.get('last_delivery', 0)})"
        )

    if league["official_partners"]:
        for partner in league["official_partners"]:
            print(f"Official partner: {league_deal_label(partner)}")
            if partner.get("last_objectives"):
                obj = partner["last_objectives"]
                print(
                    f"    Last review: perf {obj['performance']}, "
                    f"exposure {obj['exposure']}, "
                    f"conduct {obj['conduct']} "
                    f"(delivery {partner.get('last_delivery', 0)})"
                )
    else:
        print("Official partners: none")

    print(
        f"Treasury: ${league.get('treasury', 0):,} "
        f"(season commercial ${league.get('season_commercial_income', 0):,})"
    )


def run_offseason_league_sponsors():
    """Pay series deals, expire finished years, and fill empty slots."""

    ensure_league_commercial_state()
    league["season_commercial_income"] = 0
    print("\nLeague Sponsors")
    print("-" * 90)

    paid = []
    expired = []
    blocked = walk_block_set()
    declined = []

    deals = []
    if has_naming_rights():
        deals.append(("the series", league["naming_rights"]))
    for partner in list(league["official_partners"]):
        deals.append(
            (
                f"official {partner.get('category') or 'partner'}",
                partner,
            )
        )

    for party_name, deal in deals:
        amount = collect_league_deal_pay(deal)
        paid.append((party_name, deal["sponsor"], amount, league_deal_label(deal)))
        satisfaction = deal.get("satisfaction", 55)
        sponsor_name = deal["sponsor"]
        if advance_league_deal_years(deal):
            expired.append((party_name, sponsor_name, deal))
            if satisfaction < SPONSOR_RENEWAL_MIN_SATISFACTION:
                blocked.add((sponsor_name, "the series"))
                blocked.add((sponsor_name, "official partner"))
                declined.append((sponsor_name, party_name, satisfaction))
            drop_league_deal(deal)

    signed = assign_league_deals(
        season=calendar.current_season,
        apply_signing_boost=True,
        blocked=blocked,
    )

    if paid:
        print("Payouts")
        for party_name, sponsor_name, amount, label in paid:
            print(
                f"- {sponsor_name} paid the league ${amount:,} "
                f"({party_name}; {label})"
            )
    else:
        print("No series-sponsor payouts this offseason.")

    if declined:
        print("Declined renewals")
        for sponsor_name, party_name, satisfaction in declined:
            print(
                f"- {sponsor_name} will not renew {party_name} "
                f"({sponsor_satisfaction_label(satisfaction)})"
            )

    if expired:
        print("Expired contracts")
        for party_name, sponsor_name, _deal in expired:
            still = False
            for item in signed:
                role_party = (
                    "the series"
                    if item["role"] == "naming"
                    else f"official {item.get('category') or 'partner'}"
                )
                if (
                    item["sponsor"].name == sponsor_name
                    and role_party == party_name
                ):
                    still = True
            if not still:
                print(
                    f"- {sponsor_name} is off {party_name}"
                )

    renewals = []
    fresh = []
    expired_pairs = {
        (party_name, sponsor_name)
        for party_name, sponsor_name, _deal in expired
    }

    for item in signed:
        role_party = (
            "the series"
            if item["role"] == "naming"
            else f"official {item.get('category') or 'partner'}"
        )
        if (role_party, item["sponsor"].name) in expired_pairs:
            renewals.append(item)
        else:
            fresh.append(item)

    if renewals:
        print("Renewals")
        for item in renewals:
            year_word = "year" if item["years"] == 1 else "years"
            role = (
                "naming rights"
                if item["role"] == "naming"
                else f"official {item.get('category')}"
            )
            print(
                f"- {item['sponsor'].name} renews {role} — "
                f"${item['value']:,}/yr for {item['years']} {year_word}"
            )

    if fresh:
        print("New contracts")
        for item in fresh:
            year_word = "year" if item["years"] == 1 else "years"
            role = (
                "naming rights"
                if item["role"] == "naming"
                else f"official {item.get('category')}"
            )
            print(
                f"- {item['sponsor'].name} signs {role} — "
                f"${item['value']:,}/yr for {item['years']} {year_word} "
                f"(interest {item['interest']})"
            )

    if not has_naming_rights():
        print("Unsponsored")
        print(f"- The series has no naming-rights partner ({SERIES_NAME_BASE})")

    if (
        not paid
        and not declined
        and not expired
        and not signed
        and has_naming_rights()
    ):
        print("All series commercial contracts continue.")


def display_sponsor_market():
    """Display the named sponsor companies and their current tastes."""

    print("Sponsor market")
    idle_count = len(idle_sponsors())
    print(
        f"{len(sponsors)} companies, {idle_count} idle, "
        f"{len(sponsor_prospects)} waiting to enter"
    )

    if not sponsors:
        print("- No sponsor companies on the market")
        return

    for sponsor in sponsors:
        favorite, score = best_team_for_sponsor(sponsor)
        favorite_text = (
            f"{favorite.name} ({score})"
            if favorite is not None
            else "none"
        )
        backed = driver_backed_by(sponsor)
        titled = team_titled_by(sponsor)
        series_text = (
            "names the series | "
            if series_named_by(sponsor)
            else ""
        )
        official = official_partner_named(sponsor)
        official_text = (
            f"official {official['category']} | "
            if official is not None
            else ""
        )
        backer_text = (
            f"backs {backed.name} | "
            if backed is not None
            else ""
        )
        title_text = (
            f"titles {titled.name} | "
            if titled is not None
            else ""
        )
        print(
            f"- {sponsor.description()} | "
            f"{sponsor.preference_summary()} | "
            f"${sponsor.spending_power():,} | "
            f"wants {sponsor.primary_objective()} | "
            f"{series_text}{official_text}{title_text}{backer_text}"
            f"eyes {favorite_text}"
        )

    if sponsor_prospects:
        print("Waiting to enter")
        for sponsor in sponsor_prospects:
            print(
                f"- {sponsor.description()} | "
                f"{sponsor.preference_summary()} | "
                f"${sponsor.spending_power():,}"
            )


def best_weekend_for_network(network):
    """Return the track this broadcaster most wants, plus the score."""

    if not tracks:
        return None, 0

    favorite = max(
        tracks,
        key=lambda track: (
            network.interest_in_weekend(track),
            track.purse,
            track.name,
        ),
    )
    return favorite, network.interest_in_weekend(favorite)


def leading_network():
    """Return the broadcaster most interested in series rights."""

    if not networks:
        return None, 0

    leader = max(
        networks,
        key=lambda network: (
            network.interest_in_league(league),
            network.rights_value(),
            network.name,
        ),
    )
    return leader, leader.interest_in_league(league)


def display_broadcast_market():
    """Display television networks and their current tastes."""

    print("Broadcast market")
    print(f"{len(networks)} networks")
    print(f"TV rights: {tv_deal_label(league.get('tv_rights'))}")

    if not networks:
        print("- No television networks on the market")
        return

    if not has_tv_rights():
        leader, leader_score = leading_network()
        if leader is not None:
            interest, value, years = tv_rights_terms(leader)
            year_word = "year" if years == 1 else "years"
            print(
                f"Leading bid: {leader.name} "
                f"(interest {leader_score}, ${value:,}/yr, {years} {year_word})"
            )

    for network in networks:
        favorite, score = best_weekend_for_network(network)
        favorite_text = (
            f"{favorite.name} ({score})"
            if favorite is not None
            else "none"
        )
        rights_text = (
            "holds rights | "
            if series_televised_by(network)
            else ""
        )
        print(
            f"- {network.description()} | "
            f"{network.profile_summary()} | "
            f"reach {network.reach} | "
            f"${network.rights_value():,} | "
            f"interest {network.interest_in_league(league)} | "
            f"{rights_text}"
            f"eyes {favorite_text}"
        )


def has_tv_rights():
    """Return whether the series currently has a television contract."""

    ensure_league_commercial_state()
    deal = league.get("tv_rights") or {}
    return bool(deal.get("network"))


def series_televised_by(network):
    """Return True if this network holds series television rights."""

    return has_tv_rights() and league["tv_rights"]["network"] == network.name


def tv_deal_label(deal):
    """Return a readable television-rights line."""

    if not deal or not deal.get("network"):
        return "unsigned"

    year_word = "yr" if deal["years"] == 1 else "yrs"
    mood = sponsor_satisfaction_label(deal.get("satisfaction", 55))
    return (
        f"{deal['network']} "
        f"(${deal['value']:,}/yr, {deal['years']} {year_word}) "
        f"— {mood}"
    )


def format_viewers(viewers):
    """Return a compact viewer count for reports."""

    if viewers is None:
        return "n/a"
    if viewers >= 1_000_000:
        return f"{viewers / 1_000_000:.1f}M"
    return f"{viewers:,}"


def tv_rights_network():
    """Return the network holding series rights, if any."""

    if not has_tv_rights():
        return None
    return get_network(league["tv_rights"]["network"])


def average_tv_rating():
    """Return this season's mean TV rating, or None."""

    ensure_league_commercial_state()
    ratings = league.get("season_tv_ratings") or []
    if not ratings:
        return None
    return round(sum(ratings) / len(ratings))


def average_tv_viewers():
    """Return this season's mean viewer count, or None."""

    ensure_league_commercial_state()
    counts = league.get("season_tv_viewers") or []
    if not counts:
        return None
    return int(round(sum(counts) / len(counts)))


def tv_rating_trend_label():
    """Return a readable multi-season ratings trend."""

    ensure_league_commercial_state()
    return TREND_LABELS.get(league.get("tv_rating_trend", 0), "Stable")


def race_star_power(results):
    """Return top-3, winner, and field popularity means."""

    if not results:
        return 55, 55, 55

    drivers_in_race = [item["driver"] for item in results]
    field = sum(driver.popularity for driver in drivers_in_race) / len(
        drivers_in_race
    )
    top = drivers_in_race[:3]
    top_mean = sum(driver.popularity for driver in top) / len(top)
    winner = drivers_in_race[0].popularity
    return top_mean, winner, field


def compute_race_product(track, results, weekend):
    """Return a 0-100 score for how watchable the race was."""

    fan = league.get("fan_interest", 65)
    top_stars, _winner, field = race_star_power(results)
    cautions = weekend.get("cautions", 0) or 0
    wrecks = weekend.get("wrecks") or []
    wreck_size = sum(item.get("size", 1) for item in wrecks)
    weather = weekend.get("weather") or {}
    condition = weather.get("condition", "clear")

    score = 38
    score += (fan - 50) * 0.28
    score += (top_stars - 55) * 0.22
    score += (field - 55) * 0.08
    score += min(cautions, 8) * 1.3
    score += min(wreck_size, 10) * 0.8
    score += TRACK_TYPE_TV_DRAW.get(track.type, 4)
    score += min(track.purse / 150_000.0, 5)
    if condition in ("light rain", "rain"):
        score -= 5
    elif condition == "hot":
        score += 1
    return round(clamp(score))


def compute_tv_viewers(rating, reach):
    """Return an estimated audience from rating and network reach."""

    return int(
        200_000
        + reach * 28_000
        + rating * 18_000
        + league.get("fan_interest", 65) * 6_000
    )


def compute_tv_rating(track, results, weekend, network=None):
    """Return (rating, viewers, product) for a televised weekend."""

    product = compute_race_product(track, results, weekend)
    if network is None:
        rating = product
        viewers = compute_tv_viewers(rating, 40)
        return rating, viewers, product

    cautions = weekend.get("cautions", 0) or 0
    wrecks = weekend.get("wrecks") or []
    excitement = min(cautions * 6 + len(wrecks) * 8, 70)
    _top, winner_pop, _field = race_star_power(results)
    controversy = league.get("controversy", 20)
    integrity = league.get("integrity", 70)

    rating = product
    rating += (
        (network.excitement_preference / 100.0) * (excitement - 35) * 0.18
    )
    rating += (network.star_preference / 100.0) * (winner_pop - 55) * 0.16
    rating += (network.integrity_preference / 100.0) * (
        ((integrity + (100 - controversy)) / 2) - 55
    ) * 0.14
    if track.type in network.preferred_track_types:
        rating += 3
    rating = round(clamp(rating))
    viewers = compute_tv_viewers(rating, network.reach)
    return rating, viewers, product


def apply_race_tv_rating(race_record, track, results, weekend, silent=False):
    """Attach TV numbers to a race and update season rating state."""

    ensure_league_commercial_state()
    network = tv_rights_network()
    rating, viewers, product = compute_tv_rating(
        track,
        results,
        weekend,
        network,
    )
    race_record["tv_network"] = network.name if network is not None else None
    race_record["tv_rating"] = rating
    race_record["tv_viewers"] = viewers
    race_record["tv_product"] = product

    league["season_tv_ratings"].append(rating)
    league["season_tv_viewers"].append(viewers)
    league["last_tv_rating"] = rating
    league["last_tv_viewers"] = viewers

    if not silent:
        holder = network.name if network is not None else "syndication"
        print(
            f"TV rating: {rating} ({format_viewers(viewers)} viewers) "
            f"— {holder}"
        )
    return rating, viewers, product


def update_tv_rating_trend():
    """Store this season's average and update multi-season momentum."""

    ensure_league_commercial_state()
    avg = average_tv_rating()
    if avg is None:
        return None

    history = list(league.get("tv_rating_history") or [])
    history.append(avg)
    history = history[-TREND_HISTORY_SEASONS:]
    league["tv_rating_history"] = history

    if len(history) < 2:
        league["tv_rating_trend"] = 0
        return avg

    latest = history[-1]
    previous = sum(history[:-1]) / len(history[:-1])
    delta = latest - previous

    if delta >= 8:
        league["tv_rating_trend"] = 2
    elif delta >= 3:
        league["tv_rating_trend"] = 1
    elif delta <= -8:
        league["tv_rating_trend"] = -2
    elif delta <= -3:
        league["tv_rating_trend"] = -1
    else:
        league["tv_rating_trend"] = 0
    return avg


def review_tv_ratings():
    """Close the season's ratings book and grade the rights holder."""

    print("\nTelevision Ratings")
    print("-" * 90)

    ensure_league_commercial_state()
    avg = update_tv_rating_trend()
    last = league.get("last_tv_rating")
    last_viewers = league.get("last_tv_viewers")
    mean_viewers = average_tv_viewers()

    if avg is None:
        print("No televised races this season.")
        return None

    print(
        f"- Last race: {last} ({format_viewers(last_viewers)} viewers)"
    )
    print(
        f"- Season average: {avg} "
        f"({format_viewers(mean_viewers)} viewers) "
        f"— {tv_rating_trend_label()}"
    )

    if not has_tv_rights():
        print("- No rights holder to review.")
        return avg

    network = tv_rights_network()
    deal = league["tv_rights"]
    if network is None:
        print("- Rights holder is missing from the broadcast market.")
        return avg

    delivery, breakdown = network.score_audience(avg, league)
    previous, current, delta = apply_objective_review(
        deal,
        delivery,
        breakdown,
    )
    sign = f"{delta:+d}" if delta else "0"
    print(
        f"- {network.name}: {sponsor_satisfaction_label(current)} "
        f"({current}, {sign}) | "
        f"delivery {delivery} | "
        f"perf {breakdown['performance']}, "
        f"exposure {breakdown['exposure']}, "
        f"conduct {breakdown['conduct']}"
    )
    return avg


def advertised_star_power(results):
    """Return headliner and field popularity from the advertised entry list."""

    if results:
        pool = [item["driver"] for item in results]
    else:
        pool = list(drivers)
    if not pool:
        return 55, 55

    pops = sorted((driver.popularity for driver in pool), reverse=True)
    headliners = sum(pops[:3]) / min(3, len(pops))
    field = sum(pops) / len(pops)
    return headliners, field


def compute_gate_draw(track, results, weekend):
    """Return a 0-100 ticket-demand score set before the race, not by cautions."""

    fan = league.get("fan_interest", 65)
    headliners, field = advertised_star_power(results)
    weather = weekend.get("weather") or {}
    condition = (weather.get("condition") or "clear").lower()
    controversy = league.get("controversy", 20)
    integrity = league.get("integrity", 70)

    score = 48
    score += (fan - 50) * 0.32
    score += (headliners - 55) * 0.28
    score += (field - 55) * 0.10
    score += TRACK_TYPE_GATE_DRAW.get(track.type, 4)
    score += min(track.purse / 180_000.0, 4)
    if condition in ("light rain", "rain"):
        score -= 14
    elif condition == "hot":
        score -= 3
    if controversy >= 55:
        score -= 6
    elif controversy >= 40:
        score -= 2
    score += (integrity - 70) * 0.08
    return round(clamp(score))


def compute_gate_attendance(track, results, weekend):
    """Return (attendance, capacity, fill, draw). Never exceeds capacity."""

    draw = compute_gate_draw(track, results, weekend)
    capacity = track.seating_capacity()
    bias = TRACK_TYPE_FILL_BIAS.get(track.type, 1.0)
    fill = round(clamp(draw * bias))
    attendance = int(round(capacity * fill / 100.0))
    if fill >= 97:
        attendance = capacity
        fill = 100
    if attendance > capacity:
        attendance = capacity
    return attendance, capacity, fill, draw


def format_attendance(count):
    """Return a readable grandstand count."""

    if not count:
        return "0"
    return f"{int(count):,}"


def gate_is_sold_out(attendance, capacity, fill):
    """Return whether the house is at or past a sellout."""

    if not capacity:
        return False
    return fill >= 97 or attendance >= capacity


def format_gate_house(attendance, capacity, fill):
    """Return '94,200 / 125,000 (75%)' or a sold-out label."""

    if gate_is_sold_out(attendance, capacity, fill):
        return (
            f"{format_attendance(attendance)} / "
            f"{format_attendance(capacity)} (sold out)"
        )
    return (
        f"{format_attendance(attendance)} / "
        f"{format_attendance(capacity)} ({fill}%)"
    )


def average_gate_fill():
    """Return this season's mean grandstand fill, or None."""

    ensure_league_commercial_state()
    fills = league.get("season_gate_fill") or []
    if not fills:
        return None
    return round(sum(fills) / len(fills))


def average_gate_attendance():
    """Return this season's mean attendance, or None."""

    ensure_league_commercial_state()
    counts = league.get("season_gate_attendance") or []
    if not counts:
        return None
    return int(round(sum(counts) / len(counts)))


def gate_trend_label():
    """Return a readable multi-season attendance trend."""

    ensure_league_commercial_state()
    return TREND_LABELS.get(league.get("gate_trend", 0), "Stable")


def apply_race_gate(race_record, track, results, weekend, silent=False):
    """Attach gate numbers to a race and update season attendance state."""

    ensure_league_commercial_state()
    attendance, capacity, fill, draw = compute_gate_attendance(
        track,
        results,
        weekend,
    )
    race_record["gate_attendance"] = attendance
    race_record["gate_capacity"] = capacity
    race_record["gate_fill"] = fill
    race_record["gate_draw"] = draw

    league["season_gate_attendance"].append(attendance)
    league["season_gate_fill"].append(fill)
    league["last_gate_attendance"] = attendance
    league["last_gate_capacity"] = capacity
    league["last_gate_fill"] = fill
    league["last_gate_draw"] = draw

    if not silent:
        print(
            f"Gate: {format_gate_house(attendance, capacity, fill)} "
            f"— {track.name}"
        )
    return attendance, capacity, fill, draw


def update_gate_trend():
    """Store this season's average fill and update multi-season momentum."""

    ensure_league_commercial_state()
    avg = average_gate_fill()
    if avg is None:
        return None

    history = list(league.get("gate_history") or [])
    history.append(avg)
    history = history[-TREND_HISTORY_SEASONS:]
    league["gate_history"] = history

    if len(history) < 2:
        league["gate_trend"] = 0
        return avg

    latest = history[-1]
    previous = sum(history[:-1]) / len(history[:-1])
    delta = latest - previous

    if delta >= 8:
        league["gate_trend"] = 2
    elif delta >= 3:
        league["gate_trend"] = 1
    elif delta <= -8:
        league["gate_trend"] = -2
    elif delta <= -3:
        league["gate_trend"] = -1
    else:
        league["gate_trend"] = 0
    return avg


def review_race_popularity():
    """Close the season's attendance book and report the houses."""

    print("\nRace Popularity")
    print("-" * 90)

    ensure_league_commercial_state()
    avg = update_gate_trend()
    last = league.get("last_gate_attendance")
    last_cap = league.get("last_gate_capacity")
    last_fill = league.get("last_gate_fill")
    mean_house = average_gate_attendance()

    if avg is None:
        print("No race weekends this season.")
        return None

    print(
        f"- Last race: {format_gate_house(last, last_cap, last_fill)}"
    )
    print(
        f"- Season average: {avg}% full "
        f"({format_attendance(mean_house)} per race) "
        f"— {gate_trend_label()}"
    )

    best = None
    for race in race_history:
        fill = race.get("gate_fill")
        if fill is None:
            continue
        if best is None or fill > best.get("gate_fill", 0):
            best = race
    if best is not None:
        print(
            f"- Best house: {best['track']} "
            f"{format_gate_house(best.get('gate_attendance'), best.get('gate_capacity'), best.get('gate_fill'))}"
        )
    return avg


def media_outlet_name():
    """Return the byline network, or wire services when unsigned."""

    network = tv_rights_network()
    if network is not None:
        return network.name
    return "the wire services"


def race_winner_name(race_record, results):
    """Return the winning driver name from live results or the race record."""

    if results:
        driver = results[0].get("driver")
        if hasattr(driver, "name"):
            return driver.name
        if driver:
            return driver
    stored = (race_record.get("results") or [{}])[0]
    return stored.get("driver") or "the field"


def build_media_story(kind, headline, body, tone="straight"):
    """Return one media story dictionary."""

    return {
        "kind": kind,
        "headline": headline,
        "body": body,
        "outlet": media_outlet_name(),
        "tone": tone,
        "season": calendar.current_season,
    }


def collect_weekend_media_stories(race_record, track, results, weekend):
    """Build 1-3 deterministic headlines from the completed weekend."""

    winner = race_winner_name(race_record, results)
    track_name = track.name
    cautions = race_record.get("cautions")
    if cautions is None:
        cautions = weekend.get("cautions", 0) or 0
    wrecks = race_record.get("wrecks") or weekend.get("wrecks") or []
    wreck_size = 0
    for wreck in wrecks:
        wreck_size = max(wreck_size, wreck.get("size", 1) or 1)
    weather = race_record.get("weather")
    if not weather:
        weather = (weekend.get("weather") or {}).get("condition", "clear")
    weather_l = str(weather).lower()
    raining = weather_l in ("light rain", "rain")
    wreckfest = cautions >= 6 or wreck_size >= 6
    rating = race_record.get("tv_rating")
    viewers = race_record.get("tv_viewers")
    fill = race_record.get("gate_fill")
    attendance = race_record.get("gate_attendance")
    capacity = race_record.get("gate_capacity")
    investigations = (
        race_record.get("investigations")
        or weekend.get("investigations")
        or []
    )
    outlet = media_outlet_name()
    outlet_lead = outlet if outlet != "the wire services" else "Syndication"

    if wreckfest:
        headline = "{0} Survives {1} Wreckfest".format(winner, track_name)
        tone = "spicy"
    elif raining:
        headline = "{0} Wins Rain-Soaked {1}".format(winner, track_name)
        tone = "straight"
    elif fill is not None and fill >= 97:
        headline = "{0} Wins Before a Packed {1}".format(winner, track_name)
        tone = "upbeat"
    else:
        headline = "{0} Wins at {1}".format(winner, track_name)
        tone = "upbeat"

    body_bits = [
        "{0} took the checkered flag at {1}.".format(winner, track_name)
    ]
    if rating is not None:
        body_bits.append(
            "{0} posted a {1} ({2} viewers).".format(
                outlet_lead,
                rating,
                format_viewers(viewers),
            )
        )
    if attendance is not None:
        body_bits.append(
            "The gate was {0}.".format(
                format_gate_house(attendance, capacity, fill)
            )
        )
    stories = [
        build_media_story("winner", headline, " ".join(body_bits), tone)
    ]

    extras = []

    if wreck_size >= 4:
        extras.append(
            build_media_story(
                "wreck",
                "{0}-Car Crash Headlines {1}".format(wreck_size, track_name),
                "A {0}-car incident and {1} cautions turned {2} into a survival race.".format(
                    wreck_size,
                    cautions,
                    track_name,
                ),
                "spicy",
            )
        )
    elif cautions >= 6:
        extras.append(
            build_media_story(
                "wreck",
                "Caution Flag Flies {0} Times at {1}".format(
                    cautions,
                    track_name,
                ),
                "{0} went yellow {1} times, bunching the field again and again.".format(
                    track_name,
                    cautions,
                ),
                "spicy",
            )
        )

    if raining and wreckfest:
        extras.append(
            build_media_story(
                "weather",
                "Rain Turns {0} Slick".format(track_name),
                "Light rain cut the live crowd and made the already-chaotic show harder to finish.",
                "straight",
            )
        )

    if investigations:
        packet = investigations[0]
        blamed = packet.get("blame") or packet.get("driver") or "the field"
        extras.append(
            build_media_story(
                "investigation",
                "Stewards Open File After {0}".format(track_name),
                "Officials logged a post-race packet with blame on {0}.".format(
                    blamed
                ),
                "serious",
            )
        )

    if rating is not None and rating >= 80:
        extras.append(
            build_media_story(
                "ratings",
                "{0} Hits a {1} at {2}".format(
                    outlet if outlet != "the wire services" else "Wire services",
                    rating,
                    track_name,
                ),
                "The broadcast pulled {0} viewers, one of the stronger shows on the book.".format(
                    format_viewers(viewers)
                ),
                "upbeat",
            )
        )
    elif rating is not None and rating < 42:
        extras.append(
            build_media_story(
                "ratings",
                "{0} Ratings Come In Soft".format(track_name),
                "The telecast managed only a {0} ({1} viewers).".format(
                    rating,
                    format_viewers(viewers),
                ),
                "downbeat",
            )
        )

    if fill is not None and fill >= 97:
        extras.append(
            build_media_story(
                "gate",
                "Sellout Crowd at {0}".format(track_name),
                "{0} packed {1} into a {2}-seat house.".format(
                    track_name,
                    format_attendance(attendance),
                    format_attendance(capacity),
                ),
                "upbeat",
            )
        )
    elif fill is not None and fill < 55:
        extras.append(
            build_media_story(
                "gate",
                "Empty Seats at {0}".format(track_name),
                "Only {0} of {1} seats were filled ({2}%).".format(
                    format_attendance(attendance),
                    format_attendance(capacity),
                    fill,
                ),
                "downbeat",
            )
        )

    stories.extend(extras[: MEDIA_STORY_MAX - 1])
    return stories[:MEDIA_STORY_MAX]


def print_media_stories(stories, heading="Media"):
    """Print headlines and narratives for a weekend or recap."""

    print("\n" + heading)
    print("-" * 90)
    if not stories:
        print("No stories filed.")
        return
    for story in stories:
        print(f'- "{story["headline"]}" — {story["outlet"]}')
        print(f'  {story["body"]}')


def apply_race_media_stories(
    race_record,
    track,
    results,
    weekend,
    silent=False,
):
    """Attach generated stories to a race and update the season book."""

    ensure_league_commercial_state()
    stories = collect_weekend_media_stories(
        race_record,
        track,
        results,
        weekend,
    )
    race_record["media_stories"] = stories
    league["last_media_stories"] = list(stories)
    league["season_media_stories"].extend(stories)
    if not silent:
        print_media_stories(stories)
    return stories


def review_media_stories():
    """Close the season's media book with a kind breakdown."""

    print("\nMedia Recap")
    print("-" * 90)
    ensure_league_commercial_state()
    stories = league.get("season_media_stories") or []
    if not stories:
        print("No stories this season.")
        return None

    kinds = {}
    for story in stories:
        kind = story.get("kind") or "other"
        kinds[kind] = kinds.get(kind, 0) + 1
    parts = [
        "{0} {1}".format(count, kind)
        for kind, count in sorted(kinds.items(), key=lambda item: (-item[1], item[0]))
    ]
    print(f"- {len(stories)} stories this season")
    print("- Kinds: " + ", ".join(parts))
    lead = stories[0]
    print(f'- Opening lead: "{lead["headline"]}" — {lead["outlet"]}')
    last = (league.get("last_media_stories") or stories)[-1]
    print(f'- Latest: "{last["headline"]}" — {last["outlet"]}')
    return stories


def tv_rights_terms(network):
    """Return (interest, annual bid, years) for a television-rights package."""

    interest = network.interest_in_league(league)
    share = 0.50 + (interest / 200.0)
    value = int(round(network.rights_value() * share / 1_000) * 1_000)
    value = max(4_000_000, value)

    years = 3
    if network.wealth >= 60:
        years += 1
    if network.wealth >= 75:
        years += 1
    if network.prestige_preference >= 70:
        years += 1

    return interest, value, years


def make_tv_deal(network, value, years, season):
    """Build a television-rights contract dict."""

    return {
        "network": network.name,
        "role": "tv",
        "value": int(value),
        "years": int(years),
        "signed_season": season,
        "satisfaction": 55,
    }


def collect_tv_bids(blocked=None):
    """Return rights bids from interested networks, highest first."""

    blocked = blocked or set()
    bids = []

    for network in networks:
        if network.name in blocked:
            continue

        interest, value, years = tv_rights_terms(network)
        if interest < TV_RIGHTS_MIN_INTEREST:
            continue

        bids.append(
            {
                "network": network,
                "interest": interest,
                "value": value,
                "years": years,
            }
        )

    bids.sort(
        key=lambda item: (
            -item["value"],
            -item["interest"],
            item["network"].name,
        ),
    )
    return bids


def assign_tv_rights(season, apply_signing_boost=True, blocked=None, silent=True):
    """Award empty series television rights to the highest bidder."""

    ensure_league_commercial_state()
    if has_tv_rights():
        return None

    bids = collect_tv_bids(blocked)
    if not bids:
        return None

    winner = bids[0]
    network = winner["network"]
    league["tv_rights"] = make_tv_deal(
        network,
        winner["value"],
        winner["years"],
        season,
    )

    if apply_signing_boost:
        league["fan_interest"] = clamp(league["fan_interest"] + 3)

    if not silent:
        year_word = "year" if winner["years"] == 1 else "years"
        print("Bids")
        for item in bids:
            print(
                f"- {item['network'].name} bids ${item['value']:,}/yr "
                f"for {item['years']} years "
                f"(interest {item['interest']})"
            )
        print(
            f"{network.name} wins series rights — "
            f"${winner['value']:,}/yr for {winner['years']} {year_word}"
        )

    return winner


def drop_tv_deal():
    """Clear the current television-rights contract."""

    ensure_league_commercial_state()
    league["tv_rights"] = None


def collect_tv_deal_pay(deal):
    """Pay the annual television-rights check into the treasury."""

    amount = int(
        deal["value"]
        * sponsor_pay_multiplier(deal.get("satisfaction", 55))
    )
    league["treasury"] += amount
    league["season_tv_income"] += amount
    league["career_tv_income"] += amount
    return amount


def run_offseason_tv_rights():
    """Pay the TV deal, expire finished years, and auction an empty slot."""

    ensure_league_commercial_state()
    league["season_tv_income"] = 0
    print("\nTelevision Rights")
    print("-" * 90)

    blocked = set()
    expired_name = None
    went_dark = False

    if has_tv_rights():
        deal = league["tv_rights"]
        amount = collect_tv_deal_pay(deal)
        print(
            f"- {deal['network']} paid the league ${amount:,} "
            f"in television rights ({tv_deal_label(deal)})"
        )
        if advance_league_deal_years(deal):
            expired_name = deal["network"]
            if deal.get("satisfaction", 55) < SPONSOR_RENEWAL_MIN_SATISFACTION:
                blocked.add(expired_name)
                print(
                    f"- {expired_name} will not renew "
                    f"({sponsor_satisfaction_label(deal.get('satisfaction', 55))})"
                )
            drop_tv_deal()
            print(f"- {expired_name} is off series television")

    winner = assign_tv_rights(
        season=calendar.current_season,
        apply_signing_boost=True,
        blocked=blocked,
        silent=False,
    )

    if winner is None and not has_tv_rights():
        print("The series has no television contract.")
        if expired_name:
            went_dark = True
            league["fan_interest"] = clamp(league["fan_interest"] - 5)
            league["controversy"] = clamp(league["controversy"] + 4)
            print(
                "- Going dark costs fan interest and raises controversy"
            )
    elif winner is not None and expired_name:
        if winner["network"].name != expired_name:
            print(
                f"- {winner['network'].name} replaces {expired_name} "
                "on series television"
            )

    if went_dark:
        return

    if winner is None and has_tv_rights() and not expired_name:
        print(f"TV rights: {tv_deal_label(league.get('tv_rights'))}")


def sponsor_has_live_deal(sponsor):
    """Return whether a brand currently titles, endorses, or backs the series."""

    return bool(
        team_titled_by(sponsor)
        or driver_backed_by(sponsor)
        or series_named_by(sponsor)
        or official_partner_named(sponsor)
    )


def idle_sponsors():
    """Return market brands with no live commercial deal."""

    return [
        sponsor
        for sponsor in sponsors
        if not sponsor_has_live_deal(sponsor)
    ]


def record_market_move(action, sponsor, reason):
    """Append an enter/leave record to the career market log."""

    if not isinstance(league.get("sponsor_market_log"), list):
        league["sponsor_market_log"] = []

    league["sponsor_market_log"].append(
        {
            "season": calendar.current_season,
            "action": action,
            "name": sponsor.name,
            "industry": sponsor.industry,
            "reason": reason,
        }
    )


def current_season_market_moves():
    """Return enter/leave records from the active season."""

    return [
        item
        for item in league.get("sponsor_market_log") or []
        if item.get("season") == calendar.current_season
    ]


def depart_idle_sponsor():
    """Move the least interested idle brand to the prospect pool. Return it."""

    if len(sponsors) <= SPONSOR_MARKET_MIN:
        return None

    idle = idle_sponsors()
    if not idle:
        return None

    leaving = min(
        idle,
        key=lambda sponsor: (
            sponsor.interest_in_league(league),
            sponsor.wealth,
            sponsor.name,
        ),
    )
    sponsors.remove(leaving)
    sponsor_prospects.append(leaving)
    record_market_move("left", leaving, "no live deal")
    return leaving


def admit_prospect_sponsor():
    """Move the most interested waiting brand onto the market. Return it."""

    if len(sponsors) >= SPONSOR_MARKET_MAX:
        return None

    if not sponsor_prospects:
        return None

    entering = max(
        sponsor_prospects,
        key=lambda sponsor: (
            sponsor.interest_in_league(league),
            sponsor.wealth,
            sponsor.name,
        ),
    )
    sponsor_prospects.remove(entering)
    sponsors.append(entering)
    record_market_move("entered", entering, "market opening")
    return entering


def run_offseason_sponsor_market():
    """Let idle brands leave, admit prospects, and fill leftover deals."""

    print("\nSponsor Market")
    print("-" * 90)

    left = depart_idle_sponsor()
    entered = admit_prospect_sponsor()

    if left:
        print(
            f"- {left.name} ({left.industry}) left the market "
            f"— no live deal, interest {left.interest_in_league(league)}"
        )
    if entered:
        print(
            f"- {entered.name} ({entered.industry}) entered the market "
            f"— interest {entered.interest_in_league(league)}, "
            f"${entered.spending_power():,}"
        )
    if not left and not entered:
        print("The sponsor market is unchanged.")

    print(
        f"Market size: {len(sponsors)} companies, "
        f"{len(idle_sponsors())} idle, "
        f"{len(sponsor_prospects)} waiting"
    )

    new_teams = assign_team_sponsor_deals(
        season=calendar.current_season,
        apply_signing_boost=True,
        blocked=walk_block_set(),
    )
    new_drivers = assign_endorsement_deals(
        season=calendar.current_season,
        apply_signing_boost=True,
        blocked=walk_block_set(),
    )
    new_league = assign_league_deals(
        season=calendar.current_season,
        apply_signing_boost=True,
        blocked=walk_block_set(),
    )

    if new_teams or new_drivers or new_league:
        print("New market deals")
        for deal in new_teams:
            print(
                f"- {deal['team'].name} signs with {deal['sponsor'].name} "
                f"— ${deal['value']:,}/yr"
            )
        for deal in new_drivers:
            print(
                f"- {deal['driver'].name} signs with {deal['sponsor'].name} "
                f"— ${deal['value']:,}/yr"
            )
        for deal in new_league:
            role = (
                "naming rights"
                if deal["role"] == "naming"
                else f"official {deal.get('category')}"
            )
            print(
                f"- {deal['sponsor'].name} signs {role} "
                f"— ${deal['value']:,}/yr"
            )


def display_driver_endorsements():
    """Display personal endorsement deals on the grid."""

    print("\nDriver Endorsements")
    print("-" * 90)

    if not drivers:
        print("No drivers on the grid.")
        return

    for driver in drivers:
        print(
            f"{driver.name} ({driver.team_name}) — "
            f"{driver.endorsement_label()}"
        )
        if driver.career_endorsement_income:
            print(
                f"    Career personal-sponsor income: "
                f"${driver.career_endorsement_income:,}"
            )
        if driver.has_endorsement() and driver.endorsement.get("last_objectives"):
            obj = driver.endorsement["last_objectives"]
            print(
                f"    Last review: perf {obj['performance']}, "
                f"exposure {obj['exposure']}, "
                f"conduct {obj['conduct']} "
                f"(delivery {driver.endorsement.get('last_delivery', 0)})"
            )


def display_team_sponsors():
    """Display each team's main-sponsor contract."""

    print("\nTeam Sponsors")
    print("-" * 90)

    if not teams:
        print("No teams entered.")
        return

    for team in teams:
        print(
            f"{team.name} [{team.manufacturer}] — "
            f"{team.primary_sponsor_label()}"
        )
        if (
            team.has_primary_sponsor()
            and team.primary_sponsor.get("last_objectives")
        ):
            obj = team.primary_sponsor["last_objectives"]
            print(
                f"    Last review: perf {obj['performance']}, "
                f"exposure {obj['exposure']}, "
                f"conduct {obj['conduct']} "
                f"(delivery {team.primary_sponsor.get('last_delivery', 0)})"
            )


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
    print(f"Series: {series_name()}")
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
    print_approval_dashboard_line()
    print_board_dashboard_line()
    print(
        f"Treasury: ${league.get('treasury', 0):,} | "
        f"Fines collected: ${league['fines_collected']:,}"
    )
    print(f"Naming rights: {league_deal_label(league.get('naming_rights'))}")
    print(
        f"Sponsor market: {len(sponsors)} active, "
        f"{len(idle_sponsors())} idle, "
        f"{len(sponsor_prospects)} waiting"
    )
    print(f"Broadcast market: {len(networks)} networks")
    print(f"TV rights: {tv_deal_label(league.get('tv_rights'))}")
    avg_rating = average_tv_rating()
    if avg_rating is None:
        print("TV ratings: season not started")
    else:
        print(
            f"TV ratings: last {league.get('last_tv_rating')} "
            f"({format_viewers(league.get('last_tv_viewers'))}) | "
            f"season avg {avg_rating} | "
            f"{tv_rating_trend_label()}"
        )
    avg_fill = average_gate_fill()
    if avg_fill is None:
        print("Gate: season not started")
    else:
        print(
            "Gate: last "
            f"{format_gate_house(league.get('last_gate_attendance'), league.get('last_gate_capacity'), league.get('last_gate_fill'))} "
            f"| season avg {avg_fill}% | "
            f"{gate_trend_label()}"
        )
    season_stories = league.get("season_media_stories") or []
    last_stories = league.get("last_media_stories") or []
    if not season_stories:
        print("Media: season not started")
    else:
        print(
            f"Media: {len(last_stories)} last weekend | "
            f"{len(season_stories)} this season"
        )
        for story in last_stories:
            print(f'- "{story["headline"]}" — {story["outlet"]}')
    print_press_dashboard_line()
    print_scandal_dashboard_line()
    print_council_dashboard_line()
    print_driver_council_dashboard_line()
    print_proposal_dashboard_line()
    print_coalitions_dashboard_line()
    print_lobby_dashboard_line()
    print_rule_vote_dashboard_line()
    print(
        "Policies — "
        f"{policy_label('points_system')}; "
        f"{policy_label('race_format')}; "
        f"{policy_label('penalty_standard')}; "
        f"{policy_label('technical_rules')}; "
        f"{policy_label('safety_standard')}; "
        f"{policy_label('scoring_bonuses')}; "
        f"{policy_label('championship_format')}"
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
            f"Deal {driver.endorsement_label()} | "
            f"Rival {rival_text} | Ally {ally_text} | "
            f"Teammate bond {driver.teammate_bond} | "
            f"Feud {feud_text}"
        )

    print("Organizations")

    for team in teams:
        owner = team.owner
        print(
            f"- {team.name} [{team.manufacturer}]: {owner.description()} | "
            f"{team.financial_status_label()} | "
            f"Prestige {team.prestige} | "
            f"{team.performance_trend_label()} | "
            f"Shop {team.facility_rating()} "
            f"(Lv {team.facility_level}) | "
            f"Eng {team.engineering} | "
            f"Crew {team.crew_rating} | "
            f"Main {team.primary_sponsor_label()}"
        )

    display_sponsor_market()
    display_broadcast_market()

    next_index = len(race_history)

    if next_index < len(tracks):
        next_track = tracks[next_index]
        print(
            f"Next weekend: {next_track.name} ({next_track.type}) — "
            f"{next_track.description()} | purse ${next_track.purse:,} | "
            f"{format_attendance(next_track.seating_capacity())} seats"
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
        if last_race.get("tv_rating") is not None:
            print(
                f"Last TV rating: {last_race['tv_rating']} "
                f"({format_viewers(last_race.get('tv_viewers'))} viewers) "
                f"— {last_race.get('tv_network') or 'syndication'}"
            )
        if last_race.get("gate_attendance") is not None:
            print(
                f"Last gate: {format_gate_house(last_race.get('gate_attendance'), last_race.get('gate_capacity'), last_race.get('gate_fill'))} "
                f"— {last_race['track']}"
            )
        media = last_race.get("media_stories") or []
        if media:
            print("Last headlines:")
            for story in media:
                print(f'- "{story["headline"]}" — {story["outlet"]}')
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


def record_press_conference(result, stories):
    """Store the last podium answer on the league book."""

    ensure_league_commercial_state()
    lead = (stories or [{}])[0] or {}
    record = {
        "season": calendar.current_season,
        "choice_id": result.get("choice_id"),
        "choice_label": result.get("choice_label"),
        "headline": lead.get("headline"),
        "outlet": lead.get("outlet"),
        "outcome": result.get("outcome"),
    }
    league["last_press_conference"] = record
    league["season_press_conferences"].append(record)
    return record


def print_press_dashboard_line():
    """Print the last press-conference line for the dashboard."""

    ensure_league_commercial_state()
    presser = league.get("last_press_conference")
    if not presser:
        print("Press: no conference this season")
        return
    headline = presser.get("headline") or "the weekend"
    print(
        'Press: last {0} after "{1}"'.format(
            presser.get("choice_label"),
            headline,
        )
    )


def apply_scandal_sponsor_shock(amount, reason="media scandal"):
    """Let signed brands flinch when the commissioner denies a scandal."""

    amount = abs(int(amount))
    if amount <= 0:
        return []

    hits = []
    candidates = []

    for team in teams:
        if team.has_primary_sponsor():
            candidates.append(team.primary_sponsor)
    for driver in drivers:
        if driver.has_endorsement():
            candidates.append(driver.endorsement)
    for _party, deal, _kind in live_league_deals():
        candidates.append(deal)
    if has_tv_rights():
        candidates.append(league["tv_rights"])

    seen = set()
    for deal in candidates:
        if not deal or (not deal.get("sponsor") and not deal.get("network")):
            continue
        name = deal.get("sponsor") or deal.get("network")
        key = (name, id(deal))
        if key in seen:
            continue
        seen.add(key)
        sponsor = get_sponsor(name)
        network = get_network(name)
        sensitivity = 0.6
        if sponsor is not None:
            sensitivity = sponsor.controversy_sensitivity()
        elif network is not None:
            caution = (100 - network.risk_tolerance) / 100.0
            sensitivity = 0.35 + caution * 0.5
        shock = max(1, round(amount * sensitivity))
        previous, current, delta = apply_controversy_shock(deal, shock)
        hits.append((name, previous, current, delta))
        print(
            f"{name} took the {reason} hard: "
            f"{sponsor_satisfaction_label(previous)} {previous} → "
            f"{sponsor_satisfaction_label(current)} {current} "
            f"({delta:+d})."
        )
    return hits


def record_media_controversy(result, event, stories):
    """Store the scandal and file it in the season media book."""

    ensure_league_commercial_state()
    headline = (event or {}).get("scandal_headline") or "Media Controversy"
    flavor = (event or {}).get("scandal_flavor") or "public-pressure"
    lead = (stories or [{}])[0] or {}
    story = build_media_story(
        "scandal",
        headline,
        result.get("outcome") or "The scandal is the lead.",
        "serious",
    )
    league["season_media_stories"].append(story)
    record = {
        "season": calendar.current_season,
        "flavor": flavor,
        "headline": headline,
        "choice_id": result.get("choice_id"),
        "choice_label": result.get("choice_label"),
        "outlet": lead.get("outlet"),
        "outcome": result.get("outcome"),
    }
    league["last_media_controversy"] = record
    league["season_media_controversies"].append(record)
    return record


def print_scandal_dashboard_line():
    """Print the last media-scandal line for the dashboard."""

    ensure_league_commercial_state()
    scandal = league.get("last_media_controversy")
    if not scandal:
        print("Scandal: none this season")
        return
    print(
        'Scandal: last "{0}" — {1}'.format(
            scandal.get("headline"),
            scandal.get("choice_label"),
        )
    )


def record_owner_council(result):
    """Tally the rebuke vote after the commissioner addresses the chamber."""

    ensure_league_commercial_state()
    tilt = OWNER_COUNCIL_TILT.get(str(result.get("choice_id")), 0)
    tally = owner_council_tally(teams, league, tilt)
    chair_team = owner_council_chair(teams)
    passed = tally["passed"]
    if passed:
        league["owner_pressure"] = clamp(league.get("owner_pressure", 0) + 6)
        league["integrity"] = clamp(league.get("integrity", 0) - 3)
        league["controversy"] = clamp(league.get("controversy", 0) + 4)
        verdict = "the rebuke passes"
    else:
        league["owner_pressure"] = clamp(league.get("owner_pressure", 0) - 3)
        league["integrity"] = clamp(league.get("integrity", 0) + 1)
        verdict = "the rebuke fails"

    print("\nOwner Council Vote — rebuke the commissioner")
    if chair_team is not None:
        print(
            "Chair: {0} ({1})".format(
                chair_team.owner.name,
                chair_team.name,
            )
        )
    for ballot in tally["ballots"]:
        role = "chair " if ballot.get("chair") else ""
        print(
            "- {0}{1} ({2}): {3}".format(
                role,
                ballot["owner"],
                ballot["team"],
                ballot["vote"],
            )
        )
    print(
        "Tally: {0} aye, {1} nay — {2}.".format(
            tally["ayes"],
            tally["nays"],
            verdict,
        )
    )

    record = {
        "season": calendar.current_season,
        "motion": tally["motion"],
        "choice_id": result.get("choice_id"),
        "choice_label": result.get("choice_label"),
        "chair": chair_team.owner.name if chair_team else None,
        "chair_team": chair_team.name if chair_team else None,
        "seats": len(tally["ballots"]),
        "ayes": tally["ayes"],
        "nays": tally["nays"],
        "passed": passed,
        "ballots": list(tally["ballots"]),
        "outcome": result.get("outcome"),
        "verdict": verdict,
    }
    league["last_owner_council"] = record
    league["season_owner_councils"].append(record)
    return record


def print_council_dashboard_line():
    """Print the owner-council line for the dashboard."""

    ensure_league_commercial_state()
    seats = owner_council_seats(teams)
    chair_team = owner_council_chair(teams)
    mood = owner_council_mood(teams, league.get("owner_pressure", 0))
    chair_text = (
        "{0} ({1})".format(chair_team.owner.name, chair_team.name)
        if chair_team is not None
        else "vacant"
    )
    session = league.get("last_owner_council")
    if not session:
        print(
            "Council: chair {0} | {1} seats | {2}".format(
                chair_text,
                len(seats),
                mood,
            )
        )
        return
    result_word = "passes" if session.get("passed") else "fails"
    print(
        "Council: chair {0} | {1} seats | last rebuke {2} {3}–{4} ({5})".format(
            chair_text,
            len(seats),
            result_word,
            session.get("ayes"),
            session.get("nays"),
            session.get("choice_label"),
        )
    )


def record_driver_council(result):
    """Tally garage feedback after the commissioner addresses the chamber."""

    ensure_league_commercial_state()
    tilt = DRIVER_COUNCIL_TILT.get(str(result.get("choice_id")), 0)
    tally = driver_council_tally(drivers, league, tilt)
    chair = driver_council_chair(drivers)
    if tally["protested"]:
        league["driver_sentiment"] = clamp(
            league.get("driver_sentiment", 60) - 5
        )
        league["controversy"] = clamp(league.get("controversy", 0) + 3)
        verdict = "the garage files a protest"
    elif tally["split"]:
        verdict = "the garage is split"
    else:
        league["driver_sentiment"] = clamp(
            league.get("driver_sentiment", 60) + 2
        )
        verdict = "the garage stands down"

    print("\nDriver Council Feedback — officiating and safety")
    if chair is not None:
        print("Chair: {0} ({1})".format(chair.name, chair.team_name))
    for ballot in tally["ballots"]:
        role = "chair " if ballot.get("chair") else ""
        print(
            "- {0}{1} ({2}): {3}".format(
                role,
                ballot["driver"],
                ballot["team"],
                ballot["vote"],
            )
        )
    print(
        "Tally: {0} concerned, {1} satisfied — {2}.".format(
            tally["concerned"],
            tally["satisfied"],
            verdict,
        )
    )

    if tally["protested"]:
        result_word = "protest"
    elif tally["split"]:
        result_word = "split"
    else:
        result_word = "stands down"

    record = {
        "season": calendar.current_season,
        "motion": tally["motion"],
        "choice_id": result.get("choice_id"),
        "choice_label": result.get("choice_label"),
        "chair": chair.name if chair else None,
        "chair_team": chair.team_name if chair else None,
        "seats": len(tally["ballots"]),
        "concerned": tally["concerned"],
        "satisfied": tally["satisfied"],
        "protested": tally["protested"],
        "split": tally["split"],
        "ballots": list(tally["ballots"]),
        "outcome": result.get("outcome"),
        "verdict": verdict,
        "result_word": result_word,
    }
    league["last_driver_council"] = record
    league["season_driver_councils"].append(record)
    return record


def print_driver_council_dashboard_line():
    """Print the driver-council line for the dashboard."""

    ensure_league_commercial_state()
    seats = driver_council_seats(drivers)
    chair = driver_council_chair(drivers)
    mood = driver_council_mood(drivers, league.get("driver_sentiment", 60))
    chair_text = (
        "{0} ({1})".format(chair.name, chair.team_name)
        if chair is not None
        else "vacant"
    )
    session = league.get("last_driver_council")
    if not session:
        print(
            "Garage: chair {0} | {1} seats | {2}".format(
                chair_text,
                len(seats),
                mood,
            )
        )
        return
    print(
        "Garage: chair {0} | {1} seats | last feedback {2} {3}–{4} ({5})".format(
            chair_text,
            len(seats),
            session.get("result_word"),
            session.get("concerned"),
            session.get("satisfied"),
            session.get("choice_label"),
        )
    )


def _proposal_source_is_garage(proposal):
    """Return whether the sponsor is the driver council."""

    return (proposal or {}).get("source") == "driver-council"


def record_rule_proposal(result, event):
    """Store a stakeholder proposal and update the docket."""

    ensure_league_commercial_state()
    proposal = dict((event or {}).get("proposal") or {})
    choice_id = str(result.get("choice_id") or "")
    if choice_id == "1":
        status = "docketed"
    elif choice_id == "2":
        status = "tabled"
    else:
        status = "killed"

    garage = _proposal_source_is_garage(proposal)
    if status == "docketed":
        if garage:
            league["driver_sentiment"] = clamp(
                league.get("driver_sentiment", 60) + 3
            )
        else:
            league["owner_pressure"] = clamp(
                league.get("owner_pressure", 0) - 3
            )
    elif status == "tabled":
        if garage:
            league["driver_sentiment"] = clamp(
                league.get("driver_sentiment", 60) - 2
            )
        else:
            league["owner_pressure"] = clamp(
                league.get("owner_pressure", 0) + 2
            )
    else:
        if garage:
            league["driver_sentiment"] = clamp(
                league.get("driver_sentiment", 60) - 6
            )
        else:
            league["owner_pressure"] = clamp(
                league.get("owner_pressure", 0) + 6
            )

    record = {
        "season": calendar.current_season,
        "status": status,
        "choice_id": result.get("choice_id"),
        "choice_label": result.get("choice_label"),
        "outcome": result.get("outcome"),
        "source": proposal.get("source"),
        "sponsor": proposal.get("sponsor"),
        "body": proposal.get("body"),
        "policy_key": proposal.get("policy_key"),
        "current_value": proposal.get("current_value"),
        "proposed_value": proposal.get("proposed_value"),
        "headline": proposal.get("headline"),
        "current_label": proposal.get("current_label"),
    }

    if status == "docketed":
        league["rule_docket"].append(dict(record))

    print("\nRule Proposal — {0}".format(record.get("headline")))
    print(
        "Sponsor: {0} ({1})".format(
            record.get("sponsor"),
            record.get("body"),
        )
    )
    print("Current: {0}".format(record.get("current_label")))
    print("Status: {0}".format(status))

    league["last_rule_proposal"] = record
    league["season_rule_proposals"].append(record)
    return record


def print_proposal_dashboard_line():
    """Print the stakeholder-proposal line for the dashboard."""

    ensure_league_commercial_state()
    docket = league.get("rule_docket") or []
    if docket:
        lead = docket[-1]
        extra = ""
        if len(docket) > 1:
            extra = " +{0} more".format(len(docket) - 1)
        print(
            "Proposals: {0} docketed — {1} ({2}){3}".format(
                len(docket),
                lead.get("headline"),
                lead.get("body"),
                extra,
            )
        )
        return
    last = league.get("last_rule_proposal")
    if not last:
        print("Proposals: none on the docket")
        return
    print(
        'Proposals: last {0} "{1}" — {2}'.format(
            last.get("status"),
            last.get("headline"),
            last.get("body"),
        )
    )


def record_lobbying(result, event):
    """Store which coalition the commissioner hosted before the vote."""

    ensure_league_commercial_state()
    proposal = dict((event or {}).get("proposal") or {})
    backing, opposition = proposal_coalitions(teams, proposal)
    choice_id = str(result.get("choice_id") or "")
    lobby_tilt = 0
    swing_delta = 0
    swing_owner = None
    if choice_id == "2":
        swing = rule_vote_swing_seat(teams, proposal, "backing")
        swing_owner = swing.owner.name if swing is not None else None
        swing_delta = LOBBY_SWING_DELTA
        hosted = "backing"
    elif choice_id == "3":
        lobby_tilt = LOBBY_OPPOSITION_TILT
        hosted = "opposition"
    else:
        hosted = "open"

    print("\nPaddock Lobbying — {0}".format(proposal.get("headline") or "the docket"))
    print(
        "For: {0} ({1})".format(
            ", ".join(coalition_label(team.owner.priority) for team in backing) or "none",
            ", ".join(team.owner.name for team in backing) or "nobody",
        )
    )
    print(
        "Against: {0} ({1})".format(
            ", ".join(coalition_label(team.owner.priority) for team in opposition) or "none",
            ", ".join(team.owner.name for team in opposition) or "nobody",
        )
    )
    if hosted == "backing" and swing_owner:
        print("Hosted: backing bloc — peeled {0}.".format(swing_owner))
    elif hosted == "opposition":
        print("Hosted: opposition — the paper cools.")
    else:
        print("Hosted: every meeting — no promises.")

    record = {
        "season": calendar.current_season,
        "choice_id": result.get("choice_id"),
        "choice_label": result.get("choice_label"),
        "outcome": result.get("outcome"),
        "hosted": hosted,
        "lobby_tilt": lobby_tilt,
        "swing_owner": swing_owner,
        "swing_delta": swing_delta,
        "backing": [team.owner.name for team in backing],
        "opposition": [team.owner.name for team in opposition],
        "source": proposal.get("source"),
        "sponsor": proposal.get("sponsor"),
        "body": proposal.get("body"),
        "policy_key": proposal.get("policy_key"),
        "proposed_value": proposal.get("proposed_value"),
        "headline": proposal.get("headline"),
    }
    league["last_lobbying"] = record
    league["season_lobbying"].append(record)
    return record


def print_coalitions_dashboard_line():
    """Print owner blocs, or for/against when a paper is on the docket."""

    ensure_league_commercial_state()
    docket = league.get("rule_docket") or []
    if docket:
        backing, opposition = proposal_coalitions(teams, docket[0])
        for_text = ", ".join(
            "{0} ({1})".format(
                coalition_label(team.owner.priority),
                team.owner.name,
            )
            for team in backing
        ) or "none"
        against_text = ", ".join(
            "{0} ({1})".format(
                coalition_label(team.owner.priority),
                team.owner.name,
            )
            for team in opposition
        ) or "none"
        print(
            "Coalitions: for {0} | against {1}".format(
                for_text,
                against_text,
            )
        )
        return
    parts = []
    for priority, bloc in owner_coalitions(teams):
        names = ", ".join(team.owner.name for team in bloc)
        parts.append(
            "{0} {1} ({2})".format(
                coalition_label(priority),
                len(bloc),
                names,
            )
        )
    print(
        "Coalitions: {0}".format(
            " | ".join(parts) if parts else "none seated"
        )
    )


def print_lobby_dashboard_line():
    """Print the last paddock-lobbying line for the dashboard."""

    ensure_league_commercial_state()
    lobby = league.get("last_lobbying")
    if not lobby:
        print("Lobby: none this season")
        return
    hosted = lobby.get("hosted")
    if hosted == "backing":
        peeled = lobby.get("swing_owner")
        extra = " (peeled {0})".format(peeled) if peeled else ""
        print(
            "Lobby: last hosted the backing bloc{0}".format(extra)
        )
        return
    if hosted == "opposition":
        print("Lobby: last hosted the opposition")
        return
    print("Lobby: last took every meeting")


def refresh_approval_ratings():
    """Recompute and store live approval from fans, owners, and drivers."""

    ensure_league_commercial_state()
    record = approval_ratings(league, teams, drivers)
    league["approval"] = dict(record)
    return record


def print_approval_dashboard_line():
    """Print the three-constituency approval line."""

    record = refresh_approval_ratings()
    print(
        "Approval: {0} {1} | Fans {2} {3} | Owners {4} {5} | Drivers {6} {7}".format(
            record["overall"],
            record["label"],
            record["fans"],
            record["fans_label"],
            record["owners"],
            record["owners_label"],
            record["drivers"],
            record["drivers_label"],
        )
    )


def review_approval_ratings():
    """Print the season's approval book and file it in career history."""

    print("\nCommissioner Approval")
    print("-" * 90)
    record = refresh_approval_ratings()
    snapshot = dict(record)
    snapshot["season"] = calendar.current_season
    league["approval_history"].append(snapshot)
    print(
        "Fans {0} {1} | Owners {2} {3} | Drivers {4} {5}".format(
            record["fans"],
            record["fans_label"],
            record["owners"],
            record["owners_label"],
            record["drivers"],
            record["drivers_label"],
        )
    )
    print(
        "Overall: {0} {1}".format(
            record["overall"],
            record["label"],
        )
    )
    return record


def refresh_job_security():
    """Recompute and store live board confidence and dismissal risk."""

    ensure_league_commercial_state()
    record = job_security_ratings(league, teams, drivers)
    league["job_security"] = dict(record)
    return record


def print_board_dashboard_line():
    """Print the board-confidence and dismissal-risk line."""

    record = refresh_job_security()
    print(
        "Board: {0} {1} | Risk {2} {3}".format(
            record["confidence"],
            record["confidence_label"],
            record["risk"],
            record["risk_label"],
        )
    )


def record_board_review(result, event):
    """Apply the board hearing and dismiss the commissioner if they fall."""

    ensure_league_commercial_state()
    security = refresh_job_security()
    tilt = BOARD_CONFIDENCE_TILT.get(str(result.get("choice_id")), 0)
    standing = max(0, min(100, int(security["confidence"]) + int(tilt)))
    dismissed = standing < BOARD_DISMISSAL_FLOOR
    standing_label = board_confidence_label(standing)
    if dismissed:
        verdict = "the board dismisses the commissioner"
    else:
        verdict = "the board keeps the commissioner"

    print("\nBoard of Directors — confidence review")
    print(
        "Standing: {0} {1} (hearing {2}{3})".format(
            standing,
            standing_label,
            "+" if tilt >= 0 else "",
            tilt,
        )
    )
    print("Verdict: {0}.".format(verdict))
    if dismissed:
        print("The board has dismissed the commissioner.")

    record = {
        "season": calendar.current_season,
        "choice_id": result.get("choice_id"),
        "choice_label": result.get("choice_label"),
        "outcome": result.get("outcome"),
        "confidence": security["confidence"],
        "confidence_label": security["confidence_label"],
        "risk": security["risk"],
        "risk_label": security["risk_label"],
        "tilt": tilt,
        "standing": standing,
        "standing_label": standing_label,
        "dismissed": dismissed,
        "verdict": verdict,
    }
    league["last_board_review"] = record
    league["season_board_reviews"].append(record)
    league["board_history"].append(dict(record))
    if dismissed:
        league["dismissed"] = True
        league["dismissal"] = dict(record)
    return record


def review_job_security():
    """Print the season's board book and file it when no hearing was held."""

    print("\nJob Security")
    print("-" * 90)
    record = refresh_job_security()
    hearing = league.get("last_board_review")
    if hearing and hearing.get("season") == calendar.current_season:
        print(
            "Board {0} {1} | Risk {2} {3}".format(
                hearing.get("standing", record["confidence"]),
                hearing.get("standing_label")
                or hearing.get("confidence_label")
                or record["confidence_label"],
                record["risk"],
                record["risk_label"],
            )
        )
        print("Hearing: {0} — {1}.".format(
            hearing.get("choice_label") or "review",
            hearing.get("verdict"),
        ))
        return hearing
    snapshot = dict(record)
    snapshot["season"] = calendar.current_season
    snapshot["standing"] = record["confidence"]
    snapshot["dismissed"] = False
    snapshot["verdict"] = "no hearing — the chair is steady"
    league["last_board_review"] = snapshot
    league["season_board_reviews"].append(snapshot)
    league["board_history"].append(dict(snapshot))
    print(
        "Board {0} {1} | Risk {2} {3}".format(
            record["confidence"],
            record["confidence_label"],
            record["risk"],
            record["risk_label"],
        )
    )
    print("The board does not call a hearing.")
    return snapshot


def record_rule_vote(result, event):
    """Tally the docket vote and apply the policy if it passes."""

    ensure_league_commercial_state()
    proposal = dict((event or {}).get("proposal") or {})
    tilt = RULE_VOTE_TILT.get(str(result.get("choice_id")), 0)
    tally = rule_vote_tally(
        teams,
        proposal,
        tilt,
        league.get("last_lobbying"),
    )
    chair_team = owner_council_chair(teams)
    passed = tally["passed"]
    if passed:
        key = proposal.get("policy_key")
        value = proposal.get("proposed_value")
        if key:
            current_policies[key] = value
        league["integrity"] = clamp(league.get("integrity", 0) + 1)
        league["controversy"] = clamp(league.get("controversy", 0) + 2)
        verdict = "the motion passes"
    else:
        verdict = "the motion fails"

    docket = list(league.get("rule_docket") or [])
    if docket:
        league["rule_docket"] = docket[1:]

    headline = proposal.get("headline") or "a rule change"
    print("\nRule Vote — {0}".format(headline))
    if chair_team is not None:
        print(
            "Chair: {0} ({1})".format(
                chair_team.owner.name,
                chair_team.name,
            )
        )
    print(
        "Sponsor: {0} ({1})".format(
            proposal.get("sponsor") or "a stakeholder",
            proposal.get("body") or "the paddock",
        )
    )
    for ballot in tally["ballots"]:
        role = "chair " if ballot.get("chair") else ""
        print(
            "- {0}{1} ({2}): {3}".format(
                role,
                ballot["owner"],
                ballot["team"],
                ballot["vote"],
            )
        )
    print(
        "Tally: {0} aye, {1} nay — {2}.".format(
            tally["ayes"],
            tally["nays"],
            verdict,
        )
    )
    if passed:
        print(
            "Policy: {0} is now in force.".format(
                proposal.get("headline") or proposal.get("proposed_value")
            )
        )
    else:
        print("Policy: the rulebook is unchanged.")

    last_proposal = league.get("last_rule_proposal")
    if isinstance(last_proposal, dict):
        same_paper = (
            last_proposal.get("policy_key") == proposal.get("policy_key")
            and last_proposal.get("proposed_value")
            == proposal.get("proposed_value")
        )
        if same_paper:
            last_proposal["status"] = "passed" if passed else "rejected"

    record = {
        "season": calendar.current_season,
        "motion": tally["motion"],
        "choice_id": result.get("choice_id"),
        "choice_label": result.get("choice_label"),
        "chair": chair_team.owner.name if chair_team else None,
        "chair_team": chair_team.name if chair_team else None,
        "seats": len(tally["ballots"]),
        "ayes": tally["ayes"],
        "nays": tally["nays"],
        "passed": passed,
        "ballots": list(tally["ballots"]),
        "outcome": result.get("outcome"),
        "verdict": verdict,
        "source": proposal.get("source"),
        "sponsor": proposal.get("sponsor"),
        "body": proposal.get("body"),
        "policy_key": proposal.get("policy_key"),
        "current_value": proposal.get("current_value"),
        "proposed_value": proposal.get("proposed_value"),
        "headline": proposal.get("headline"),
        "current_label": proposal.get("current_label"),
    }
    league["last_rule_vote"] = record
    league["season_rule_votes"].append(record)
    return record


def print_rule_vote_dashboard_line():
    """Print the last rule-vote line for the dashboard."""

    ensure_league_commercial_state()
    vote = league.get("last_rule_vote")
    if not vote:
        print("Vote: none this season")
        return
    verb = "passes" if vote.get("passed") else "fails"
    print(
        "Vote: last {0} {1} {2}–{3} ({4})".format(
            vote.get("headline") or "proposal",
            verb,
            vote.get("ayes"),
            vote.get("nays"),
            vote.get("choice_label") or "vote",
        )
    )


def present_events(event_list):
    """Present each unresolved event in order."""

    results = []

    for event in event_list:
        result = present_decision_event(event)
        if result and result.get("category") == "press-conference":
            record_press_conference(
                result,
                league.get("last_media_stories") or [],
            )
        if result and result.get("category") == "media-controversy":
            record_media_controversy(
                result,
                event,
                league.get("last_media_stories") or [],
            )
            if result.get("choice_id") == "1":
                apply_scandal_sponsor_shock(6)
        if result and result.get("category") == "owner-council":
            record_owner_council(result)
        if result and result.get("category") == "driver-council":
            record_driver_council(result)
        if result and result.get("category") == "rule-proposal":
            record_rule_proposal(result, event)
        if result and result.get("category") == "lobbying":
            record_lobbying(result, event)
        if result and result.get("category") == "rule-vote":
            record_rule_vote(result, event)
        if result and result.get("category") == "board-confidence":
            record_board_review(result, event)
        if result:
            results.append(result)

    return results


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


def unsponsored_stipend(team):
    """Return contingency cash for a team with no main sponsor."""

    team_drivers = get_team_drivers(team.name)

    if team_drivers:
        average_popularity = (
            sum(driver.popularity for driver in team_drivers)
            / len(team_drivers)
        )
    else:
        average_popularity = 50

    income = BASE_SPONSORSHIP
    income += team.facility_level * 100_000
    income += team.championships * 300_000
    income += get_team_season_wins(team.name) * 75_000
    income += int(average_popularity * 2_500)
    income += team.sponsor_appeal() * 2_000
    income = int(income * UNSPONSORED_STIPEND_FACTOR)

    if team.financial_status_label() == "Insolvent":
        income = int(income * 0.75)
    elif team.financial_status_label() == "Struggling":
        income = int(income * 0.90)

    return max(100_000, income)


def calculate_sponsorship_income(team):
    """Return this offseason's team sponsorship check."""

    if team.has_primary_sponsor():
        base = team.primary_sponsor["value"]
        return int(
            base
            * sponsor_pay_multiplier(
                team.primary_sponsor.get("satisfaction", 55)
            )
        )

    return unsponsored_stipend(team)


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
        print(f"  Main sponsor: {team.primary_sponsor_label()}")
        print(f"  Sponsorship revenue: ${summary['sponsorship']:,}")

        top_interest = top_sponsors_for_team(team)

        if top_interest:
            market_text = ", ".join(
                f"{sponsor.name} {score}"
                for score, sponsor in top_interest
            )
            print(f"  Market interest: {market_text}")
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


def run_offseason_team_sponsors():
    """Tick main-sponsor years, expire finished deals, and sign free teams."""

    print("\nTeam Sponsors")
    print("-" * 90)

    expired = []
    blocked = walk_block_set()
    declined = []

    for team in teams:
        previous_sponsor = (
            team.primary_sponsor["sponsor"]
            if team.has_primary_sponsor()
            else None
        )
        satisfaction = (
            team.primary_sponsor.get("satisfaction", 55)
            if team.has_primary_sponsor()
            else 55
        )

        if team.advance_primary_sponsor():
            expired.append((team, previous_sponsor))
            if satisfaction < SPONSOR_RENEWAL_MIN_SATISFACTION:
                blocked.add((previous_sponsor, team.name))
                declined.append((previous_sponsor, team.name, satisfaction))

    signed = assign_team_sponsor_deals(
        season=calendar.current_season,
        apply_signing_boost=False,
        blocked=blocked,
    )
    signed_by_name = {deal["team"].name: deal for deal in signed}

    lapsed = []
    renewals = []
    fresh = []

    for team, previous_sponsor in expired:
        deal = signed_by_name.get(team.name)
        if deal and deal["sponsor"].name == previous_sponsor:
            renewals.append(deal)
        elif not deal:
            lapsed.append(team)

    for deal in signed:
        if deal not in renewals:
            fresh.append(deal)

    for team in lapsed:
        team.prestige = clamp(team.prestige - 4)
        team.owner.pressure = clamp(team.owner.pressure + 5)

    for deal in fresh:
        team = deal["team"]
        team.prestige = clamp(team.prestige + 2)
        team.owner.patience = clamp(team.owner.patience + 2)
        team.owner.pressure = clamp(team.owner.pressure - 3)

    if declined:
        print("Declined renewals")
        for sponsor_name, team_name, satisfaction in declined:
            print(
                f"- {sponsor_name} will not renew with {team_name} "
                f"({sponsor_satisfaction_label(satisfaction)})"
            )

    if lapsed:
        print("Expired contracts")
        for team in lapsed:
            print(f"- {team.name} is now unsponsored")

    if renewals:
        print("Renewals")
        for deal in renewals:
            year_word = "year" if deal["years"] == 1 else "years"
            print(
                f"- {deal['team'].name} renews with "
                f"{deal['sponsor'].name} — ${deal['value']:,}/yr "
                f"for {deal['years']} {year_word}"
            )

    if fresh:
        print("New contracts")
        for deal in fresh:
            year_word = "year" if deal["years"] == 1 else "years"
            print(
                f"- {deal['team'].name} signs with "
                f"{deal['sponsor'].name} — ${deal['value']:,}/yr "
                f"for {deal['years']} {year_word} "
                f"(interest {deal['interest']})"
            )

    unsigned = [
        team for team in teams if not team.has_primary_sponsor()
    ]

    if unsigned:
        print("Unsponsored")
        for team in unsigned:
            print(
                f"- {team.name} has no main sponsor "
                "(contingency stipend only)"
            )

    if not lapsed and not renewals and not fresh and not unsigned:
        print("All main-sponsor contracts continue.")


def run_offseason_endorsements():
    """Pay personal deals, expire finished years, and sign free drivers."""

    print("\nDriver Endorsements")
    print("-" * 90)

    paid = []
    expired = []
    blocked = walk_block_set()
    declined = []

    for driver in drivers:
        previous_sponsor = (
            driver.endorsement["sponsor"]
            if driver.has_endorsement()
            else None
        )
        satisfaction = (
            driver.endorsement.get("satisfaction", 55)
            if driver.has_endorsement()
            else 55
        )
        amount = driver.collect_endorsement_pay()

        if amount:
            paid.append((driver, amount, driver.endorsement_label()))

        if driver.advance_endorsement():
            expired.append((driver, previous_sponsor))
            if satisfaction < SPONSOR_RENEWAL_MIN_SATISFACTION:
                blocked.add((previous_sponsor, driver.name))
                declined.append((previous_sponsor, driver.name, satisfaction))

    if paid:
        print("Payouts")
        for driver, amount, label in paid:
            print(f"- {driver.name} collected ${amount:,} ({label})")
    else:
        print("No personal-sponsor payouts this offseason.")

    signed = assign_endorsement_deals(
        season=calendar.current_season,
        apply_signing_boost=True,
        blocked=blocked,
    )
    signed_by_name = {
        deal["driver"].name: deal for deal in signed
    }

    lapsed = []
    renewals = []
    fresh = []

    for driver, previous_sponsor in expired:
        deal = signed_by_name.get(driver.name)
        if deal and deal["sponsor"].name == previous_sponsor:
            renewals.append(deal)
        elif not deal:
            lapsed.append(driver)

    for deal in signed:
        if deal not in renewals:
            fresh.append(deal)

    if declined:
        print("Declined renewals")
        for sponsor_name, driver_name, satisfaction in declined:
            print(
                f"- {sponsor_name} will not re-sign {driver_name} "
                f"({sponsor_satisfaction_label(satisfaction)})"
            )

    if lapsed:
        print("Expired deals")
        for driver in lapsed:
            print(f"- {driver.name} is now unsponsored")

    if renewals:
        print("Renewals")
        for deal in renewals:
            year_word = "year" if deal["years"] == 1 else "years"
            print(
                f"- {deal['driver'].name} renews with "
                f"{deal['sponsor'].name} — ${deal['value']:,}/yr "
                f"for {deal['years']} {year_word}"
            )

    if fresh:
        print("New deals")
        for deal in fresh:
            year_word = "year" if deal["years"] == 1 else "years"
            print(
                f"- {deal['driver'].name} signs with "
                f"{deal['sponsor'].name} — ${deal['value']:,}/yr "
                f"for {deal['years']} {year_word} "
                f"(interest {deal['interest']})"
            )

    unsigned = [
        driver for driver in drivers if not driver.has_endorsement()
    ]

    if unsigned:
        print("Unsigned")
        for driver in unsigned:
            print(f"- {driver.name} remains unsponsored")

    refresh_all_driver_happiness()


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
    run_offseason_team_sponsors()
    run_offseason_endorsements()
    run_offseason_league_sponsors()
    run_offseason_tv_rights()
    run_offseason_sponsor_market()
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


def record_race_history(track, race_number, results, weekend, race_points=None):
    """Save the results of a completed race."""

    race_points = race_points or {}

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
                "points_earned": race_points.get(driver.name, 0),
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
    apply_race_tv_rating(race_record, track, results, weekend)
    apply_race_gate(race_record, track, results, weekend)
    apply_race_media_stories(race_record, track, results, weekend)
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

    bonuses = get_scoring_bonuses()
    speeding_penalty = get_points_speeding_penalty()
    race_points = {}

    pole_name = None
    for entry in results:
        if entry.get("qualifying_position") == 1:
            pole_name = entry["driver"].name
            break

    hard_charger_name = None
    best_gain = 0

    for entry_position, entry in enumerate(results, start=1):
        if entry["status"] != "Running":
            continue

        gain = entry.get("start", entry_position) - entry_position

        if gain > best_gain:
            best_gain = gain
            hard_charger_name = entry["driver"].name

    for position, result in enumerate(results, start=1):
        driver = result["driver"]
        status = result["status"]
        finish_points = get_points_by_position()[position - 1]
        stage_points = weekend["stage_points"].get(driver.name, 0)
        prize_money = int(
            track.purse * PRIZE_PERCENTAGES[position - 1]
        )
        start_position = result.get("start", position)
        strategy = result_strategy_text(result)

        bonus_points = 0
        bonus_parts = []

        if status == "Running" and position == 1 and bonuses["win"]:
            bonus_points += bonuses["win"]
            bonus_parts.append(f"win +{bonuses['win']}")

        if driver.name == pole_name and bonuses["pole"]:
            bonus_points += bonuses["pole"]
            bonus_parts.append(f"pole +{bonuses['pole']}")

        if driver.name == hard_charger_name and bonuses["hard_charger"]:
            bonus_points += bonuses["hard_charger"]
            bonus_parts.append(f"charger +{bonuses['hard_charger']}")

        points_penalty = 0

        if speeding_penalty and result.get("pit_mistake_type") == "speeding":
            points_penalty = speeding_penalty
            bonus_parts.append(f"speeding -{speeding_penalty}")

        points_earned = max(
            0,
            finish_points + stage_points + bonus_points - points_penalty,
        )

        race_points[driver.name] = points_earned

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

        breakdown = []

        if stage_points:
            breakdown.append(f"finish {finish_points} + stage {stage_points}")
        elif bonus_parts:
            breakdown.append(f"finish {finish_points}")

        breakdown.extend(bonus_parts)

        if breakdown:
            points_text = f"{points_earned} pts ({'; '.join(breakdown)})"
        else:
            points_text = f"{points_earned} pts"

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
    record_race_history(track, race_number, results, weekend, race_points)
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
    apply_ruling_sponsor_fallout(choice, driver, team)


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
        print(f"  Main sponsor: {team.primary_sponsor_label()}")
        top_interest = top_sponsors_for_team(team)

        if top_interest:
            market_text = ", ".join(
                f"{sponsor.name} {score}"
                for score, sponsor in top_interest
            )
            print(f"  Market interest: {market_text}")


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


def compute_playoff_results():
    """Compute playoff seeds and champion from the season's race history.

    Seeds are the top drivers by points earned in the regular-season races;
    the champion is the seed with the most points across the final playoff
    races (regular-season points break ties). Returns None when the playoff
    format is off or there is not enough of a season to run one.
    """

    if not uses_playoff():
        return None

    total_races = len(race_history)
    race_count = min(get_playoff_race_count(), max(0, total_races - 1))

    if total_races < 2 or race_count < 1:
        return None

    cutoff = total_races - race_count
    active_names = {driver.name for driver in drivers}

    seed_points = {}
    playoff_points = {}

    for index, race in enumerate(race_history):
        for entry in race["results"]:
            name = entry["driver"]
            earned = entry.get("points_earned", 0)

            if index < cutoff:
                seed_points[name] = seed_points.get(name, 0) + earned
            else:
                playoff_points[name] = playoff_points.get(name, 0) + earned

    ranked = sorted(
        (name for name in seed_points if name in active_names),
        key=lambda name: (seed_points[name], playoff_points.get(name, 0)),
        reverse=True,
    )

    seeds = ranked[: get_playoff_field_size()]

    if not seeds:
        return None

    champion = max(
        seeds,
        key=lambda name: (
            playoff_points.get(name, 0),
            seed_points.get(name, 0),
        ),
    )

    return {
        "cutoff": cutoff,
        "race_count": race_count,
        "seeds": seeds,
        "seed_points": seed_points,
        "playoff_points": playoff_points,
        "champion": champion,
    }


def get_driver_champion():
    playoff = compute_playoff_results()

    if playoff is not None:
        return get_driver(playoff["champion"])

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
            f"- Bond {driver.teammate_bond} "
            f"- Deal: {driver.endorsement_label()}"
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
        if race.get("tv_rating") is not None:
            print(
                f"    TV: {race['tv_rating']} "
                f"({format_viewers(race.get('tv_viewers'))} viewers) "
                f"— {race.get('tv_network') or 'syndication'}"
            )
        if race.get("gate_attendance") is not None:
            print(
                f"    Gate: {format_gate_house(race.get('gate_attendance'), race.get('gate_capacity'), race.get('gate_fill'))}"
            )
        media = race.get("media_stories") or []
        if media:
            lead = media[0]
            print(f'    Media: "{lead["headline"]}" — {lead["outlet"]}')


def get_manufacturer_standings():
    """Return manufacturers ranked by season points.

    Each race awards manufacturer points based on the finishing position of
    that manufacturer's best-placed car (NASCAR-style best-finisher scoring).
    """

    team_manufacturer = {team.name: team.manufacturer for team in teams}
    points_table = get_manufacturer_points_by_position()
    points = {}

    for race in race_history:
        best_position = {}

        for entry in race["results"]:
            manufacturer = team_manufacturer.get(entry["team"], "Independent")
            position = entry["position"]

            if (
                manufacturer not in best_position
                or position < best_position[manufacturer]
            ):
                best_position[manufacturer] = position

        for manufacturer, position in best_position.items():
            index = position - 1
            earned = (
                points_table[index]
                if index < len(points_table)
                else points_table[-1]
            )
            points[manufacturer] = points.get(manufacturer, 0) + earned

    return sorted(points.items(), key=lambda item: item[1], reverse=True)


def get_manufacturer_champion():
    """Return the name of the manufacturer leading the standings, if any."""

    standings = get_manufacturer_standings()

    return standings[0][0] if standings else None


def display_manufacturer_standings():
    """Display the manufacturer championship standings."""

    standings = get_manufacturer_standings()

    if not standings:
        return

    print("\nManufacturer Standings")
    print("-" * 90)

    for rank, (manufacturer, points) in enumerate(standings, start=1):
        badged_teams = ", ".join(
            team.name
            for team in teams
            if team.manufacturer == manufacturer
        )
        print(f"{rank}. {manufacturer} — {points} pts ({badged_teams})")


def get_team_points(team):
    """Return a team's season points (sum of its drivers' championship points)."""

    return sum(driver.points for driver in get_team_drivers(team.name))


def get_team_standings():
    """Return teams ranked by season points, then race wins."""

    return sorted(
        teams,
        key=lambda team: (
            get_team_points(team),
            get_team_season_wins(team.name),
        ),
        reverse=True,
    )


def get_team_champion():
    """Return the organization (team-points) champion, if any."""

    standings = get_team_standings()

    return standings[0] if standings else None


def display_team_standings():
    """Display the organization championship standings by team points."""

    standings = get_team_standings()

    if not standings:
        return

    print("\nTeam Standings — Organization Championship")
    print("-" * 90)

    for rank, team in enumerate(standings, start=1):
        print(
            f"{rank}. {team.name} [{team.manufacturer}] "
            f"- {get_team_points(team)} pts "
            f"- {get_team_season_wins(team.name)} wins "
            f"- Owner: {team.owner.name}"
        )


def display_playoff_results():
    """Display the championship playoff bracket, when the format is active."""

    playoff = compute_playoff_results()

    if playoff is None:
        return

    champion = playoff["champion"]
    ranked_seeds = sorted(
        playoff["seeds"],
        key=lambda name: (
            playoff["playoff_points"].get(name, 0),
            playoff["seed_points"].get(name, 0),
        ),
        reverse=True,
    )

    print("\nChampionship Playoff")
    print("-" * 90)
    print(
        f"Format: {policy_label('championship_format')} — "
        f"top {len(playoff['seeds'])} seeds decided over "
        f"the final {playoff['race_count']} races"
    )

    for rank, name in enumerate(ranked_seeds, start=1):
        marker = "  <-- Champion" if name == champion else ""
        print(
            f"{rank}. {name} — "
            f"seeded {playoff['seed_points'].get(name, 0)} pts, "
            f"playoff {playoff['playoff_points'].get(name, 0)} pts"
            f"{marker}"
        )


def display_season_awards():
    """Display championship and end-of-season awards."""

    champion = get_driver_champion()
    most_wins = get_most_wins_driver()
    most_popular = get_most_popular_driver()
    reliable_team = get_most_reliable_team()
    manufacturer_champion = get_manufacturer_champion()
    commissioner_score, commissioner_grade = calculate_commissioner_grade()

    print("\nSeason Awards")
    print("-" * 90)

    print(
        f"Series Champion: {champion.name} "
        f"({champion.team_name}) "
        f"- {champion.points} points"
    )

    organization_champion = get_team_champion()

    if organization_champion is not None:
        print(
            f"Organization Champion: {organization_champion.name} "
            f"- {get_team_points(organization_champion)} team points"
        )

    if manufacturer_champion:
        print(f"Manufacturer Champion: {manufacturer_champion}")

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
    print(f"Series: {series_name()}")
    print(f"Naming rights: {league_deal_label(league.get('naming_rights'))}")
    print(
        f"Sponsor market: {len(sponsors)} active, "
        f"{len(idle_sponsors())} idle, "
        f"{len(sponsor_prospects)} waiting"
    )
    print(f"Broadcast market: {len(networks)} networks")
    print(f"TV rights: {tv_deal_label(league.get('tv_rights'))}")
    avg_rating = average_tv_rating()
    if avg_rating is None:
        print("TV ratings: season not started")
    else:
        print(
            f"TV ratings: last {league.get('last_tv_rating')} "
            f"({format_viewers(league.get('last_tv_viewers'))}) | "
            f"season avg {avg_rating} | "
            f"{tv_rating_trend_label()}"
        )
    avg_fill = average_gate_fill()
    if avg_fill is None:
        print("Gate: season not started")
    else:
        print(
            "Gate: last "
            f"{format_gate_house(league.get('last_gate_attendance'), league.get('last_gate_capacity'), league.get('last_gate_fill'))} "
            f"| season avg {avg_fill}% | "
            f"{gate_trend_label()}"
        )
    season_stories = league.get("season_media_stories") or []
    last_stories = league.get("last_media_stories") or []
    if not season_stories:
        print("Media: season not started")
    else:
        print(
            f"Media: {len(last_stories)} last weekend | "
            f"{len(season_stories)} this season"
        )
        for story in last_stories:
            print(f'- "{story["headline"]}" — {story["outlet"]}')
    print_press_dashboard_line()
    print_scandal_dashboard_line()
    print_council_dashboard_line()
    print_driver_council_dashboard_line()
    print_proposal_dashboard_line()
    print_coalitions_dashboard_line()
    print_lobby_dashboard_line()
    print_rule_vote_dashboard_line()
    print(f"League integrity: {league['integrity']}/100")
    print(f"Fan interest: {league['fan_interest']}/100")
    print(f"Controversy: {league['controversy']}/100")
    print(f"Treasury: ${league.get('treasury', 0):,}")
    print(f"Fines collected: ${league['fines_collected']:,}")
    print(f"Owner pressure: {league['owner_pressure']}/100")
    print(f"Driver sentiment: {league['driver_sentiment']}/100")
    print_approval_dashboard_line()
    print_board_dashboard_line()


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
            "sponsor_conflicts": current_season_conflicts(),
            "series_name": series_name(),
            "treasury": league.get("treasury", 0),
            "naming_rights": (
                dict(league["naming_rights"])
                if has_naming_rights()
                else None
            ),
            "official_partners": [
                dict(partner)
                for partner in league.get("official_partners") or []
            ],
            "season_commercial_income": league.get(
                "season_commercial_income",
                0,
            ),
            "career_commercial_income": league.get(
                "career_commercial_income",
                0,
            ),
            "sponsor_market_size": len(sponsors),
            "idle_sponsors": [
                sponsor.name for sponsor in idle_sponsors()
            ],
            "waiting_prospects": [
                sponsor.name for sponsor in sponsor_prospects
            ],
            "sponsor_market_log": current_season_market_moves(),
            "tv_rights": (
                dict(league["tv_rights"])
                if has_tv_rights()
                else None
            ),
            "season_tv_income": league.get("season_tv_income", 0),
            "career_tv_income": league.get("career_tv_income", 0),
            "season_tv_rating": average_tv_rating(),
            "season_tv_viewers": average_tv_viewers(),
            "tv_rating_trend": tv_rating_trend_label(),
            "tv_rating_history": list(league.get("tv_rating_history") or []),
            "season_gate_fill": average_gate_fill(),
            "season_gate_attendance": average_gate_attendance(),
            "gate_trend": gate_trend_label(),
            "gate_history": list(league.get("gate_history") or []),
            "season_media_count": len(league.get("season_media_stories") or []),
            "last_media_stories": list(league.get("last_media_stories") or []),
            "season_press_conferences": list(
                league.get("season_press_conferences") or []
            ),
            "last_press_conference": (
                dict(league["last_press_conference"])
                if league.get("last_press_conference")
                else None
            ),
            "season_media_controversies": list(
                league.get("season_media_controversies") or []
            ),
            "last_media_controversy": (
                dict(league["last_media_controversy"])
                if league.get("last_media_controversy")
                else None
            ),
            "season_owner_councils": list(
                league.get("season_owner_councils") or []
            ),
            "last_owner_council": (
                dict(league["last_owner_council"])
                if league.get("last_owner_council")
                else None
            ),
            "season_driver_councils": list(
                league.get("season_driver_councils") or []
            ),
            "last_driver_council": (
                dict(league["last_driver_council"])
                if league.get("last_driver_council")
                else None
            ),
            "season_rule_proposals": list(
                league.get("season_rule_proposals") or []
            ),
            "last_rule_proposal": (
                dict(league["last_rule_proposal"])
                if league.get("last_rule_proposal")
                else None
            ),
            "rule_docket": list(league.get("rule_docket") or []),
            "season_rule_votes": list(
                league.get("season_rule_votes") or []
            ),
            "last_rule_vote": (
                dict(league["last_rule_vote"])
                if league.get("last_rule_vote")
                else None
            ),
            "season_lobbying": list(
                league.get("season_lobbying") or []
            ),
            "last_lobbying": (
                dict(league["last_lobbying"])
                if league.get("last_lobbying")
                else None
            ),
            "approval": (
                dict(league["approval"])
                if league.get("approval")
                else None
            ),
            "approval_history": list(
                league.get("approval_history") or []
            ),
            "job_security": (
                dict(league["job_security"])
                if league.get("job_security")
                else None
            ),
            "season_board_reviews": list(
                league.get("season_board_reviews") or []
            ),
            "last_board_review": (
                dict(league["last_board_review"])
                if league.get("last_board_review")
                else None
            ),
            "board_history": list(league.get("board_history") or []),
            "dismissed": bool(league.get("dismissed")),
            "dismissal": (
                dict(league["dismissal"])
                if league.get("dismissal")
                else None
            ),
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
            "manufacturer_champion": get_manufacturer_champion(),
            "organization_champion": (
                get_team_champion().name
                if get_team_champion() is not None
                else None
            ),
        },
        "manufacturer_standings": [
            {"manufacturer": manufacturer, "points": points}
            for manufacturer, points in get_manufacturer_standings()
        ],
        "team_standings": [
            {
                "position": position,
                "team": team.name,
                "manufacturer": team.manufacturer,
                "points": get_team_points(team),
                "wins": get_team_season_wins(team.name),
            }
            for position, team in enumerate(get_team_standings(), start=1)
        ],
        "sponsors": [
            {
                "name": sponsor.name,
                "industry": sponsor.industry,
                "wealth": sponsor.wealth,
                "risk_tolerance": sponsor.risk_tolerance,
                "prestige_preference": sponsor.prestige_preference,
                "performance_preference": sponsor.performance_preference,
                "popularity_preference": sponsor.popularity_preference,
                "conduct_preference": sponsor.conduct_preference,
                "manufacturer_affinity": sponsor.manufacturer_affinity,
                "preferred_track_types": list(sponsor.preferred_track_types),
                "spending_power": sponsor.spending_power(),
                "preference_summary": sponsor.preference_summary(),
                "risk_posture": sponsor.risk_posture(),
                "primary_objective": sponsor.primary_objective(),
                "favorite_team": (
                    best_team_for_sponsor(sponsor)[0].name
                    if best_team_for_sponsor(sponsor)[0] is not None
                    else None
                ),
                "favorite_team_interest": best_team_for_sponsor(sponsor)[1],
                "endorsed_driver": (
                    driver_backed_by(sponsor).name
                    if driver_backed_by(sponsor) is not None
                    else None
                ),
                "titled_team": (
                    team_titled_by(sponsor).name
                    if team_titled_by(sponsor) is not None
                    else None
                ),
                "names_series": series_named_by(sponsor),
                "official_partner": (
                    official_partner_named(sponsor)["category"]
                    if official_partner_named(sponsor) is not None
                    else None
                ),
                "team_interest": [
                    {
                        "team": team.name,
                        "score": sponsor.interest_in_team(
                            team,
                            get_team_drivers(team.name),
                            get_team_season_wins(team.name),
                        ),
                    }
                    for team in teams
                ],
            }
            for sponsor in sponsors
        ],
        "networks": [
            {
                "name": network.name,
                "kind": network.kind,
                "reach": network.reach,
                "wealth": network.wealth,
                "risk_tolerance": network.risk_tolerance,
                "prestige_preference": network.prestige_preference,
                "excitement_preference": network.excitement_preference,
                "star_preference": network.star_preference,
                "integrity_preference": network.integrity_preference,
                "preferred_track_types": list(network.preferred_track_types),
                "rights_value": network.rights_value(),
                "profile_summary": network.profile_summary(),
                "risk_posture": network.risk_posture(),
                "league_interest": network.interest_in_league(league),
                "holds_rights": series_televised_by(network),
                "rights_bid": tv_rights_terms(network)[1],
                "rights_years": tv_rights_terms(network)[2],
                "favorite_weekend": (
                    best_weekend_for_network(network)[0].name
                    if best_weekend_for_network(network)[0] is not None
                    else None
                ),
                "favorite_weekend_interest": best_weekend_for_network(network)[1],
            }
            for network in networks
        ],
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
                "endorsement": (
                    dict(driver.endorsement) if driver.endorsement else None
                ),
                "endorsement_label": driver.endorsement_label(),
                "season_endorsement_income": (
                    driver.season_endorsement_income
                ),
                "career_endorsement_income": (
                    driver.career_endorsement_income
                ),
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
                "manufacturer": team.manufacturer,
                "owner": team.owner.name,
                "owner_personality": team.owner.personality,
                "owner_priority": team.owner.priority,
                "organization_titles": team.organization_titles,
                "budget": team.budget,
                "facility_level": team.facility_level,
                "facility_rating": team.facility_rating(),
                "financial_status": team.financial_status_label(),
                "prestige": team.prestige,
                "attractiveness": team.attractiveness(),
                "sponsor_appeal": team.sponsor_appeal(),
                "primary_sponsor": (
                    dict(team.primary_sponsor)
                    if team.primary_sponsor
                    else None
                ),
                "primary_sponsor_label": team.primary_sponsor_label(),
                "unsponsored": not team.has_primary_sponsor(),
                "market_interest": [
                    {
                        "sponsor": sponsor.name,
                        "score": score,
                    }
                    for score, sponsor in top_sponsors_for_team(team)
                ],
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

    tracks.clear()
    tracks.extend(generate_season_schedule(season_number))

    league["integrity"] = 70
    league["fan_interest"] = 65
    league["controversy"] = 20
    league["fines_collected"] = 0
    league["sponsor_walk_blocks"] = []
    league["season_commercial_income"] = 0
    league["season_tv_income"] = 0
    league["season_tv_ratings"] = []
    league["season_tv_viewers"] = []
    league["last_tv_rating"] = None
    league["last_tv_viewers"] = None
    league["season_gate_attendance"] = []
    league["season_gate_fill"] = []
    league["last_gate_attendance"] = None
    league["last_gate_capacity"] = None
    league["last_gate_fill"] = None
    league["last_gate_draw"] = None
    league["season_media_stories"] = []
    league["last_media_stories"] = []
    league["season_press_conferences"] = []
    league["last_press_conference"] = None
    league["season_media_controversies"] = []
    league["last_media_controversy"] = None
    league["season_owner_councils"] = []
    league["last_owner_council"] = None
    league["season_driver_councils"] = []
    league["last_driver_council"] = None
    league["season_rule_proposals"] = []
    league["last_rule_proposal"] = None
    league["season_rule_votes"] = []
    league["last_rule_vote"] = None
    league["season_lobbying"] = []
    league["last_lobbying"] = None
    league["season_board_reviews"] = []
    league["last_board_review"] = None
    league["job_security"] = None

    for team in teams:
        team.start_new_season()

    for driver in drivers:
        driver.reset_season()

        # Small recovery between seasons
        driver.morale = clamp(driver.morale + 5)

    refresh_all_driver_happiness()

    print("\n" + "=" * 90)
    print(f"STOCK CAR COMMISSIONER — {series_name().upper()} — SEASON {season_number}")
    print("=" * 90)
    present_events(
        lobbying_events(
            season_number,
            teams,
            events_resolved,
            league,
        )
    )
    present_events(
        rule_vote_events(
            season_number,
            teams,
            events_resolved,
            league,
        )
    )
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

    organization_champion = get_team_champion()

    if organization_champion is not None:
        organization_champion.record_organization_title()
        print(
            f"\n{organization_champion.name} wins the organization "
            f"championship with {get_team_points(organization_champion)} "
            "team points."
        )
        print(
            "Organization titles: "
            f"{organization_champion.organization_titles}"
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
        "approval": (
            dict(league["approval"])
            if league.get("approval")
            else None
        ),
        "job_security": (
            dict(league["job_security"])
            if league.get("job_security")
            else None
        ),
        "dismissed": bool(league.get("dismissed")),
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
                media_stories=league.get("last_media_stories"),
            )
        )
        present_events(
            media_controversy_events(
                race_number,
                league.get("last_media_stories"),
                league.get("last_press_conference"),
                events_resolved,
                controversy=league.get("controversy", 0),
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
    display_playoff_results()
    record_team_season_trends()
    review_sponsor_objectives()
    review_tv_ratings()
    review_race_popularity()
    review_media_stories()
    review_approval_ratings()
    resolve_sponsor_conflicts()
    display_team_finances()
    display_team_sponsors()
    display_driver_endorsements()
    display_league_sponsors()
    display_team_standings()
    display_manufacturer_standings()
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
        postseason_events(
            teams,
            drivers,
            events_resolved,
            league,
            season_number,
        )
    )
    present_events(
        rule_proposal_events(
            season_number,
            teams,
            drivers,
            events_resolved,
            league,
            current_policies,
        )
    )
    present_events(
        board_confidence_events(
            season_number,
            teams,
            drivers,
            events_resolved,
            league,
        )
    )
    review_job_security()


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
    if league.get("dismissed"):
        dismissal = league.get("dismissal") or {}
        print(
            "Career ended: dismissed after season {0} ({1} {2}).".format(
                dismissal.get("season") or "?",
                dismissal.get("standing", "?"),
                dismissal.get("standing_label") or "Collapsing",
            )
        )
    else:
        print("Career completed: the commissioner finished the contract.")

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
            f"- Earnings: ${driver.career_earnings:,} "
            f"- Endorsements: ${driver.career_endorsement_income:,} "
            f"- Deal: {driver.endorsement_label()}"
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
            f"- Org titles: {team.organization_titles} "
            f"- Wins: {team.career_wins} "
            f"- Prestige: {team.prestige} "
            f"- {team.performance_trend_label()} "
            f"- Shop: {team.facility_rating()} "
            f"(Lv {team.facility_level}) "
            f"- Eng: {team.engineering} "
            f"- Crew: {team.crew_rating} "
            f"- Career prize money: ${team.career_prize_money:,} "
            f"- Sponsorship income: ${team.career_sponsorship_income:,} "
            f"- Main sponsor: {team.primary_sponsor_label()} "
            f"- Current budget: ${team.budget:,} "
            f"- Status: {team.financial_status_label()}"
        )

    display_record_book()


def display_record_book():
    """Display the all-time record book at the end of a career."""

    book = build_record_book(
        drivers,
        retired_drivers,
        teams,
        career_history,
    )

    print("\nAll-Time Record Book")
    print("-" * 100)

    def show(label, record, formatter):
        if record and record[0] is not None:
            print(f"{label}: {formatter(record)}")
        else:
            print(f"{label}: n/a")

    show(
        "Most race wins",
        book["most_career_wins"],
        lambda record: f"{record[0]} ({record[1]})",
    )
    show(
        "Most championships",
        book["most_championships"],
        lambda record: f"{record[0]} ({record[1]})",
    )
    show(
        "Most wins in a season",
        book["most_wins_in_a_season"],
        lambda record: f"{record[0]} — {record[1]} in season {record[2]}",
    )
    show(
        "Highest season points",
        book["highest_season_points"],
        lambda record: f"{record[0]} — {record[1]} in season {record[2]}",
    )
    show(
        "Longest win streak",
        book["longest_win_streak"],
        lambda record: f"{record[0]} — {record[1]} straight races",
    )
    show(
        "Longest title streak",
        book["longest_title_streak"],
        lambda record: f"{record[0]} — {record[1]} straight seasons",
    )
    show(
        "Most team wins",
        book["most_team_wins"],
        lambda record: f"{record[0]} ({record[1]})",
    )
    show(
        "Most organization titles",
        book["most_organization_titles"],
        lambda record: f"{record[0]} ({record[1]})",
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
        if league.get("dismissed"):
            break
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

        if league.get("dismissed"):
            dismissal = league.get("dismissal") or {}
            print("\n" + "=" * 90)
            print("CAREER ENDED — DISMISSED BY THE BOARD")
            print("=" * 90)
            print(
                "The board dismissed the commissioner after season {0} "
                "({1}).".format(
                    dismissal.get("season") or calendar.current_season,
                    dismissal.get("verdict") or "confidence failed",
                )
            )
            break

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
    if drivers:
        print(series_name())
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

    if not any(driver.has_endorsement() for driver in drivers):
        assign_endorsement_deals(
            season=calendar.current_season,
            apply_signing_boost=False,
        )

    if not any(team.has_primary_sponsor() for team in teams):
        assign_team_sponsor_deals(
            season=calendar.current_season,
            apply_signing_boost=False,
        )

    ensure_league_commercial_state()
    if not has_naming_rights() and not league["official_partners"]:
        assign_league_deals(
            season=calendar.current_season,
            apply_signing_boost=False,
        )

    if not has_tv_rights():
        assign_tv_rights(
            season=calendar.current_season,
            apply_signing_boost=False,
        )

    run_single_season(calendar.current_season)
    calendar.advance_to_next_season()
    sync_calendar_aliases()


if __name__ == "__main__":
    main()
