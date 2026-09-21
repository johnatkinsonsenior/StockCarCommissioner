"""Deterministic reconstruction of viewer state from a RaceViewerBundle."""

from __future__ import annotations

import hashlib
import json


def _sorted_by_time(rows, key="sim_time_ms"):
    return sorted(list(rows or []), key=lambda row: (int(row.get(key) or 0), str(row.get("entry_id") or "")))


def index_bundle(bundle):
    """Precompute per-entry keyframe lists and ordered HUD rows."""

    frames = {}
    for frame in bundle.get("keyframes") or []:
        frames.setdefault(frame["entry_id"], []).append(frame)
    for entry_id in frames:
        frames[entry_id] = _sorted_by_time(frames[entry_id])
    return {
        "frames": frames,
        "markers": _sorted_by_time(bundle.get("markers") or []),
        "phases": _sorted_by_time(bundle.get("phase_timeline") or []),
        "timing": _sorted_by_time(bundle.get("timing_frames") or []),
    }


def _latest_at_or_before(rows, time_ms):
    chosen = None
    for row in rows:
        if int(row.get("sim_time_ms") or 0) <= int(time_ms):
            chosen = row
        else:
            break
    return chosen


def _next_after(rows, time_ms):
    for row in rows:
        if int(row.get("sim_time_ms") or 0) > int(time_ms):
            return row
    return None


def _total_progress(frame):
    laps = int(frame.get("laps_completed") or 0)
    ppm = int(frame.get("path_progress_ppm") or 0)
    return laps * 1_000_000 + ppm


def interpolate_car(previous, nxt, time_ms):
    """Interpolate one car between two keyframes using integer progress."""

    if previous is None:
        return dict(nxt) if nxt else None
    if nxt is None or int(nxt["sim_time_ms"]) <= int(previous["sim_time_ms"]):
        return dict(previous)
    span = int(nxt["sim_time_ms"]) - int(previous["sim_time_ms"])
    done = max(0, min(span, int(time_ms) - int(previous["sim_time_ms"])))
    mixed = dict(previous)
    if previous.get("path") != nxt.get("path"):
        chosen = nxt if done * 2 >= span else previous
        mixed.update(chosen)
        mixed["sim_time_ms"] = int(time_ms)
        return mixed
    start = _total_progress(previous)
    end = _total_progress(nxt)
    total = start + (end - start) * done // span
    mixed["laps_completed"] = total // 1_000_000
    mixed["path_progress_ppm"] = total % 1_000_000
    mixed["sim_time_ms"] = int(time_ms)
    mixed["race_lap"] = int(nxt.get("race_lap") or previous.get("race_lap") or 0)
    mixed["running_position"] = int(previous.get("running_position") or 0)
    mixed["status"] = previous.get("status") or "RUNNING"
    mixed["source_event_seq"] = int(previous.get("source_event_seq") or 0)
    return mixed


def cars_at(bundle, time_ms, indexed=None):
    """Return interpolated car states at a simulation timestamp."""

    indexed = indexed or index_bundle(bundle)
    states = {}
    for entry in bundle.get("entries") or []:
        frames = indexed["frames"].get(entry["entry_id"]) or []
        previous = _latest_at_or_before(frames, time_ms)
        nxt = None
        if previous is not None:
            nxt = _next_after(frames, previous["sim_time_ms"])
        elif frames:
            nxt = frames[0]
        state = interpolate_car(previous, nxt, time_ms)
        if state:
            states[entry["entry_id"]] = state
    return states


def timing_at(bundle, time_ms, indexed=None):
    indexed = indexed or index_bundle(bundle)
    row = _latest_at_or_before(indexed["timing"], time_ms)
    if row:
        return dict(row)
    classification = bundle.get("classification") or []
    order = [item["entry_id"] for item in classification]
    return {
        "leader_entry_id": order[0] if order else "",
        "order": order,
        "race_lap": 0,
        "sim_time_ms": int(time_ms),
    }


def phase_at(bundle, time_ms, indexed=None):
    indexed = indexed or index_bundle(bundle)
    row = _latest_at_or_before(indexed["phases"], time_ms)
    return dict(row) if row else {"phase": "FORMATION", "race_lap": 0}


def markers_until(bundle, time_ms, indexed=None):
    indexed = indexed or index_bundle(bundle)
    return [row for row in indexed["markers"] if int(row.get("sim_time_ms") or 0) <= int(time_ms)]


def next_marker_time(bundle, time_ms, kind=None, indexed=None):
    indexed = indexed or index_bundle(bundle)
    for row in indexed["markers"]:
        if int(row.get("sim_time_ms") or 0) <= int(time_ms):
            continue
        if kind and str(row.get("kind") or "") != kind:
            continue
        return int(row["sim_time_ms"])
    return int(bundle.get("duration_ms") or time_ms)


def reconstruct(bundle, time_ms, indexed=None):
    """Return the complete read-only viewer state at one timestamp."""

    indexed = indexed or index_bundle(bundle)
    cars = cars_at(bundle, time_ms, indexed)
    timing = timing_at(bundle, time_ms, indexed)
    phase = phase_at(bundle, time_ms, indexed)
    finished = int(time_ms) >= int(bundle.get("duration_ms") or 0)
    return {
        "cars": cars,
        "finished": finished,
        "markers": markers_until(bundle, time_ms, indexed),
        "phase": phase.get("phase"),
        "race_lap": int(timing.get("race_lap") or phase.get("race_lap") or 0),
        "sim_time_ms": int(time_ms),
        "timing": timing,
    }


def state_digest(state):
    """Hash reconstructed state so scrubbing can be compared exactly."""

    compact = {
        "cars": {
            entry_id: {
                "laps_completed": int(row.get("laps_completed") or 0),
                "path": row.get("path"),
                "path_progress_ppm": int(row.get("path_progress_ppm") or 0),
                "running_position": int(row.get("running_position") or 0),
                "status": row.get("status"),
            }
            for entry_id, row in sorted((state.get("cars") or {}).items())
        },
        "phase": state.get("phase"),
        "race_lap": int(state.get("race_lap") or 0),
        "timing_order": list((state.get("timing") or {}).get("order") or []),
    }
    encoded = json.dumps(compact, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def final_order_matches_classification(bundle):
    timing = timing_at(bundle, int(bundle.get("duration_ms") or 0))
    classified = [row["entry_id"] for row in bundle.get("classification") or [] if row.get("status") == "FINISHED"]
    live = [entry_id for entry_id in timing.get("order") or [] if entry_id in classified]
    return live == classified or not classified
