# Stock Car Commissioner 2.0 Race Contract

Status: **Approved direction; implementation contract**

Contract version: **`scc-race-v1`**

## 1. Purpose

This document defines the boundary of the Stock Car Commissioner 2.0 race
engine before implementation begins.

The engine must simulate one coherent race from qualifying through the
checkered flag. Quick simulation, race summaries, detailed viewing,
statistics, investigations, and historical replay must all consume the same
result. No presentation mode may manufacture a second result.

This is an executable contract in the specification sense: it defines inputs,
outputs, event schemas, invariants, deterministic behavior, and acceptance
tests. It does not select UI technology or implement the engine.

## 2. Product constraints

The race engine serves a commissioner game.

- The player does not drive or call a team's pit strategy.
- AI drivers and teams make race decisions.
- The commissioner changes rules and reviews incidents.
- A season must remain fast enough to simulate in one sitting.
- A career must support at least 30 seasons.
- Detail is available on demand without creating player busywork.

The target is not continuous vehicle physics. The target is a causal,
lap-aware sports simulation whose race file can explain why the result
happened.

## 3. Architectural boundary

The race engine is a pure application service:

```text
RaceEngine.simulate(RaceInput) -> RaceResult
```

For identical canonical input, contract version, engine version, and random
provider version, the engine must return byte-equivalent canonical output.

The engine:

- receives immutable snapshots of race-relevant data;
- owns qualifying and on-track simulation;
- emits an ordered event stream and derived on-track classification;
- identifies incidents that may require commissioner review;
- does not read or mutate career globals;
- does not save files;
- does not award season points, money, approval, TV ratings, or sponsorship;
- does not ask for player input;
- does not render text or UI.

The application layer persists the result, applies the ruleset's points,
creates commissioner decisions, updates the universe, and builds UI
projections.

## 4. Identity and scalar conventions

All identities are stable opaque strings. Display names are never foreign
keys.

Required IDs:

- `career_id`
- `season_id`
- `race_id`
- `track_id`
- `entry_id`
- `driver_id`
- `team_id`
- `manufacturer_id`

`entry_id` identifies one persistent licensed competitive entry in a career,
not a driver, team, season, or single-race result. A substitute driver may
occupy the same entry. A multi-car organization owns multiple entry IDs.
Participation in one race is identified by the composite `(race_id,
entry_id)`.

Scalar rules:

- Distances use integer meters.
- Speeds use integer millimeters per second internally.
- Time uses integer milliseconds.
- Fuel uses integer milliliters.
- Tire wear uses integer basis points from `0` through `10_000`.
- Ratings use integers from `0` through `100`.
- Probabilities are represented as integer parts per million.
- On-track location uses `(session_kind, session_lap, segment_index,
  progress_mm)`.
- Currency, standings points, and commissioner state are outside this
  contract.
- Floating-point values must not appear in canonical persisted race output.

## 5. Canonical input

`RaceInput` is immutable and contains:

```text
RaceInput
  contract_version: "scc-race-v1"
  race_id: RaceId
  career_id: CareerId
  season_id: SeasonId
  season_number: int >= 1
  race_number: int >= 1
  seed: uint64
  track: TrackSnapshot
  rules: RaceRulesSnapshot
  conditions: ConditionsSpec
  entrants: non-empty tuple[RaceEntrantSnapshot]
```

### 5.1 TrackSnapshot

```text
TrackSnapshot
  track_id: TrackId
  name: display-only string
  track_type: SHORT | INTERMEDIATE | SUPERSPEEDWAY | ROAD
  lap_length_m: int > 0
  scheduled_laps: int > 0
  banking_degrees: int >= 0
  surface: ASPHALT | CONCRETE
  baseline_grip_bp: 0..10_000
  tire_stress: 0..100
  fuel_stress: 0..100
  passing_difficulty: 0..100
  incident_risk: 0..100
  pit_lane_loss_ms: int >= 0
  caution_laps: int >= 1
  restart_zone_start_segment: int >= 0
  restart_zone_end_segment: int >= start
  segments: non-empty tuple[TrackSegment]
```

