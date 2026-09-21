"""Deterministic V2 race fixtures used by the watchable viewer."""

from __future__ import annotations

from game.race_playback import content_hash
from game.track_layouts import layout_for_track


RACE_CONTRACT_VERSION = "scc-race-v1"
ENGINE_VERSION = "fixture-v1"
RNG_PROVIDER_VERSION = "scripted-v1"
RIVERSIDE_RACE_ID = "race_riverside_200_s1r1"
RIVERSIDE_40_RACE_ID = "race_riverside_200_40_s1r1"
RIVERSIDE_TRACK_ID = "trk_riverside_short"
CAREER_ID = "career_fixture_v2"
SEASON_ID = "season_fixture_1984"

NAMED_ROLES = (
    {
        "role": "pace",
        "entry_id": "entry_pace",
        "driver_id": "drv_cole_hart",
        "team_id": "team_hart",
        "manufacturer_id": "mfr_apex",
        "body_id": "generic_coupe",
        "car_number": "3",
        "driver_name": "Cole Hart",
        "team_name": "Hart Racing",
        "primary_color": "f5c400",
        "secondary_color": "101010",
        "qualifying_ms": 16120,
    },
    {
        "role": "restart",
        "entry_id": "entry_restart",
        "driver_id": "drv_ray_dunham",
        "team_id": "team_dunham",
        "manufacturer_id": "mfr_summit",
        "body_id": "generic_coupe",
        "car_number": "21",
        "driver_name": "Ray Dunham",
        "team_name": "Dunham Motor Co.",
        "primary_color": "c4122e",
        "secondary_color": "f4f4f4",
        "qualifying_ms": 16180,
    },
    {
        "role": "engine",
        "entry_id": "entry_engine",
        "driver_id": "drv_bud_keene",
        "team_id": "team_keene",
        "manufacturer_id": "mfr_apex",
        "body_id": "generic_coupe",
        "car_number": "7",
        "driver_name": "Bud Keene",
        "team_name": "Keene Garage",
        "primary_color": "1f4e8c",
        "secondary_color": "f4f4f4",
        "qualifying_ms": 16240,
    },
    {
        "role": "agg_a",
        "entry_id": "entry_agg_a",
        "driver_id": "drv_lane_vickers",
        "team_id": "team_vickers",
        "manufacturer_id": "mfr_ridge",
        "body_id": "generic_coupe",
        "car_number": "18",
        "driver_name": "Lane Vickers",
        "team_name": "Vickers Racing",
        "primary_color": "0a7a32",
        "secondary_color": "f5c400",
        "qualifying_ms": 16310,
    },
    {
        "role": "agg_b",
        "entry_id": "entry_agg_b",
        "driver_id": "drv_tex_moran",
        "team_id": "team_moran",
        "manufacturer_id": "mfr_summit",
        "body_id": "generic_coupe",
        "car_number": "88",
        "driver_name": "Tex Moran",
        "team_name": "Moran Speed",
        "primary_color": "7a1f8c",
        "secondary_color": "f4f4f4",
        "qualifying_ms": 16370,
    },
    {
        "role": "pit_early",
        "entry_id": "entry_pit_early",
        "driver_id": "drv_cal_brooks",
        "team_id": "team_brooks",
        "manufacturer_id": "mfr_ridge",
        "body_id": "generic_coupe",
        "car_number": "12",
        "driver_name": "Cal Brooks",
        "team_name": "Brooks & Son",
        "primary_color": "d46500",
        "secondary_color": "101010",
        "qualifying_ms": 16440,
    },
    {
        "role": "pit_late",
        "entry_id": "entry_pit_late",
        "driver_id": "drv_ned_parrish",
        "team_id": "team_parrish",
        "manufacturer_id": "mfr_apex",
        "body_id": "generic_coupe",
        "car_number": "43",
        "driver_name": "Ned Parrish",
        "team_name": "Parrish Motors",
        "primary_color": "3d5a80",
        "secondary_color": "f5c400",
        "qualifying_ms": 16500,
    },
    {
        "role": "steady",
        "entry_id": "entry_steady",
        "driver_id": "drv_wally_pike",
        "team_id": "team_pike",
        "manufacturer_id": "mfr_ridge",
        "body_id": "generic_coupe",
        "car_number": "9",
        "driver_name": "Wally Pike",
        "team_name": "Pike Racing",
        "primary_color": "5c4033",
        "secondary_color": "f4f4f4",
        "qualifying_ms": 16580,
    },
)

