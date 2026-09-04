"""Commissioner decision templates for rule, safety, owner, and driver events."""

from game.calendar import (
    OFFSEASON,
    POSTSEASON,
    PRESEASON,
    REGULAR_SEASON,
)
from game.policies import policy_label


def _team_by_pressure(teams):
    """Return the team whose owner is most likely to complain."""

    return min(
        teams,
        key=lambda team: (
            -team.financial_distress_level,
            team.owner.patience,
            -team.owner.pressure,
            team.budget,
        ),
    )


def _driver_by_unrest(drivers):
    """Return the driver most likely to file a grievance."""

    return min(
        drivers,
        key=lambda driver: (
            driver.morale + driver.commissioner_trust,
            driver.popularity,
        ),
    )


def points_system_event(policies):
    """Preseason decision about championship points."""

    current = policy_label("points_system", policies["points_system"])

    return {
        "id": "rule-points-system",
        "title": "Championship Points Structure",
        "category": "rule-change",
        "phase": PRESEASON,
        "prompt": (
            "Competition committee asks whether the championship should "
            "keep rewarding consistent finishers or swing more toward race "
            f"winners. Current policy: {current}."
        ),
        "choices": [
            {
                "id": "1",
                "label": "Keep the standard points table",
                "effects": [
                    {"type": "policy", "key": "points_system", "value": "standard"},
                    {"type": "league", "stat": "integrity", "delta": 1},
                ],
                "outcomes": [
                    {
                        "weight": 70,
                        "text": "Most garages treat it as business as usual.",
                        "effects": [],
                    },
                    {
                        "weight": 30,
                        "text": "Broadcast partners call the product predictable.",
                        "effects": [
                            {"type": "league", "stat": "fan_interest", "delta": -3},
                        ],
                    },
                ],
            },
            {
                "id": "2",
                "label": "Adopt winner-heavy scoring",
                "effects": [
                    {
                        "type": "policy",
                        "key": "points_system",
                        "value": "winner-heavy",
                    },
                    {"type": "league", "stat": "fan_interest", "delta": 6},
                    {"type": "league", "stat": "controversy", "delta": 4},
                ],
                "outcomes": [
                    {
                        "weight": 60,
                        "text": "Star drivers praise the emphasis on winning.",
                        "effects": [
                            {"type": "all_drivers", "stat": "morale", "delta": 2},
                        ],
                    },
                    {
                        "weight": 40,
                        "text": "Backmarker teams say the title hunt just got bought.",
                        "effects": [
                            {"type": "league", "stat": "owner_pressure", "delta": 8},
                            {
                                "type": "league",
                                "stat": "driver_sentiment",
                                "delta": -4,
                            },
                        ],
                    },
                ],
            },
            {
                "id": "3",
                "label": "Flatten the points so more finishers stay alive",
                "effects": [
                    {
                        "type": "policy",
                        "key": "points_system",
                        "value": "flattened",
                    },
                    {"type": "league", "stat": "integrity", "delta": 3},
                    {"type": "league", "stat": "fan_interest", "delta": -4},
                ],
                "outcomes": [
                    {
                        "weight": 65,
                        "text": "Smaller teams welcome a longer championship fight.",
                        "effects": [
                            {"type": "league", "stat": "owner_pressure", "delta": -6},
                        ],
                    },
                    {
                        "weight": 35,
                        "text": "Fans complain that winning a race barely matters.",
                        "effects": [
                            {"type": "league", "stat": "controversy", "delta": 5},
                        ],
                    },
                ],
            },
        ],
    }


def scoring_bonus_event(policies):
    """Preseason decision about bonus points for wins, poles, and charges."""

    current = policy_label("scoring_bonuses", policies["scoring_bonuses"])

    return {
        "id": "rule-scoring-bonuses",
        "title": "Bonus Points Structure",
        "category": "rule-change",
        "phase": PRESEASON,
        "prompt": (
            "Marketing wants extra storylines in the points race through "
            "bonuses for race wins, pole positions, and drivers who charge "
            f"through the field. Current policy: {current}."
        ),
        "choices": [
            {
                "id": "1",
                "label": "Keep standard bonus points",
                "effects": [
                    {
                        "type": "policy",
                        "key": "scoring_bonuses",
                        "value": "standard",
                    },
                ],
                "outcomes": [
                    {
                        "weight": 80,
                        "text": "The garage is comfortable with the current bonuses.",
                        "effects": [],
                    },
                    {
                        "weight": 20,
                        "text": "A broadcaster wishes the swings were bigger.",
                        "effects": [
                            {"type": "league", "stat": "fan_interest", "delta": -2},
                        ],
                    },
                ],
            },
            {
                "id": "2",
                "label": "Reward winning and charging with rich bonuses",
                "effects": [
                    {
                        "type": "policy",
                        "key": "scoring_bonuses",
                        "value": "rich",
                    },
                    {"type": "league", "stat": "fan_interest", "delta": 6},
                    {"type": "league", "stat": "controversy", "delta": 3},
                ],
                "outcomes": [
                    {
                        "weight": 60,
                        "text": "Aggressive drivers love the upside of a big day.",
                        "effects": [
                            {"type": "all_drivers", "stat": "morale", "delta": 2},
                        ],
                    },
                    {
                        "weight": 40,
                        "text": "Consistent points racers call the swings a gimmick.",
                        "effects": [
                            {
                                "type": "league",
                                "stat": "driver_sentiment",
                                "delta": -3,
                            },
                        ],
                    },
                ],
            },
            {
                "id": "3",
                "label": "Remove bonus points and score on finish only",
                "effects": [
                    {
                        "type": "policy",
                        "key": "scoring_bonuses",
                        "value": "none",
                    },
                    {"type": "league", "stat": "integrity", "delta": 3},
                    {"type": "league", "stat": "fan_interest", "delta": -4},
                ],
                "outcomes": [
                    {
                        "weight": 70,
                        "text": "Purists applaud a clean finishing-order table.",
                        "effects": [],
                    },
                    {
                        "weight": 30,
                        "text": "Promoters grumble that the title math got boring.",
                        "effects": [
                            {"type": "league", "stat": "controversy", "delta": 3},
                        ],
                    },
                ],
            },
        ],
    }


def championship_format_event(policies):
    """Preseason decision about how the champion is crowned."""

    current = policy_label("championship_format", policies["championship_format"])

    return {
        "id": "rule-championship-format",
        "title": "Championship Format",
        "category": "rule-change",
        "phase": PRESEASON,
        "prompt": (
            "The board wants a decision on how the title is decided: a "
            "season-long points championship, or a playoff where the top "
            "seeds settle it over the final races. "
            f"Current policy: {current}."
        ),
        "choices": [
            {
                "id": "1",
                "label": "Keep the season-long points championship",
                "effects": [
                    {
                        "type": "policy",
                        "key": "championship_format",
                        "value": "season-long",
                    },
                    {"type": "league", "stat": "integrity", "delta": 2},
                ],
                "outcomes": [
                    {
                        "weight": 75,
                        "text": "Traditionalists praise a full-season title fight.",
                        "effects": [],
                    },
                    {
                        "weight": 25,
                        "text": "Broadcasters wish for a bigger finale hook.",
                        "effects": [
                            {"type": "league", "stat": "fan_interest", "delta": -2},
                        ],
                    },
                ],
            },
            {
                "id": "2",
                "label": "Adopt a playoff to decide the champion",
                "effects": [
                    {
                        "type": "policy",
                        "key": "championship_format",
                        "value": "playoff",
                    },
                    {"type": "league", "stat": "fan_interest", "delta": 7},
                    {"type": "league", "stat": "controversy", "delta": 4},
                ],
                "outcomes": [
                    {
                        "weight": 60,
                        "text": "A win-or-go-home finale electrifies the schedule.",
                        "effects": [
                            {"type": "all_drivers", "stat": "morale", "delta": 1},
                        ],
                    },
                    {
                        "weight": 40,
                        "text": "Points purists call the reset a gimmick.",
                        "effects": [
                            {"type": "league", "stat": "integrity", "delta": -3},
                            {
                                "type": "league",
                                "stat": "driver_sentiment",
                                "delta": -3,
                            },
                        ],
                    },
                ],
            },
        ],
    }


def race_format_event(policies):
    """Preseason decision about race format."""

    current = policy_label("race_format", policies["race_format"])

    return {
        "id": "rule-race-format",
        "title": "Race Format",
        "category": "rule-change",
        "phase": PRESEASON,
        "prompt": (
            "Officials want a ruling on how Sunday afternoons are structured. "
            f"Current policy: {current}."
        ),
        "choices": [
            {
                "id": "1",
                "label": "Keep single-feature races",
                "effects": [
                    {
                        "type": "policy",
                        "key": "race_format",
                        "value": "single-feature",
                    },
                ],
                "outcomes": [
                    {
                        "weight": 80,
                        "text": "The traditional format stays in place.",
                        "effects": [],
                    },
                    {
                        "weight": 20,
                        "text": "A few promoters say the show needs more segments.",
                        "effects": [
                            {"type": "league", "stat": "fan_interest", "delta": -2},
                        ],
                    },
                ],
            },
            {
                "id": "2",
                "label": "Add heat races before the feature",
                "effects": [
                    {
                        "type": "policy",
                        "key": "race_format",
                        "value": "heat-and-feature",
                    },
                    {"type": "league", "stat": "fan_interest", "delta": 5},
                    {"type": "league", "stat": "controversy", "delta": 3},
                ],
                "outcomes": [
                    {
                        "weight": 55,
                        "text": "Qualifying heats create extra passing and extra risk.",
                        "effects": [],
                    },
                    {
                        "weight": 45,
                        "text": "Crew chiefs warn about wrecked cars before the main.",
                        "effects": [
                            {"type": "league", "stat": "owner_pressure", "delta": 6},
                        ],
                    },
                ],
            },
            {
                "id": "3",
                "label": "Use stage racing with intermediate breaks",
                "effects": [
                    {
                        "type": "policy",
                        "key": "race_format",
                        "value": "stage-racing",
                    },
                    {"type": "league", "stat": "integrity", "delta": 2},
                    {"type": "league", "stat": "fan_interest", "delta": 3},
                ],
                "outcomes": [
                    {
                        "weight": 70,
                        "text": "Stages keep mid-pack racing relevant.",
                        "effects": [
                            {
                                "type": "league",
                                "stat": "driver_sentiment",
                                "delta": 3,
                            },
                        ],
                    },
                    {
                        "weight": 30,
                        "text": "Purists call the cautions manufactured.",
                        "effects": [
                            {"type": "league", "stat": "controversy", "delta": 4},
                        ],
                    },
                ],
            },
        ],
    }


