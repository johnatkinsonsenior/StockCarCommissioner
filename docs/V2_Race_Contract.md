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

For identical canonical input and contract version, the engine must return
byte-equivalent canonical output.

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

Scalar rules:

- Distances use integer meters.
- Speeds use integer millimeters per second internally.
- Time uses integer milliseconds.
- Fuel uses integer milliliters.
- Tire wear uses integer basis points from `0` through `10_000`.
- Ratings use integers from `0` through `100`.
- Probabilities are represented as integer parts per million.
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
  restart_zone: track-specific immutable value
```

### 5.2 RaceRulesSnapshot

The rules snapshot freezes every rule that can affect this race.

```text
RaceRulesSnapshot
  rules_version: string
  field_limit: int > 0
  qualifying_format: SINGLE_CAR
  race_format: SINGLE_FEATURE
  overtime_enabled: bool
  maximum_overtime_attempts: int >= 0
  caution_policy: immutable policy value
  pit_road_speed_limit_mms: int > 0
  pit_penalty_policy: immutable policy value
  minimum_fuel_reserve_ml: int >= 0
  tire_sets_available: int >= 1
  safety_level: 0..100
  technical_package: TechnicalPackageSnapshot
```

Version 1 deliberately supports one qualifying format and one race format.
Additional formats require a contract revision and must not be simulated by
unrelated special cases.

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

A change window states when a condition may change and the deterministic
weighted alternatives. The engine records every realized change as an event.

### 5.5 RaceEntrantSnapshot

```text
RaceEntrantSnapshot
  entry_id: EntryId
  driver_id: DriverId
  team_id: TeamId
  manufacturer_id: ManufacturerId
  car_number: display-only string
  driver: DriverRaceRatings
  car: CarRaceRatings
  crew: CrewRaceRatings
  strategy: StrategyProfile
  penalties: PreRacePenaltySnapshot
```

Required driver ratings:

- raw speed
- consistency
- aggression
- racecraft
- restart skill
- tire management
- fuel management
- wet-weather skill
- short-track skill
- intermediate skill
- superspeedway skill
- road-course skill
- error resistance

Required car and team ratings:

- base pace
- reliability
- power
- braking
- aero efficiency
- mechanical grip
- fuel capacity in milliliters
- starting fuel in milliliters
- baseline fuel burn in milliliters per lap
- tire durability
- pit crew speed
- pit crew consistency
- engineering

`StrategyProfile` expresses AI tendencies such as aggression, fuel risk,
undercut preference, tire conservation, and caution reaction. It is not a
preselected final strategy label.

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

`RaceResult` is the complete on-track truth. Human-readable recaps, box
scores, and leaderboards are projections and are not stored as competing
facts. `output_hash` is SHA-256 over canonical UTF-8 JSON of the complete
result with the `output_hash` field omitted.

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

### 6.2 OnTrackClassification

```text
OnTrackClassification
  position: int >= 1
  entry_id: EntryId
  status: FINISHED | RUNNING | CRASH | MECHANICAL | OUT_OF_FUEL
  laps_completed: int >= 0
  elapsed_ms: optional int
  gap_ms: optional int
  retirement_event_seq: optional int
```

This is the on-track result before post-race commissioner sanctions. A later
sanction may create a separate official-classification revision, but must
never rewrite the original event stream.

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
  phase: QUALIFYING | FORMATION | GREEN | CAUTION | RESTART | FINISHED
  lap: int >= 0
  sim_time_ms: int >= 0
  kind: RaceEventKind
  entry_ids: tuple[EntryId]
  payload: kind-specific immutable object
```

Ordering is canonical by `seq`. `sim_time_ms` must be nondecreasing but is
not an identity or tie-breaker.

## 8. Required event kinds

Version 1 must support the following kinds.

### 8.1 Session lifecycle

- `QualifyingStarted`
- `QualifyingLapCompleted`
- `GridSet`
- `RaceStarted`
- `LapCompleted`
- `RaceFinished`

`LapCompleted` contains:

```text
  leader_entry_id
  running_order: tuple[EntryId]
  laps_completed_by_entry: tuple[(EntryId, int)]
  gaps_ms: tuple[(EntryId, optional int)]
```

One `LapCompleted` event is emitted for every official race lap. This is the
canonical replay checkpoint and the source of running-position statistics.

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
`FieldFrozen`, zero or more incident/cleanup events, one
`RestartOrderSet`, and either `RaceRestarted` or `RaceFinished`.

### 8.6 Minimum payload requirements

Payload schemas may gain optional fields in a compatible contract revision,
but version 1 requires these facts:

