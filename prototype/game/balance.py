"""AI commissioner helpers and balance-simulation reports."""

import json
from datetime import datetime
from pathlib import Path

DEFAULT_TARGET_SEASONS = 50
LONG_TARGET_SEASONS = 100
DEFAULT_SEASONS_PER_CAREER = 5

CATEGORY_CHOICES = {
    "board-confidence": "1",
    "team-closure": "2",
    "manufacturer-switch": "2",
    "team-entry": "2",
}


def _clamp_choice(picked, count):
    """Keep a 1-based choice id inside 1..count."""

    if count < 1:
        return "1"
    try:
        number = int(picked)
    except (TypeError, ValueError):
        number = (count + 1) // 2
    number = max(1, min(count, number))
    return str(number)


def ai_pick_numbered(count, prompt="", extra_lines=None, event=None):
    """Pick a numbered commissioner choice without waiting on input."""

    event = event or {}
    category = event.get("category") or ""
    if category in CATEGORY_CHOICES:
        return _clamp_choice(CATEGORY_CHOICES[category], count)

    blob = " ".join(
        [
            category,
            event.get("title") or "",
            prompt or "",
            " ".join(extra_lines or []),
        ]
    ).lower()

    if any(
        token in blob
        for token in (
            "withdraw the charter",
            "bridge loan",
            "insolvent",
            "team closure",
        )
    ):
        return _clamp_choice("2", count)

    if any(
        token in blob
        for token in (
            "factory switch",
            "hold the current badge",
            "manufacturer",
        )
    ):
        return _clamp_choice("2", count)

    if "grant a charter" in blob or "new team applicant" in blob:
        return _clamp_choice("2", count)

    if any(
        token in blob
        for token in (
            "board of directors",
            "confidence review",
            "defy the board",
        )
    ):
        return _clamp_choice("1", count)

    return _clamp_choice((count + 1) // 2, count)


def ai_pick_discipline(investigation=None, controversy=20):
    """Pick a 1-5 post-race ruling from the investigation packet."""

    investigation = investigation or {}
    if not investigation:
        return "2"

    confidence = str(investigation.get("confidence") or "").lower()
    blame = str(investigation.get("blame") or "").lower()
    contact = str(investigation.get("contact") or "").lower()
    severe = (
        "high" in confidence
        or "reckless" in blame
        or "intentional" in blame
        or "wreck" in contact
    )
    if severe:
        if controversy >= 40:
            return "4"
        return "3"
    if "low" in confidence:
        return "2"
    return "3"


def slim_season_record(record):
    """Keep the balance-report season row small."""

    record = record or {}
    approval = record.get("approval")
    security = record.get("job_security")
    return {
        "season": record.get("season"),
        "champion": record.get("champion"),
        "champion_team": record.get("champion_team"),
        "champion_points": record.get("champion_points"),
        "champion_wins": record.get("champion_wins"),
        "commissioner_score": record.get("commissioner_score"),
        "commissioner_grade": record.get("commissioner_grade"),
        "integrity": record.get("league_integrity"),
        "fan_interest": record.get("fan_interest"),
        "controversy": record.get("controversy"),
        "dismissed": bool(record.get("dismissed")),
        "approval": (
            approval.get("overall") if isinstance(approval, dict) else None
        ),
        "board_confidence": (
            security.get("confidence") if isinstance(security, dict) else None
        ),
    }


def collect_career_metrics(
    career_index,
    seasons_planned,
    career_history,
    league,
    teams,
    retired_drivers,
    driver_prospects,
    decision_log,
):
    """Snapshot one finished (or dismissed) AI career."""

    history = [slim_season_record(row) for row in (career_history or [])]
    closures = list(league.get("closure_history") or [])
    entries = list(league.get("entry_history") or [])
    switches = list(league.get("factory_history") or [])
    call_ups = list(league.get("promotion_history") or [])
    dismissed = bool(league.get("dismissed"))
    return {
        "career": career_index,
        "seasons_planned": seasons_planned,
        "seasons_completed": len(history),
        "finished": (not dismissed) and len(history) >= seasons_planned,
        "dismissed": dismissed,
        "dismissal": (
            dict(league.get("dismissal") or {}) if dismissed else None
        ),
        "champions": [row.get("champion") for row in history],
        "grades": [row.get("commissioner_grade") for row in history],
        "scores": [row.get("commissioner_score") for row in history],
        "final_integrity": league.get("integrity"),
        "final_fan_interest": league.get("fan_interest"),
        "final_controversy": league.get("controversy"),
        "final_owner_pressure": league.get("owner_pressure"),
        "final_driver_sentiment": league.get("driver_sentiment"),
        "final_treasury": league.get("treasury", 0),
        "team_count": len(list(teams or [])),
        "budgets": {team.name: team.budget for team in (teams or [])},
        "factory_badges": {
            team.name: team.manufacturer for team in (teams or [])
        },
        "closures": len(closures),
        "folded": sum(1 for row in closures if row.get("action") == "folded"),
        "bailed": sum(
            1 for row in closures if row.get("action") == "bailed out"
        ),
        "deferred": sum(
            1 for row in closures if row.get("action") == "deferred"
        ),
        "entries": len(entries),
        "admitted": sum(
            1 for row in entries if row.get("action") == "admitted"
        ),
        "entry_deferred": sum(
            1 for row in entries if row.get("action") == "deferred"
        ),
        "entry_denied": sum(
            1 for row in entries if row.get("action") == "denied"
        ),
        "factory_switches": len(switches),
        "call_ups": len(call_ups),
        "retirements": len(list(retired_drivers or [])),
        "prospects": len(list(driver_prospects or [])),
        "decisions": len(list(decision_log or [])),
        "seasons": history,
    }


def _mean(values):
    numbers = [value for value in values if isinstance(value, (int, float))]
    if not numbers:
        return None
    return round(sum(numbers) / float(len(numbers)), 1)


def _counts(values):
    tallies = {}
    for value in values:
        if value is None:
            continue
        key = str(value)
        tallies[key] = tallies.get(key, 0) + 1
    return dict(sorted(tallies.items(), key=lambda item: (-item[1], item[0])))


def summarize_report(careers, target_seasons, seasons_per_career, difficulty):
    """Roll career snapshots into one balance report."""

    careers = list(careers or [])
    seasons = []
    for career in careers:
        seasons.extend(career.get("seasons") or [])

    return {
        "target_seasons": target_seasons,
        "seasons_per_career": seasons_per_career,
        "difficulty": difficulty,
        "careers_started": len(careers),
        "careers_finished": sum(1 for row in careers if row.get("finished")),
        "careers_dismissed": sum(1 for row in careers if row.get("dismissed")),
        "seasons_completed": len(seasons),
        "champions": _counts(
            champion for row in careers for champion in (row.get("champions") or [])
        ),
        "grades": _counts(
            grade for row in careers for grade in (row.get("grades") or [])
        ),
        "avg_commissioner_score": _mean(
            score for row in careers for score in (row.get("scores") or [])
        ),
        "avg_integrity": _mean(
            row.get("final_integrity") for row in careers
        ),
        "avg_fan_interest": _mean(
            row.get("final_fan_interest") for row in careers
        ),
        "avg_controversy": _mean(
            row.get("final_controversy") for row in careers
        ),
        "avg_owner_pressure": _mean(
            row.get("final_owner_pressure") for row in careers
        ),
        "avg_driver_sentiment": _mean(
            row.get("final_driver_sentiment") for row in careers
        ),
        "avg_treasury": _mean(row.get("final_treasury") for row in careers),
        "avg_team_count": _mean(row.get("team_count") for row in careers),
        "closures": sum(row.get("closures") or 0 for row in careers),
        "folded": sum(row.get("folded") or 0 for row in careers),
        "bailed": sum(row.get("bailed") or 0 for row in careers),
        "deferred": sum(row.get("deferred") or 0 for row in careers),
        "entries": sum(row.get("entries") or 0 for row in careers),
        "admitted": sum(row.get("admitted") or 0 for row in careers),
        "entry_deferred": sum(
            row.get("entry_deferred") or 0 for row in careers
        ),
        "entry_denied": sum(row.get("entry_denied") or 0 for row in careers),
        "factory_switches": sum(
            row.get("factory_switches") or 0 for row in careers
        ),
        "call_ups": sum(row.get("call_ups") or 0 for row in careers),
        "retirements": sum(row.get("retirements") or 0 for row in careers),
        "decisions": sum(row.get("decisions") or 0 for row in careers),
        "careers": careers,
    }


def write_balance_report(report, project_root=None):
    """Write the balance report next to the season JSON dumps."""

    if project_root is None:
        project_root = Path(__file__).resolve().parent.parent.parent
    report_folder = Path(project_root) / "season_reports"
    report_folder.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    target = (report or {}).get("target_seasons") or "batch"
    report_path = report_folder / ("balance_%s_%s.json" % (target, timestamp))
    with report_path.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=4)
    return report_path