def penalty_standard_event(policies):
    """Preseason decision about disciplinary standards."""

    current = policy_label("penalty_standard", policies["penalty_standard"])

    return {
        "id": "rule-penalty-standard",
        "title": "Penalty Standards",
        "category": "rule-change",
        "phase": PRESEASON,
        "prompt": (
            "Race control wants a published standard for reckless-driving "
            f"penalties. Current policy: {current}."
        ),
        "choices": [
            {
                "id": "1",
                "label": "Publish a lenient standard",
                "effects": [
                    {
                        "type": "policy",
                        "key": "penalty_standard",
                        "value": "lenient",
                    },
                    {"type": "league", "stat": "integrity", "delta": -5},
                    {"type": "league", "stat": "fan_interest", "delta": 4},
                    {"type": "league", "stat": "controversy", "delta": 3},
                ],
                "outcomes": [
                    {
                        "weight": 60,
                        "text": "Aggressive drivers cheer the extra rope.",
                        "effects": [
                            {"type": "all_drivers", "stat": "morale", "delta": 3},
                        ],
                    },
                    {
                        "weight": 40,
                        "text": "Veterans say the series just invited wrecks.",
                        "effects": [
                            {
                                "type": "league",
                                "stat": "driver_sentiment",
                                "delta": -5,
                            },
                        ],
                    },
                ],
            },
            {
                "id": "2",
                "label": "Keep balanced enforcement",
                "effects": [
                    {
                        "type": "policy",
                        "key": "penalty_standard",
                        "value": "balanced",
                    },
                    {"type": "league", "stat": "integrity", "delta": 2},
                ],
                "outcomes": [
                    {
                        "weight": 75,
                        "text": "The garage calls it a fair middle ground.",
                        "effects": [],
                    },
                    {
                        "weight": 25,
                        "text": "Both hawks and doves still want movement.",
                        "effects": [
                            {"type": "league", "stat": "controversy", "delta": 2},
                        ],
                    },
                ],
            },
            {
                "id": "3",
                "label": "Adopt a strict penalty book",
                "effects": [
                    {
                        "type": "policy",
                        "key": "penalty_standard",
                        "value": "strict",
                    },
                    {"type": "league", "stat": "integrity", "delta": 6},
                    {"type": "league", "stat": "fan_interest", "delta": -3},
                    {"type": "league", "stat": "controversy", "delta": 2},
                ],
                "outcomes": [
                    {
                        "weight": 55,
                        "text": "Officials say the standard will clean up the racing.",
                        "effects": [
                            {
                                "type": "all_drivers",
                                "stat": "commissioner_trust",
                                "delta": 2,
                            },
                        ],
                    },
                    {
                        "weight": 45,
                        "text": "Owners fear bigger fines and parked star cars.",
                        "effects": [
                            {"type": "league", "stat": "owner_pressure", "delta": 7},
                            {
                                "type": "all_drivers",
                                "stat": "morale",
                                "delta": -3,
                            },
                        ],
                    },
                ],
            },
        ],
    }


def technical_rules_event(policies):
    """Preseason decision about the technical package."""

    current = policy_label("technical_rules", policies["technical_rules"])

    return {
        "id": "rule-technical-package",
        "title": "Technical Rules Package",
        "category": "rule-change",
        "phase": PRESEASON,
        "prompt": (
            "The competition director wants a technical direction for the "
            f"cars. Current policy: {current}."
        ),
        "choices": [
            {
                "id": "1",
                "label": "Leave the open package in place",
                "effects": [
                    {"type": "policy", "key": "technical_rules", "value": "open"},
                ],
                "outcomes": [
                    {
                        "weight": 70,
                        "text": "Engineering departments keep their current playbooks.",
                        "effects": [],
                    },
                    {
                        "weight": 30,
                        "text": "Parity complaints continue in the media.",
                        "effects": [
                            {"type": "league", "stat": "controversy", "delta": 3},
                        ],
                    },
                ],
            },
            {
                "id": "2",
                "label": "Restrict aero development",
                "effects": [
                    {
                        "type": "policy",
                        "key": "technical_rules",
                        "value": "aero-restrict",
                    },
                    {"type": "league", "stat": "integrity", "delta": 3},
                    {"type": "league", "stat": "fan_interest", "delta": 2},
                ],
                "outcomes": [
                    {
                        "weight": 60,
                        "text": "Closer handling packages should help side-by-side racing.",
                        "effects": [],
                    },
                    {
                        "weight": 40,
                        "text": "Well-funded teams accuse the series of capping speed.",
                        "effects": [
                            {"type": "league", "stat": "owner_pressure", "delta": 8},
                        ],
                    },
                ],
            },
            {
                "id": "3",
                "label": "Tighten inspection and technical scrutiny",
                "effects": [
                    {
                        "type": "policy",
                        "key": "technical_rules",
                        "value": "inspection-heavy",
                    },
                    {"type": "league", "stat": "integrity", "delta": 5},
                    {"type": "league", "stat": "controversy", "delta": 2},
                ],
                "outcomes": [
                    {
                        "weight": 65,
                        "text": "Inspectors get more time and more authority.",
                        "effects": [
                            {"type": "league", "stat": "owner_pressure", "delta": 5},
                        ],
                    },
                    {
                        "weight": 35,
                        "text": "Garages quietly budget for extra compliance staff.",
                        "effects": [
                            {
                                "type": "all_teams_budget",
                                "delta": -40_000,
                            },
                        ],
                    },
                ],
            },
        ],
    }


def safety_mandate_event(policies):
    """Offseason safety decision with equipment costs."""

    current = policy_label("safety_standard", policies["safety_standard"])

    return {
        "id": "safety-mandate",
        "title": "Safety Mandate",
        "category": "safety",
        "phase": OFFSEASON,
        "prompt": (
            "The medical director and drivers' council ask for a ruling on "
            "next season's safety equipment. Stronger mandates reduce crash "
            f"risk but raise team costs. Current policy: {current}."
        ),
        "choices": [
            {
                "id": "1",
                "label": "Hold at the current safety standard",
                "effects": [
                    {
                        "type": "policy",
                        "key": "safety_standard",
                        "value": "current",
                    },
                    {"type": "league", "stat": "owner_pressure", "delta": -2},
                ],
                "outcomes": [
                    {
                        "weight": 60,
                        "text": "Owners are relieved. Safety advocates are not.",
                        "effects": [
                            {
                                "type": "league",
                                "stat": "driver_sentiment",
                                "delta": -4,
                            },
                        ],
                    },
                    {
                        "weight": 40,
                        "text": "A columnist asks how many close calls the series needs.",
                        "effects": [
                            {"type": "league", "stat": "controversy", "delta": 5},
                            {"type": "league", "stat": "integrity", "delta": -3},
                        ],
                    },
                ],
            },
            {
                "id": "2",
                "label": "Require an enhanced equipment package",
                "effects": [
                    {
                        "type": "policy",
                        "key": "safety_standard",
                        "value": "enhanced",
                    },
                    {"type": "league", "stat": "integrity", "delta": 4},
                    {"type": "league", "stat": "owner_pressure", "delta": 5},
                    {"type": "all_drivers", "stat": "commissioner_trust", "delta": 3},
                ],
                "outcomes": [
                    {
                        "weight": 70,
                        "text": "Teams absorb the extra gear cost and move on.",
                        "effects": [
                            {"type": "all_teams_budget", "delta": -60_000},
                        ],
                    },
                    {
                        "weight": 30,
                        "text": "One shop leaks that the mandate will squeeze payroll.",
                        "effects": [
                            {"type": "all_teams_budget", "delta": -60_000},
                            {"type": "league", "stat": "controversy", "delta": 3},
                        ],
                    },
                ],
            },
            {
                "id": "3",
                "label": "Impose the maximum safety package",
                "effects": [
                    {
                        "type": "policy",
                        "key": "safety_standard",
                        "value": "maximum",
                    },
                    {"type": "league", "stat": "integrity", "delta": 7},
                    {"type": "league", "stat": "fan_interest", "delta": -2},
                    {"type": "league", "stat": "owner_pressure", "delta": 10},
                    {"type": "all_drivers", "stat": "morale", "delta": 2},
                    {
                        "type": "all_drivers",
                        "stat": "commissioner_trust",
                        "delta": 4,
                    },
                ],
                "outcomes": [
                    {
                        "weight": 50,
                        "text": "Drivers thank the podium. Owners send cost memos.",
                        "effects": [
                            {"type": "all_teams_budget", "delta": -120_000},
                            {
                                "type": "league",
                                "stat": "driver_sentiment",
                                "delta": 6,
                            },
                        ],
                    },
                    {
                        "weight": 50,
                        "text": "A joint owner letter calls the mandate unsustainable.",
                        "effects": [
                            {"type": "all_teams_budget", "delta": -120_000},
                            {"type": "league", "stat": "controversy", "delta": 6},
                        ],
                    },
                ],
            },
        ],
    }


def owner_complaint_event(team):
    """In-season owner pressure over costs and officiating."""

    owner = team.owner

    return {
        "id": "owner-complaint",
        "title": "Owner Complaint",
        "category": "owner-complaint",
        "phase": REGULAR_SEASON,
        "subject_team_name": team.name,
        "prompt": (
            f"{owner.description()}, owner of {team.name}, requests a "
            f"private meeting. Patience {owner.patience}/100. "
            f"The team budget sits at ${team.budget:,} "
            f"({team.financial_status_label()}). They want relief on "
            "fines, inspection time, and what they call 'costly officiating.'"
        ),
        "choices": [
            {
                "id": "1",
                "label": "Dismiss the complaint",
                "effects": [
                    {"type": "league", "stat": "integrity", "delta": 3},
                    {"type": "league", "stat": "owner_pressure", "delta": 8},
                    {"type": "subject_owner", "stat": "patience", "delta": -8},
                    {"type": "subject_owner", "stat": "pressure", "delta": 12},
                    {"type": "team_drivers", "stat": "morale", "delta": -4},
                ],
                "outcomes": [
                    {
                        "weight": 60,
                        "text": "The owner leaves angry but the rulebook holds.",
                        "effects": [],
                    },
                    {
                        "weight": 40,
                        "text": "The complaint leaks and other shops start calling.",
                        "effects": [
                            {"type": "league", "stat": "controversy", "delta": 5},
                        ],
                    },
                ],
            },
            {
                "id": "2",
                "label": "Promise a formal review after the season",
                "effects": [
                    {"type": "league", "stat": "owner_pressure", "delta": -2},
                    {"type": "league", "stat": "controversy", "delta": 1},
                    {"type": "subject_owner", "stat": "patience", "delta": 2},
                    {"type": "subject_owner", "stat": "pressure", "delta": -4},
                ],
                "outcomes": [
                    {
                        "weight": 70,
                        "text": "The owner accepts the delay, for now.",
                        "effects": [],
                    },
                    {
                        "weight": 30,
                        "text": "They call it a stall and brief a reporter anyway.",
                        "effects": [
                            {"type": "league", "stat": "fan_interest", "delta": -2},
                        ],
                    },
                ],
            },
            {
                "id": "3",
                "label": "Grant limited financial relief",
                "effects": [
                    {"type": "subject_team_budget", "delta": 150_000},
                    {"type": "league", "stat": "integrity", "delta": -4},
                    {"type": "league", "stat": "owner_pressure", "delta": -8},
                    {"type": "subject_owner", "stat": "patience", "delta": 4},
                    {"type": "subject_owner", "stat": "pressure", "delta": -10},
                    {"type": "team_drivers", "stat": "morale", "delta": 3},
                ],
                "outcomes": [
                    {
                        "weight": 55,
                        "text": "The shop stands down. Rival owners notice the favor.",
                        "effects": [
                            {"type": "league", "stat": "controversy", "delta": 4},
                        ],
                    },
                    {
                        "weight": 45,
                        "text": "Relief buys peace in that hauler.",
                        "effects": [
                            {
                                "type": "team_drivers",
                                "stat": "commissioner_trust",
                                "delta": 3,
                            },
                        ],
                    },
                ],
            },
        ],
    }


