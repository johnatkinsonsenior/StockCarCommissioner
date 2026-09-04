"""Career game settings: difficulty, season length, and autosave."""

import copy

DIFFICULTY_EASY = "easy"
DIFFICULTY_NORMAL = "normal"
DIFFICULTY_HARD = "hard"

AUTOSAVE_OFF = "off"
AUTOSAVE_OFFSEASON = "offseason"
AUTOSAVE_RACE = "race"

VALID_DIFFICULTIES = (DIFFICULTY_EASY, DIFFICULTY_NORMAL, DIFFICULTY_HARD)
VALID_AUTOSAVE = (AUTOSAVE_OFF, AUTOSAVE_OFFSEASON, AUTOSAVE_RACE)
VALID_CAREER_SEASONS = (3, 5, 10)
AUTOSAVE_FILENAME = "autosave.json"

DEFAULT_SETTINGS = {
    "difficulty": DIFFICULTY_NORMAL,
    "career_seasons": 3,
    "autosave": AUTOSAVE_OFF,
}

DIFFICULTY_LABELS = {
    DIFFICULTY_EASY: "Easy",
    DIFFICULTY_NORMAL: "Normal",
    DIFFICULTY_HARD: "Hard",
}

AUTOSAVE_LABELS = {
    AUTOSAVE_OFF: "Off",
    AUTOSAVE_OFFSEASON: "After each offseason",
    AUTOSAVE_RACE: "After each race",
}

DIFFICULTY_PROFILES = {
    DIFFICULTY_EASY: {
        "integrity": 78,
        "fan_interest": 75,
        "controversy": 12,
        "owner_pressure": 15,
        "driver_sentiment": 70,
        "treasury": 500_000,
        "budget_bonus": 750_000,
        "incident_risk_mod": -8,
        "dismissal_floor": 27,
        "review_floor": 55,
    },
    DIFFICULTY_NORMAL: {
        "integrity": 70,
        "fan_interest": 65,
        "controversy": 20,
        "owner_pressure": 25,
        "driver_sentiment": 60,
        "treasury": 0,
        "budget_bonus": 0,
        "incident_risk_mod": 0,
        "dismissal_floor": 35,
        "review_floor": 65,
    },
    DIFFICULTY_HARD: {
        "integrity": 62,
        "fan_interest": 52,
        "controversy": 30,
        "owner_pressure": 42,
        "driver_sentiment": 50,
        "treasury": 0,
        "budget_bonus": -600_000,
        "incident_risk_mod": 8,
        "dismissal_floor": 43,
        "review_floor": 72,
    },
}

current_settings = dict(DEFAULT_SETTINGS)


def reset_settings():
    """Restore default career settings."""

    current_settings.clear()
    current_settings.update(DEFAULT_SETTINGS)


def fill_settings_defaults(data):
    """Return a valid settings dict, filling any missing slots."""

    filled = dict(DEFAULT_SETTINGS)
    data = data or {}
    difficulty = data.get("difficulty")
    if difficulty in VALID_DIFFICULTIES:
        filled["difficulty"] = difficulty
    seasons = data.get("career_seasons")
    if seasons in VALID_CAREER_SEASONS:
        filled["career_seasons"] = int(seasons)
    elif isinstance(seasons, int) and 1 <= seasons <= 20:
        filled["career_seasons"] = int(seasons)
    autosave = data.get("autosave")
    if autosave in VALID_AUTOSAVE:
        filled["autosave"] = autosave
    return filled


def settings_from_save(save_data):
    """Restore settings from a save, inferring defaults for legacy files."""

    save_data = save_data or {}
    raw = save_data.get("settings")
    if not raw:
        raw = {
            "difficulty": DIFFICULTY_NORMAL,
            "career_seasons": save_data.get("career_seasons_total") or 3,
            "autosave": AUTOSAVE_OFF,
        }
    return fill_settings_defaults(raw)


def load_settings(saved_settings, replace=False):
    """Replace or merge current settings from a save file or menu choice."""

    if replace:
        base = dict(DEFAULT_SETTINGS)
    else:
        base = dict(current_settings)
    base.update(saved_settings or {})
    current_settings.clear()
    current_settings.update(fill_settings_defaults(base))
    return dict(current_settings)


def difficulty_profile(difficulty=None):
    """Return the live difficulty profile."""

    key = difficulty or current_settings.get("difficulty") or DIFFICULTY_NORMAL
    return dict(DIFFICULTY_PROFILES.get(key) or DIFFICULTY_PROFILES[DIFFICULTY_NORMAL])


def difficulty_label(difficulty=None):
    """Return a readable difficulty name."""

    key = difficulty or current_settings.get("difficulty") or DIFFICULTY_NORMAL
    return DIFFICULTY_LABELS.get(key, "Normal")


def autosave_label(mode=None):
    """Return a readable autosave name."""

    key = mode or current_settings.get("autosave") or AUTOSAVE_OFF
    return AUTOSAVE_LABELS.get(key, "Off")


def incident_risk_mod():
    """Return the weekend incident-risk adjustment for the live difficulty."""

    return int(difficulty_profile().get("incident_risk_mod") or 0)


def dismissal_floor():
    """Return the board dismissal threshold for the live difficulty."""

    return int(difficulty_profile().get("dismissal_floor") or 35)


def review_floor():
    """Return the board-review threshold for the live difficulty."""

    return int(difficulty_profile().get("review_floor") or 65)


def autosave_on(moment):
    """Return whether autosave should fire after this career moment."""

    mode = current_settings.get("autosave") or AUTOSAVE_OFF
    if mode == AUTOSAVE_OFF:
        return False
    if moment == AUTOSAVE_RACE:
        return mode == AUTOSAVE_RACE
    if moment == AUTOSAVE_OFFSEASON:
        return mode in (AUTOSAVE_OFFSEASON, AUTOSAVE_RACE)
    return False


def settings_dashboard_text():
    """Return the compact settings dashboard line."""

    seasons = current_settings.get("career_seasons") or 3
    season_word = "season" if seasons == 1 else "seasons"
    return "Settings: %s | %s %s | Autosave %s" % (
        difficulty_label(),
        seasons,
        season_word,
        autosave_label(),
    )


def settings_to_dict():
    """Return a JSON-safe copy of the live settings."""

    return copy.deepcopy(fill_settings_defaults(current_settings))