| Event | Required payload facts |
| --- | --- |
| `QualifyingLapCompleted` | entry, elapsed time, valid/invalid state |
| `GridSet` | complete ordered grid and applied penalties |
| `RaceStarted` | complete starting order |
| `LapCompleted` | leader, running order, laps by entry, gaps |
| `PassCompleted` | passing entry, passed entry, old and new positions |
| `LeadChanged` | previous leader, new leader |
| `DriverError` | entry, error code, severity, time or positions lost |
| `ConditionChanged` | old/new weather, temperature, and grip |
| `PitStopPlanned` | entry, reason code, requested fuel and tires |
| `PitRoadEntered` | entry, running position, fuel, tire wear |
| `PitServiceCompleted` | entry, service time, fuel added, tires changed, resulting state |
| `PitRoadExited` | entry, running position, total pit-lane time |
| `PitRoadViolation` | entry, violation code, assessed race penalty |
| `MechanicalProblemDetected` | entry, component code, severity |
| `MechanicalProblemWorsened` | entry, component code, old/new severity |
| `MechanicalRepairCompleted` | entry, component code, repair time, resulting health |
| `EntryRetired` | entry, reason code, laps completed |
| `OutOfFuel` | entry, location code, laps completed |
| `ContactOccurred` | involved entries, track zone, severity |
| `SpinOccurred` | entry, triggering event sequence, continued/terminal state |
| `CrashOccurred` | involved entries, triggering event sequence, terminal states |
| `CautionCalled` | reason code and triggering event sequence |
| `FieldFrozen` | complete eligible running order |
| `CleanupCompleted` | caution identifier and elapsed caution laps |
| `RestartOrderSet` | complete eligible order and restart lap |
| `RaceRestarted` | complete order at green and restart lap |
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

At each lap boundary the engine resolves, in this order:

1. active conditions and track state;
2. pending race-control state;
3. AI pit and conservation decisions;
4. pace and traffic interactions;
5. attempted passes;
6. driver errors, mechanical failures, and contact;
7. pit-lane service and violations;
8. lap completion and running order;
9. caution trigger and field freeze;
10. finish or overtime state.

An implementation may optimize calculations, but it may not reorder these
semantic phases in a way that makes an event depend on information from the
future.

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
6. No race event occurs before `RaceStarted` except qualifying/grid events.
7. No event occurs after `RaceFinished`.
8. Event `sim_time_ms` and `lap` never decrease.

### Running order

9. Each official lap has exactly one `LapCompleted` checkpoint.
10. Running order contains every non-retired entry exactly once.
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

### Cautions and restarts

19. A caution has one complete race-control lifecycle.
20. No green-flag pass is recorded during caution.
21. Restart order includes every eligible running entry exactly once.
22. `RaceRestarted` order equals the preceding `RestartOrderSet`.

### Classification and summaries

23. Classification reconciles with the final lap checkpoint and terminal
    events.
24. Finishing order follows finish-line crossing order.
25. Retired entries rank by laps completed, then terminal event time, then
    starting position.
26. Laps led, pit stops, contact, and failures in entrant summaries equal
    event-derived totals.

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
  evidence_codes: tuple[string]
  severity: MINOR | SIGNIFICANT | MAJOR
  recommended_review: bool
```

Evidence must cite event sequence numbers or measurable race state. Driver
aggression may influence the simulation, but an aggression rating alone is
not evidence of blame.

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
- on-track classification;
- entrant summaries;
- incident review packets;
- engine, contract, and RNG-provider versions;
- input and output hashes;
- later sanctions and official-classification revisions as linked records.

Events are append-only within the transaction that commits a completed race.
A race is either fully committed or absent. Partial event streams are never
visible as completed races.

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
- The winner, pole sitter, laps led, lead changes, pit stops, DNFs, and
  caution count match their projections.
- The review packet cites the contact and caution event sequence numbers.
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
14. schema round-trip and migration tests.

Statistical tests use broad, documented bounds and fixed seed sets. They must
not assert one hand-tuned winner.

## 20. Performance budgets

On the supported baseline development machine:

- One 40-entry, 500-lap race completes in at most 250 milliseconds at the
  95th percentile.
- One 24-race season completes in at most 6 seconds without UI rendering.
- Thirty 24-race seasons complete in at most 180 seconds.
- Persisted canonical race data averages no more than 2 MiB per race before
  optional compression.
- Historical queries for one driver, team, track, or season return in at
  most 100 milliseconds for a 30-season career.

These are acceptance budgets, not permission to create an alternate quick
engine.

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
- every official lap has a replay checkpoint;
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