def owner_lobbying_event(team):
    """Postseason lobbying for next year's rules."""

    owner = team.owner

    return {
        "id": "owner-lobbying",
        "title": "Owner Lobbying",
        "category": "owner-complaint",
        "phase": POSTSEASON,
        "subject_team_name": team.name,
        "prompt": (
            f"{owner.description()} of {team.name} organizes a postseason "
            "owners' call. Priority: "
            f"{owner.priority}. Patience {owner.patience}/100. They want "
            "looser technical scrutiny and a friendlier cost environment "
            "before next year's contracts lock."
        ),
        "choices": [
            {
                "id": "1",
                "label": "Refuse and keep the current direction",
                "effects": [
                    {"type": "league", "stat": "integrity", "delta": 4},
                    {"type": "league", "stat": "owner_pressure", "delta": 6},
                    {"type": "subject_owner", "stat": "patience", "delta": -6},
                    {"type": "subject_owner", "stat": "pressure", "delta": 8},
                ],
                "outcomes": [
                    {
                        "weight": 65,
                        "text": "The commissioner is called stubborn — and consistent.",
                        "effects": [],
                    },
                    {
                        "weight": 35,
                        "text": "Two owners hint they may skip promotional dates.",
                        "effects": [
                            {"type": "league", "stat": "fan_interest", "delta": -3},
                        ],
                    },
                ],
            },
            {
                "id": "2",
                "label": "Offer a limited offseason working group",
                "effects": [
                    {"type": "league", "stat": "owner_pressure", "delta": -4},
                    {"type": "league", "stat": "integrity", "delta": 1},
                    {"type": "subject_owner", "stat": "patience", "delta": 3},
                    {"type": "subject_owner", "stat": "pressure", "delta": -6},
                ],
                "outcomes": [
                    {
                        "weight": 80,
                        "text": "The temperature drops. Nothing is promised in writing.",
                        "effects": [],
                    },
                    {
                        "weight": 20,
                        "text": "A leak frames it as the series folding under pressure.",
                        "effects": [
                            {"type": "league", "stat": "controversy", "delta": 3},
                        ],
                    },
                ],
            },
            {
                "id": "3",
                "label": "Concede a lighter inspection posture",
                "effects": [
                    {"type": "policy", "key": "technical_rules", "value": "open"},
                    {"type": "league", "stat": "integrity", "delta": -5},
                    {"type": "league", "stat": "owner_pressure", "delta": -10},
                    {"type": "league", "stat": "controversy", "delta": 4},
                    {"type": "subject_owner", "stat": "patience", "delta": 6},
                    {"type": "subject_owner", "stat": "pressure", "delta": -12},
                ],
                "outcomes": [
                    {
                        "weight": 50,
                        "text": "Owners celebrate. Inspectors do not.",
                        "effects": [],
                    },
                    {
                        "weight": 50,
                        "text": "Drivers ask who is actually running the series.",
                        "effects": [
                            {
                                "type": "league",
                                "stat": "driver_sentiment",
                                "delta": -6,
                            },
                            {
                                "type": "all_drivers",
                                "stat": "commissioner_trust",
                                "delta": -3,
                            },
                        ],
                    },
                ],
            },
        ],
    }


def driver_complaint_event(driver):
    """In-season driver grievance about officiating or safety."""

    return {
        "id": "driver-complaint",
        "title": "Driver Complaint",
        "category": "driver-complaint",
        "phase": REGULAR_SEASON,
        "subject_driver_name": driver.name,
        "prompt": (
            f"{driver.name} ({driver.personality}, {driver.team_name}) "
            "asks for a closed-door meeting. Morale is "
            f"{driver.morale} and commissioner trust is "
            f"{driver.commissioner_trust}. The grievance: inconsistent "
            "calls and too little protection from aggressive driving."
        ),
        "choices": [
            {
                "id": "1",
                "label": "Dismiss the grievance",
                "effects": [
                    {"type": "subject_driver", "stat": "morale", "delta": -8},
                    {
                        "type": "subject_driver",
                        "stat": "commissioner_trust",
                        "delta": -8,
                    },
                    {"type": "league", "stat": "driver_sentiment", "delta": -5},
                    {"type": "league", "stat": "integrity", "delta": 2},
                ],
                "outcomes": [
                    {
                        "weight": 55,
                        "text": "The driver stays quiet. The hauler does not.",
                        "effects": [
                            {"type": "team_drivers", "stat": "morale", "delta": -2},
                        ],
                    },
                    {
                        "weight": 45,
                        "text": "A heated quote hits social media within the hour.",
                        "effects": [
                            {"type": "league", "stat": "controversy", "delta": 6},
                            {"type": "league", "stat": "fan_interest", "delta": 2},
                        ],
                    },
                ],
            },
            {
                "id": "2",
                "label": "Issue a paddock memo on cleaner racing",
                "effects": [
                    {"type": "subject_driver", "stat": "morale", "delta": 3},
                    {
                        "type": "subject_driver",
                        "stat": "commissioner_trust",
                        "delta": 4,
                    },
                    {"type": "league", "stat": "integrity", "delta": 2},
                    {"type": "all_drivers", "stat": "morale", "delta": 1},
                ],
                "outcomes": [
                    {
                        "weight": 70,
                        "text": "The memo cools the argument without rewriting the book.",
                        "effects": [
                            {
                                "type": "league",
                                "stat": "driver_sentiment",
                                "delta": 4,
                            },
                        ],
                    },
                    {
                        "weight": 30,
                        "text": "Aggressive drivers call it a lecture.",
                        "effects": [
                            {"type": "league", "stat": "controversy", "delta": 2},
                        ],
                    },
                ],
            },
            {
                "id": "3",
                "label": "Publicly back the driver and tighten next week's look",
                "effects": [
                    {"type": "subject_driver", "stat": "morale", "delta": 6},
                    {
                        "type": "subject_driver",
                        "stat": "commissioner_trust",
                        "delta": 6,
                    },
                    {"type": "league", "stat": "fan_interest", "delta": 3},
                    {"type": "league", "stat": "owner_pressure", "delta": 4},
                    {"type": "league", "stat": "driver_sentiment", "delta": 5},
                ],
                "outcomes": [
                    {
                        "weight": 60,
                        "text": "The locker room reads it as the commissioner listening.",
                        "effects": [],
                    },
                    {
                        "weight": 40,
                        "text": "Owners say race control is now running on feelings.",
                        "effects": [
                            {"type": "league", "stat": "integrity", "delta": -3},
                            {"type": "league", "stat": "controversy", "delta": 4},
                        ],
                    },
                ],
            },
        ],
    }


def driver_grievance_event(driver):
    """Postseason driver grievance about the title fight."""

    return {
        "id": "driver-grievance",
        "title": "Driver Grievance",
        "category": "driver-complaint",
        "phase": POSTSEASON,
        "subject_driver_name": driver.name,
        "prompt": (
            f"{driver.name} files a postseason grievance over officiating "
            "during the title run. They want either an apology or a public "
            "review of race-control procedures."
        ),
        "choices": [
            {
                "id": "1",
                "label": "Stand by the officials",
                "effects": [
                    {"type": "league", "stat": "integrity", "delta": 3},
                    {"type": "subject_driver", "stat": "morale", "delta": -5},
                    {
                        "type": "subject_driver",
                        "stat": "commissioner_trust",
                        "delta": -6,
                    },
                    {"type": "league", "stat": "driver_sentiment", "delta": -3},
                ],
                "outcomes": [
                    {
                        "weight": 70,
                        "text": "Race control feels protected. The driver does not.",
                        "effects": [],
                    },
                    {
                        "weight": 30,
                        "text": "A retirement rumor briefly trends.",
                        "effects": [
                            {"type": "league", "stat": "fan_interest", "delta": 2},
                            {"type": "league", "stat": "controversy", "delta": 4},
                        ],
                    },
                ],
            },
            {
                "id": "2",
                "label": "Issue a limited public statement",
                "effects": [
                    {"type": "subject_driver", "stat": "morale", "delta": 3},
                    {
                        "type": "subject_driver",
                        "stat": "commissioner_trust",
                        "delta": 3,
                    },
                    {"type": "league", "stat": "controversy", "delta": 2},
                ],
                "outcomes": [
                    {
                        "weight": 75,
                        "text": "The statement is bland enough that both sides claim it.",
                        "effects": [],
                    },
                    {
                        "weight": 25,
                        "text": "Critics say the office is trying to have it both ways.",
                        "effects": [
                            {"type": "league", "stat": "integrity", "delta": -2},
                        ],
                    },
                ],
            },
            {
                "id": "3",
                "label": "Open a procedures review",
                "effects": [
                    {"type": "league", "stat": "integrity", "delta": 4},
                    {"type": "league", "stat": "driver_sentiment", "delta": 5},
                    {
                        "type": "all_drivers",
                        "stat": "commissioner_trust",
                        "delta": 2,
                    },
                    {"type": "league", "stat": "owner_pressure", "delta": 3},
                ],
                "outcomes": [
                    {
                        "weight": 65,
                        "text": "Drivers credit the office for looking in the mirror.",
                        "effects": [],
                    },
                    {
                        "weight": 35,
                        "text": "Owners worry the review will mean more penalties.",
                        "effects": [
                            {"type": "league", "stat": "controversy", "delta": 3},
                        ],
                    },
                ],
            },
        ],
    }


def _driver_by_name(drivers, name):
    """Return a driver by name, or None."""

    for driver in drivers:
        if driver.name == name:
            return driver

    return None


def _hottest_rivalry_pair(drivers):
    """Return the active pair with the strongest named rivalry."""

    best_pair = None
    best_score = -1

    for driver in drivers:
        if not driver.rival:
            continue

        rival = _driver_by_name(drivers, driver.rival)

        if rival is None:
            continue

        score = driver.rivalry_intensity

        if score > best_score:
            best_pair = (driver, rival)
            best_score = score

    return best_pair


def _hottest_feud_pair(drivers):
    """Return the drivers in the strongest active or cooling feud."""

    best = None
    best_score = -1

    for driver in drivers:
        for feud in driver.feuds:
            if feud.get("status") == "dormant":
                continue

            opponent = _driver_by_name(drivers, feud.get("opponent"))

            if opponent is None:
                continue

            intensity = feud.get("intensity", 0)

            if intensity > best_score:
                best = (driver, opponent, feud)
                best_score = intensity

    return best


