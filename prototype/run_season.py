"""Run a prototype season and print race results plus standings."""

from __future__ import annotations

import argparse
import random
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from prototype.season_data import (
    Driver,
    Season,
    driver_team,
    points_for_finish,
    sample_season,
    track_by_id,
)


TRACK_WEIGHTS = {
    "Superspeedway": {"speed": 0.55, "consistency": 0.20, "aggression": 0.25},
    "Intermediate": {"speed": 0.45, "consistency": 0.35, "aggression": 0.20},
    "Short Track": {"speed": 0.25, "consistency": 0.40, "aggression": 0.35},
    "Road Course": {"speed": 0.20, "consistency": 0.55, "aggression": 0.25},
}


@dataclass
class RaceResult:
    round: int
    track_name: str
    track_type: str
    date: str
    finish_order: tuple[tuple[Driver, int, int], ...]


@dataclass
class Standing:
    driver: Driver
    points: int
    wins: int
    top_fives: int


def driver_race_score(driver: Driver, track_type: str, rng: random.Random) -> float:
    weights = TRACK_WEIGHTS.get(
        track_type,
        {"speed": 0.34, "consistency": 0.33, "aggression": 0.33},
    )
    base = (
        driver.speed * weights["speed"]
        + driver.consistency * weights["consistency"]
        + driver.aggression * weights["aggression"]
    )
    variance = rng.uniform(-8, 8) * (1 - driver.consistency / 100)
    return base + variance


def simulate_race(
    season: Season,
    *,
    round_number: int,
    track_id: str,
    date: str,
    rng: random.Random,
) -> RaceResult:
    track = track_by_id(season, track_id)
    scored_drivers = [
        (driver, driver_race_score(driver, track.track_type, rng))
        for driver in season.drivers
    ]
    scored_drivers.sort(key=lambda item: item[1], reverse=True)

    finish_order = tuple(
        (driver, position, points_for_finish(position))
        for position, (driver, _) in enumerate(scored_drivers, start=1)
    )
    return RaceResult(
        round=round_number,
        track_name=track.name,
        track_type=track.track_type,
        date=date,
        finish_order=finish_order,
    )


def build_standings(results: list[RaceResult]) -> list[Standing]:
    totals: dict[str, Standing] = {}

    for result in results:
        for driver, position, points in result.finish_order:
            if driver.id not in totals:
                totals[driver.id] = Standing(driver=driver, points=0, wins=0, top_fives=0)
            standing = totals[driver.id]
            standing.points += points
            if position == 1:
                standing.wins += 1
            if position <= 5:
                standing.top_fives += 1

    return sorted(
        totals.values(),
        key=lambda standing: (
            -standing.points,
            -standing.wins,
            -standing.top_fives,
            standing.driver.name,
        ),
    )


def format_driver_label(season: Season, driver: Driver) -> str:
    team = driver_team(season, driver)
    if team is None:
        return f"#{driver.number} {driver.name}"
    return f"#{driver.number} {driver.name} ({team.name})"


def print_race_result(season: Season, result: RaceResult) -> None:
    print(f"Race {result.round}: {result.track_name} ({result.track_type}) - {result.date}")
    for driver, position, points in result.finish_order:
        print(
            f"  {position:>2}. {format_driver_label(season, driver):<40} "
            f"{points:>2} pts"
        )
    print()


def print_standings(season: Season, standings: list[Standing]) -> None:
    print(f"{season.year} {season.series} Standings")
    if season.use_teams:
        print("Teams enabled")
    else:
        print("Independent drivers")
    print()

    for index, standing in enumerate(standings, start=1):
        print(
            f"{index:>2}. {format_driver_label(season, standing.driver):<40} "
            f"{standing.points:>3} pts  "
            f"W {standing.wins}  T5 {standing.top_fives}"
        )


def run_season(season: Season, *, seed: int = 42) -> list[RaceResult]:
    rng = random.Random(seed)
    results = [
        simulate_race(
            season,
            round_number=race.round,
            track_id=race.track_id,
            date=race.date,
            rng=rng,
        )
        for race in season.schedule
    ]

    print(f"Simulating {season.year} {season.series}\n")
    for result in results:
        print_race_result(season, result)

    print_standings(season, build_standings(results))
    return results


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a prototype stock car season.")
    parser.add_argument(
        "--no-teams",
        action="store_true",
        help="Run the season with independent drivers instead of teams.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for race simulation (default: 42).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    season = sample_season(use_teams=not args.no_teams)
    run_season(season, seed=args.seed)


if __name__ == "__main__":
    main()
