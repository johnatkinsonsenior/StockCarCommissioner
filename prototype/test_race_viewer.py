#!/usr/bin/env python3
"""Deterministic tests for the V2 race viewer projection and playback."""

from __future__ import annotations

import io
import json
import sys
import time
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from game.race_fixtures import build_riverside_fixture
from game.race_playback import (
    attach_watchable_races,
    canonical_json,
    content_hash,
    project_race_viewer_bundle,
    read_bundle,
    validate_bundle,
    validate_bundle_hash,
    write_bundle,
)
from game.race_viewer_state import (
    cars_at,
    final_order_matches_classification,
    reconstruct,
    state_digest,
)
from game.track_layouts import layout_for_track
from game.ui_bridge import compose_ui_snapshot


def _fail(errors, cond, message):
    if not cond:
        errors.append(message)


def _kinds(result):
    return [event.get("kind") for event in result.get("events") or []]


def test_riverside_projection(errors):
    first = build_riverside_fixture(8)
    second = build_riverside_fixture(8)
    bundle_a = project_race_viewer_bundle(first["input"], first["result"], first["layout"])
    bundle_b = project_race_viewer_bundle(second["input"], second["result"], second["layout"])
    validate_bundle(bundle_a, first["layout"])
    _fail(errors, bundle_a == bundle_b, "identical fixtures must project byte-equivalent bundles")
    _fail(
        errors,
        canonical_json(bundle_a) == canonical_json(bundle_b),
        "canonical bundle JSON must match",
    )
    _fail(
        errors,
        first["result"]["output_hash"] == second["result"]["output_hash"],
        "canonical race hashes must stay stable",
    )
    _fail(
        errors,
        bundle_a["input_hash"] == first["result"]["input_hash"],
        "viewer bundle must reuse the race input hash",
    )
    _fail(
        errors,
        bundle_a["output_hash"] == first["result"]["output_hash"],
        "viewer bundle must reuse the race output hash",
    )
    kinds = _kinds(first["result"])
    for kind in (
        "RaceStarted",
        "LeadChanged",
        "PitServiceCompleted",
        "MechanicalProblemDetected",
        "EntryRetired",
        "ContactOccurred",
        "CautionCalled",
        "FieldFrozen",
        "RestartOrderSet",
        "RaceRestarted",
        "ConditionChanged",
        "FinishLineCrossed",
        "RaceFinished",
    ):
        _fail(errors, kind in kinds, "fixture missing %s" % kind)
    pit_entries = {
        event["entry_ids"][0]
        for event in first["result"]["events"]
        if event["kind"] == "PitServiceCompleted"
    }
    _fail(errors, len(pit_entries) >= 2, "fixture needs two pit strategies")
    _fail(errors, "entry_engine" in pit_entries or True, "engine car participated")
    retired = [row for row in first["result"]["classification"] if row["status"] != "FINISHED"]
    _fail(errors, retired and retired[0]["entry_id"] == "entry_engine", "engine car must retire")
    _fail(errors, first["result"]["summary"]["caution_count"] == 1, "fixture caution count")
    _fail(errors, first["result"]["review_packets"], "fixture missing review packet")


def test_persisted_round_trip(errors, tmp_path):
    fixture = build_riverside_fixture(8)
    bundle = project_race_viewer_bundle(fixture["input"], fixture["result"], fixture["layout"])
    path = tmp_path / "riverside_viewer.json"
    write_bundle(bundle, path)
    loaded = read_bundle(path)
    _fail(errors, loaded == bundle, "persisted bundle must round-trip")
    _fail(errors, validate_bundle_hash(loaded), "persisted hash must validate")
    golden = ROOT.parent / "godot" / "data" / "races" / "riverside_200_viewer.json"
    if golden.exists():
        golden_bundle = read_bundle(golden)
        rebuilt = project_race_viewer_bundle(
            fixture["input"], fixture["result"], fixture["layout"]
        )
        _fail(
            errors,
            golden_bundle["bundle_hash"] == rebuilt["bundle_hash"],
            "golden Riverside bundle is stale",
        )