def rivalry_contact_event(driver, rival):
    """In-season contact between rivals, without new crash physics."""

    return {
        "id": "rivalry-contact",
        "title": "Rivalry Contact",
        "category": "rivalry",
        "phase": REGULAR_SEASON,
        "subject_driver_name": driver.name,
        "subject_other_driver_name": rival.name,
        "prompt": (
            f"{driver.name} ({driver.personality}) and {rival.name} "
            f"({rival.personality}) made contact off a restart. "
            f"Rivalry intensity {driver.rivalry_intensity}/100. "
            f"{driver.name} risk tolerance {driver.risk_tolerance}, "
            f"{rival.name} temperament {rival.temperament}. "
            "Garage cameras caught the chop. Race control wants a ruling "
            "before it becomes a weekly feature."
        ),
        "choices": [
            {
                "id": "1",
                "label": "Let them race it out",
                "effects": [
                    {"type": "league", "stat": "fan_interest", "delta": 5},
                    {"type": "league", "stat": "controversy", "delta": 6},
                    {"type": "league", "stat": "integrity", "delta": -3},
                    {"type": "rivalry", "delta": 10},
                    {
                        "type": "feud",
                        "delta": 12,
                        "incident": "on-track contact",
                    },
                    {
                        "type": "subject_driver",
                        "stat": "competitive_frustration",
                        "delta": 6,
                    },
                    {
                        "type": "subject_other_driver",
                        "stat": "competitive_frustration",
                        "delta": 6,
                    },
                ],
                "outcomes": [
                    {
                        "weight": 55,
                        "text": "The crowd loves it. Crew chiefs do not.",
                        "effects": [
                            {
                                "type": "subject_driver",
                                "stat": "popularity",
                                "delta": 3,
                            },
                            {
                                "type": "subject_other_driver",
                                "stat": "popularity",
                                "delta": 2,
                            },
                        ],
                    },
                    {
                        "weight": 45,
                        "text": "A second chop on the next run makes it personal.",
                        "effects": [
                            {"type": "rivalry", "delta": 6},
                            {
                                "type": "feud",
                                "delta": 8,
                                "incident": "follow-up contact",
                            },
                        ],
                    },
                ],
            },
            {
                "id": "2",
                "label": "Call both to the hauler for a private warning",
                "effects": [
                    {"type": "league", "stat": "integrity", "delta": 3},
                    {"type": "rivalry", "delta": -8},
                    {
                        "type": "subject_driver",
                        "stat": "commissioner_trust",
                        "delta": 2,
                    },
                    {
                        "type": "subject_other_driver",
                        "stat": "commissioner_trust",
                        "delta": 2,
                    },
                ],
                "outcomes": [
                    {
                        "weight": 70,
                        "text": "They nod, glare, and park it — for this week.",
                        "effects": [],
                    },
                    {
                        "weight": 30,
                        "text": "One of them leaks that the office is babysitting.",
                        "effects": [
                            {"type": "league", "stat": "controversy", "delta": 3},
                            {
                                "type": "subject_driver",
                                "stat": "morale",
                                "delta": -3,
                            },
                        ],
                    },
                ],
            },
            {
                "id": "3",
                "label": "Park the aggressor and put the feud on notice",
                "effects": [
                    {"type": "league", "stat": "integrity", "delta": 5},
                    {"type": "league", "stat": "fan_interest", "delta": -3},
                    {"type": "league", "stat": "controversy", "delta": 4},
                    {
                        "type": "subject_driver",
                        "stat": "morale",
                        "delta": -8,
                    },
                    {
                        "type": "subject_driver",
                        "stat": "reputation",
                        "delta": -4,
                    },
                    {"type": "rivalry", "delta": -12},
                    {
                        "type": "feud",
                        "delta": 4,
                        "incident": "commissioner parked a car",
                    },
                ],
                "outcomes": [
                    {
                        "weight": 60,
                        "text": "The message lands. The rivalry cools on camera.",
                        "effects": [
                            {
                                "type": "subject_other_driver",
                                "stat": "morale",
                                "delta": 3,
                            },
                        ],
                    },
                    {
                        "weight": 40,
                        "text": "Fans boo the caution. The other shop claims favoritism.",
                        "effects": [
                            {"type": "league", "stat": "driver_sentiment", "delta": -3},
                            {
                                "type": "subject_other_driver",
                                "stat": "commissioner_trust",
                                "delta": -2,
                            },
                        ],
                    },
                ],
            },
        ],
    }


def rivalry_argument_event(driver, rival):
    """Garage or media argument between rivals."""

    return {
        "id": "rivalry-argument",
        "title": "Rivalry Argument",
        "category": "rivalry",
        "phase": REGULAR_SEASON,
        "subject_driver_name": driver.name,
        "subject_other_driver_name": rival.name,
        "prompt": (
            f"{driver.name} and {rival.name} go at it in the garage. "
            f"Media skill {driver.media_skill} vs {rival.media_skill}. "
            f"Rivalry {driver.rivalry_intensity}/100. "
            "Microphones are hot. The series needs a line."
        ),
        "choices": [
            {
                "id": "1",
                "label": "Ignore it and let the clip run",
                "effects": [
                    {"type": "league", "stat": "fan_interest", "delta": 6},
                    {"type": "league", "stat": "controversy", "delta": 7},
                    {"type": "rivalry", "delta": 8},
                    {
                        "type": "feud",
                        "delta": 10,
                        "incident": "garage argument",
                    },
                    {
                        "type": "subject_driver",
                        "stat": "credibility",
                        "delta": -3,
                    },
                    {
                        "type": "subject_other_driver",
                        "stat": "credibility",
                        "delta": -3,
                    },
                ],
                "outcomes": [
                    {
                        "weight": 60,
                        "text": "The sound bite leads every show. Sponsors wince.",
                        "effects": [
                            {
                                "type": "subject_driver",
                                "stat": "popularity",
                                "delta": 4,
                            },
                        ],
                    },
                    {
                        "weight": 40,
                        "text": "A shove is caught on a phone. The feud is now a storyline.",
                        "effects": [
                            {"type": "rivalry", "delta": 6},
                            {
                                "type": "feud",
                                "delta": 8,
                                "incident": "shove on camera",
                            },
                        ],
                    },
                ],
            },
            {
                "id": "2",
                "label": "Fine both for conduct detrimental",
                "effects": [
                    {"type": "league", "stat": "integrity", "delta": 3},
                    {"type": "league", "stat": "controversy", "delta": 2},
                    {"type": "rivalry", "delta": -6},
                    {
                        "type": "subject_driver",
                        "stat": "morale",
                        "delta": -4,
                    },
                    {
                        "type": "subject_other_driver",
                        "stat": "morale",
                        "delta": -4,
                    },
                    {
                        "type": "subject_driver",
                        "stat": "reputation",
                        "delta": -2,
                    },
                    {
                        "type": "subject_other_driver",
                        "stat": "reputation",
                        "delta": -2,
                    },
                ],
                "outcomes": [
                    {
                        "weight": 75,
                        "text": "Both haulers pay. The volume drops.",
                        "effects": [],
                    },
                    {
                        "weight": 25,
                        "text": "They call it a tax on personality.",
                        "effects": [
                            {
                                "type": "league",
                                "stat": "driver_sentiment",
                                "delta": -4,
                            },
                        ],
                    },
                ],
            },
            {
                "id": "3",
                "label": "Force a joint media session to cool it",
                "effects": [
                    {"type": "league", "stat": "fan_interest", "delta": 3},
                    {"type": "league", "stat": "integrity", "delta": 1},
                    {"type": "rivalry", "delta": -4},
                    {
                        "type": "subject_driver",
                        "stat": "media_skill",
                        "delta": 1,
                    },
                    {
                        "type": "subject_other_driver",
                        "stat": "media_skill",
                        "delta": 1,
                    },
                ],
                "outcomes": [
                    {
                        "weight": 65,
                        "text": "The staged handshake is awkward. It still airs.",
                        "effects": [
                            {"type": "friendship", "delta": 4},
                        ],
                    },
                    {
                        "weight": 35,
                        "text": "One of them uses the mic to reload the feud.",
                        "effects": [
                            {"type": "league", "stat": "controversy", "delta": 4},
                            {
                                "type": "feud",
                                "delta": 6,
                                "incident": "press-conference shot",
                            },
                        ],
                    },
                ],
            },
        ],
    }


def feud_review_event(driver, rival, feud):
    """Postseason sit-down over a long-running feud."""

    started = feud.get("started_season", 1)
    intensity = feud.get("intensity", 0)

    return {
        "id": "feud-review",
        "title": "Long-Term Feud Review",
        "category": "rivalry",
        "phase": POSTSEASON,
        "subject_driver_name": driver.name,
        "subject_other_driver_name": rival.name,
        "prompt": (
            f"The {driver.name}–{rival.name} feud is still on the board "
            f"(intensity {intensity}/100, started season {started}, "
            f"last incident: {feud.get('last_incident', 'unknown')}). "
            "Owners want it managed before next year's sponsor decks lock."
        ),
        "choices": [
            {
                "id": "1",
                "label": "Let the storyline ride into next season",
                "effects": [
                    {"type": "league", "stat": "fan_interest", "delta": 5},
                    {"type": "league", "stat": "controversy", "delta": 5},
                    {"type": "rivalry", "delta": 6},
                    {
                        "type": "feud",
                        "delta": 8,
                        "incident": "postseason green light",
                    },
                ],
                "outcomes": [
                    {
                        "weight": 70,
                        "text": "Marketing is thrilled. Race control is not.",
                        "effects": [],
                    },
                    {
                        "weight": 30,
                        "text": "A columnist asks who is actually in charge of safety.",
                        "effects": [
                            {"type": "league", "stat": "integrity", "delta": -3},
                        ],
                    },
                ],
            },
            {
                "id": "2",
                "label": "Mediate a closed-door truce",
                "effects": [
                    {"type": "league", "stat": "integrity", "delta": 3},
                    {"type": "rivalry", "delta": -14},
                    {
                        "type": "feud",
                        "delta": -18,
                        "incident": "offseason truce",
                    },
                    {"type": "friendship", "delta": 8},
                    {
                        "type": "subject_driver",
                        "stat": "morale",
                        "delta": 3,
                    },
                    {
                        "type": "subject_other_driver",
                        "stat": "morale",
                        "delta": 3,
                    },
                ],
                "outcomes": [
                    {
                        "weight": 60,
                        "text": "They shake on it. Nobody believes it will last.",
                        "effects": [],
                    },
                    {
                        "weight": 40,
                        "text": "One owner claims the other shop got the better deal.",
                        "effects": [
                            {"type": "league", "stat": "owner_pressure", "delta": 4},
                        ],
                    },
                ],
            },
            {
                "id": "3",
                "label": "Put both on a conduct watch for next year",
                "effects": [
                    {"type": "league", "stat": "integrity", "delta": 5},
                    {"type": "league", "stat": "fan_interest", "delta": -2},
                    {"type": "rivalry", "delta": -8},
                    {
                        "type": "feud",
                        "delta": -6,
                        "incident": "conduct watch",
                    },
                    {
                        "type": "subject_driver",
                        "stat": "commissioner_trust",
                        "delta": -3,
                    },
                    {
                        "type": "subject_other_driver",
                        "stat": "commissioner_trust",
                        "delta": -3,
                    },
                    {
                        "type": "subject_driver",
                        "stat": "credibility",
                        "delta": 3,
                    },
                    {
                        "type": "subject_other_driver",
                        "stat": "credibility",
                        "delta": 3,
                    },
                ],
                "outcomes": [
                    {
                        "weight": 80,
                        "text": "The watch list is public. The feud goes quieter.",
                        "effects": [],
                    },
                    {
                        "weight": 20,
                        "text": "Both drivers say the office is writing the script.",
                        "effects": [
                            {
                                "type": "league",
                                "stat": "driver_sentiment",
                                "delta": -4,
                            },
                        ],
                    },
                ],
            },
        ],
    }


RULE_EVENTS = (
    points_system_event,
    race_format_event,
    penalty_standard_event,
    technical_rules_event,
    scoring_bonus_event,
    championship_format_event,
)


def press_conference_needed(stories):
    """Return whether last weekend's copy warrants a podium appearance."""

    for story in stories or []:
        if story.get("kind") in ("wreck", "investigation", "weather"):
            return True
        if story.get("tone") in ("spicy", "downbeat", "serious"):
            return True
    return False