```text
TrackSegment
  segment_index: contiguous int starting at 0
  length_mm: int > 0
  path: RACING | PIT
  kind: STRAIGHT | CORNER | PIT_ENTRY | PIT_LANE | PIT_EXIT | START_FINISH
  lane_count: int >= 1
  passing_factor: 0..100
  contact_factor: 0..100
  pit_speed_limit_mms: optional int
  joins_racing_segment_index: optional int
```

Racing-path segment lengths must sum to `lap_length_m * 1_000`. Exactly one
racing segment contains the start/finish line. Pit entry, lane, and exit
segments form one ordered alternate path and identify where they leave and
rejoin the racing path. Segment detail is intentionally tactical rather than
geometric: it supplies causal location without becoming a vehicle-physics
model.

### 5.2 RaceRulesSnapshot

The rules snapshot freezes every rule that can affect this race.

```text
RaceRulesSnapshot
  rules_version: string
  field_limit: int > 0
  qualifying_format: SINGLE_CAR | HEAT_QUALIFYING
  race_format: SINGLE_FEATURE | STAGE_RACE | HEAT_AND_FEATURE
  stage_end_laps: tuple[int]
  heat_count: int >= 0
  heat_laps: int >= 0
  heat_transfer_count: int >= 0
  overtime_enabled: bool
  maximum_overtime_attempts: int >= 0
  overtime_laps_per_attempt: int >= 2
  finish_under_caution: bool
  caution_laps_count: bool
  pit_road_speed_limit_mms: int > 0
  pit_penalty_policy: DRIVE_THROUGH | STOP_AND_GO | TAIL_OF_FIELD
  restart_lane_rule: SINGLE_FILE | DOUBLE_FILE
  minimum_fuel_reserve_ml: int >= 0
  tire_sets_available: int >= 1
  safety_level: 0..100
  technical_package: TechnicalPackageSnapshot
```

Stage and heat formats use the same segment, resource, incident, and event
model as a single feature. They are sessions within one weekend result, not
alternate race engines. Empty stage/heat fields are required when the chosen
format does not use them.

For `STAGE_RACE`, each configured stage boundary emits `StageEnded`, freezes
that stage's order, and then emits the next `StageStarted`; stage scoring is
performed later by the application from the frozen order. For
`HEAT_AND_FEATURE`, every heat emits its own result and `FeatureGridSet`
records exactly which heat positions transferred.

Overtime is deterministic:

1. If scheduled distance is reached while a caution is active,
   `finish_under_caution` decides whether the race ends.
2. Otherwise the next green starts an overtime attempt and extends official
   distance by `overtime_laps_per_attempt`.
3. A caution before the leader starts the final lap aborts the attempt.
4. A caution after the leader starts the final lap ends the race under the
   configured caution procedure.
5. An aborted attempt may be replaced until
   `maximum_overtime_attempts` is exhausted.
6. After the final permitted aborted attempt, the race finishes under
   caution.

Every extension updates `official_distance_laps` and is represented by
overtime lifecycle events.

### 5.3 TechnicalPackageSnapshot

This is the race-effective output of the commissioner's rulebook, not the
entire political or commercial rule system.

```text
TechnicalPackageSnapshot
  package_id: string
  power_factor: 0..100
  downforce_factor: 0..100
  drag_factor: 0..100
  mechanical_stress_factor: 0..100
  pack_racing_factor: 0..100
```

Body catalogs, homologation politics, operating costs, TV effects, and
manufacturer lobbying remain outside the race engine. Their resolved
performance effects enter through this snapshot.

### 5.4 ConditionsSpec

```text
ConditionsSpec
  starting_weather: CLEAR | CLOUDY | HOT | WINDY | LIGHT_RAIN
  starting_temperature_c: int
  starting_grip_bp: 0..10_000
  change_windows: tuple[ConditionChangeWindow]
```

```text
ConditionChangeWindow
  earliest_race_lap: int >= 0
  latest_race_lap: int >= earliest
  probability_ppm: 0..1_000_000
  alternatives: non-empty tuple[ConditionAlternative]

ConditionAlternative
  weather
  temperature_delta_c: int
  grip_delta_bp: int
  weight: int > 0
```

A change window states when a condition may change and the deterministic
weighted alternatives. The engine records every realized change as an event.

### 5.5 RaceEntrantSnapshot

