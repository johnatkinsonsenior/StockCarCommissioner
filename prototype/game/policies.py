"""Persistent league rules that the commissioner may change."""

DEFAULT_POLICIES = {
    "points_system": "standard",
    "race_format": "single-feature",
    "penalty_standard": "balanced",
    "technical_rules": "open",
    "safety_standard": "current",
}

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
}

POINTS_TABLES = {
    "standard": [40, 35, 32, 30, 28, 26],
    "winner-heavy": [50, 35, 28, 24, 20, 16],
    "flattened": [32, 30, 28, 26, 24, 22],
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