def press_conference_event(race_number, stories):
    """In-season podium after a newsworthy weekend."""

    stories = list(stories or [])
    lead = stories[0] if stories else {}
    headline = lead.get("headline") or "the weekend"
    outlet = lead.get("outlet") or "the wire services"
    extras = [
        story.get("headline")
        for story in stories[1:]
        if story.get("headline")
    ]
    extra_text = ""
    if extras:
        quoted = ", ".join('"{0}"'.format(item) for item in extras)
        extra_text = " Follow-ups: {0}.".format(quoted)

    kinds = [story.get("kind") for story in stories]
    if "wreck" in kinds or lead.get("tone") == "spicy":
        hook = "Reporters want to know if the product is too rough."
    elif "investigation" in kinds:
        hook = "Reporters want a comment on the steward file."
    elif any(story.get("tone") == "downbeat" for story in stories):
        hook = "Reporters want to know why the show did not land."
    else:
        hook = "Reporters want the league's read on the weekend."

    return {
        "id": "press-conference-r{0}".format(race_number),
        "title": "Press Conference",
        "category": "press-conference",
        "phase": REGULAR_SEASON,
        "prompt": (
            "{0} has you at the podium after the weekend. "
            'Lead story: "{1}".{2} {3}'
        ).format(outlet, headline, extra_text, hook),
        "choices": [
            {
                "id": "1",
                "label": "Stay on script",
                "effects": [
                    {"type": "league", "stat": "integrity", "delta": 2},
                    {"type": "league", "stat": "controversy", "delta": -2},
                    {"type": "league", "stat": "fan_interest", "delta": -1},
                ],
                "outcomes": [
                    {
                        "weight": 100,
                        "text": "The podium is dry. The clip does not go viral.",
                        "effects": [],
                    },
                ],
            },
            {
                "id": "2",
                "label": "Celebrate the show",
                "effects": [
                    {"type": "league", "stat": "fan_interest", "delta": 5},
                    {"type": "league", "stat": "controversy", "delta": 4},
                    {"type": "league", "stat": "integrity", "delta": -3},
                ],
                "outcomes": [
                    {
                        "weight": 100,
                        "text": "You call it great racing. The clip does too.",
                        "effects": [],
                    },
                ],
            },
            {
                "id": "3",
                "label": "Promise a review",
                "effects": [
                    {"type": "league", "stat": "integrity", "delta": 4},
                    {"type": "league", "stat": "controversy", "delta": -3},
                    {"type": "league", "stat": "fan_interest", "delta": -2},
                    {"type": "league", "stat": "driver_sentiment", "delta": 3},
                ],
                "outcomes": [
                    {
                        "weight": 100,
                        "text": "The garage hears that the league is watching.",
                        "effects": [],
                    },
                ],
            },
        ],
    }


SCANDAL_HEADLINES = {
    "cheers-chaos": "League Cheers the Chaos",
    "stonewall": "League Accused of Stonewalling",
    "public-pressure": "Public Pressure Mounts on the Series",
}


def media_controversy_flavor(stories, presser, controversy=0):
    """Return a scandal flavor, or None if the weekend stays contained."""

    stories = list(stories or [])
    kinds = [story.get("kind") for story in stories]
    spicy = any(story.get("tone") == "spicy" for story in stories)
    wreck = "wreck" in kinds or spicy
    investigation = "investigation" in kinds
    label = (presser or {}).get("choice_label")

    if label == "Promise a review":
        return None
    if label == "Celebrate the show" and wreck:
        return "cheers-chaos"
    if label == "Stay on script" and investigation:
        return "stonewall"
    if wreck or investigation:
        if controversy >= 50:
            return "public-pressure"
    return None


def media_controversy_needed(stories, presser, controversy=0):
    """Return whether the weekend boiled into a public scandal."""

    return media_controversy_flavor(stories, presser, controversy) is not None


def media_controversy_event(race_number, stories, presser, controversy=0):
    """In-season scandal after a mishandled podium or boiling pressure."""

    flavor = media_controversy_flavor(stories, presser, controversy)
    flavor = flavor or "public-pressure"
    headline = SCANDAL_HEADLINES[flavor]
    lead = (stories or [{}])[0] or {}
    prior = lead.get("headline") or "the weekend"
    outlet = lead.get("outlet") or "the wire services"
    answer = (presser or {}).get("choice_label") or "no comment"

    if flavor == "cheers-chaos":
        hook = (
            "Columnists say the league sold wrecks as entertainment "
            "after you celebrated the show."
        )
    elif flavor == "stonewall":
        hook = (
            "Columnists say the steward file was buried when you "
            "stayed on script."
        )
    else:
        hook = "Talk radio and the papers are piling on the series."

    return {
        "id": "media-controversy-r{0}".format(race_number),
        "title": "Media Controversy",
        "category": "media-controversy",
        "phase": REGULAR_SEASON,
        "scandal_flavor": flavor,
        "scandal_headline": headline,
        "prompt": (
            '{0} is running "{1}" after "{2}" ({3}). {4} '
            "Public pressure is on the podium."
        ).format(outlet, headline, prior, answer, hook),
        "choices": [
            {
                "id": "1",
                "label": "Deny everything",
                "effects": [
                    {"type": "league", "stat": "controversy", "delta": 6},
                    {"type": "league", "stat": "integrity", "delta": -5},
                    {"type": "league", "stat": "fan_interest", "delta": -3},
                    {"type": "league", "stat": "owner_pressure", "delta": 2},
                ],
                "outcomes": [
                    {
                        "weight": 100,
                        "text": "The denial clips. Sponsors flinch. The story grows.",
                        "effects": [],
                    },
                ],
            },
            {
                "id": "2",
                "label": "Apologize",
                "effects": [
                    {"type": "league", "stat": "controversy", "delta": -4},
                    {"type": "league", "stat": "integrity", "delta": 1},
                    {"type": "league", "stat": "fan_interest", "delta": 2},
                    {"type": "league", "stat": "owner_pressure", "delta": 3},
                ],
                "outcomes": [
                    {
                        "weight": 100,
                        "text": "Fans take the apology. Owners call it a fold.",
                        "effects": [],
                    },
                ],
            },
            {
                "id": "3",
                "label": "Launch a public inquiry",
                "effects": [
                    {"type": "league", "stat": "integrity", "delta": 4},
                    {"type": "league", "stat": "controversy", "delta": -5},
                    {"type": "league", "stat": "owner_pressure", "delta": 6},
                    {"type": "league", "stat": "driver_sentiment", "delta": 2},
                ],
                "outcomes": [
                    {
                        "weight": 100,
                        "text": "The inquiry cools the papers. The board starts calling.",
                        "effects": [],
                    },
                ],
            },
        ],
    }


def media_controversy_events(
    race_number,
    stories,
    presser,
    resolved_ids,
    controversy=0,
):
    """Return a scandal event when the weekend boiled over."""

    event_id = "media-controversy-r{0}".format(race_number)
    if event_id in (resolved_ids or []):
        return []
    if not media_controversy_needed(stories, presser, controversy):
        return []
    return [
        media_controversy_event(
            race_number,
            stories,
            presser,
            controversy,
        )
    ]


OWNER_COUNCIL_AYE_FLOOR = 55
OWNER_COUNCIL_TILT = {
    "1": 0,
    "2": -18,
    "3": 12,
}


def owner_council_weight(team):
    """Return political weight for chair and seating order."""

    owner = team.owner
    return (
        team.prestige
        + owner.pressure
        + (100 - owner.patience)
        + owner.wealth // 2
        + team.financial_distress_level * 8
    )


def owner_council_seats(teams):
    """Return teams seated on the owner council, chair first."""

    return sorted(
        list(teams or []),
        key=lambda team: (
            -owner_council_weight(team),
            -team.prestige,
            team.name,
        ),
    )


def owner_council_chair(teams):
    """Return the team whose owner chairs the council, or None."""

    seats = owner_council_seats(teams)
    if not seats:
        return None
    return seats[0]


def owner_council_mood(teams, owner_pressure=0):
    """Return quiet, watchful, or restless from owner heat."""

    pressures = [team.owner.pressure for team in (teams or [])]
    mean = sum(pressures) / len(pressures) if pressures else 0
    heat = max(int(owner_pressure or 0), mean)
    if heat >= 45:
        return "restless"
    if heat >= 30:
        return "watchful"
    return "quiet"


def owner_council_vote_heat(team, league, tilt=0):
    """Return a seat's heat toward rebuking the commissioner."""

    owner = team.owner
    league = league or {}
    heat = owner.pressure + (100 - owner.patience) // 2
    heat += team.financial_distress_level * 10
    heat += max(0, int(league.get("owner_pressure", 0)) - 25)
    heat += max(0, int(league.get("controversy", 0)) - 25)
    heat += int(tilt or 0)
    return heat


def owner_council_tally(teams, league, tilt=0):
    """Return recorded aye/nay ballots on a rebuke motion."""

    ballots = []
    chair_team = owner_council_chair(teams)
    for team in owner_council_seats(teams):
        heat = owner_council_vote_heat(team, league, tilt)
        vote = "aye" if heat >= OWNER_COUNCIL_AYE_FLOOR else "nay"
        ballots.append(
            {
                "owner": team.owner.name,
                "team": team.name,
                "vote": vote,
                "heat": heat,
                "chair": team is chair_team,
            }
        )
    ayes = [item for item in ballots if item["vote"] == "aye"]
    nays = [item for item in ballots if item["vote"] == "nay"]
    return {
        "motion": "rebuke",
        "ballots": ballots,
        "ayes": len(ayes),
        "nays": len(nays),
        "passed": len(ayes) > len(nays),
    }


def owner_council_event(season_number, teams, league=None):
    """Postseason chamber session: representation, then a rebuke vote."""

    league = league or {}
    seats = owner_council_seats(teams)
    chair_team = seats[0] if seats else None
    chair_name = chair_team.owner.name if chair_team else "the chair"
    chair_team_name = chair_team.name if chair_team else "the grid"
    mood = owner_council_mood(teams, league.get("owner_pressure", 0))
    roster = ", ".join(
        "{0} ({1})".format(team.owner.name, team.name)
        for team in seats
    )
    if not roster:
        roster = "no seated owners"

    return {
        "id": "owner-council-s{0}".format(season_number),
        "title": "Owner Council",
        "category": "owner-council",
        "phase": POSTSEASON,
        "prompt": (
            "The owner council is in session. Chair {0} of {1} gavels "
            "the room. Seats: {2}. Mood: {3}. The motion is to rebuke "
            "the commissioner. How do you handle the chamber?"
        ).format(chair_name, chair_team_name, roster, mood),
        "choices": [
            {
                "id": "1",
                "label": "Defer to the chamber",
                "effects": [
                    {"type": "league", "stat": "integrity", "delta": 1},
                ],
                "outcomes": [
                    {
                        "weight": 100,
                        "text": "You let the owners vote the room they brought.",
                        "effects": [],
                    },
                ],
            },
            {
                "id": "2",
                "label": "Work the room",
                "effects": [
                    {"type": "league", "stat": "owner_pressure", "delta": -4},
                    {"type": "league", "stat": "integrity", "delta": -2},
                    {"type": "league", "stat": "fan_interest", "delta": -1},
                ],
                "outcomes": [
                    {
                        "weight": 100,
                        "text": "You work the haulers. A few votes soften.",
                        "effects": [],
                    },
                ],
            },
            {
                "id": "3",
                "label": "Stare them down",
                "effects": [
                    {"type": "league", "stat": "integrity", "delta": 3},
                    {"type": "league", "stat": "owner_pressure", "delta": 5},
                    {"type": "league", "stat": "controversy", "delta": 2},
                ],
                "outcomes": [
                    {
                        "weight": 100,
                        "text": "You tell the room the league is not a committee.",
                        "effects": [],
                    },
                ],
            },
        ],
    }