```text
RaceEntrantSnapshot
  entry_id: EntryId
  driver_id: DriverId
  team_id: TeamId
  manufacturer_id: ManufacturerId
  body_id: stable homologated body ID
  car_number: display-only string
  driver: DriverRaceRatings
  car: CarRaceRatings
  crew: CrewRaceRatings
  strategy: StrategyProfile
  penalties: PreRacePenaltySnapshot
  effective_package: EntrantPackageSnapshot
```

```text
DriverRaceRatings
  pace: 0..100
  consistency: 0..100
  aggression: 0..100
  racecraft: 0..100
  restart_skill: 0..100
  tire_management: 0..100
  fuel_management: 0..100
  wet_skill: 0..100
  track_affinity: map[track_type, 0..100]

CarRaceRatings
  base_pace: 0..100
  reliability: 0..100
  power: 0..100
  braking: 0..100
  aero_efficiency: 0..100
  mechanical_grip: 0..100
  fuel_capacity_ml: int > 0
  starting_fuel_ml: 0..fuel_capacity_ml
  baseline_fuel_burn_ml_per_lap: int > 0
  tire_durability: 0..100

CrewRaceRatings
  pit_speed: 0..100
  pit_consistency: 0..100

StrategyProfile
  aggression: 0..100
  fuel_risk: 0..100
  undercut_preference: 0..100
  tire_conservation: 0..100
  caution_reaction: 0..100

PreRacePenaltySnapshot
  grid_positions: int >= 0
  start_from_pit_lane: bool
  reason_code: optional closed enumeration

EntrantPackageSnapshot
  body_id
  source_rulebook_version
  pace_modifier: signed int
  reliability_modifier: signed int
  aero_modifier: signed int
  pack_modifier: signed int
```

These are effective race inputs. Manufacturer, body, and rulebook provenance
remain attached so historical reports can explain what the winter book did.
`StrategyProfile` contains AI tendencies, not a preselected final strategy
label.

## 6. Canonical output

```text
RaceResult
  contract_version: "scc-race-v1"
  engine_version: semantic version
  rng_provider_version: "pcg32-v1"
  race_id: RaceId
  seed: uint64
  input_hash: lowercase SHA-256 hex
  output_hash: lowercase SHA-256 hex
  started_at_sim_ms: 0
  ended_at_sim_ms: int > 0
  official_distance_laps: int > 0
  grid: tuple[GridPosition]
  events: tuple[RaceEvent]
  classification: tuple[OnTrackClassification]
  entrant_summaries: tuple[EntrantRaceSummary]
  review_packets: tuple[IncidentReviewPacket]
```

The immutable input and ordered events are canonical on-track facts.
Classification, entrant summaries, and review packets are validated,
rebuildable projections bundled with `RaceResult` for transaction integrity
and fast reads. Human-readable recaps, box scores, and leaderboards are
additional projections and are not stored as competing facts. `output_hash`
is SHA-256 over canonical UTF-8 JSON of the complete result with the
`output_hash` field omitted.

### 6.1 GridPosition

```text
GridPosition
  position: int >= 1
  entry_id: EntryId
  qualifying_time_ms: int > 0
  raw_qualifying_position: int >= 1
  penalty_positions: int >= 0
  penalty_reason_code: optional string
```

`RaceResult.grid` is the final feature starting grid. Qualifying and heat
session grids remain available in their lifecycle events.

### 6.2 OnTrackClassification

```text
OnTrackClassification
  position: int >= 1
  entry_id: EntryId
  status: FINISHED | RUNNING | CRASH | MECHANICAL | OUT_OF_FUEL | DISQUALIFIED
  laps_completed: int >= 0
  elapsed_ms: optional int
  gap_ms: optional int
  laps_down: int >= 0
  finish_crossing_event_seq: optional int
  retirement_event_seq: optional int
```

This is the on-track result before post-race commissioner sanctions. A later
sanction may create a separate official-classification revision, but must
never rewrite the original event stream.

`FINISHED` means the entry crossed the finish line after the checkered flag.
`RUNNING` means the event ended before that entry crossed, including a finish
under caution. Lead-lap finishers have `laps_down = 0`; lapped entries use
`laps_down` rather than encoding a multi-lap deficit in `gap_ms`.
`elapsed_ms` is required for finishers. `gap_ms` is required only when a
same-lap time gap is meaningful. Ties are broken by the order of
`FinishLineCrossed` events.

