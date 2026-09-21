# Stock Car Commissioner 2.0 Race Viewer Contract

Status: implementation contract

Viewer contract version: `scc-viewer-v1`

## Purpose

The race viewer is a read-only broadcast client for a completed V2 race. It
uses the same immutable race result as quick simulation, reports, and
historical replay. It never reruns the race engine and never changes race,
career, commissioner, or team state.

The first presentation is a two-dimensional top-down track with moving car
sprites, a timing tower, flag and lap state, an event ticker, and passive
playback controls. The player may pause, change playback speed, scrub, skip,
change camera, and inspect data. The player may not call pits, select tires,
change fuel or engine modes, or otherwise manage a team.

## Data flow

```text
RaceInput + RaceResult
        |
        v
RacePlaybackProjector
        |
        v
RaceViewerBundle (rebuildable)
        |
        v
Godot RaceViewer (read-only)
```

`RaceInput` and `RaceResult.events` remain canonical. Every other field in a
viewer bundle is a cache that can be discarded and rebuilt.

## RaceViewerBundle

```text
RaceViewerBundle
  viewer_contract_version: "scc-viewer-v1"
  race_contract_version: string
  engine_version: string
  race_id: stable race ID
  input_hash: canonical race-input hash
  output_hash: canonical race-result hash
  bundle_hash: SHA-256 of canonical bundle without bundle_hash
  duration_ms: int > 0
  track: ViewerTrack
  race: ViewerRaceSummary
  entries: tuple[ViewerEntry]
  phase_timeline: tuple[ViewerPhase]
  keyframes: tuple[ViewerKeyframe]
  timing_frames: tuple[ViewerTimingFrame]
  markers: tuple[ViewerMarker]
  classification: tuple[ViewerClassification]
```

Canonical bundle JSON uses UTF-8, sorted object keys, compact separators,
ordered arrays, and integer scalars. Floating-point values are forbidden.

### ViewerTrack

```text
ViewerTrack
  track_id
  track_layout_id
  track_layout_version
  name
  track_type
  scheduled_laps
  official_distance_laps
  lap_length_mm
```

`track_layout_id` selects a presentation resource. It is not simulation
geometry and does not participate in race outcomes.

### ViewerRaceSummary

```text
ViewerRaceSummary
  title
  winner_entry_id
  pole_entry_id
  lead_changes
  caution_count
  weather
```

### ViewerEntry

```text
ViewerEntry
  entry_id
  driver_id
  team_id
  manufacturer_id
  body_id
  car_number
  driver_name
  team_name
  primary_color: "rrggbb"
  secondary_color: "rrggbb"
  sprite_id
```

Names and colors are display metadata. All viewer joins use IDs.

### ViewerPhase

```text
ViewerPhase
  sim_time_ms
  phase
  race_lap
  caution_id: optional
  source_event_seq
```

### ViewerKeyframe

```text
ViewerKeyframe
  sim_time_ms
  entry_id
  path: RACING | PIT
  segment_index
  progress_mm
  path_progress_ppm: 0..1_000_000
  lane_index
  race_lap
  running_position
  laps_completed
  status
  source_event_seq
```

Keyframes are ordered by `(sim_time_ms, entry_id)`. They are emitted from
located canonical events and individual lap crossings. The projector may add
deterministic interpolation anchors, but those anchors must cite the two
canonical event sequences from which they were derived.

### ViewerTimingFrame

```text
ViewerTimingFrame
  sim_time_ms
  race_lap
  leader_entry_id
  order: tuple[entry_id]
  gaps_ms: tuple[(entry_id, optional int)]
  laps_completed: tuple[(entry_id, int)]
  source_event_seq
```

Timing frames derive from `RunningOrderRecorded`. The viewer must not reorder
cars independently of these frames and located pass/restart events.

### ViewerMarker

```text
ViewerMarker
  sim_time_ms
  event_seq
  kind
  entry_ids
  label_code
  detail_values
```