EXTRA_COLORS = (
    ("2a6f97", "f4f4f4"),
    ("8c2f13", "f5c400"),
    ("2f3d2c", "f4f4f4"),
    ("6b4c7a", "101010"),
    ("114b5f", "f5c400"),
    ("8a1414", "f4f4f4"),
    ("3f4b3b", "f5c400"),
    ("1b1b3a", "f4f4f4"),
)


def riverside_track():
    """Return the 800 m short-track snapshot used by the acceptance fixture."""

    racing = (
        ("START_FINISH", 80_000),
        ("CORNER", 140_000),
        ("STRAIGHT", 220_000),
        ("CORNER", 140_000),
        ("STRAIGHT", 220_000),
    )
    segments = []
    for index, (kind, length) in enumerate(racing):
        segments.append(
            {
                "contact_factor": 42 if kind == "CORNER" else 18,
                "kind": kind,
                "lane_count": 2,
                "length_mm": length,
                "passing_factor": 55 if kind == "STRAIGHT" else 38,
                "path": "RACING",
                "segment_index": index,
            }
        )
    segments.extend(
        [
            {
                "contact_factor": 8,
                "joins_racing_segment_index": 4,
                "kind": "PIT_ENTRY",
                "lane_count": 1,
                "length_mm": 40_000,
                "passing_factor": 5,
                "path": "PIT",
                "pit_speed_limit_mms": 22_000,
                "segment_index": 5,
            },
            {
                "contact_factor": 4,
                "kind": "PIT_LANE",
                "lane_count": 1,
                "length_mm": 90_000,
                "passing_factor": 0,
                "path": "PIT",
                "pit_speed_limit_mms": 22_000,
                "segment_index": 6,
            },
            {
                "contact_factor": 8,
                "joins_racing_segment_index": 0,
                "kind": "PIT_EXIT",
                "lane_count": 1,
                "length_mm": 40_000,
                "passing_factor": 8,
                "path": "PIT",
                "pit_speed_limit_mms": 22_000,
                "segment_index": 7,
            },
        ]
    )
    return {
        "banking_degrees": 12,
        "baseline_grip_bp": 7800,
        "caution_laps": 3,
        "fuel_stress": 48,
        "incident_risk": 36,
        "lap_length_m": 800,
        "name": "Riverside Motor Speedway",
        "passing_difficulty": 58,
        "pit_lane_loss_ms": 24000,
        "restart_zone_end_segment": 0,
        "restart_zone_start_segment": 4,
        "scheduled_laps": 20,
        "segments": segments,
        "surface": "ASPHALT",
        "tire_stress": 72,
        "track_id": RIVERSIDE_TRACK_ID,
        "track_type": "SHORT",
    }


def _extra_entrants(count):
    extras = []
    for index in range(count):
        number = 50 + index
        color, secondary = EXTRA_COLORS[index % len(EXTRA_COLORS)]
        extras.append(
            {
                "role": "extra_%02d" % (index + 1),
                "entry_id": "entry_extra_%02d" % (index + 1),
                "driver_id": "drv_extra_%02d" % (index + 1),
                "team_id": "team_extra_%02d" % (index + 1),
                "manufacturer_id": ("mfr_apex", "mfr_summit", "mfr_ridge")[index % 3],
                "body_id": "generic_coupe",
                "car_number": str(number),
                "driver_name": "Field Car %s" % number,
                "team_name": "Independent %s" % number,
                "primary_color": color,
                "secondary_color": secondary,
                "qualifying_ms": 16640 + index * 35,
            }
        )
    return extras