### 6.3 EntrantRaceSummary

Every summary value must be derivable from `grid`, `events`, and
`classification`.

Required fields:

- start
- finish
- status
- laps completed
- laps led
- lead changes participated in
- green-flag passes
- fastest lap
- average running position
- pit stops
- fuel added
- tire sets used
- cautions involved in
- contact count
- incident responsibility state
- failed component, if any
- positions gained

## 7. Event envelope

Every event uses this envelope:

```text
RaceEvent
  schema_version: 1
  race_id: RaceId
  seq: int >= 1
  event_id: "{race_id}:{seq}"
  session_kind: QUALIFYING | HEAT | FEATURE
  session_index: int >= 0
  phase: QUALIFYING | FORMATION | GREEN | CAUTION | RESTART | STAGE_BREAK | OVERTIME | FINISHED
  session_lap: int >= 0
  race_lap: optional int >= 0
  location: optional RaceLocation
  sim_time_ms: int >= 0
  kind: RaceEventKind
  entry_ids: tuple[EntryId]
  payload: kind-specific immutable object
```

Ordering is canonical by `seq`. `sim_time_ms` must be nondecreasing but is
not an identity or tie-breaker.

```text
RaceLocation
  segment_index: valid TrackSegment index
  progress_mm: 0..segment.length_mm
  lane_index: 0..segment.lane_count-1
```

`session_lap` resets at the start of each qualifying, heat, or feature
session. `race_lap` is absent outside the feature and never decreases within
the feature.

## 8. Required event kinds

Version 1 must support the following kinds.

### 8.1 Session lifecycle

- `QualifyingStarted`
- `QualifyingLapCompleted`
- `GridSet`
- `HeatStarted`
- `HeatFinished`
- `FeatureGridSet`
- `RaceStarted`
- `LapCompleted`
- `RunningOrderRecorded`
- `StageStarted`
- `StageEnded`
- `OvertimeAttemptStarted`
- `OvertimeAttemptEnded`
- `FinishLineCrossed`
- `RaceFinished`

`LapCompleted` contains:

```text
  entry_id
  completed_lap
  lap_time_ms
  running_position
  fuel_ml
  tire_wear_bp
```

One `LapCompleted` is emitted whenever an entry crosses the start/finish line.
It is the source of individual lap times, completed distance, and fastest
laps.

`RunningOrderRecorded` contains:

```text
  race_lap
  leader_entry_id
  running_order: tuple[EntryId]
  laps_completed_by_entry: tuple[(EntryId, int)]
  gaps_ms: tuple[(EntryId, optional int)]
```

One `RunningOrderRecorded` checkpoint is emitted after the leader completes
every official feature lap. Significant actions carry segment locations
between checkpoints. Together they are the canonical replay source.

### 8.2 Competition

- `PassCompleted`
- `LeadChanged`
- `DriverError`
- `ConditionChanged`

`PassCompleted` identifies the passing entry, passed entry, and position.
A `LeadChanged` event is mandatory whenever the leader changes under green.

### 8.3 Pit and strategy

- `PitStopPlanned`
- `PitRoadEntered`
- `PitServiceCompleted`
- `PitRoadExited`
- `PitRoadViolation`
- `PenaltyIssued`
- `PenaltyServed`
- `PenaltyCleared`
- `EntryDisqualified`
- `FuelConservationStarted`
- `FuelConservationEnded`

`PitServiceCompleted` records service duration, fuel added, tire change
count, resulting fuel, and resulting tire wear. Strategy explanations are
derived from these actions rather than stored as unsupported labels.

### 8.4 Reliability

- `MechanicalProblemDetected`
- `MechanicalProblemWorsened`
- `MechanicalRepairCompleted`
- `EntryRetired`
- `OutOfFuel`

Mechanical events identify a component and severity. A terminal mechanical
problem must be followed by `EntryRetired`.

### 8.5 Contact and race control

- `ContactOccurred`
- `SpinOccurred`
- `CrashOccurred`
- `CautionCalled`
- `FieldFrozen`
- `CleanupCompleted`
- `RestartOrderSet`
- `RaceRestarted`