Version 1 marker kinds are `START`, `LEAD_CHANGE`, `PASS`, `PIT`,
`MECHANICAL`, `CONTACT`, `CAUTION`, `RESTART`, `CONDITION`, `RETIREMENT`,
and `FINISH`. Display text is localized by the client; canonical event prose
is not copied into the bundle.

## TrackLayout

Track layouts are original presentation resources stored separately from the
race bundle.

```text
TrackLayout
  track_layout_id
  version
  track_type
  canvas_width
  canvas_height
  racing_polyline: tuple[(x_int, y_int)]
  pit_polyline: tuple[(x_int, y_int)]
  segment_ranges:
    segment_index
    path
    start_ppm
    end_ppm
  lane_offset_px
  start_finish_ppm
  camera_bounds
```

Polylines use integer canvas coordinates. Racing polylines are closed; pit
polylines are open. Segment ranges cover their path without overlap and map
the simulation's `(segment_index, progress_mm)` to display position.

The projector rejects a layout when:

- IDs or versions do not match the requested layout;
- a simulation segment has no display range;
- a range is outside `0..1_000_000`;
- racing ranges overlap or leave gaps;
- racing or pit polylines have too few points.

Reusable oval, intermediate, superspeedway, and road-course layouts are
allowed as fallbacks. Authored venue layouts can replace them without
changing historical race facts.

## Playback rules

- The display clock is measured in simulation milliseconds.
- Pause and speed controls only change how quickly the display clock moves.
- Scrubbing reconstructs state from the beginning or a verified timing
  checkpoint; it never reverses canonical events in place.
- Car motion between keyframes is cosmetic interpolation.
- Pass order changes at `PassCompleted`, never before it.
- Pit entry, service, and exit use the pit path.
- Caution order freezes at `FieldFrozen`.
- Restart lanes and order come from `RestartOrderSet`.
- Retired and disqualified cars stop at their terminal location.
- Final timing-tower order must equal the stored classification.
- No random number generator is available to the viewer.

When sparse events leave a long visual interval, the viewer may smooth speed
and spacing while preserving endpoint time, location, lap, order, and status.
It may not invent a pass, pit stop, contact, caution, retirement, or finish.

## Godot scene boundary

The viewer lives in its own scene tree:

```text
RaceViewer
  BroadcastHud
  TrackCanvas
  PlaybackControls
```

The commissioner desk passes only a bundle path and return scene through a
small session autoload. Godot reads the bundle and track layout. It does not
shell out to Python while playback is open.

The viewer must provide:

- full-field, leader, battle, and selected-car camera modes;
- pause;
- `0.5x`, `1x`, `2x`, `4x`, and `8x` playback;
- scrub to time;
- next significant event;
- next caution;
- jump to finish;
- timing tower;
- lap and flag state;
- event ticker;
- optional data overlay.

No control may send a command to the race engine or career application.

## Integration

Completed V2 race summaries expose:

```text
replay
  available: bool
  race_id
  bundle_path
  duration_ms
  track_layout_id
```

The commissioner desk displays `WATCH` only when `available` is true. V1
box-score history remains readable but is not replayable because it has no
canonical lap or location facts.

First viewing may hide winner and final classification until playback reaches
the finish. Reopening a completed race uses the same persisted bundle.

## Validation

A conforming implementation must prove:

1. the same race input/result produces byte-identical bundle JSON;
2. bundle hashes validate after persistence round-trip;
3. every keyframe references a known entry and valid track segment;
4. every keyframe cites canonical provenance;
5. scrubbing backward then forward reconstructs identical state;
6. pit, caution, restart, retirement, and finish states match source events;
7. final timing and classification match the race result;
8. 40 cars can play without creating or deleting sprites during playback;
9. viewer controls do not mutate race, career, commissioner, or strategy
   data;
10. historical replay never invokes the race engine.

The Riverside 200 acceptance fixture is the first golden bundle. A separate
40-car Riverside bundle is the scale fixture.
