"""Build deterministic, read-only bundles for the Godot V2 race viewer."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


VIEWER_CONTRACT_VERSION = "scc-viewer-v1"
MARKER_KINDS = {
    "RaceStarted": ("START", "race-start"),
    "LeadChanged": ("LEAD_CHANGE", "lead-change"),
    "PassCompleted": ("PASS", "pass"),
    "PitRoadEntered": ("PIT", "pit-entry"),
    "PitServiceCompleted": ("PIT", "pit-service"),
    "MechanicalProblemDetected": ("MECHANICAL", "mechanical"),
    "ContactOccurred": ("CONTACT", "contact"),
    "CautionCalled": ("CAUTION", "caution"),
    "RaceRestarted": ("RESTART", "restart"),
    "ConditionChanged": ("CONDITION", "condition"),
    "EntryRetired": ("RETIREMENT", "retirement"),
    "FinishLineCrossed": ("FINISH", "finish"),
    "RaceFinished": ("FINISH", "checkered"),
}
TERMINAL_STATUS = {
    "EntryRetired": "RETIRED",
    "OutOfFuel": "OUT_OF_FUEL",
    "EntryDisqualified": "DISQUALIFIED",
}


def canonical_json(value):
    """Return the canonical JSON representation used for bundle hashes."""

    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def content_hash(value):
    """Return a lowercase SHA-256 hash for a JSON-compatible value."""

    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def write_bundle(bundle, path):
    """Write a viewer bundle with stable formatting."""

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(bundle, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return path


def read_bundle(path):
    """Read and validate a viewer bundle from disk."""

    data = json.loads(Path(path).read_text(encoding="utf-8"))
    validate_bundle_hash(data)
    return data


def validate_bundle_hash(bundle):
    """Raise ValueError when the bundle hash is missing or incorrect."""

    expected = str(bundle.get("bundle_hash") or "")
    if not expected:
        raise ValueError("Viewer bundle has no bundle_hash")
    unsigned = dict(bundle)
    unsigned.pop("bundle_hash", None)
    actual = content_hash(unsigned)
    if actual != expected:
        raise ValueError("Viewer bundle hash mismatch")
    return True


def validate_layout(layout, track_snapshot):
    """Validate a presentation layout against canonical track segments."""

    errors = []
    if not layout.get("track_layout_id"):
        errors.append("track_layout_id is required")
    racing = list(layout.get("racing_polyline") or [])
    pit = list(layout.get("pit_polyline") or [])
    if len(racing) < 3:
        errors.append("racing_polyline needs at least three points")
    if len(pit) < 2:
        errors.append("pit_polyline needs at least two points")

    canonical = {
        int(row["segment_index"]): row
        for row in track_snapshot.get("segments") or []
    }
    ranges = {}
    for row in layout.get("segment_ranges") or []:
        index = int(row.get("segment_index", -1))
        if index in ranges:
            errors.append("duplicate segment range %s" % index)
            continue
        ranges[index] = row
        if index not in canonical:
            errors.append("layout segment %s is not canonical" % index)
            continue
        start = int(row.get("start_ppm", -1))
        end = int(row.get("end_ppm", -1))
        if not (0 <= start <= 1_000_000 and 0 <= end <= 1_000_000):
            errors.append("segment %s range is outside ppm bounds" % index)
        if start == end:
            errors.append("segment %s range has no length" % index)
        if str(row.get("path")) != str(canonical[index].get("path")):
            errors.append("segment %s path does not match track" % index)

    missing = sorted(set(canonical) - set(ranges))
    if missing:
        errors.append("layout is missing segments %s" % missing)
    racing_ranges = sorted(
        (row for row in ranges.values() if str(row.get("path")) == "RACING"),
        key=lambda row: int(row.get("start_ppm") or 0),
    )
    if racing_ranges:
        if int(racing_ranges[0].get("start_ppm") or 0) != 0:
            errors.append("racing ranges must start at 0")
        if int(racing_ranges[-1].get("end_ppm") or 0) != 1_000_000:
            errors.append("racing ranges must end at 1000000")
        previous_end = 0
        for row in racing_ranges:
            start = int(row.get("start_ppm") or 0)
            end = int(row.get("end_ppm") or 0)
            if start < previous_end:
                errors.append("racing ranges overlap at %s" % start)
            if start > previous_end:
                errors.append("racing ranges leave a gap before %s" % start)
            previous_end = end
    if errors:
        raise ValueError("; ".join(errors))
    return True


def _event_location(event):
    location = event.get("location")
    return dict(location) if isinstance(location, dict) else None


def _layout_range(layout, segment_index):
    for row in layout.get("segment_ranges") or []:
        if int(row.get("segment_index", -1)) == int(segment_index):
            return row
    raise ValueError("No layout range for segment %s" % segment_index)


def _path_progress_ppm(layout, location):
    row = _layout_range(layout, location["segment_index"])
    start = int(row["start_ppm"])
    end = int(row["end_ppm"])
    segment_length = max(1, int(row.get("length_mm") or 1))
    fraction_ppm = max(
        0,
        min(
            1_000_000,
            int(location.get("progress_mm") or 0) * 1_000_000 // segment_length,
        ),
    )
    if end >= start:
        value = start + (end - start) * fraction_ppm // 1_000_000
    else:
        span = (1_000_000 - start) + end
        value = (start + span * fraction_ppm // 1_000_000) % 1_000_000
    return value


def _display_entries(race_input):
    entries = []
    for row in race_input.get("entrants") or []:
        entries.append(
            {
                "body_id": row.get("body_id") or "generic_coupe",
                "car_number": str(row.get("car_number") or ""),
                "driver_id": row["driver_id"],
                "driver_name": str(row.get("driver_name") or row["driver_id"]),
                "entry_id": row["entry_id"],
                "manufacturer_id": row.get("manufacturer_id") or "",
                "primary_color": str(row.get("primary_color") or "f5c400"),
                "secondary_color": str(row.get("secondary_color") or "101010"),
                "sprite_id": str(row.get("sprite_id") or "stock_car_topdown"),
                "team_id": row["team_id"],
                "team_name": str(row.get("team_name") or row["team_id"]),
            }
        )
    return entries


def _initial_keyframes(event, race_input, layout, state):
    payload = event.get("payload") or {}
    order = list(payload.get("starting_order") or [])
    if not order:
        order = [row["entry_id"] for row in race_input.get("entrants") or []]
    result = []
    for position, entry_id in enumerate(order, start=1):
        progress = (1_000_000 - (position - 1) * 7_500) % 1_000_000
        state[entry_id] = {
            "lane_index": (position - 1) % 2,
            "laps_completed": 0,
            "path": "RACING",
            "position": position,
            "race_lap": 0,
            "status": "RUNNING",
        }
        result.append(
            {
                "entry_id": entry_id,
                "lane_index": state[entry_id]["lane_index"],
                "laps_completed": 0,
                "path": "RACING",
                "path_progress_ppm": progress,
                "progress_mm": 0,
                "race_lap": 0,
                "running_position": position,
                "segment_index": 0,
                "sim_time_ms": int(event["sim_time_ms"]),
                "source_event_seq": int(event["seq"]),
                "status": "RUNNING",
            }
        )
    return result


def _located_keyframes(event, layout, state):
    location = _event_location(event)
    if location is None:
        return []
    kind = str(event.get("kind") or "")
    payload = event.get("payload") or {}
    frames = []
    for entry_id in event.get("entry_ids") or []:
        current = state.setdefault(
            entry_id,
            {
                "lane_index": 0,
                "laps_completed": 0,
                "path": "RACING",
                "position": 0,
                "race_lap": 0,
                "status": "RUNNING",
            },
        )
        current["lane_index"] = int(location.get("lane_index") or 0)
        range_row = _layout_range(layout, location["segment_index"])
        current["path"] = str(
            range_row.get("path") or location.get("path") or "RACING"
        )
        current["race_lap"] = int(event.get("race_lap") or current["race_lap"])
        if kind == "LapCompleted":
            current["laps_completed"] = int(
                payload.get("completed_lap") or current["laps_completed"]
            )
            current["position"] = int(
                payload.get("running_position") or current["position"]
            )
        if kind == "PassCompleted" and payload.get("passing_entry_id") == entry_id:
            current["position"] = int(
                payload.get("new_position") or current["position"]
            )
        if kind in TERMINAL_STATUS:
            current["status"] = TERMINAL_STATUS[kind]
        frames.append(
            {
                "entry_id": entry_id,
                "lane_index": current["lane_index"],
                "laps_completed": current["laps_completed"],
                "path": current["path"],
                "path_progress_ppm": _path_progress_ppm(layout, location),
                "progress_mm": int(location.get("progress_mm") or 0),
                "race_lap": current["race_lap"],
                "running_position": current["position"],
                "segment_index": int(location["segment_index"]),
                "sim_time_ms": int(event["sim_time_ms"]),
                "source_event_seq": int(event["seq"]),
                "status": current["status"],
            }
        )
    return frames


def _timing_frame(event, state):
    payload = event.get("payload") or {}
    order = list(
        payload.get("running_order")
        or payload.get("starting_order")
        or payload.get("finish_crossing_order")
        or []
    )
    laps = [
        [str(row[0]), int(row[1])]
        for row in payload.get("laps_completed_by_entry") or []
    ]
    gaps = [
        [str(row[0]), None if row[1] is None else int(row[1])]
        for row in payload.get("gaps_ms") or []
    ]
    lap_map = dict(laps)
    for position, entry_id in enumerate(order, start=1):
        current = state.setdefault(entry_id, {})
        current["position"] = position
        if entry_id in lap_map:
            current["laps_completed"] = int(lap_map.get(entry_id, 0))
        if not laps:
            laps.append([entry_id, int(current.get("laps_completed") or 0)])
        if not gaps:
            gaps.append([entry_id, None if position == 1 else (position - 1) * 200])
    return {
        "gaps_ms": gaps,
        "laps_completed": laps,
        "leader_entry_id": payload.get("leader_entry_id") or (order[0] if order else ""),
        "order": order,
        "race_lap": int(payload.get("race_lap") or event.get("race_lap") or 0),
        "sim_time_ms": int(event["sim_time_ms"]),
        "source_event_seq": int(event["seq"]),
    }


def _marker(event):
    mapped = MARKER_KINDS.get(str(event.get("kind") or ""))
    if not mapped:
        return None
    marker_kind, label_code = mapped
    payload = event.get("payload") or {}
    detail_values = {}
    for key in (
        "component_code",
        "new_weather",
        "penalty_code",
        "reason_code",
        "severity",
    ):
        if key in payload:
            detail_values[key] = payload[key]
    return {
        "detail_values": detail_values,
        "entry_ids": list(event.get("entry_ids") or []),
        "event_seq": int(event["seq"]),
        "kind": marker_kind,
        "label_code": label_code,
        "sim_time_ms": int(event["sim_time_ms"]),
    }


def project_race_viewer_bundle(race_input, race_result, layout):
    """Project canonical race facts into a deterministic viewer bundle."""

    if race_input.get("race_id") != race_result.get("race_id"):
        raise ValueError("RaceInput and RaceResult race IDs differ")
    validate_layout(layout, race_input["track"])

    state = {}
    keyframes = []
    timing_frames = []
    markers = []
    phase_timeline = []
    previous_phase = None

    events = sorted(
        list(race_result.get("events") or []),
        key=lambda row: (int(row["seq"]), int(row["sim_time_ms"])),
    )
    for event in events:
        phase = str(event.get("phase") or "")
        if phase != previous_phase or event.get("kind") in (
            "CautionCalled",
            "RaceRestarted",
        ):
            phase_timeline.append(
                {
                    "caution_id": (event.get("payload") or {}).get("caution_id"),
                    "phase": phase,
                    "race_lap": int(event.get("race_lap") or 0),
                    "sim_time_ms": int(event["sim_time_ms"]),
                    "source_event_seq": int(event["seq"]),
                }
            )
            previous_phase = phase
        if event.get("kind") == "RaceStarted":
            keyframes.extend(_initial_keyframes(event, race_input, layout, state))
        if event.get("kind") in (
            "RunningOrderRecorded",
            "FieldFrozen",
            "RestartOrderSet",
            "RaceRestarted",
            "RaceFinished",
        ):
            timing_frames.append(_timing_frame(event, state))
        keyframes.extend(_located_keyframes(event, layout, state))
        marker = _marker(event)
        if marker:
            markers.append(marker)

    entries = _display_entries(race_input)
    entry_ids = {row["entry_id"] for row in entries}
    for frame in keyframes:
        if frame["entry_id"] not in entry_ids:
            raise ValueError("Unknown keyframe entry %s" % frame["entry_id"])
    keyframes.sort(key=lambda row: (row["sim_time_ms"], row["entry_id"]))

    classification = []
    for row in race_result.get("classification") or []:
        classification.append(
            {
                "entry_id": row["entry_id"],
                "laps_completed": int(row.get("laps_completed") or 0),
                "position": int(row["position"]),
                "status": str(row.get("status") or "RUNNING"),
            }
        )

    summary = race_result.get("summary") or {}
    bundle = {
        "bundle_hash": "",
        "classification": classification,
        "duration_ms": int(race_result.get("ended_at_sim_ms") or 0),
        "engine_version": str(race_result.get("engine_version") or "fixture-v1"),
        "entries": entries,
        "input_hash": str(race_result.get("input_hash") or content_hash(race_input)),
        "keyframes": keyframes,
        "markers": markers,
        "output_hash": str(race_result.get("output_hash") or ""),
        "phase_timeline": phase_timeline,
        "race": {
            "caution_count": int(summary.get("caution_count") or 0),
            "lead_changes": int(summary.get("lead_changes") or 0),
            "pole_entry_id": str(summary.get("pole_entry_id") or ""),
            "title": str(summary.get("title") or "Race"),
            "weather": str(summary.get("weather") or "CLEAR"),
            "winner_entry_id": str(summary.get("winner_entry_id") or ""),
        },
        "race_contract_version": str(
            race_result.get("contract_version") or "scc-race-v1"
        ),
        "race_id": race_input["race_id"],
        "timing_frames": timing_frames,
        "track": {
            "lap_length_mm": int(race_input["track"]["lap_length_m"]) * 1_000,
            "name": str(race_input["track"]["name"]),
            "official_distance_laps": int(
                race_result.get("official_distance_laps")
                or race_input["track"]["scheduled_laps"]
            ),
            "scheduled_laps": int(race_input["track"]["scheduled_laps"]),
            "track_id": race_input["track"]["track_id"],
            "track_layout_id": layout["track_layout_id"],
            "track_layout_version": int(layout.get("version") or 1),
            "track_type": str(race_input["track"]["track_type"]),
        },
        "viewer_contract_version": VIEWER_CONTRACT_VERSION,
    }
    unsigned = dict(bundle)
    unsigned.pop("bundle_hash", None)
    bundle["bundle_hash"] = content_hash(unsigned)
    return bundle


def validate_bundle(bundle, layout=None):
    """Raise ValueError when a viewer bundle violates the contract."""

    errors = []
    if str(bundle.get("viewer_contract_version") or "") != VIEWER_CONTRACT_VERSION:
        errors.append("unsupported viewer contract version")
    if int(bundle.get("duration_ms") or 0) <= 0:
        errors.append("duration_ms must be > 0")
    try:
        validate_bundle_hash(bundle)
    except ValueError as exc:
        errors.append(str(exc))

    entry_ids = {row.get("entry_id") for row in bundle.get("entries") or []}
    if not entry_ids:
        errors.append("bundle has no entries")
    for frame in bundle.get("keyframes") or []:
        if frame.get("entry_id") not in entry_ids:
            errors.append("unknown keyframe entry %s" % frame.get("entry_id"))
        ppm = frame.get("path_progress_ppm")
        if ppm is None or int(ppm) < 0:
            errors.append("keyframe ppm is negative")
        elif int(ppm) > 1_000_000:
            errors.append("keyframe ppm is out of range")
        if int(frame.get("source_event_seq") or 0) < 1:
            errors.append("keyframe missing provenance")
        if str(frame.get("path") or "") not in {"RACING", "PIT"}:
            errors.append("keyframe path is invalid")
    times = [int(row.get("sim_time_ms") or 0) for row in bundle.get("keyframes") or []]
    if times != sorted(times):
        errors.append("keyframes are not time-ordered")
    classified = [row.get("entry_id") for row in bundle.get("classification") or []]
    if classified and set(classified) != entry_ids:
        errors.append("classification does not cover every entry")
    if layout is not None:
        ranges = {
            int(row["segment_index"]): row for row in layout.get("segment_ranges") or []
        }
        for frame in bundle.get("keyframes") or []:
            segment_index = frame.get("segment_index")
            if segment_index is None or int(segment_index) not in ranges:
                errors.append("keyframe segment %s is unknown" % segment_index)
    if errors:
        raise ValueError("; ".join(errors[:8]))
    return True


def replay_metadata(bundle, bundle_path):
    """Return the desk-facing replay projection for one bundle."""

    return {
        "available": True,
        "bundle_path": str(bundle_path),
        "duration_ms": int(bundle.get("duration_ms") or 0),
        "race_id": bundle.get("race_id"),
        "track_layout_id": (bundle.get("track") or {}).get("track_layout_id"),
    }


def watchable_rows(bundles):
    """Build Reports watchable rows from persisted viewer bundles."""

    rows = []
    for bundle, bundle_path in bundles:
        race = bundle.get("race") or {}
        track = bundle.get("track") or {}
        rows.append(
            {
                "caution_count": int(race.get("caution_count") or 0),
                "field": len(bundle.get("entries") or []),
                "id": bundle.get("race_id"),
                "lead_changes": int(race.get("lead_changes") or 0),
                "replay": replay_metadata(bundle, bundle_path),
                "title": race.get("title") or track.get("name") or "Race",
                "track": track.get("name") or "",
                "type": track.get("track_type") or "",
                "weather": race.get("weather") or "",
                "winner_entry_id": race.get("winner_entry_id") or "",
            }
        )
    return rows


def load_watchable_rows(godot_root):
    """Load persisted viewer bundles as desk watchable rows."""

    folder = Path(godot_root) / "data" / "races"
    rows = []
    for name in ("riverside_200_viewer.json", "riverside_200_40_viewer.json"):
        path = folder / name
        if not path.exists():
            continue
        bundle = json.loads(path.read_text(encoding="utf-8"))
        rows.append(
            {
                "caution_count": int((bundle.get("race") or {}).get("caution_count") or 0),
                "field": len(bundle.get("entries") or []),
                "id": bundle.get("race_id"),
                "lead_changes": int((bundle.get("race") or {}).get("lead_changes") or 0),
                "replay": replay_metadata(bundle, "res://data/races/%s" % name),
                "title": (bundle.get("race") or {}).get("title") or "Race",
                "track": (bundle.get("track") or {}).get("name") or "",
                "type": (bundle.get("track") or {}).get("track_type") or "",
                "weather": (bundle.get("race") or {}).get("weather") or "",
                "winner_entry_id": (bundle.get("race") or {}).get("winner_entry_id") or "",
            }
        )
    return rows


def attach_watchable_races(snapshot, rows=None):
    """Attach V2 replay rows to a desk snapshot without rewriting V1 races."""

    snapshot = dict(snapshot or {})
    reports = dict(snapshot.get("reports") or {})
    watchable = list(rows if rows is not None else reports.get("watchable") or [])
    reports["watchable"] = watchable
    recap = dict(snapshot.get("recap") or {})
    if recap.get("title") and watchable and not recap.get("replay"):
        recap["replay"] = dict(watchable[0].get("replay") or {})
        snapshot["recap"] = recap
    snapshot["reports"] = reports
    return snapshot