Contact identifies the involved entries without automatically assigning
blame. Evidence and responsibility are derived into a review packet.

Every caution period must have exactly one `CautionCalled`, one
`FieldFrozen`, zero or more incident/cleanup events, and then either
`RestartOrderSet` followed by `RaceRestarted`, or `RaceFinished`.
All lifecycle events carry the same stable `caution_id`. Cautions cannot
overlap. Every caution triggered by debris, a stopped entry, or a crash must
include `CleanupCompleted`; a competition caution may omit cleanup.

### 8.6 Minimum payload requirements

Payload schemas may gain optional fields in a compatible contract revision,
but version 1 requires these facts:

| Event | Required payload facts |
| --- | --- |
| `QualifyingLapCompleted` | entry, elapsed time, valid/invalid state |
| `GridSet` | session, complete ordered grid, applied penalties |
| `HeatStarted` / `HeatFinished` | heat index, entrants, ordered result |
| `FeatureGridSet` | complete feature grid and heat-transfer provenance |
| `RaceStarted` | complete starting order |
| `LapCompleted` | entry, completed lap, lap time, position, fuel, tire wear |
| `RunningOrderRecorded` | race lap, leader, running order, laps by entry, gaps |
| `StageStarted` / `StageEnded` | stage index, boundary lap, ordered result |
| `OvertimeAttemptStarted` / `OvertimeAttemptEnded` | attempt index, start/end lap, outcome code |
| `FinishLineCrossed` | entry, crossing order, elapsed time, completed laps |
| `PassCompleted` | passing entry, passed entry, old and new positions |
| `LeadChanged` | previous leader, new leader |
| `DriverError` | entry, error code, severity, time or positions lost |
| `ConditionChanged` | old/new weather, temperature, and grip |
| `PitStopPlanned` | entry, reason code, requested fuel and tires |
| `PitRoadEntered` | entry, running position, fuel, tire wear |
| `PitServiceCompleted` | entry, service time, fuel added, tires changed, resulting state |
| `PitRoadExited` | entry, running position, total pit-lane time |
| `PitRoadViolation` | entry, violation code, measured value, limit |
| `PenaltyIssued` | entry, source event sequence, penalty code |
| `PenaltyServed` | entry, penalty event sequence, service facts |
| `PenaltyCleared` | entry, penalty event sequence |
| `EntryDisqualified` | entry, source event sequence, reason code |
| `MechanicalProblemDetected` | entry, component code, severity |
| `MechanicalProblemWorsened` | entry, component code, old/new severity |
| `MechanicalRepairCompleted` | entry, component code, repair time, resulting health |
| `EntryRetired` | entry, reason code, laps completed |
| `OutOfFuel` | entry, location code, laps completed |
| `ContactOccurred` | incident ID, involved entries, location, severity |
| `SpinOccurred` | incident ID, entry, triggering event sequence, continued/terminal state |
| `CrashOccurred` | incident ID, involved entries, triggering event sequence, terminal states |
| `CautionCalled` | caution ID, reason code, triggering event sequence |
| `FieldFrozen` | caution ID, complete eligible running order |
| `CleanupCompleted` | caution ID and elapsed caution laps |
| `RestartOrderSet` | caution ID, complete eligible order, restart lap |
| `RaceRestarted` | caution ID, complete order at green, restart lap |
| `RaceFinished` | finish crossing order and scheduled/overtime state |

Component codes in version 1 are `ENGINE`, `TRANSMISSION`, `BRAKES`,
`SUSPENSION`, and `ELECTRICAL`. Reason, error, violation, and location codes
are closed versioned enumerations, not display text.

## 9. Internal simulation state

The implementation may simulate in efficient green-flag segments, but it
must maintain per-entry state sufficient to emit truthful lap checkpoints:

```text
EntryRaceState
  entry_id
  status
  position
  laps_completed
  segment_index
  progress_mm
  lane_index
  elapsed_ms
  current_lap_time_ms
  fuel_ml
  tire_wear_bp
  component_health
  pit_state
  penalty_state
  traffic_state
```

`tire_wear_bp` is accumulated wear: `0` is a fresh set and `10_000` is fully
worn. Starting fuel may not exceed the entrant's fuel capacity.

