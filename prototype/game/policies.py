"""Persistent league rules that the commissioner may change."""

DEFAULT_POLICIES = {
    "points_system": "standard",
    "race_format": "single-feature",
    "penalty_standard": "balanced",
    "technical_rules": "open",
    "safety_standard": "current",
    "scoring_bonuses": "standard",
    "championship_format": "season-long",
}

# Playoff configuration used when championship_format is "playoff".
PLAYOFF_FIELD_SIZE = 4
PLAYOFF_RACE_COUNT = 4

POLICY_LABELS = {
    "points_system": {
        "standard": "Standard points",
        "winner-heavy": "Winner-heavy points",
        "flattened": "Flattened points",
    },
    "race_format": {
        "single-feature": "Single-feature race",
        "heat-and-feature": "Heat and feature",
        "stage-racing": "Stage racing",
    },
    "penalty_standard": {
        "lenient": "Lenient enforcement",
        "balanced": "Balanced enforcement",
        "strict": "Strict enforcement",
    },
    "technical_rules": {
        "open": "Open technical package",
        "aero-restrict": "Aero restriction package",
        "inspection-heavy": "Inspection-heavy package",
    },
    "safety_standard": {
        "current": "Current safety standard",
        "enhanced": "Enhanced safety mandate",
        "maximum": "Maximum safety package",
    },
    "scoring_bonuses": {
        "none": "No bonus points",
        "standard": "Standard bonus points",
        "rich": "Rich bonus points",
    },
    "championship_format": {
        "season-long": "Season-long championship",
        "playoff": "Playoff championship",
    },
}

POINTS_TABLES = {
    "standard": [40, 35, 32, 30, 28, 26],
    "winner-heavy": [50, 35, 28, 24, 20, 16],
    "flattened": [32, 30, 28, 26, 24, 22],
}

# Bonus points awarded on top of the finishing-position table. "hard_charger"
# goes to the driver who gains the most positions from their start.
SCORING_BONUSES = {
    "none": {"win": 0, "pole": 0, "hard_charger": 0},
    "standard": {"win": 5, "pole": 1, "hard_charger": 3},
    "rich": {"win": 10, "pole": 3, "hard_charger": 5},
}

current_policies = dict(DEFAULT_POLICIES)


def reset_policies():
    """Restore default league policies."""

    current_policies.clear()
    current_policies.update(DEFAULT_POLICIES)


def load_policies(saved_policies):
    """Replace current policies from a save file."""

    reset_policies()

    if not saved_policies:
        return

    for key, value in saved_policies.items():
        if key in current_policies:
            current_policies[key] = value


def policy_label(policy_key, value=None):
    """Return a readable label for a policy setting."""

    if value is None:
        value = current_policies[policy_key]

    return POLICY_LABELS[policy_key][value]


def get_points_by_position():
    """Return the active championship points table."""

    return POINTS_TABLES[current_policies["points_system"]]


def get_stage_points_by_position():
    """Return stage points derived from the active championship table."""

    return [
        max(1, points // 4)
        for points in get_points_by_position()
    ]


def get_scoring_bonuses():
    """Return the active bonus-point values for win, pole, and hard charger."""

    return dict(SCORING_BONUSES[current_policies["scoring_bonuses"]])


def uses_playoff():
    """Return whether the champion is decided by a playoff postseason."""

    return current_policies["championship_format"] == "playoff"


def get_playoff_field_size():
    """Return how many drivers make the championship playoff."""

    return PLAYOFF_FIELD_SIZE


def get_playoff_race_count():
    """Return how many end-of-season races make up the playoff round."""

    return PLAYOFF_RACE_COUNT


def get_points_speeding_penalty():
    """Return championship points docked for a pit-road speeding infraction.

    Scales with the league's penalty standard. Returns 0 when bonus scoring is
    switched off entirely, keeping "No bonus points" a clean vanilla table.
    """

    if current_policies["scoring_bonuses"] == "none":
        return 0

    return {
        "lenient": 0,
        "balanced": 1,
        "strict": 2,
    }[current_policies["penalty_standard"]]


def uses_stage_racing():
    """Return whether the current race format awards stage points."""

    return current_policies["race_format"] == "stage-racing"


def uses_heat_races():
    """Return whether the current format runs a heat before the feature."""

    return current_policies["race_format"] == "heat-and-feature"


def get_crash_modifier():
    """Return an incident-risk adjustment from active policies."""

    safety = {
        "current": 0,
        "enhanced": -4,
        "maximum": -7,
    }[current_policies["safety_standard"]]

    race_format = {
        "single-feature": 0,
        "heat-and-feature": 2,
        "stage-racing": 1,
    }[current_policies["race_format"]]

    technical = {
        "open": 0,
        "aero-restrict": -2,
        "inspection-heavy": -1,
    }[current_policies["technical_rules"]]

    return safety + race_format + technical


def get_penalty_fine_amount():
    """Return the standard reckless-driving fine."""

    return {
        "lenient": 25_000,
        "balanced": 50_000,
        "strict": 75_000,
    }[current_policies["penalty_standard"]]


def get_penalty_points_amount():
    """Return the standard championship points penalty."""

    return {
        "lenient": 5,
        "balanced": 10,
        "strict": 15,
    }[current_policies["penalty_standard"]]


def pit_road_enforcement():
    """Return how hard pit-road speeding is punished."""

    return {
        "lenient": 0,
        "balanced": 1,
        "strict": 2,
    }[current_policies["penalty_standard"]]


def get_policy_operating_cost():
    """Return extra per-team operating cost from league mandates."""

    safety_cost = {
        "current": 0,
        "enhanced": 75_000,
        "maximum": 150_000,
    }[current_policies["safety_standard"]]

    inspection_cost = 0

    if current_policies["technical_rules"] == "inspection-heavy":
        inspection_cost = 50_000

    return safety_cost + inspection_cost
