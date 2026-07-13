"""Sample season data for early prototyping."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Driver:
    id: str
    name: str
    number: int
    speed: int
    consistency: int
    aggression: int
    team_id: str | None = None


@dataclass(frozen=True)
class Team:
    id: str
    name: str
    manufacturer: str


@dataclass(frozen=True)
class Track:
    id: str
    name: str
    track_type: str


@dataclass(frozen=True)
class Race:
    round: int
    track_id: str
    date: str


@dataclass(frozen=True)
class Season:
    year: int
    series: str
    use_teams: bool
    teams: tuple[Team, ...]
    drivers: tuple[Driver, ...]
    tracks: tuple[Track, ...]
    schedule: tuple[Race, ...]


POINTS_BY_FINISH = (
    40, 35, 34, 33, 32, 31, 30, 29, 28, 27,
    26, 25, 24, 23, 22, 21, 20, 19, 18, 17,
    16, 15, 14, 13, 12, 11, 10, 9, 8, 7,
    6, 5, 4, 3, 2, 1,
)

DRIVER_DATA = [
    {"name": "Cole Baker", "speed": 84, "consistency": 78, "aggression": 62},
    {"name": "Ryan Holt", "speed": 76, "consistency": 88, "aggression": 55},
    {"name": "Mason Reed", "speed": 91, "consistency": 69, "aggression": 81},
    {"name": "Tyler Knox", "speed": 73, "consistency": 82, "aggression": 70},
    {"name": "Derek Lane", "speed": 88, "consistency": 74, "aggression": 77},
    {"name": "Austin Vale", "speed": 80, "consistency": 80, "aggression": 60},
]

TRACK_DATA = [
    {"name": "Atlantic Speedway", "type": "Superspeedway"},
    {"name": "Carolina Motor Speedway", "type": "Intermediate"},
    {"name": "Thunder Valley", "type": "Superspeedway"},
    {"name": "Pine Ridge Raceway", "type": "Short Track"},
    {"name": "Lone Star Circuit", "type": "Road Course"},
]

TEAMS = (
    Team("t1", "Redline Racing", "Ford"),
    Team("t2", "Summit Motorsports", "Chevrolet"),
    Team("t3", "Coastal Performance", "Toyota"),
)

DRIVER_NUMBERS = (12, 24, 7, 33, 88, 19)
DRIVER_TEAM_IDS = ("t1", "t1", "t2", "t2", "t3", "t3")
TRACK_IDS = (
    "atlantic-speedway",
    "carolina-motor-speedway",
    "thunder-valley",
    "pine-ridge-raceway",
    "lone-star-circuit",
)
SCHEDULE_DATES = (
    "2026-02-15",
    "2026-04-06",
    "2026-05-18",
    "2026-08-22",
    "2026-10-11",
)


def _driver_id(name: str) -> str:
    return name.lower().replace(" ", "-")


def build_drivers(use_teams: bool) -> tuple[Driver, ...]:
    drivers = []
    for index, data in enumerate(DRIVER_DATA):
        team_id = DRIVER_TEAM_IDS[index] if use_teams else None
        drivers.append(
            Driver(
                id=_driver_id(data["name"]),
                name=data["name"],
                number=DRIVER_NUMBERS[index],
                speed=data["speed"],
                consistency=data["consistency"],
                aggression=data["aggression"],
                team_id=team_id,
            )
        )
    return tuple(drivers)


def build_tracks() -> tuple[Track, ...]:
    return tuple(
        Track(
            id=TRACK_IDS[index],
            name=data["name"],
            track_type=data["type"],
        )
        for index, data in enumerate(TRACK_DATA)
    )


def build_schedule() -> tuple[Race, ...]:
    return tuple(
        Race(round=index + 1, track_id=TRACK_IDS[index], date=SCHEDULE_DATES[index])
        for index in range(len(TRACK_DATA))
    )


TRACKS = build_tracks()
SCHEDULE = build_schedule()


def sample_season(use_teams: bool = True) -> Season:
    return Season(
        year=2026,
        series="Stock Car Series",
        use_teams=use_teams,
        teams=TEAMS if use_teams else (),
        drivers=build_drivers(use_teams),
        tracks=TRACKS,
        schedule=SCHEDULE,
    )


SAMPLE_SEASON = sample_season(use_teams=True)
SAMPLE_SEASON_NO_TEAMS = sample_season(use_teams=False)


def points_for_finish(position: int) -> int:
    if position < 1 or position > len(POINTS_BY_FINISH):
        return 0
    return POINTS_BY_FINISH[position - 1]


def driver_by_id(season: Season, driver_id: str) -> Driver:
    return next(driver for driver in season.drivers if driver.id == driver_id)


def team_by_id(season: Season, team_id: str) -> Team:
    return next(team for team in season.teams if team.id == team_id)


def track_by_id(season: Season, track_id: str) -> Track:
    return next(track for track in season.tracks if track.id == track_id)


def driver_team(season: Season, driver: Driver) -> Team | None:
    if not season.use_teams or driver.team_id is None:
        return None
    return team_by_id(season, driver.team_id)