The implementation may resolve fixed-distance segments, variable green-flag
chunks, or another deterministic internal step. Only observable causality is
contractual:

- an entry must reach a location before an event can occur there;
- a pit plan precedes pit entry, service, and exit;
- contact or a race-control cause precedes its caution;
- field freeze precedes cleanup and restart ordering;
- restart order precedes return to green;
- a lap crossing precedes its lap-time and running-order projection;
- finish crossings precede final classification;
- no event may depend on state from a later sequence.

This permits optimization without allowing post-hoc cautions, incidents, or
strategy.

## 10. Determinism

### 10.1 Canonical input hash

`input_hash` is SHA-256 over canonical UTF-8 JSON of `RaceInput`:

- object keys sorted lexicographically;
- array order preserved;
- no insignificant whitespace;
- integer scalars only;
- UTF-8 without byte-order mark.

### 10.2 Random provider

The production provider is identified as **`pcg32-v1`**. Its exact constants,
seeding sequence, and sampling algorithms must be fixed in the first
implementation ADR and covered by golden vectors before simulation work
merges.

No code may call module-global randomness.

Deterministic substreams are derived from:

```text
SHA-256("{contract_version}|{race_seed}|{stream_name}|{scope_id}")
```

The first unsigned 64 bits seed the substream. Required stream names include:

- `conditions`
- `qualifying`
- `pace`
- `strategy`
- `pit`
- `errors`
- `mechanical`
- `contact`
- `race_control`

Entrant-specific rolls use `entry_id` as `scope_id`. Adding an unrelated
media or UI feature must never change a race result.

### 10.3 Replay guarantee

Given identical:

- contract version;
- engine version;
- canonical input;
- random-provider version;

the grid, event stream, classification, summaries, and review packets must
be identical.

## 11. State and event invariants

An implementation is nonconforming if any invariant fails.

### Identity

1. Every entrant has a unique `entry_id`, `driver_id`, and car number.
2. Every event references only entrants in the input.
3. Every grid and classification entry appears exactly once.
4. Event IDs and sequence numbers are unique and contiguous.

### Lifecycle

5. Exactly one `RaceStarted` and one `RaceFinished` exist.
6. No feature-race event occurs before `RaceStarted` except qualifying,
   heat, and grid events.
7. No event occurs after `RaceFinished`.
8. Event `sim_time_ms` never decreases; `session_lap` resets only at a new
   session, and `race_lap` never decreases within the feature.

### Running order

9. Every entry crossing emits one `LapCompleted`; every leader lap emits
   exactly one `RunningOrderRecorded`.
10. Each recorded running order contains every non-retired entry exactly
    once.
11. Positions are unique and contiguous.
12. The checkpoint leader equals running order position one.
13. Every leader change under green has a corresponding `LeadChanged`.

### Resources and status

14. Elapsed time, laps completed, and accumulated tire wear never decrease;
    a tire change explicitly replaces the active tire wear value.
15. Fuel never increases without a recorded service and component health
    never increases without a recorded repair.
16. Fuel and component health never become negative.
17. A retired entry cannot pass, pit, restart, or return to running.
18. Every non-finishing status is supported by a terminal event.
19. Segment and lane locations always reference the current track snapshot.

### Cautions and restarts

20. A caution ID has one complete race-control lifecycle and caution periods
    never overlap.
21. No green-flag pass is recorded during caution.
22. Restart order includes every eligible running entry exactly once.
23. `RaceRestarted` order equals the preceding `RestartOrderSet`.

### Penalties

24. Every race penalty cites its source event.
25. A penalty is issued before it is served or cleared.
26. A disqualification has exactly one supporting `EntryDisqualified` event.

### Classification and summaries

27. Classification reconciles with lap crossings, finish crossings, and
    terminal events.
28. `FINISHED` entries follow `FinishLineCrossed` sequence; a race ending
    under caution uses the final frozen order for entries still `RUNNING`.
29. Retired entries rank by laps completed, then terminal event time, then
    starting position.
30. Fastest lap, laps led, average position, pit stops, contact, and failures
    in entrant summaries equal event-derived totals.

## 12. Commissioner evidence contract

The race engine reports facts, not punishment.

An `IncidentReviewPacket` contains:

```text
IncidentReviewPacket
  incident_id: string
  trigger_event_seq: int
  involved_entry_ids: tuple[EntryId]
  alleged_responsible_entry_id: optional EntryId
  confidence: LOW | MODERATE | HIGH
  evidence: non-empty tuple[EvidenceItem]
  severity: MINOR | SIGNIFICANT | MAJOR
  recommended_review: bool

EvidenceItem
  evidence_code: closed versioned enumeration
  event_seqs: non-empty tuple[int]
  measured_entry_id: optional EntryId
  measured_value: optional int
  measurement_unit: optional closed enumeration
```

Evidence must cite event sequence numbers or measurable race state. Driver
aggression may influence the simulation, but an aggression rating alone is
not evidence of blame. Every contact, spin, and crash event carries the same
`incident_id` used by its review packet.

Commissioner rulings are separate application events:

```text
SanctionDecision
  decision_id
  race_id
  incident_id
  choice
  penalties
  explanation
```

Raw race events remain immutable. If a sanction changes official results,
the application stores an official-classification revision linked to both
the on-track classification and sanction.

## 13. Statistics and projections

The following must be reproducible exclusively from persisted race inputs
and results:

- starts
- wins
- poles
- top fives
- top tens
- DNFs by cause
- laps led
- average finish
- average start
- points after application of the season rules
- earnings after application of the purse rules
- track-type splits
- team and manufacturer results
- lead changes
- green-flag passes
- pit stops and pit violations
- mechanical failures by component
- cautions and caution laps
- incident involvement
- race and track records

The engine does not maintain career totals. A stats projector consumes race
results into queryable season and career tables. Rebuilding projections from
the canonical facts must produce the same values.

## 14. Presentation modes

All presentation modes consume one persisted `RaceResult`.

### Quick simulation

Displays classification and a short recap. It does not use a reduced-fidelity
engine.

### Race summary

Projects decisive events, lead changes, pit cycles, cautions, failures, and
the finish.

### Detailed race viewer

Steps through `LapCompleted` checkpoints and significant events. It may
animate or skip quiet laps without changing history.

### Historical replay

Reads the persisted input and result. It never reruns current engine code to
invent the old race again.

## 15. Persistence contract

V2 persistence uses stable IDs and a queryable store. SQLite is the default
implementation target.

At minimum, persistence stores:

- immutable canonical `RaceInput`;
- immutable ordered `RaceEvent` rows;
- rebuildable on-track classification cache;
- rebuildable entrant-summary cache;
- rebuildable incident-review cache;
- engine, contract, and RNG-provider versions;
- input and output hashes;
- later sanctions and official-classification revisions as linked records.

Events are append-only within the transaction that commits a completed race.
A race is either fully committed or absent. Partial event streams are never
visible as completed races.

Dropping and rebuilding all three caches from input and events must reproduce
their canonical serialized values and the stored `output_hash`.

Storage may compress lap checkpoints, but decompression must restore the
canonical event payload exactly.

## 16. Failure behavior

The engine returns a typed failure and no `RaceResult` when:

- the contract version is unsupported;
- IDs are missing or duplicated;
- the field is empty or exceeds the ruleset limit;
- track or rules values are outside their allowed ranges;
- an entrant snapshot is incomplete;
- deterministic output validation fails;
- any invariant fails before commit.

The engine must not silently clamp invalid contract input. Validation errors
identify the field and rule violated.

## 17. Versioning

Contract changes follow semantic versioning:

- Patch: clarification that does not change canonical data.
- Minor: backward-compatible optional field or event kind.
- Major: changed meaning, required field, ordering, determinism, or invariant.

Persisted races retain their original contract and engine versions. Migration
may add projections, but never rewrites the historical event truth.

## 18. Acceptance fixture: Riverside 200

The first implementation must include one deterministic end-to-end fixture.
The names are descriptive only; IDs are authoritative.

### Given

- An eight-entry, 20-lap short-track race.
- A fixed `RaceInput` fixture and fixed seed.
- A scripted test random provider that conforms to the production random
  interface.
- One entrant with strong qualifying pace.
- One entrant with high restart skill.
- One entrant with poor engine reliability.
- Two aggressive entrants starting near each other.
- Tire stress sufficient to create a green-flag pit cycle.
- A condition-change window late in the race.