def owner_council_events(season_number, teams, resolved_ids, league=None):
    """Return the postseason owner-council session when unresolved."""

    event_id = "owner-council-s{0}".format(season_number)
    if event_id in (resolved_ids or []):
        return []
    if not teams:
        return []
    return [owner_council_event(season_number, teams, league)]


DRIVER_COUNCIL_CONCERN_FLOOR = 55
DRIVER_COUNCIL_TILT = {
    "1": 0,
    "2": -16,
    "3": 14,
}
DRIVER_COUNCIL_PERSONALITY_HEAT = {
    "Temperamental": 12,
    "Aggressive": 8,
    "Rookie": 6,
    "Popular": -8,
    "Veteran": -4,
    "Professional": -2,
}


def driver_council_weight(driver):
    """Return political weight for chair and seating order."""

    return (
        driver.popularity
        + driver.reputation
        + driver.credibility
        + driver.media_skill // 2
    )


def driver_council_seats(drivers):
    """Return drivers seated on the driver council, chair first."""

    return sorted(
        list(drivers or []),
        key=lambda driver: (
            -driver_council_weight(driver),
            -driver.popularity,
            driver.name,
        ),
    )


def driver_council_chair(drivers):
    """Return the driver who chairs the council, or None."""

    seats = driver_council_seats(drivers)
    if not seats:
        return None
    return seats[0]


def driver_council_mood(drivers, driver_sentiment=60):
    """Return settled, watchful, or restless from garage heat."""

    morals = [driver.morale for driver in (drivers or [])]
    mean_morale = sum(morals) / len(morals) if morals else 70
    if int(driver_sentiment or 0) < 45 or mean_morale < 50:
        return "restless"
    if int(driver_sentiment or 0) < 55 or mean_morale < 62:
        return "watchful"
    return "settled"


def driver_council_feedback_heat(driver, league, tilt=0):
    """Return a seat's heat toward concerned feedback."""

    league = league or {}
    heat = (100 - driver.morale) + (100 - driver.commissioner_trust) // 2
    heat += DRIVER_COUNCIL_PERSONALITY_HEAT.get(driver.personality, 0)
    heat += max(0, 60 - int(league.get("driver_sentiment", 60)))
    heat += max(0, int(league.get("controversy", 0)) - 25)
    heat += int(tilt or 0)
    return heat


def driver_council_tally(drivers, league, tilt=0):
    """Return recorded satisfied/concerned feedback from the garage."""

    ballots = []
    chair = driver_council_chair(drivers)
    for driver in driver_council_seats(drivers):
        heat = driver_council_feedback_heat(driver, league, tilt)
        vote = (
            "concerned"
            if heat >= DRIVER_COUNCIL_CONCERN_FLOOR
            else "satisfied"
        )
        ballots.append(
            {
                "driver": driver.name,
                "team": driver.team_name,
                "vote": vote,
                "heat": heat,
                "chair": driver is chair,
            }
        )
    concerned = [item for item in ballots if item["vote"] == "concerned"]
    satisfied = [item for item in ballots if item["vote"] == "satisfied"]
    return {
        "motion": "feedback",
        "ballots": ballots,
        "concerned": len(concerned),
        "satisfied": len(satisfied),
        "protested": len(concerned) > len(satisfied),
        "split": len(concerned) == len(satisfied),
    }


def driver_council_event(season_number, drivers, league=None):
    """Postseason garage session: representation, then feedback."""

    league = league or {}
    seats = driver_council_seats(drivers)
    chair = seats[0] if seats else None
    chair_name = chair.name if chair else "the chair"
    chair_team = chair.team_name if chair else "the grid"
    mood = driver_council_mood(
        drivers,
        league.get("driver_sentiment", 60),
    )
    roster = ", ".join(
        "{0} ({1})".format(driver.name, driver.team_name)
        for driver in seats
    )
    if not roster:
        roster = "no seated drivers"

    return {
        "id": "driver-council-s{0}".format(season_number),
        "title": "Driver Council",
        "category": "driver-council",
        "phase": POSTSEASON,
        "prompt": (
            "The driver council is in session. Chair {0} of {1} speaks "
            "for the garage. Seats: {2}. Mood: {3}. They want a read on "
            "officiating and safety. How do you take the feedback?"
        ).format(chair_name, chair_team, roster, mood),
        "choices": [
            {
                "id": "1",
                "label": "Hear the garage",
                "effects": [
                    {"type": "league", "stat": "integrity", "delta": 1},
                    {"type": "league", "stat": "driver_sentiment", "delta": 2},
                ],
                "outcomes": [
                    {
                        "weight": 100,
                        "text": "You let every seat talk. The notes go in the file.",
                        "effects": [],
                    },
                ],
            },
            {
                "id": "2",
                "label": "Promise a working group",
                "effects": [
                    {"type": "league", "stat": "driver_sentiment", "delta": 4},
                    {"type": "league", "stat": "integrity", "delta": 1},
                    {"type": "league", "stat": "owner_pressure", "delta": 3},
                ],
                "outcomes": [
                    {
                        "weight": 100,
                        "text": "You promise a working group. The owners roll their eyes.",
                        "effects": [],
                    },
                ],
            },
            {
                "id": "3",
                "label": "Dismiss the gripes",
                "effects": [
                    {"type": "league", "stat": "integrity", "delta": 2},
                    {"type": "league", "stat": "driver_sentiment", "delta": -5},
                    {"type": "league", "stat": "fan_interest", "delta": -1},
                ],
                "outcomes": [
                    {
                        "weight": 100,
                        "text": "You tell them to drive. The garage goes cold.",
                        "effects": [],
                    },
                ],
            },
        ],
    }


def driver_council_events(season_number, drivers, resolved_ids, league=None):
    """Return the postseason driver-council session when unresolved."""

    event_id = "driver-council-s{0}".format(season_number)
    if event_id in (resolved_ids or []):
        return []
    if not drivers:
        return []
    return [driver_council_event(season_number, drivers, league)]


OWNER_PRIORITY_PROPOSALS = {
    "wins": (
        ("points_system", "winner-heavy"),
        ("championship_format", "playoff"),
        ("scoring_bonuses", "rich"),
    ),
    "stability": (
        ("points_system", "flattened"),
        ("championship_format", "season-long"),
        ("penalty_standard", "balanced"),
    ),
    "cost-control": (
        ("technical_rules", "aero-restrict"),
        ("safety_standard", "current"),
        ("penalty_standard", "lenient"),
    ),
    "prestige": (
        ("scoring_bonuses", "rich"),
        ("race_format", "stage-racing"),
        ("championship_format", "playoff"),
    ),
}

DRIVER_COUNCIL_PROPOSALS = (
    ("safety_standard", "enhanced"),
    ("penalty_standard", "strict"),
    ("technical_rules", "inspection-heavy"),
)


def _first_new_policy(policies, options):
    """Return the first (key, value) that is not already in force."""

    policies = policies or {}
    options = list(options or [])
    for key, value in options:
        if policies.get(key) != value:
            return key, value
    if options:
        return options[0]
    return None, None


def _owner_by_priority(teams, priority):
    """Return a team whose owner has this priority, or None."""

    for team in teams or []:
        if team.owner.priority == priority:
            return team
    return None


def build_rule_proposal(source, sponsor, body, policy_key, proposed_value, policies):
    """Return a stakeholder rule-proposal dictionary."""

    policies = policies or {}
    current_value = policies.get(policy_key)
    return {
        "source": source,
        "sponsor": sponsor,
        "body": body,
        "policy_key": policy_key,
        "current_value": current_value,
        "proposed_value": proposed_value,
        "headline": policy_label(policy_key, proposed_value),
        "current_label": policy_label(policy_key, current_value),
    }


def owner_chair_rule_proposal(teams, policies):
    """Return a proposal from the owner-council chair's priority."""

    chair = owner_council_chair(teams)
    if chair is None:
        return None
    options = OWNER_PRIORITY_PROPOSALS.get(
        chair.owner.priority,
        OWNER_PRIORITY_PROPOSALS["stability"],
    )
    key, value = _first_new_policy(policies, options)
    if key is None:
        return None
    return build_rule_proposal(
        "owner-council",
        chair.owner.name,
        "Owner Council",
        key,
        value,
        policies,
    )


def driver_chair_rule_proposal(drivers, policies):
    """Return a proposal from the driver-council chair."""

    chair = driver_council_chair(drivers)
    if chair is None:
        return None
    key, value = _first_new_policy(policies, DRIVER_COUNCIL_PROPOSALS)
    if key is None:
        return None
    return build_rule_proposal(
        "driver-council",
        chair.name,
        "Driver Council",
        key,
        value,
        policies,
    )


def cost_control_rule_proposal(teams, policies):
    """Return a cost-control owner's technical proposal."""

    team = _owner_by_priority(teams, "cost-control")
    if team is None:
        return owner_chair_rule_proposal(teams, policies)
    key, value = _first_new_policy(
        policies,
        OWNER_PRIORITY_PROPOSALS["cost-control"],
    )
    if key is None:
        return None
    return build_rule_proposal(
        "owner",
        team.owner.name,
        team.name,
        key,
        value,
        policies,
    )


def select_rule_proposal(teams, drivers, league, policies, season_number=1):
    """Pick this season's stakeholder proposal."""

    league = league or {}
    last_garage = league.get("last_driver_council") or {}
    last_owners = league.get("last_owner_council") or {}

    if last_garage.get("protested"):
        return driver_chair_rule_proposal(drivers, policies)
    if last_owners.get("passed"):
        return owner_chair_rule_proposal(teams, policies)

    cycle = (int(season_number or 1) - 1) % 3
    if cycle == 1:
        return driver_chair_rule_proposal(drivers, policies)
    if cycle == 2:
        return cost_control_rule_proposal(teams, policies)
    return owner_chair_rule_proposal(teams, policies)


def rule_proposal_event(season_number, proposal):
    """Postseason stakeholder proposal the commissioner may docket."""

    proposal = proposal or {}
    headline = proposal.get("headline") or "a rule change"
    sponsor = proposal.get("sponsor") or "a stakeholder"
    body = proposal.get("body") or "the paddock"
    current = proposal.get("current_label") or "the current rule"

    return {
        "id": "rule-proposal-s{0}".format(season_number),
        "title": "Rule Proposal",
        "category": "rule-proposal",
        "phase": POSTSEASON,
        "proposal": dict(proposal),
        "prompt": (
            "{0} of the {1} introduces a rule proposal: adopt {2} "
            "(currently {3}). They want it on the next agenda. "
            "A vote comes later. What do you do with the paper?"
        ).format(sponsor, body, headline, current),
        "choices": [
            {
                "id": "1",
                "label": "Docket it for a later vote",
                "effects": [
                    {"type": "league", "stat": "integrity", "delta": 1},
                ],
                "outcomes": [
                    {
                        "weight": 100,
                        "text": "The paper goes on the docket. Voting comes later.",
                        "effects": [],
                    },
                ],
            },
            {
                "id": "2",
                "label": "Table it",
                "effects": [
                    {"type": "league", "stat": "controversy", "delta": 1},
                ],
                "outcomes": [
                    {
                        "weight": 100,
                        "text": "You table it. The sponsor calls it a stall.",
                        "effects": [],
                    },
                ],
            },
            {
                "id": "3",
                "label": "Kill the proposal",
                "effects": [
                    {"type": "league", "stat": "integrity", "delta": 2},
                    {"type": "league", "stat": "controversy", "delta": 2},
                ],
                "outcomes": [
                    {
                        "weight": 100,
                        "text": "You kill it. The sponsor leaves angry.",
                        "effects": [],
                    },
                ],
            },
        ],
    }


