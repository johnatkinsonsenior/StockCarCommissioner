"""League calendar and formal career game states."""

PRESEASON = "preseason"
REGULAR_SEASON = "regular-season"
POSTSEASON = "postseason"
OFFSEASON = "offseason"

SEASON_PHASES = (
    PRESEASON,
    REGULAR_SEASON,
    POSTSEASON,
    OFFSEASON,
)

PHASE_LABELS = {
    PRESEASON: "Preseason",
    REGULAR_SEASON: "Regular Season",
    POSTSEASON: "Postseason",
    OFFSEASON: "Offseason",
}


def infer_phase(season_in_progress, race_count=0, track_count=0):
    """Infer a calendar phase from Day 14 save fields."""

    if season_in_progress:
        if track_count and race_count >= track_count:
            return POSTSEASON

        return REGULAR_SEASON

    return PRESEASON


class LeagueCalendar:
    """Tracks the current season and league calendar phase."""

    def __init__(
        self,
        current_season=1,
        career_seasons_total=3,
        phase=PRESEASON,
    ):
        self.current_season = current_season
        self.career_seasons_total = career_seasons_total
        self.phase = phase

    def phase_label(self):
        """Return a readable name for the current phase."""

        return PHASE_LABELS.get(self.phase, self.phase)

    def description(self):
        """Return a short calendar status line."""

        return (
            f"Season {self.current_season} of "
            f"{self.career_seasons_total} — {self.phase_label()}"
        )

    def season_in_progress(self):
        """Return whether the regular season is currently underway."""

        return self.phase == REGULAR_SEASON

    def has_more_seasons(self):
        """Return whether another season follows the current one."""

        return self.current_season < self.career_seasons_total

    def enter_preseason(self):
        self.phase = PRESEASON

    def enter_regular_season(self):
        self.phase = REGULAR_SEASON

    def enter_postseason(self):
        self.phase = POSTSEASON

    def enter_offseason(self):
        self.phase = OFFSEASON

    def advance_to_next_season(self):
        """Move the calendar into preseason of the next season."""

        self.current_season += 1
        self.phase = PRESEASON

    def to_dict(self):
        """Serialize the calendar for a save file."""

        return {
            "current_season": self.current_season,
            "career_seasons_total": self.career_seasons_total,
            "phase": self.phase,
        }

    @classmethod
    def from_save_data(cls, save_data, track_count=0):
        """Restore a calendar from save data, including Day 14 files."""

        current_season = save_data["current_season"]
        career_seasons_total = save_data["career_seasons_total"]
        phase = save_data.get("calendar_phase")

        if phase not in SEASON_PHASES:
            race_count = len(save_data.get("race_history") or [])
            phase = infer_phase(
                save_data.get("season_in_progress", False),
                race_count=race_count,
                track_count=track_count,
            )

        return cls(
            current_season=current_season,
            career_seasons_total=career_seasons_total,
            phase=phase,
        )