### Required event story

1. Qualifying sets a complete eight-entry grid.
2. The race starts under green.
3. At least one green-flag lead change occurs.
4. At least two distinct pit strategies produce recorded services.
5. One mechanical problem worsens into retirement.
6. Contact between two entries produces a caution and review packet.
7. The field is frozen and a valid restart order is set.
8. The high-restart-skill entrant gains position on restart.
9. Conditions change and affect subsequent tire or pace state.
10. The race finishes with a complete classification.

### Then

- Repeating the fixture produces byte-equivalent canonical output.
- Changing only presentation mode produces identical output.
- Every invariant in section 11 passes.
- Classification can be rebuilt from the event stream.
- Entrant summaries can be rebuilt from the event stream.
- Every finisher's lap times and finish crossing can be rebuilt.
- Contact and pit actions carry valid segment locations.
- The winner, pole sitter, laps led, lead changes, pit stops, DNFs, and
  caution count match their projections.
- The review packet contains structured evidence citing the contact and
  caution event sequence numbers and at least one measured race-state value.
- No season points, treasury, approval, TV, or sponsor state appears in the
  engine output.

The scripted provider is an acceptance-test tool only. Production races use
the versioned production provider.

## 19. Required automated test groups

Before the race engine can support gameplay, it must have:

1. input validation tests;
2. RNG golden-vector tests;
3. deterministic replay tests;
4. event ordering and lifecycle tests;
5. resource conservation tests for fuel and tires;
6. caution/restart state-machine tests;
7. pit and penalty tests;
8. failure and retirement tests;
9. contact and review-packet tests;
10. classification reconstruction tests;
11. statistics projection tests;
12. seeded statistical balance tests;
13. 30-season throughput and storage tests;
14. schema round-trip and migration tests;
15. segment location and finish-crossing tests;
16. heat, stage, and overtime lifecycle tests;

Statistical tests use broad, documented bounds and fixed seed sets. They must
not assert one hand-tuned winner.

## 20. Performance budgets

The first engine milestone must create a fixed benchmark suite containing
40-entry races of 50, 200, and 500 laps plus one 30-season universe. The
benchmark record identifies CPU, memory, operating system, runtime version,
database settings, whether validation and persistence are included, event
counts, and compressed and uncompressed sizes.

Measured results establish quantitative release gates in a dedicated
benchmark ADR. Until that baseline exists, this contract requires:

- no alternate reduced-fidelity quick engine;
- approximately linear growth with entrants, segments, laps, and races;
- no full-career scan to render one race, driver, team, track, or season;
- bounded-memory streaming of completed event batches into persistence;
- completion of the fixed 30-season benchmark without timeout, corruption,
  or loss of canonical events;
- interactive historical queries backed by database indexes.

Performance is a release criterion, but invented machine-independent
millisecond or byte limits are not.

## 21. Migration policy

The V2 engine does not load or replay V1 race saves.

Selective migration is allowed for:

- driver, team, manufacturer, and track seed data;
- rating concepts;
- qualifying and incident probability calibration;
- track-type and weather concepts;
- commissioner investigation language as writing reference;
- balance scenarios.

The following are explicitly not migrated as architecture:

- module-global mutable state;
- final-score sorting as the race model;
- post-hoc caution compression;
- strategy labels without timed actions;
- name-based relationships;
- nested JSON career history;
- separate premier and development race engines.

## 22. Definition of done

The contract is implemented only when:

- `RaceEngine` accepts immutable snapshots and has no universe globals;
- production randomness is versioned and injected;
- the event stream covers qualifying through finish;
- heat, stage, and single-feature formats use the same event model;
- events identify segment location where on-track actions occur;
- every official lap has a replay checkpoint;
- every entrant crossing records an individual lap time;
- cautions, restarts, pits, fuel, tires, failures, errors, contact, and
  changing conditions are causal;
- classification and required statistics rebuild from canonical facts;
- quick, summary, detailed, and replay modes share one result;
- the Riverside 200 fixture passes;
- all invariant, deterministic, statistical, persistence, and performance
  tests pass;
- a 30-season automated universe run completes without history corruption.

No commissioner, career, commercial, or graphical UI feature should be built
on V2 race results until this definition is satisfied.