def rule_proposal_events(
    season_number,
    teams,
    drivers,
    resolved_ids,
    league=None,
    policies=None,
):
    """Return a stakeholder rule-proposal event when unresolved."""

    event_id = "rule-proposal-s{0}".format(season_number)
    if event_id in (resolved_ids or []):
        return []
    proposal = select_rule_proposal(
        teams,
        drivers,
        league,
        policies,
        season_number,
    )
    if not proposal:
        return []
    return [rule_proposal_event(season_number, proposal)]


RULE_VOTE_AYE_FLOOR = 60
RULE_VOTE_TILT = {
    "1": 0,
    "2": 18,
    "3": -18,
}
COALITION_LABELS = {
    "wins": "Wins",
    "stability": "Stability",
    "cost-control": "Cost-control",
    "prestige": "Prestige",
}
COALITION_ORDER = (
    "wins",
    "stability",
    "cost-control",
    "prestige",
)
LOBBY_SWING_DELTA = 12
LOBBY_OPPOSITION_TILT = -12


def coalition_label(priority):
    """Return the display name for an owner-priority bloc."""

    return COALITION_LABELS.get(priority, priority or "Independent")


def owner_coalitions(teams):
    """Return owner blocs grouped by priority, largest first."""

    blocs = {}
    for team in owner_council_seats(teams):
        key = team.owner.priority
        blocs.setdefault(key, []).append(team)
    return sorted(
        blocs.items(),
        key=lambda item: (
            -len(item[1]),
            COALITION_ORDER.index(item[0])
            if item[0] in COALITION_ORDER
            else 99,
            coalition_label(item[0]),
        ),
    )


def proposal_coalitions(teams, proposal):
    """Return backing and opposing seats for a docketed paper."""

    proposal = proposal or {}
    pair = (proposal.get("policy_key"), proposal.get("proposed_value"))
    backing = []
    opposition = []
    for team in owner_council_seats(teams):
        options = OWNER_PRIORITY_PROPOSALS.get(team.owner.priority) or ()
        if pair in options:
            backing.append(team)
        else:
            opposition.append(team)
    return backing, opposition


def rule_vote_heat(team, proposal, tilt=0, lobbying=None):
    """Return a seat's heat toward adopting the docketed paper."""

    owner = team.owner
    proposal = proposal or {}
    lobbying = lobbying or {}
    heat = 40
    pair = (proposal.get("policy_key"), proposal.get("proposed_value"))
    options = OWNER_PRIORITY_PROPOSALS.get(owner.priority) or ()
    if pair in options:
        heat += 25
    heat += (100 - owner.patience) // 4
    heat += owner.pressure // 5
    heat += int(tilt or 0)
    heat += int(lobbying.get("lobby_tilt") or 0)
    if owner.name == lobbying.get("swing_owner"):
        heat += int(lobbying.get("swing_delta") or 0)
    return heat


def rule_vote_swing_seat(teams, proposal, side="backing"):
    """Return the seat closest to the aye floor on this side of the paper."""

    backing, opposition = proposal_coalitions(teams, proposal)
    pool = opposition if side == "backing" else backing
    candidates = []
    for team in pool:
        heat = rule_vote_heat(team, proposal, tilt=0)
        if side == "backing" and heat < RULE_VOTE_AYE_FLOOR:
            candidates.append((RULE_VOTE_AYE_FLOOR - heat, team.name, team))
        elif side == "opposition" and heat >= RULE_VOTE_AYE_FLOOR:
            candidates.append((heat - RULE_VOTE_AYE_FLOOR, team.name, team))
    if not candidates:
        return None
    candidates.sort()
    return candidates[0][2]


def rule_vote_tally(teams, proposal, tilt=0, lobbying=None):
    """Return recorded aye/nay ballots on the oldest docketed paper."""

    ballots = []
    chair_team = owner_council_chair(teams)
    proposal = proposal or {}
    for team in owner_council_seats(teams):
        heat = rule_vote_heat(team, proposal, tilt, lobbying)
        vote = "aye" if heat >= RULE_VOTE_AYE_FLOOR else "nay"
        ballots.append(
            {
                "owner": team.owner.name,
                "team": team.name,
                "vote": vote,
                "heat": heat,
                "chair": team is chair_team,
            }
        )
    ayes = [item for item in ballots if item["vote"] == "aye"]
    nays = [item for item in ballots if item["vote"] == "nay"]
    return {
        "motion": "rule-change",
        "proposal": dict(proposal),
        "ballots": ballots,
        "ayes": len(ayes),
        "nays": len(nays),
        "passed": len(ayes) > len(nays),
    }


def rule_vote_event(season_number, proposal, teams, league=None):
    """Preseason chamber session: vote the oldest docketed paper."""

    league = league or {}
    proposal = proposal or {}
    seats = owner_council_seats(teams)
    chair_team = seats[0] if seats else None
    chair_name = chair_team.owner.name if chair_team else "the chair"
    chair_team_name = chair_team.name if chair_team else "the grid"
    headline = proposal.get("headline") or "a rule change"
    current = proposal.get("current_label") or "the current rule"
    sponsor = proposal.get("sponsor") or "a stakeholder"
    body = proposal.get("body") or "the paddock"
    roster = ", ".join(
        "{0} ({1})".format(team.owner.name, team.name)
        for team in seats
    )
    if not roster:
        roster = "no seated owners"

    return {
        "id": "rule-vote-s{0}".format(season_number),
        "title": "Rule Vote",
        "category": "rule-vote",
        "phase": PRESEASON,
        "proposal": dict(proposal),
        "prompt": (
            "The owner council reconvenes to vote the oldest paper on "
            "the docket. Chair {0} of {1} gavels the roll. Seats: {2}. "
            "{3} of the {4} asks the chamber to adopt {5} (currently "
            "{6}). How do you handle the vote?"
        ).format(
            chair_name,
            chair_team_name,
            roster,
            sponsor,
            body,
            headline,
            current,
        ),
        "choices": [
            {
                "id": "1",
                "label": "Let the chamber vote",
                "effects": [
                    {"type": "league", "stat": "integrity", "delta": 1},
                ],
                "outcomes": [
                    {
                        "weight": 100,
                        "text": "You let the owners vote the paper they brought.",
                        "effects": [],
                    },
                ],
            },
            {
                "id": "2",
                "label": "Whip for passage",
                "effects": [
                    {"type": "league", "stat": "owner_pressure", "delta": 3},
                    {"type": "league", "stat": "integrity", "delta": -2},
                ],
                "outcomes": [
                    {
                        "weight": 100,
                        "text": "You spend capital to line up the ayes.",
                        "effects": [],
                    },
                ],
            },
            {
                "id": "3",
                "label": "Whip against",
                "effects": [],
                "outcomes": [
                    {
                        "weight": 100,
                        "text": "You signal the chair to kill the paper.",
                        "effects": [],
                    },
                ],
            },
        ],
    }


def rule_vote_events(season_number, teams, resolved_ids, league=None):
    """Return a preseason rule vote when a paper is on the docket."""

    event_id = "rule-vote-s{0}".format(season_number)
    if event_id in (resolved_ids or []):
        return []
    docket = (league or {}).get("rule_docket") or []
    if not docket:
        return []
    if not teams:
        return []
    return [rule_vote_event(season_number, docket[0], teams, league)]


def _coalition_names(teams):
    """Return owner names for a coalition, comma-separated."""

    return ", ".join(team.owner.name for team in teams) or "nobody"


def _coalition_priorities(teams):
    """Return unique priority labels for a coalition."""

    labels = []
    seen = set()
    for team in teams:
        label = coalition_label(team.owner.priority)
        if label not in seen:
            seen.add(label)
            labels.append(label)
    return ", ".join(labels) or "Independent"


def lobbying_event(season_number, proposal, teams, league=None):
    """Preseason lobbying: pick a coalition before the floor vote."""

    proposal = proposal or {}
    backing, opposition = proposal_coalitions(teams, proposal)
    headline = proposal.get("headline") or "a rule change"
    sponsor = proposal.get("sponsor") or "a stakeholder"
    body = proposal.get("body") or "the paddock"
    for_names = _coalition_names(backing)
    against_names = _coalition_names(opposition)
    for_blocs = _coalition_priorities(backing)
    against_blocs = _coalition_priorities(opposition)
    swing = rule_vote_swing_seat(teams, proposal, "backing")
    swing_name = swing.owner.name if swing is not None else "a swing seat"

    return {
        "id": "lobbying-s{0}".format(season_number),
        "title": "Paddock Lobbying",
        "category": "lobbying",
        "phase": PRESEASON,
        "proposal": dict(proposal),
        "prompt": (
            "Coalitions are working the docket before the vote. "
            "{0} of the {1} wants {2}. The {3} bloc ({4}) is lining "
            "up for it. The {5} owners ({6}) are lining up against. "
            "{7} is the swing. Who do you take meetings with?"
        ).format(
            sponsor,
            body,
            headline,
            for_blocs,
            for_names,
            against_blocs,
            against_names,
            swing_name,
        ),
        "choices": [
            {
                "id": "1",
                "label": "Take every meeting",
                "effects": [
                    {"type": "league", "stat": "integrity", "delta": 1},
                ],
                "outcomes": [
                    {
                        "weight": 100,
                        "text": "You hear both blocs. Nobody leaves with a promise.",
                        "effects": [],
                    },
                ],
            },
            {
                "id": "2",
                "label": "Cultivate the backing bloc",
                "effects": [
                    {"type": "league", "stat": "integrity", "delta": -1},
                    {"type": "league", "stat": "owner_pressure", "delta": -2},
                ],
                "outcomes": [
                    {
                        "weight": 100,
                        "text": "You work the backing coalition. They peel a swing vote.",
                        "effects": [],
                    },
                ],
            },
            {
                "id": "3",
                "label": "Cultivate the opposition",
                "effects": [
                    {"type": "league", "stat": "integrity", "delta": -1},
                    {"type": "league", "stat": "owner_pressure", "delta": -2},
                ],
                "outcomes": [
                    {
                        "weight": 100,
                        "text": "You take the opposing coalition's meetings. The paper cools.",
                        "effects": [],
                    },
                ],
            },
        ],
    }


def lobbying_events(season_number, teams, resolved_ids, league=None):
    """Return a preseason lobbying session when a paper is on the docket."""

    event_id = "lobbying-s{0}".format(season_number)
    if event_id in (resolved_ids or []):
        return []
    docket = (league or {}).get("rule_docket") or []
    if not docket:
        return []
    if not teams:
        return []
    return [lobbying_event(season_number, docket[0], teams, league)]


def preseason_events(policies, season_number):
    """Return the preseason rule-change event for this season."""

    builder = RULE_EVENTS[(season_number - 1) % len(RULE_EVENTS)]
    return [builder(policies)]


