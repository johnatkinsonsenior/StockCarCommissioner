"""Commissioner decision templates for rule, safety, owner, and driver events."""

from game.calendar import (
    OFFSEASON,
    POSTSEASON,
    PRESEASON,
    REGULAR_SEASON,
)
from game.policies import policy_label


def _team_by_pressure(teams):
    """Return the team most likely to complain."""

    return min(
        teams,
        key=lambda team: (
            -team.financial_distress_level,
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

    return {
        "id": "owner-complaint",
        "title": "Owner Complaint",
        "category": "owner-complaint",
        "phase": REGULAR_SEASON,
        "subject_team_name": team.name,
        "prompt": (
            f"The owner of {team.name} requests a private meeting. "
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

    return {
        "id": "owner-lobbying",
        "title": "Owner Lobbying",
        "category": "owner-complaint",
        "phase": POSTSEASON,
        "subject_team_name": team.name,
        "prompt": (
            f"{team.name} organizes a postseason owners' call. They want "
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


RULE_EVENTS = (
    points_system_event,
    race_format_event,
    penalty_standard_event,
    technical_rules_event,
)


def preseason_events(policies, season_number):
    """Return the preseason rule-change event for this season."""

    builder = RULE_EVENTS[(season_number - 1) % len(RULE_EVENTS)]
    return [builder(policies)]


def regular_season_events(race_number, teams, drivers, resolved_ids):
    """Return in-season complaint events tied to specific races."""

    events = []

    if race_number == 2 and "owner-complaint" not in resolved_ids:
        events.append(owner_complaint_event(_team_by_pressure(teams)))

    if race_number == 4 and "driver-complaint" not in resolved_ids:
        events.append(driver_complaint_event(_driver_by_unrest(drivers)))

    return events


def postseason_events(teams, drivers, resolved_ids):
    """Return postseason owner and driver events."""

    events = []

    if "owner-lobbying" not in resolved_ids:
        events.append(owner_lobbying_event(_team_by_pressure(teams)))

    if "driver-grievance" not in resolved_ids:
        events.append(driver_grievance_event(_driver_by_unrest(drivers)))

    return events


def offseason_events(policies, resolved_ids):
    """Return the offseason safety decision."""

    if "safety-mandate" in resolved_ids:
        return []

    return [safety_mandate_event(policies)]