def _entrant_snapshot(spec, index):
    return {
        "body_id": spec["body_id"],
        "car": {
            "aero_rating": 72,
            "chassis_rating": 70,
            "engine_reliability": 38 if spec["role"] == "engine" else 74,
            "horsepower_rating": 78 if spec["role"] == "pace" else 70,
            "short_track_rating": 76,
        },
        "car_number": spec["car_number"],
        "crew": {
            "over_the_wall": 71,
            "pit_strategy": 80 if spec["role"].startswith("pit") else 66,
            "spotting": 68,
        },
        "driver": {
            "aggression": 88 if spec["role"].startswith("agg") else 54,
            "qualifying_pace": 92 if spec["role"] == "pace" else 64,
            "race_craft": 74,
            "restart_skill": 94 if spec["role"] == "restart" else 60,
            "short_track_rating": 77,
        },
        "driver_id": spec["driver_id"],
        "driver_name": spec["driver_name"],
        "entry_id": spec["entry_id"],
        "fuel_capacity_ml": 68_000,
        "manufacturer_id": spec["manufacturer_id"],
        "package": {
            "body_id": spec["body_id"],
            "era_book": "pinnacle",
            "rules_version": "fixture-1984",
        },
        "penalties": [],
        "primary_color": spec["primary_color"],
        "secondary_color": spec["secondary_color"],
        "sprite_id": "stock_car_topdown",
        "starting_fuel_ml": 68_000,
        "strategy": {
            "aggression": 80 if spec["role"].startswith("agg") else 50,
            "pit_window_preference": spec["role"],
            "restart_aggression": 90 if spec["role"] == "restart" else 50,
        },
        "team_id": spec["team_id"],
        "team_name": spec["team_name"],
    }


def _rules(field_limit):
    return {
        "caution_laps_count": True,
        "field_limit": field_limit,
        "finish_under_caution": False,
        "heat_count": 0,
        "heat_laps": 0,
        "heat_transfer_count": 0,
        "maximum_overtime_attempts": 1,
        "minimum_fuel_reserve_ml": 1500,
        "overtime_enabled": False,
        "overtime_laps_per_attempt": 2,
        "pit_penalty_policy": "DRIVE_THROUGH",
        "pit_road_speed_limit_mms": 22_000,
        "qualifying_format": "SINGLE_CAR",
        "race_format": "SINGLE_FEATURE",
        "restart_lane_rule": "DOUBLE_FILE",
        "rules_version": "fixture-1984",
        "safety_level": 62,
        "stage_end_laps": [],
        "technical_package": {
            "aero_level": 40,
            "engine_package": "carbureted-v8",
            "spoiler_code": "standard",
        },
        "tire_sets_available": 4,
    }


def build_riverside_input(field_size=8):
    """Return the immutable RaceInput for a Riverside 200 fixture."""

    if field_size < 8:
        raise ValueError("Riverside fixture needs at least the eight named cars")
    specs = list(NAMED_ROLES) + _extra_entrants(field_size - 8)
    race_id = RIVERSIDE_RACE_ID if field_size == 8 else RIVERSIDE_40_RACE_ID
    if field_size not in (8, 40):
        race_id = "race_riverside_%s_s1r1" % field_size
    track = riverside_track()
    payload = {
        "career_id": CAREER_ID,
        "conditions": {
            "alternatives": [
                {
                    "grip_delta_bp": -600,
                    "temperature_c": 24,
                    "weather": "CLOUDY",
                    "window_end_lap": 20,
                    "window_start_lap": 16,
                }
            ],
            "starting": {
                "grip_bp": 7800,
                "temperature_c": 28,
                "weather": "CLEAR",
            },
        },
        "contract_version": RACE_CONTRACT_VERSION,
        "entrants": [_entrant_snapshot(spec, index) for index, spec in enumerate(specs)],
        "race_id": race_id,
        "race_number": 1,
        "rules": _rules(field_size),
        "season_id": SEASON_ID,
        "season_number": 1,
        "seed": 19840219,
        "track": track,
    }
    return payload, specs


class _EventWriter:
    def __init__(self, race_id):
        self.race_id = race_id
        self.seq = 0
        self.events = []

    def add(
        self,
        kind,
        sim_time_ms,
        phase,
        session_kind="FEATURE",
        session_index=0,
        session_lap=0,
        race_lap=None,
        location=None,
        entry_ids=None,
        payload=None,
    ):
        self.seq += 1
        event = {
            "entry_ids": list(entry_ids or []),
            "event_id": "%s:%s" % (self.race_id, self.seq),
            "kind": kind,
            "location": location,
            "payload": payload or {},
            "phase": phase,
            "race_id": self.race_id,
            "race_lap": race_lap,
            "schema_version": 1,
            "seq": self.seq,
            "session_index": session_index,
            "session_kind": session_kind,
            "session_lap": session_lap,
            "sim_time_ms": int(sim_time_ms),
        }
        self.events.append(event)
        return event


def _sf_location(lane=0):
    return {"lane_index": int(lane), "progress_mm": 0, "segment_index": 0}


def _mid_location(segment_index, progress_mm, lane=0):
    return {
        "lane_index": int(lane),
        "progress_mm": int(progress_mm),
        "segment_index": int(segment_index),
    }


