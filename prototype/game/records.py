"""All-time historical records for the league.

Everything here is derived from data the game already tracks: driver and team
career totals plus the per-season ``career_history`` (which stores each
season's final standings and full race history). Records are computed on
demand, so nothing extra needs to be persisted in a save file.
"""


def _all_drivers(active_drivers, retired_drivers):
    """Return active and retired drivers as one list."""

    return list(active_drivers) + list(retired_drivers)


def most_career_wins(active_drivers, retired_drivers):
    """Return (name, wins) for the all-time race-wins leader, or None."""

    drivers = _all_drivers(active_drivers, retired_drivers)

    if not drivers:
        return None

    leader = max(
        drivers,
        key=lambda driver: (driver.career_wins, driver.career_points),
    )

    return (leader.name, leader.career_wins)


def most_championships(active_drivers, retired_drivers):
    """Return (name, championships) for the most-decorated driver, or None."""

    drivers = _all_drivers(active_drivers, retired_drivers)

    if not drivers:
        return None

    leader = max(
        drivers,
        key=lambda driver: (driver.championships, driver.career_wins),
    )

    return (leader.name, leader.championships)


def most_team_wins(teams):
    """Return (name, wins) for the winningest team, or None."""

    if not teams:
        return None

    leader = max(teams, key=lambda team: team.career_wins)

    return (leader.name, leader.career_wins)


def most_organization_titles(teams):
    """Return (name, titles) for the team with the most org titles, or None."""

    if not teams:
        return None

    leader = max(teams, key=lambda team: team.organization_titles)

    return (leader.name, leader.organization_titles)


def most_wins_in_a_season(career_history):
    """Return (driver, wins, season) for the best single-season win haul."""

    best = None

    for season in career_history:
        for row in season.get("standings", []):
            wins = row.get("wins", 0)

            if best is None or wins > best[1]:
                best = (row["driver"], wins, season.get("season"))

    return best


def highest_season_points(career_history):
    """Return (driver, points, season) for the highest single-season total."""

    best = None

    for season in career_history:
        for row in season.get("standings", []):
            points = row.get("points", 0)

            if best is None or points > best[1]:
                best = (row["driver"], points, season.get("season"))

    return best


def longest_title_streak(career_history):
    """Return (driver, streak) for the longest run of consecutive titles."""

    best_name = None
    best = 0
    current_name = None
    current = 0

    for season in career_history:
        champion = season.get("champion")

        if champion is None:
            current_name = None
            current = 0
            continue

        if champion == current_name:
            current += 1
        else:
            current_name = champion
            current = 1

        if current > best:
            best = current
            best_name = champion

    return (best_name, best) if best_name else None


def longest_win_streak(career_history):
    """Return (driver, streak) for the longest run of consecutive race wins."""

    best_name = None
    best = 0
    current_name = None
    current = 0

    for season in career_history:
        for race in season.get("race_history", []):
            results = race.get("results") or []

            if not results:
                continue

            winner = results[0]["driver"]

            if winner == current_name:
                current += 1
            else:
                current_name = winner
                current = 1

            if current > best:
                best = current
                best_name = winner

    return (best_name, best) if best_name else None


def build_record_book(active_drivers, retired_drivers, teams, career_history):
    """Assemble the all-time record book as a dictionary of records."""

    return {
        "most_career_wins": most_career_wins(active_drivers, retired_drivers),
        "most_championships": most_championships(
            active_drivers,
            retired_drivers,
        ),
        "most_team_wins": most_team_wins(teams),
        "most_organization_titles": most_organization_titles(teams),
        "most_wins_in_a_season": most_wins_in_a_season(career_history),
        "highest_season_points": highest_season_points(career_history),
        "longest_title_streak": longest_title_streak(career_history),
        "longest_win_streak": longest_win_streak(career_history),
    }