def regular_season_events(
    race_number,
    teams,
    drivers,
    resolved_ids,
    media_stories=None,
):
    """Return in-season complaint, rivalry, and press-conference events."""

    events = []

    if press_conference_needed(media_stories):
        event_id = "press-conference-r{0}".format(race_number)
        if event_id not in resolved_ids:
            events.append(press_conference_event(race_number, media_stories))

    if race_number == 2 and "owner-complaint" not in resolved_ids:
        events.append(owner_complaint_event(_team_by_pressure(teams)))

    if race_number == 3 and "rivalry-contact" not in resolved_ids:
        pair = _hottest_rivalry_pair(drivers)

        if pair is not None and pair[0].rivalry_intensity >= 40:
            events.append(rivalry_contact_event(pair[0], pair[1]))

    if race_number == 4 and "driver-complaint" not in resolved_ids:
        events.append(driver_complaint_event(_driver_by_unrest(drivers)))

    if race_number == 5 and "rivalry-argument" not in resolved_ids:
        pair = _hottest_rivalry_pair(drivers)

        if pair is not None and pair[0].rivalry_intensity >= 45:
            events.append(rivalry_argument_event(pair[0], pair[1]))

    return events


def postseason_events(
    teams,
    drivers,
    resolved_ids,
    league=None,
    season_number=1,
):
    """Return postseason owner, driver-council, and feud events."""

    events = []

    if "owner-lobbying" not in resolved_ids:
        events.append(owner_lobbying_event(_team_by_pressure(teams)))

    events.extend(
        owner_council_events(
            season_number,
            teams,
            resolved_ids,
            league,
        )
    )

    if "driver-grievance" not in resolved_ids:
        events.append(driver_grievance_event(_driver_by_unrest(drivers)))

    events.extend(
        driver_council_events(
            season_number,
            drivers,
            resolved_ids,
            league,
        )
    )

    if "feud-review" not in resolved_ids:
        feud_pair = _hottest_feud_pair(drivers)

        if feud_pair is not None and feud_pair[2].get("intensity", 0) >= 50:
            events.append(
                feud_review_event(feud_pair[0], feud_pair[1], feud_pair[2])
            )

    return events


def offseason_events(policies, resolved_ids):
    """Return the offseason safety decision."""

    if "safety-mandate" in resolved_ids:
        return []

    return [safety_mandate_event(policies)]


APPROVAL_SLIP_FLOOR = 50


def _approval_clamp(value):
    """Clamp a rating to 0–100."""

    return max(0, min(100, int(round(value))))


def approval_label(score):
    """Return Popular, Accepted, Mixed, Unpopular, or Hostile."""

    score = _approval_clamp(score)
    if score >= 80:
        return "Popular"
    if score >= 65:
        return "Accepted"
    if score >= 50:
        return "Mixed"
    if score >= 35:
        return "Unpopular"
    return "Hostile"


def fan_approval_score(league):
    """Return fan approval from league fan interest."""

    return _approval_clamp((league or {}).get("fan_interest", 65))


def owner_approval_score(league, teams):
    """Return owner approval from pressure, eased by patience."""

    league = league or {}
    pressure = int(league.get("owner_pressure", 25))
    score = 100 - pressure
    owners = [team.owner for team in (teams or [])]
    if owners:
        patience = sum(owner.patience for owner in owners) / float(len(owners))
        score = score * 0.7 + patience * 0.3
    return _approval_clamp(score)


def driver_approval_score(league, drivers):
    """Return driver approval from sentiment, trust, and morale."""

    league = league or {}
    sentiment = int(league.get("driver_sentiment", 60))
    roster = list(drivers or [])
    if roster:
        trust = sum(driver.commissioner_trust for driver in roster) / float(
            len(roster)
        )
        morale = sum(driver.morale for driver in roster) / float(len(roster))
        score = sentiment * 0.5 + trust * 0.3 + morale * 0.2
    else:
        score = sentiment
    return _approval_clamp(score)


def approval_ratings(league, teams, drivers):
    """Return overall and constituency approval ratings."""

    fans = fan_approval_score(league)
    owners = owner_approval_score(league, teams)
    garage = driver_approval_score(league, drivers)
    overall = _approval_clamp((fans + owners + garage) / 3.0)
    return {
        "overall": overall,
        "label": approval_label(overall),
        "fans": fans,
        "fans_label": approval_label(fans),
        "owners": owners,
        "owners_label": approval_label(owners),
        "drivers": garage,
        "drivers_label": approval_label(garage),
    }


BOARD_REVIEW_FLOOR = 65
BOARD_DISMISSAL_FLOOR = 35
BOARD_REBUKE_PENALTY = 12
BOARD_PROTEST_PENALTY = 8
BOARD_SCANDAL_PENALTY = 5
BOARD_CONFIDENCE_TILT = {
    "1": 8,
    "2": 4,
    "3": -14,
}


def board_confidence_label(score):
    """Return Secure, Steady, Watched, Precarious, or Collapsing."""

    score = _approval_clamp(score)
    if score >= 80:
        return "Secure"
    if score >= 65:
        return "Steady"
    if score >= 50:
        return "Watched"
    if score >= 35:
        return "Precarious"
    return "Collapsing"


def dismissal_risk_score(confidence):
    """Return dismissal risk as the inverse of board confidence."""

    return _approval_clamp(100 - confidence)


def dismissal_risk_label(risk):
    """Return Low, Moderate, Elevated, High, or Critical."""

    risk = _approval_clamp(risk)
    if risk < 20:
        return "Low"
    if risk < 35:
        return "Moderate"
    if risk < 50:
        return "Elevated"
    if risk < 65:
        return "High"
    return "Critical"


def board_confidence_score(league, teams, drivers):
    """Return board confidence from approval, integrity, and political hits."""

    league = league or {}
    approval = approval_ratings(league, teams, drivers)
    integrity = int(league.get("integrity", 70))
    controversy = int(league.get("controversy", 20))
    score = (
        approval["overall"] * 0.45
        + integrity * 0.25
        + (100 - controversy) * 0.20
        + approval["owners"] * 0.10
    )
    last_owners = league.get("last_owner_council") or {}
    last_garage = league.get("last_driver_council") or {}
    if last_owners.get("passed"):
        score -= BOARD_REBUKE_PENALTY
    if last_garage.get("protested"):
        score -= BOARD_PROTEST_PENALTY
    if league.get("last_media_controversy"):
        score -= BOARD_SCANDAL_PENALTY
    return _approval_clamp(score)


def job_security_ratings(league, teams, drivers):
    """Return board confidence and dismissal risk."""

    confidence = board_confidence_score(league, teams, drivers)
    risk = dismissal_risk_score(confidence)
    return {
        "confidence": confidence,
        "confidence_label": board_confidence_label(confidence),
        "risk": risk,
        "risk_label": dismissal_risk_label(risk),
        "review": confidence < BOARD_REVIEW_FLOOR,
        "threatened": confidence < BOARD_DISMISSAL_FLOOR,
    }


def board_confidence_event(season_number, security):
    """Postseason board review when confidence is no longer steady."""

    security = security or {}
    confidence = security.get("confidence", 0)
    risk = security.get("risk", 0)
    conf_label = security.get("confidence_label") or board_confidence_label(
        confidence
    )
    risk_label = security.get("risk_label") or dismissal_risk_label(risk)

    return {
        "id": "board-confidence-s{0}".format(season_number),
        "title": "Board of Directors",
        "category": "board-confidence",
        "phase": POSTSEASON,
        "prompt": (
            "The board of directors has called a confidence review. "
            "Board confidence is {0} {1}. Dismissal risk is {2} {3}. "
            "A poor hearing can end the career. How do you face them?"
        ).format(confidence, conf_label, risk, risk_label),
        "choices": [
            {
                "id": "1",
                "label": "Present the season",
                "effects": [
                    {"type": "league", "stat": "integrity", "delta": 1},
                ],
                "outcomes": [
                    {
                        "weight": 100,
                        "text": "You walk them through the year. A few chairs nod.",
                        "effects": [],
                    },
                ],
            },
            {
                "id": "2",
                "label": "Promise reforms",
                "effects": [
                    {"type": "league", "stat": "owner_pressure", "delta": -4},
                    {"type": "league", "stat": "integrity", "delta": -1},
                ],
                "outcomes": [
                    {
                        "weight": 100,
                        "text": "You promise a quieter paddock. They want to see it.",
                        "effects": [],
                    },
                ],
            },
            {
                "id": "3",
                "label": "Defy the board",
                "effects": [
                    {"type": "league", "stat": "integrity", "delta": 3},
                    {"type": "league", "stat": "controversy", "delta": 5},
                ],
                "outcomes": [
                    {
                        "weight": 100,
                        "text": "You tell the board the league is not a committee.",
                        "effects": [],
                    },
                ],
            },
        ],
    }


TEAM_FIELD_MAX = 5


def team_entry_event(season_number, applicant, field_size):
    """Offseason charter decision for the next owner in line."""

    applicant = applicant or {}
    name = applicant.get("owner_name") or "An owner"
    shop = applicant.get("team_name") or "a new team"
    priority = applicant.get("priority") or "stability"
    wealth = applicant.get("wealth", 50)
    manufacturer = applicant.get("manufacturer") or "Independent"

    return {
        "id": "team-entry-s{0}".format(season_number),
        "title": "New Team Applicant: {0}".format(shop),
        "category": "team-entry",
        "phase": OFFSEASON,
        "prompt": (
            "{0} wants a charter for {1}. Wealth {2}, priority {3}, "
            "{4} cars. The grid is {5} teams. Grant a charter, defer, "
            "or deny?"
        ).format(name, shop, wealth, priority, manufacturer, field_size),
        "choices": [
            {
                "id": "1",
                "label": "Grant a charter",
                "effects": [
                    {"type": "league", "stat": "fan_interest", "delta": 4},
                    {"type": "league", "stat": "owner_pressure", "delta": 4},
                ],
                "outcomes": [
                    {
                        "weight": 100,
                        "text": (
                            "{0} is in. Fans like a new shop. "
                            "Incumbent owners feel the squeeze."
                        ).format(shop),
                        "effects": [],
                    },
                ],
            },
            {
                "id": "2",
                "label": "Defer the application",
                "effects": [
                    {"type": "league", "stat": "owner_pressure", "delta": -1},
                ],
                "outcomes": [
                    {
                        "weight": 100,
                        "text": (
                            "{0} stays first in line. "
                            "Incumbent owners ease slightly."
                        ).format(name),
                        "effects": [],
                    },
                ],
            },
            {
                "id": "3",
                "label": "Deny the application",
                "effects": [
                    {"type": "league", "stat": "integrity", "delta": 2},
                    {"type": "league", "stat": "fan_interest", "delta": -3},
                ],
                "outcomes": [
                    {
                        "weight": 100,
                        "text": (
                            "The book closes on {0}. The series looks "
                            "disciplined. Fans wanted a new shop."
                        ).format(shop),
                        "effects": [],
                    },
                ],
            },
        ],
    }


def team_entry_events(season_number, teams, applicants, resolved_ids):
    """Return a charter hearing when the field is open and someone is waiting."""

    event_id = "team-entry-s{0}".format(season_number)
    if event_id in (resolved_ids or []):
        return []
    field = list(teams or [])
    if len(field) >= TEAM_FIELD_MAX:
        return []
    waiting = list(applicants or [])
    if not waiting:
        return []
    return [team_entry_event(season_number, waiting[0], len(field))]


def board_confidence_events(season_number, teams, drivers, resolved_ids, league=None):
    """Return a board review when confidence has slipped off Steady."""

    event_id = "board-confidence-s{0}".format(season_number)
    if event_id in (resolved_ids or []):
        return []
    security = job_security_ratings(league, teams, drivers)
    if not security["review"]:
        return []
    return [board_confidence_event(season_number, security)]