def _pit_location(segment_index, progress_mm=0):
    return {
        "lane_index": 0,
        "progress_mm": int(progress_mm),
        "segment_index": int(segment_index),
    }


def _move_to_back(order, entry_id):
    next_order = [item for item in order if item != entry_id]
    next_order.append(entry_id)
    return next_order


def _swap_up(order, entry_id):
    if entry_id not in order:
        return order
    index = order.index(entry_id)
    if index == 0:
        return list(order)
    next_order = list(order)
    next_order[index - 1], next_order[index] = next_order[index], next_order[index - 1]
    return next_order


def _gaps(order, lap_ms):
    rows = []
    for index, entry_id in enumerate(order):
        rows.append([entry_id, None if index == 0 else index * max(180, lap_ms // 80)])
    return rows


def _laps_map(order, laps_by_entry):
    return [[entry_id, int(laps_by_entry.get(entry_id, 0))] for entry_id in order]


def build_riverside_result(race_input, specs, scheduled_laps=None):
    """Script the Riverside 200 event story as a deterministic RaceResult."""

    race_id = race_input["race_id"]
    writer = _EventWriter(race_id)
    specs_by_id = {row["entry_id"]: row for row in specs}
    grid_ids = [row["entry_id"] for row in specs]
    laps = int(scheduled_laps or race_input["track"]["scheduled_laps"])
    base_lap_ms = 16000
    time_ms = 0

    writer.add(
        "QualifyingStarted",
        time_ms,
        "QUALIFYING",
        session_kind="QUALIFYING",
        payload={"format": "SINGLE_CAR", "entry_ids": list(grid_ids)},
        entry_ids=list(grid_ids),
    )
    for index, spec in enumerate(specs):
        time_ms += 2500
        writer.add(
            "QualifyingLapCompleted",
            time_ms,
            "QUALIFYING",
            session_kind="QUALIFYING",
            location=_sf_location(0),
            entry_ids=[spec["entry_id"]],
            payload={
                "elapsed_ms": spec["qualifying_ms"],
                "entry_id": spec["entry_id"],
                "valid": True,
            },
        )
    time_ms += 1000
    grid = [
        {
            "entry_id": spec["entry_id"],
            "penalty_positions": 0,
            "position": index + 1,
            "qualifying_time_ms": spec["qualifying_ms"],
            "raw_qualifying_position": index + 1,
        }
        for index, spec in enumerate(specs)
    ]
    writer.add(
        "GridSet",
        time_ms,
        "QUALIFYING",
        session_kind="QUALIFYING",
        payload={"grid": grid, "session_kind": "FEATURE"},
        entry_ids=list(grid_ids),
    )
    writer.add(
        "FeatureGridSet",
        time_ms + 200,
        "FORMATION",
        payload={"grid": grid, "provenance": "SINGLE_CAR_QUALIFYING"},
        entry_ids=list(grid_ids),
    )
    time_ms = 80_000
    writer.add(
        "RaceStarted",
        time_ms,
        "GREEN",
        race_lap=0,
        location=_sf_location(0),
        payload={"starting_order": list(grid_ids)},
        entry_ids=list(grid_ids),
    )

    order = list(grid_ids)
    laps_by_entry = {entry_id: 0 for entry_id in grid_ids}
    fuel = {entry_id: 68_000 for entry_id in grid_ids}
    tires = {entry_id: 0 for entry_id in grid_ids}
    status = {entry_id: "RUNNING" for entry_id in grid_ids}
    pit_stops = {entry_id: 0 for entry_id in grid_ids}
    lead_changes = 0
    leader = order[0]
    laps_led = {entry_id: 0 for entry_id in grid_ids}
    caution_count = 0
    retired = set()
    finish_seq = {}
    green_passes = 0
    current_weather = "CLEAR"

    def running_ids():
        return [entry_id for entry_id in order if entry_id not in retired]

    def emit_running_order(sim_time, race_lap, phase):
        live = running_ids()
        writer.add(
            "RunningOrderRecorded",
            sim_time,
            phase,
            race_lap=race_lap,
            session_lap=race_lap,
            location=_sf_location(0),
            payload={
                "gaps_ms": _gaps(live, base_lap_ms),
                "laps_completed_by_entry": _laps_map(order, laps_by_entry),
                "leader_entry_id": live[0] if live else "",
                "race_lap": race_lap,
                "running_order": list(live),
            },
            entry_ids=list(live),
        )

    def emit_lap(entry_id, sim_time, race_lap, phase, lap_time):
        laps_by_entry[entry_id] += 1
        fuel[entry_id] = max(4_000, fuel[entry_id] - 2_400)
        tires[entry_id] = min(10_000, tires[entry_id] + 380)
        live = running_ids()
        position = live.index(entry_id) + 1 if entry_id in live else len(live)
        writer.add(
            "LapCompleted",
            sim_time,
            phase,
            race_lap=race_lap,
            session_lap=race_lap,
            location=_sf_location((position - 1) % 2),
            entry_ids=[entry_id],
            payload={
                "completed_lap": laps_by_entry[entry_id],
                "entry_id": entry_id,
                "fuel_ml": fuel[entry_id],
                "lap_time_ms": lap_time,
                "running_position": position,
                "tire_wear_bp": tires[entry_id],
            },
        )

    def emit_pass(sim_time, race_lap, passing, passed, phase="GREEN"):
        nonlocal green_passes, lead_changes, leader
        old_order = list(order)
        if passing not in order or passed not in order:
            return
        if order.index(passing) >= order.index(passed):
            order[:] = _swap_up(order, passing)
        new_pos = running_ids().index(passing) + 1
        old_pos = old_order.index(passing) + 1
        writer.add(
            "PassCompleted",
            sim_time,
            phase,
            race_lap=race_lap,
            session_lap=race_lap,
            location=_mid_location(2, 80_000, 1),
            entry_ids=[passing, passed],
            payload={
                "new_position": new_pos,
                "old_position": old_pos,
                "passed_entry_id": passed,
                "passing_entry_id": passing,
            },
        )
        green_passes += 1
        live = running_ids()
        if live and live[0] != leader:
            previous = leader
            leader = live[0]
            lead_changes += 1
            writer.add(
                "LeadChanged",
                sim_time + 20,
                phase,
                race_lap=race_lap,
                session_lap=race_lap,
                location=_mid_location(2, 90_000, 0),
                entry_ids=[leader, previous],
                payload={"new_leader": leader, "previous_leader": previous},
            )

    def emit_pit(sim_time, race_lap, entry_id, reason):
        live_before = running_ids()
        position = live_before.index(entry_id) + 1 if entry_id in live_before else 0
        writer.add(
            "PitStopPlanned",
            sim_time,
            "GREEN",
            race_lap=race_lap,
            session_lap=race_lap,
            entry_ids=[entry_id],
            payload={
                "entry_id": entry_id,
                "reason_code": reason,
                "requested_fuel_ml": 28_000,
                "requested_tires": 4,
            },
        )
        writer.add(
            "PitRoadEntered",
            sim_time + 400,
            "GREEN",
            race_lap=race_lap,
            session_lap=race_lap,
            location=_pit_location(5, 8_000),
            entry_ids=[entry_id],
            payload={
                "entry_id": entry_id,
                "fuel_ml": fuel[entry_id],
                "running_position": position,
                "tire_wear_bp": tires[entry_id],
            },
        )
        fuel[entry_id] = min(68_000, fuel[entry_id] + 28_000)
        tires[entry_id] = 0
        pit_stops[entry_id] += 1
        writer.add(
            "PitServiceCompleted",
            sim_time + 3_200,
            "GREEN",
            race_lap=race_lap,
            session_lap=race_lap,
            location=_pit_location(6, 40_000),
            entry_ids=[entry_id],
            payload={
                "entry_id": entry_id,
                "fuel_added_ml": 28_000,
                "resulting_fuel_ml": fuel[entry_id],
                "resulting_tire_wear_bp": 0,
                "service_time_ms": 2_800,
                "tires_changed": 4,
            },
        )
        order[:] = _move_to_back(order, entry_id)
        live_after = running_ids()
        writer.add(
            "PitRoadExited",
            sim_time + 6_400,
            "GREEN",
            race_lap=race_lap,
            session_lap=race_lap,
            location=_pit_location(7, 30_000),
            entry_ids=[entry_id],
            payload={
                "entry_id": entry_id,
                "running_position": live_after.index(entry_id) + 1,
                "total_pit_lane_time_ms": 6_000,
            },
        )

    pit_early_lap = 7
    main_pit_lap = 11
    late_pit_lap = 12
    caution_lap = min(13, laps - 4) if laps >= 8 else max(3, laps - 1)
    restart_lap = min(caution_lap + 3, laps - 2) if laps >= 8 else laps
    condition_lap = min(17, laps - 1) if laps >= 8 else laps

    for race_lap in range(1, laps + 1):
        phase = "GREEN"
        lap_time = base_lap_ms + (80 if race_lap > 10 else 0)
        if caution_lap <= race_lap < restart_lap:
            phase = "CAUTION"
            lap_time = 22_000

        if race_lap == 3 and "entry_restart" in order:
            emit_pass(time_ms + 4_800, race_lap, "entry_restart", "entry_pace")
        if race_lap == 5 and "entry_agg_a" in order and "entry_engine" in order:
            emit_pass(time_ms + 6_200, race_lap, "entry_agg_a", "entry_engine")

        if race_lap == pit_early_lap:
            for entry_id in ("entry_pit_early", "entry_engine"):
                if entry_id in running_ids():
                    emit_pit(time_ms + 1_200, race_lap, entry_id, "TIRES")

        if race_lap == 8 and "entry_engine" not in retired:
            writer.add(
                "MechanicalProblemDetected",
                time_ms + 7_000,
                "GREEN",
                race_lap=race_lap,
                session_lap=race_lap,
                location=_mid_location(1, 40_000, 0),
                entry_ids=["entry_engine"],
                payload={
                    "component_code": "ENGINE",
                    "entry_id": "entry_engine",
                    "severity": 40,
                },
            )

        if race_lap == 9 and "entry_engine" not in retired:
            writer.add(
                "MechanicalProblemWorsened",
                time_ms + 3_000,
                "GREEN",
                race_lap=race_lap,
                session_lap=race_lap,
                location=_mid_location(3, 20_000, 0),
                entry_ids=["entry_engine"],
                payload={
                    "component_code": "ENGINE",
                    "entry_id": "entry_engine",
                    "new_severity": 95,
                    "old_severity": 40,
                },
            )
            writer.add(
                "EntryRetired",
                time_ms + 3_400,
                "GREEN",
                race_lap=race_lap,
                session_lap=race_lap,
                location=_mid_location(3, 30_000, 0),
                entry_ids=["entry_engine"],
                payload={
                    "entry_id": "entry_engine",
                    "laps_completed": laps_by_entry["entry_engine"],
                    "reason_code": "ENGINE",
                },
            )
            status["entry_engine"] = "MECHANICAL"
            retired.add("entry_engine")
            order[:] = [entry_id for entry_id in order if entry_id != "entry_engine"] + [
                "entry_engine"
            ]

        if race_lap == main_pit_lap:
            cycle = [
                entry_id
                for entry_id in running_ids()
                if entry_id not in {"entry_pit_early", "entry_pit_late"}
            ]
            for offset, entry_id in enumerate(cycle):
                emit_pit(time_ms + 800 + offset * 180, race_lap, entry_id, "TIRES")

        if race_lap == late_pit_lap and "entry_pit_late" in running_ids():
            emit_pit(time_ms + 1_000, race_lap, "entry_pit_late", "TIRES")

        if race_lap == caution_lap and "entry_agg_a" in running_ids() and "entry_agg_b" in running_ids():
            caution_count += 1
            caution_id = "caution_riverside_1"
            contact_time = time_ms + 5_500
            writer.add(
                "ContactOccurred",
                contact_time,
                "GREEN",
                race_lap=race_lap,
                session_lap=race_lap,
                location=_mid_location(1, 70_000, 1),
                entry_ids=["entry_agg_a", "entry_agg_b"],
                payload={
                    "incident_id": "inc_riverside_1",
                    "involved_entry_ids": ["entry_agg_a", "entry_agg_b"],
                    "severity": 62,
                },
            )
            writer.add(
                "CautionCalled",
                contact_time + 200,
                "CAUTION",
                race_lap=race_lap,
                session_lap=race_lap,
                location=_mid_location(1, 72_000, 0),
                entry_ids=["entry_agg_a", "entry_agg_b"],
                payload={
                    "caution_id": caution_id,
                    "reason_code": "CONTACT",
                    "triggering_event_seq": writer.seq,
                },
            )
            live = running_ids()
            writer.add(
                "FieldFrozen",
                contact_time + 400,
                "CAUTION",
                race_lap=race_lap,
                session_lap=race_lap,
                payload={"caution_id": caution_id, "running_order": list(live)},
                entry_ids=list(live),
            )
            phase = "CAUTION"

        if race_lap == restart_lap - 1 and caution_count:
            live = running_ids()
            writer.add(
                "CleanupCompleted",
                time_ms + 10_000,
                "CAUTION",
                race_lap=race_lap,
                session_lap=race_lap,
                payload={"caution_id": "caution_riverside_1", "elapsed_caution_laps": 2},
                entry_ids=list(live),
            )
            writer.add(
                "RestartOrderSet",
                time_ms + 11_000,
                "RESTART",
                race_lap=race_lap,
                session_lap=race_lap,
                payload={
                    "caution_id": "caution_riverside_1",
                    "restart_lap": restart_lap,
                    "running_order": list(live),
                },
                entry_ids=list(live),
            )

        if race_lap == restart_lap and caution_count:
            if "entry_restart" in running_ids():
                before = list(running_ids())
                order[:] = _swap_up(order, "entry_restart")
                after = running_ids()
                if after and after[0] != leader:
                    previous = leader
                    leader = after[0]
                    lead_changes += 1
                    writer.add(
                        "LeadChanged",
                        time_ms + 600,
                        "RESTART",
                        race_lap=race_lap,
                        session_lap=race_lap,
                        location=_sf_location(0),
                        entry_ids=[leader, previous],
                        payload={"new_leader": leader, "previous_leader": previous},
                    )
                if before != after and len(after) > 1:
                    writer.add(
                        "PassCompleted",
                        time_ms + 580,
                        "RESTART",
                        race_lap=race_lap,
                        session_lap=race_lap,
                        location=_sf_location(1),
                        entry_ids=["entry_restart", before[0]],
                        payload={
                            "new_position": after.index("entry_restart") + 1,
                            "old_position": before.index("entry_restart") + 1,
                            "passed_entry_id": before[0],
                            "passing_entry_id": "entry_restart",
                        },
                    )
            live = running_ids()
            writer.add(
                "RaceRestarted",
                time_ms + 200,
                "GREEN",
                race_lap=race_lap,
                session_lap=race_lap,
                location=_sf_location(0),
                payload={
                    "caution_id": "caution_riverside_1",
                    "restart_lap": restart_lap,
                    "running_order": list(live),
                },
                entry_ids=list(live),
            )
            phase = "GREEN"

        if race_lap == condition_lap:
            writer.add(
                "ConditionChanged",
                time_ms + 2_000,
                phase,
                race_lap=race_lap,
                session_lap=race_lap,
                payload={
                    "new_grip_bp": 7200,
                    "new_temperature_c": 24,
                    "new_weather": "CLOUDY",
                    "old_grip_bp": 7800,
                    "old_temperature_c": 28,
                    "old_weather": current_weather,
                },
            )
            current_weather = "CLOUDY"

        live = running_ids()
        if live:
            laps_led[live[0]] += 1
        for offset, entry_id in enumerate(live):
            car_time = time_ms + lap_time + offset * 220
            emit_lap(entry_id, car_time, race_lap, phase, lap_time + offset * 220)
        time_ms += lap_time + max(0, len(live) - 1) * 220
        emit_running_order(time_ms, race_lap, phase)

    finish_time = time_ms + 80
    live = running_ids()
    crossing_order = []
    for index, entry_id in enumerate(live):
        crossing_time = finish_time + index * 180
        event = writer.add(
            "FinishLineCrossed",
            crossing_time,
            "FINISHED",
            race_lap=laps,
            session_lap=laps,
            location=_sf_location(index % 2),
            entry_ids=[entry_id],
            payload={
                "completed_laps": laps_by_entry[entry_id],
                "crossing_order": index + 1,
                "elapsed_ms": crossing_time - 80_000,
                "entry_id": entry_id,
            },
        )
        finish_seq[entry_id] = event["seq"]
        crossing_order.append(entry_id)
        status[entry_id] = "FINISHED"
    end_time = finish_time + max(1, len(live)) * 180
    writer.add(
        "RaceFinished",
        end_time,
        "FINISHED",
        race_lap=laps,
        session_lap=laps,
        payload={
            "finish_crossing_order": crossing_order,
            "overtime": False,
            "scheduled_laps": laps,
        },
        entry_ids=list(crossing_order),
    )

    classification = []
    classified = list(crossing_order) + [entry_id for entry_id in grid_ids if entry_id in retired]
    for index, entry_id in enumerate(classified):
        row_status = status[entry_id]
        classification.append(
            {
                "elapsed_ms": end_time - 80_000 if row_status == "FINISHED" else None,
                "entry_id": entry_id,
                "finish_crossing_event_seq": finish_seq.get(entry_id),
                "gap_ms": None if index == 0 else index * 180,
                "laps_completed": laps_by_entry[entry_id],
                "laps_down": max(0, laps - laps_by_entry[entry_id]),
                "position": index + 1,
                "retirement_event_seq": None
                if row_status == "FINISHED"
                else next(
                    (
                        event["seq"]
                        for event in writer.events
                        if event["kind"] == "EntryRetired"
                        and entry_id in event["entry_ids"]
                    ),
                    None,
                ),
                "status": row_status,
            }
        )

    summaries = []
    for spec in specs:
        entry_id = spec["entry_id"]
        start = grid_ids.index(entry_id) + 1
        finish = next(
            row["position"] for row in classification if row["entry_id"] == entry_id
        )
        summaries.append(
            {
                "average_running_position": start,
                "cautions_involved": 1
                if entry_id in {"entry_agg_a", "entry_agg_b"}
                else 0,
                "contact_count": 1 if entry_id in {"entry_agg_a", "entry_agg_b"} else 0,
                "failed_component": "ENGINE" if entry_id == "entry_engine" else None,
                "fastest_lap_ms": base_lap_ms + start * 40,
                "finish": finish,
                "fuel_added_ml": 28_000 * pit_stops[entry_id],
                "green_flag_passes": 1 if entry_id == "entry_restart" else 0,
                "incident_responsibility_state": "UNRESOLVED"
                if entry_id in {"entry_agg_a", "entry_agg_b"}
                else "NONE",
                "laps_completed": laps_by_entry[entry_id],
                "laps_led": laps_led.get(entry_id, 0),
                "lead_changes_participated": 1 if laps_led.get(entry_id, 0) else 0,
                "pit_stops": pit_stops[entry_id],
                "positions_gained": start - finish,
                "start": start,
                "status": status[entry_id],
                "tire_sets_used": 1 + pit_stops[entry_id],
            }
        )

    review_packets = []
    contact = next(event for event in writer.events if event["kind"] == "ContactOccurred")
    caution = next(event for event in writer.events if event["kind"] == "CautionCalled")
    review_packets.append(
        {
            "evidence": [
                {
                    "cited_event_seq": contact["seq"],
                    "kind": "CONTACT",
                    "measured_values": {"severity": 62},
                },
                {
                    "cited_event_seq": caution["seq"],
                    "kind": "CAUTION",
                    "measured_values": {"caution_laps": 3},
                },
            ],
            "incident_id": "inc_riverside_1",
            "involved_entry_ids": ["entry_agg_a", "entry_agg_b"],
            "recommended_action": "REVIEW",
            "responsibility_state": "UNRESOLVED",
        }
    )

    winner_id = crossing_order[0] if crossing_order else ""
    result = {
        "classification": classification,
        "contract_version": RACE_CONTRACT_VERSION,
        "ended_at_sim_ms": end_time,
        "engine_version": ENGINE_VERSION,
        "entrant_summaries": summaries,
        "events": writer.events,
        "grid": grid,
        "input_hash": content_hash(race_input),
        "official_distance_laps": laps,
        "output_hash": "",
        "race_id": race_id,
        "review_packets": review_packets,
        "rng_provider_version": RNG_PROVIDER_VERSION,
        "seed": race_input["seed"],
        "started_at_sim_ms": 0,
        "summary": {
            "caution_count": caution_count,
            "lead_changes": lead_changes,
            "pole_entry_id": grid_ids[0],
            "title": "Riverside 200",
            "weather": current_weather,
            "winner_entry_id": winner_id,
            "winner_name": specs_by_id.get(winner_id, {}).get("driver_name", ""),
        },
    }
    unsigned = dict(result)
    unsigned.pop("output_hash", None)
    result["output_hash"] = content_hash(unsigned)
    return result


def build_riverside_fixture(field_size=8, scheduled_laps=None):
    """Return input, result, layout, and display specs for Riverside."""

    race_input, specs = build_riverside_input(field_size)
    if scheduled_laps is not None:
        race_input = dict(race_input)
        track = dict(race_input["track"])
        track["scheduled_laps"] = int(scheduled_laps)
        race_input["track"] = track
    result = build_riverside_result(race_input, specs, scheduled_laps=scheduled_laps)
    layout = layout_for_track(race_input["track"])
    return {
        "input": race_input,
        "layout": layout,
        "result": result,
        "specs": specs,
    }