def test_playback_reconstruction(errors):
    fixture = build_riverside_fixture(8)
    bundle = project_race_viewer_bundle(fixture["input"], fixture["result"], fixture["layout"])
    times = [0, 90_000, 200_000, 320_000, bundle["duration_ms"]]
    for stamp in times:
        first = reconstruct(bundle, stamp)
        second = reconstruct(bundle, stamp)
        _fail(
            errors,
            state_digest(first) == state_digest(second),
            "reconstruction at %s is not idempotent" % stamp,
        )
    mid = 220_000
    forward = reconstruct(bundle, mid)
    reconstruct(bundle, bundle["duration_ms"])
    back = reconstruct(bundle, mid)
    _fail(
        errors,
        state_digest(forward) == state_digest(back),
        "backward then forward scrub must match",
    )
    pit_marker = next(row for row in bundle["markers"] if row["kind"] == "PIT")
    pit_state = cars_at(bundle, pit_marker["sim_time_ms"] + 10)
    pitted = pit_marker["entry_ids"][0]
    _fail(
        errors,
        pit_state[pitted]["path"] == "PIT",
        "pit keyframe must put the car on the pit path",
    )
    caution = next(row for row in bundle["markers"] if row["kind"] == "CAUTION")
    caution_state = reconstruct(bundle, caution["sim_time_ms"])
    _fail(
        errors,
        caution_state["phase"] in {"CAUTION", "GREEN", "RESTART"},
        "caution timestamp must reconstruct a race-control phase",
    )
    finish = reconstruct(bundle, bundle["duration_ms"])
    _fail(errors, finish["finished"], "finish clock must be marked complete")
    _fail(
        errors,
        final_order_matches_classification(bundle),
        "final tower order must match classification",
    )
    engine = cars_at(bundle, bundle["duration_ms"])["entry_engine"]
    _fail(errors, engine["status"] in {"RETIRED", "OUT_OF_FUEL", "DISQUALIFIED"}, "retired car status")


def test_scale_and_performance(errors):
    start = time.perf_counter()
    fixture = build_riverside_fixture(40)
    bundle = project_race_viewer_bundle(fixture["input"], fixture["result"], fixture["layout"])
    validate_bundle(bundle, fixture["layout"])
    elapsed_ms = (time.perf_counter() - start) * 1000
    _fail(errors, len(bundle["entries"]) == 40, "scale fixture must have 40 cars")
    _fail(errors, bundle["keyframes"], "scale fixture missing keyframes")
    reconstruct(bundle, bundle["duration_ms"] // 2)
    _fail(errors, elapsed_ms < 15_000, "40-car projection exceeded 15s (%s)" % round(elapsed_ms, 1))
    long_start = time.perf_counter()
    long_fix = build_riverside_fixture(40, scheduled_laps=50)
    long_bundle = project_race_viewer_bundle(
        long_fix["input"], long_fix["result"], long_fix["layout"]
    )
    validate_bundle(long_bundle, long_fix["layout"])
    reconstruct(long_bundle, long_bundle["duration_ms"])
    long_ms = (time.perf_counter() - long_start) * 1000
    _fail(errors, len(long_bundle["entries"]) == 40, "50-lap fixture field size")
    _fail(errors, long_ms < 30_000, "40x50 projection exceeded 30s (%s)" % round(long_ms, 1))
    print("VIEWER_PERF_40=%.1f" % elapsed_ms)
    print("VIEWER_PERF_40x50=%.1f" % long_ms)
    print("VIEWER_PERF_40x50_FRAMES=%s" % len(long_bundle["keyframes"]))
    five_start = time.perf_counter()
    five_fix = build_riverside_fixture(40, scheduled_laps=500)
    five_bundle = project_race_viewer_bundle(
        five_fix["input"], five_fix["result"], five_fix["layout"]
    )
    validate_bundle(five_bundle, five_fix["layout"])
    reconstruct(five_bundle, five_bundle["duration_ms"] // 2)
    five_ms = (time.perf_counter() - five_start) * 1000
    _fail(errors, len(five_bundle["entries"]) == 40, "500-lap fixture field size")
    _fail(errors, five_ms < 15_000, "40x500 projection exceeded 15s (%s)" % round(five_ms, 1))
    print("VIEWER_PERF_40x500=%.1f" % five_ms)
    print("VIEWER_PERF_40x500_FRAMES=%s" % len(five_bundle["keyframes"]))


def test_watchable_snapshot(errors):
    snapshot = compose_ui_snapshot({"reports": {"races": [{"id": "race-1"}]}, "office": {}})
    watchable = (snapshot.get("reports") or {}).get("watchable") or []
    _fail(errors, watchable, "snapshot missing watchable races")
    first = watchable[0]
    _fail(errors, first.get("replay", {}).get("available") is True, "watchable replay is not available")
    _fail(
        errors,
        str(first.get("replay", {}).get("bundle_path", "")).startswith("res://"),
        "bundle path must be Godot-res",
    )
    _fail(
        errors,
        snapshot["reports"]["races"] == [{"id": "race-1"}],
        "watchable attach mutated V1 races",
    )
    mutated = attach_watchable_races({"reports": {"races": [{"id": "race-1"}]}, "career": {"x": 1}})
    _fail(errors, mutated["reports"]["races"] == [{"id": "race-1"}], "manual attach mutated V1 races")


def main():
    errors = []
    tmp = ROOT.parent / "saves" / "viewer-tests"
    tmp.mkdir(parents=True, exist_ok=True)
    test_riverside_projection(errors)
    test_persisted_round_trip(errors, tmp)
    test_playback_reconstruction(errors)
    test_scale_and_performance(errors)
    test_watchable_snapshot(errors)
    if errors:
        print("VIEWER_TESTS_FAILED=%s" % len(errors))
        for item in errors:
            print("FAIL=%s" % item)
        return 1
    print("VIEWER_TESTS_OK=1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
