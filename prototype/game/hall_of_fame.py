"""Hall of Fame inductions for retired premier drivers."""

HOF_WIN_BAR = 15
HOF_POINTS_BAR = 4000


def hall_reason(driver):
    """Return why this retiree belongs in the Hall, or None."""

    if driver is None:
        return None
    titles = int(getattr(driver, "championships", 0) or 0)
    wins = int(getattr(driver, "career_wins", 0) or 0)
    points = int(getattr(driver, "career_points", 0) or 0)
    if titles >= 1:
        return "champion"
    if wins >= HOF_WIN_BAR:
        return "wins"
    if points >= HOF_POINTS_BAR:
        return "points"
    return None


def hall_blurb(driver, reason):
    """Return a short plaque line."""

    name = getattr(driver, "name", "A driver")
    team = getattr(driver, "team_name", "the series")
    titles = int(getattr(driver, "championships", 0) or 0)
    wins = int(getattr(driver, "career_wins", 0) or 0)
    points = int(getattr(driver, "career_points", 0) or 0)
    if reason == "champion":
        word = "title" if titles == 1 else "titles"
        return "%s parked with %s Cup %s in a %s seat." % (name, titles, word, team)
    if reason == "wins":
        return "%s won %s Cup races for %s." % (name, wins, team)
    return "%s scored %s career Cup points for %s." % (name, points, team)


def make_plaque(driver, season, reason):
    """Return one Hall of Fame plaque dictionary."""

    from game.ui_bridge import office_slug

    return {
        "id": office_slug(getattr(driver, "name", "")),
        "name": getattr(driver, "name", ""),
        "team": getattr(driver, "team_name", ""),
        "season": int(season or 0),
        "reason": reason,
        "championships": int(getattr(driver, "championships", 0) or 0),
        "career_wins": int(getattr(driver, "career_wins", 0) or 0),
        "career_points": int(getattr(driver, "career_points", 0) or 0),
        "blurb": hall_blurb(driver, reason),
    }


def consider_hall_of_fame(league, driver, season):
    """Induct a retiree who clears the bar. Return the plaque or None."""

    league = league if isinstance(league, dict) else {}
    plaques = list(league.get("hall_of_fame") or [])
    reason = hall_reason(driver)
    if not reason:
        return None
    name = getattr(driver, "name", "")
    for row in plaques:
        if row.get("name") == name or row.get("id") == name:
            return None
    plaque = make_plaque(driver, season, reason)
    plaques.append(plaque)
    league["hall_of_fame"] = plaques
    return plaque
