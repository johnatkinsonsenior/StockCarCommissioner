# Stock Car Commissioner — Development Roadmap

Version-controlled progress tracker. Mirrors feature status in
[`docs/Backlog.md`](docs/Backlog.md).

- **This version (0.6.0-cup):** you sit as **lead commissioner** of a
  high-level stock car series in the Winston Cup years (1970s / 1980s /
  pinnacle late-’80s–mid-’90s). **Forty Cup cars, forty named drivers,
  one driver per entry.** Weekly Advance. The winter book (Ford,
  Pontiac, Plymouth, Chevrolet and the rest — homologated coupes, aero
  edges, plates). Mail, standings, entries, drivers, rulebook. Reports
  (TV, gate, wrecks, driver form). Treasury, television, sponsors.
  That is the game.
- **Primary goal:** a stock car *commissioner* simulation in the same
  family as **Out of the Park Baseball**, **Front Office Football**, and
  **Baseball Mogul** — league office, not franchise owner. There is no
  team-owner mode. Steam shots should look like those games: dense
  tables, box scores, financials — not chrome alone.
- **Parked for this build:** prospect pool / development series, owner
  and driver councils, board politics, charter expansion, Hall of Fame,
  multi-car team organizations, and the **Beyond** era picker. Those
  systems still exist in the sim; they are off the desk until player
  feedback says to bring them back.
- **Kept / restored:** 16-bit Winston Cup chrome and car portraits on
  the grid, weekly cadence, era start, writable Aero Wars book, Cup
  entries and drivers, hearings that belong to a sanctioning body
  (rules, safety, garage complaints, rivalries), TV / sponsors /
  treasury as commissioner work, analytics that tie the winter book to
  ratings and attendance.
- **Desk flow:** commissioner office (nav, mail, checklist, Advance).
  Godot is the office; Python simulates.
- **Working method:** each day ends with a working build, a quick test,
  and a Git commit.

**Current position:** Days 1–131 complete. **Day 131 — Cup analytics
desk** is the current build. Era 7 (Beyond) stays parked. Multi-car
teams and Era 8 density (sortable reports, reopenable race file) wait
on playtest feedback.

Legend: `[x]` done · `[ ]` not started · `[~]` in progress · `[p]` parked

## Week 1 — Core Racing Prototype
- [x] Day 1 — Project setup (repo, folders, GDD, backlog, README)
- [x] Day 2 — Drivers, tracks and races (random sim, points, standings)
- [x] Day 3 — Teams and finances (budgets, crews, car ratings, purses)
- [x] Day 4 — Incidents and DNFs (crashes, mechanical failures, reliability)
- [x] Day 5 — Commissioner discipline (warnings, fines, penalties, suspensions)
- [x] Day 6 — Relationships and personalities (trust, rivalries, reactions)
- [x] Day 7 — Season history and awards (champion, grade, JSON season report)

## Week 2 — Career Mode Foundation
- [x] Day 8 — Modularize prototype (data, race logic, reusable modules)
- [x] Day 9 — Driver and Team classes
- [x] Day 10 — Multiple seasons (career stats, persistent budgets, history)
- [x] Day 11 — Aging and retirement (development, decline, rookies)
- [x] Day 12 — Contracts and free agency (salaries, market value, renewals)
- [x] Day 13 — Team upgrades and finances (sponsorship, facilities, distress)
- [x] Day 14 — Main menu and save/load (New/Continue career, JSON save/load)

## Week 3 — Commissioner Management
- [x] Day 15 — League calendar (preseason, regular, postseason, offseason)
- [x] Day 16 — Commissioner dashboard (league health, finances, alerts)
- [x] Day 17 — Decision-event framework (reusable event/choice engine)
- [x] Day 18 — Rule-change decisions (points, formats, penalties, tech rules)
- [x] Day 19 — Safety decisions (mandates, equipment, costs, reactions)
- [x] Day 20 — Owner complaints (requests, pressure, lobbying)
- [x] Day 21 — Driver complaints (grievances, morale, trust)

> **Milestone — Day 21 Commissioner Loop:** the player feels responsible for
> the sport, not merely watching simulated races. ✅

## Week 4 — Teams as Organizations
- [x] Day 22 — Team owners (personalities, wealth, patience, priorities)
- [x] Day 23 — Team reputation (prestige, driver attractiveness, sponsor appeal)
- [x] Day 24 — Performance trends (multi-season momentum and regression)
- [x] Day 25 — Facilities (shop rating and upgrade effects)
- [x] Day 26 — Engineering departments
- [x] Day 27 — Pit crews (skill, training, mistakes)
- [x] Day 28 — Financial health (stable, profitable, struggling, insolvent)

## Week 5 — Driver Personality Depth
- [x] Day 29 — Expanded personalities (temperament, loyalty, ambition, etc.)
- [x] Day 30 — Driver happiness (team/contract satisfaction, frustration)
- [x] Day 31 — Driver reputation and credibility
- [x] Day 32 — Rivalry strength (intensity, decay/escalation)
- [x] Day 33 — Rivalry events (contact, retaliation, reviews)
- [x] Day 34 — Long-term feuds (multi-race, multi-season storylines)
- [x] Day 35 — Driver friendships (allies, teammate relationships)

> **Milestone — Day 35 Emergent Personalities:** drivers and teams develop
> relationships, rivalries, loyalties, and histories. ✅

## Week 6 — Race Simulation 2.0
- [x] Day 36 — Track attributes (length, banking, surface, tire wear, passing)
- [x] Day 37 — Driver track skills (short track, road, intermediate, superspeedway)
- [x] Day 38 — Qualifying (starting grid, penalties)
- [x] Day 39 — Race stages (segments and stage scoring)
- [x] Day 40 — Cautions (yellows, restarts, field compression)
- [x] Day 41 — Pit strategy (tires, fuel, timing)
- [x] Day 42 — Weather (generation and race-condition effects)

## Week 7 — Strategy and Incidents
- [x] Day 43 — Tire wear (degradation and strategy)
- [x] Day 44 — Fuel strategy (windows, conservation, late gambles)
- [x] Day 45 — Pit-road mistakes (crew errors, speeding, penalties)
- [x] Day 46 — Mechanical components (engine, transmission, brakes)
- [x] Day 47 — Contact model (minor contact, spins, escalation)
- [x] Day 48 — Multi-car crashes (chain reactions, major incidents)
- [x] Day 49 — Post-race investigation (evidence, blame, review material)

> **Milestone — Day 49 Race Simulation Depth:** race weekends produce
> believable strategy, incidents, and post-race investigations. ✅

## Week 8 — Championship Structure
- [x] Day 50 — Expanded schedule (22-race championship calendar)
- [x] Day 51 — Schedule generator (yearly calendars, rotate venues)
- [x] Day 52 — Expanded points (bonuses, penalties, configurable scoring)
- [x] Day 53 — Playoff format (optional postseason/championship system)
- [x] Day 54 — Manufacturer standings
- [x] Day 55 — Team standings (organization championship)
- [x] Day 56 — Historical records (all-time wins, championships, streaks)

## Week 9 — Sponsors and Commercial Model
- [x] Day 57 — Sponsor entities (companies, industries, preferences)
- [x] Day 58 — Driver sponsors (endorsement deals)
- [x] Day 59 — Team sponsors (multi-year contracts, revenue)
- [x] Day 60 — Sponsor objectives (performance, exposure, conduct)
- [x] Day 61 — Sponsor conflicts (controversies, withdrawals)
- [x] Day 62 — League sponsorship (naming rights, league-wide partners)
- [x] Day 63 — Sponsorship market (companies enter/leave over time)

> **Milestone — Day 63 Business Ecosystem:** teams, sponsors, and league
> finances connect to performance and decisions. ✅

## Week 10 — Television and Media
- [x] Day 64 — TV networks (broadcasters and profiles)
- [x] Day 65 — TV contracts (rights bids, length, negotiations)
- [x] Day 66 — Ratings (audience simulation and trends)
- [x] Day 67 — Race popularity (event audience and attendance)
- [x] Day 68 — Media stories (generated headlines and narratives)
- [x] Day 69 — Press conferences (commissioner response choices)
- [x] Day 70 — Media controversies (scandals, public pressure)

> **Milestone — Day 70 Television and Media:** networks, rights, ratings, the
> gate, headlines, pressers, and scandals feed one media loop. ✅

## Week 11 — League Politics
- [x] Day 71 — Owner council (representation and voting)
- [x] Day 72 — Driver council (representation and feedback)
- [x] Day 73 — Rule proposals (stakeholder-introduced changes)
- [x] Day 74 — Voting system (approve/reject rules, record votes)
- [x] Day 75 — Political influence (lobbying, coalitions)
- [x] Day 76 — Approval rating (fans, owners, drivers)
- [x] Day 77 — Job security (board confidence, dismissal risk)

> **Milestone — Day 77 Political Career:** the commissioner has approval
> ratings, political pressure, and job-security risk. ✅

## Week 12 — World Expansion
- [x] Day 78 — Prospect pool (drivers outside the premier series)
- [x] Day 79 — Development series (lower-level feeder championship)
- [x] Day 80 — Prospect progression (young drivers earn promotion)
- [x] Day 81 — New team entry (owners apply to enter)
- [x] Day 82 — Team closure (failed teams leave the sport)
- [x] Day 83 — Manufacturers (automakers with performance identities)
- [x] Day 84 — Manufacturer contracts (team deals and switching)

> **Milestone — Day 84 Living Racing World:** prospects, new teams, failed
> teams, and manufacturers evolve independently. ✅

## Final Six Days — Alpha Preparation
- [x] Day 85 — Complete save architecture (serialize the full career world)
- [x] Day 86 — Game settings (difficulty, season length, autosave)
- [x] Day 87 — Balance simulation (run 50–100 AI seasons)
- [x] Day 88 — Bug fixing (rosters, finances, contracts, saves, edge cases)
- [x] Day 89 — UI prototype (begin the graphical interface, preferably in Godot)
- [x] Day 90 — Playable alpha (packaged career-mode build for playtesting)

> **Milestone — Day 90 Playable Alpha:** the complete career loop can be played
> repeatedly and evaluated for balance and fun. ✅

## Milestone Summary
| Day | Name | Status |
| --- | --- | --- |
| 14 | Career Foundation | ✅ Done |
| 21 | Commissioner Loop | ✅ Done |
| 35 | Emergent Personalities | ✅ Done |
| 49 | Race Simulation Depth | ✅ Done |
| 63 | Business Ecosystem | ✅ Done |
| 70 | Television and Media | ✅ Done |
| 77 | Political Career | ✅ Done |
| 84 | Living Racing World | ✅ Done |
| 90 | Playable Alpha | ✅ Done |
| 97 | Commissioner Office | ✅ Done |
| 112 | Era Books | ✅ Done |
| 114 | Aero Wars | ✅ Done |
| 122 | Kit Politics | ✅ Done |
| 126 | Playable Aero Wars | ✅ Done |
| 127 | Commissioner Basics | ✅ Done |
| 128 | Steam screenshot pack | ✅ Done |
| 133 | Beyond the Peak | ⏸ Parked |
| 140 | League-Office Density | ⏸ Parked |

## Post-Alpha — Commissioner Office

The 90-day plan proved the sim. Post-alpha built a Winston Cup
commissioner desk. **This version strips that desk back to the job:**
lead commissioner, current Cup roster, weekly Advance, winter book.
Politics, young drivers, and Beyond wait on player feedback.

**Product lock:** commissioner only. Shop owners are NPCs. There is no
team-owner career, now or later.

This version **stops after the playable Aero Wars office** and strips
the desk to commissioner basics. Kit politics, prospects, councils,
and Beyond stay in the sim but off the rail. Player feedback decides
what comes back. Do not add a franchise mode.

### Era 1 — The Desk
- [x] Day 91 — Commissioner office shell (sidebar, status bar, Advance, mail, checklist)
- [x] Day 92 — Live mail inbox (hearings and league letters in the center pane)
- [x] Day 93 — Advance one week from the office (race week or off week)
- [x] Day 94 — Standings, schedule, and race recap screens
- [x] Day 95 — Teams, drivers, and prospect pages
- [x] Day 96 — Business screens (treasury, TV, sponsors)
- [x] Day 97 — Rulebook, councils, and board on the desk

> Screens in this era use the early-80s broadcast package (black field,
> yellow chyron bars, Winston stripe, LIVE/SPORTS bugs, scanlines).
> Palette id `cbs-broadcast-83`. Day 91's charcoal/blue shell is the
> layout prototype only.

> **Milestone — Day 97 Commissioner Office:** the player sits in an office and
> Advances a week at a time; they do not scroll a season log.

### Era 2 — Player-paced career
- [x] Day 98 — Hearing choices in the office write back to the sim
- [x] Day 99 — Save and load from the office
- [x] Day 100 — New career and continue from the office (including era book)
- [x] Day 101 — Offseason as desk weeks, not a print dump
- [x] Day 102 — Race-weekend recap card (qualifying, cautions, investigation)
- [x] Day 103 — Alerts arrive as mail
- [x] Day 104 — Windows play path (no Git required for testers)

> **Milestone — Day 104 Playable Office Career:** a commissioner career can be
> started, advanced, saved, and resumed from the Godot desk. ✅

### Era 3 — Full paddock
- [x] Day 105 — Full premier grid (more teams and a Cup-sized field)
- [x] Day 106 — Clickable driver and team profiles
- [x] Day 107 — Historical season database you can reopen
- [x] Day 108 — Hall of Fame
- [x] Day 109 — News ticker and beat-writer headlines on the desk
- [x] Day 110 — Balance pass so meters hold for a decade
- [x] Day 111 — Packaged office build for playtesters
- [x] Day 112 — Era books: 1970s, 1980s, pinnacle (late ’80s–mid ’90s), and beyond

> **Milestone — Day 112 Living Office:** the desk sits on a full-sized paddock
> with history you can inspect, and a new career can start in the pinnacle
> Winston Cup or rewind the same model into the 1970s, 1980s, or beyond. ✅

### Era 4 — Aero Wars
- [x] Day 113 — Homologated two-door coupe bodies and manufacturer track maps (Ford / GM / Chrysler families; aero + driver skill)
- [x] Day 114 — Per-track rules packages and a customizable Winston Cup rulebook (homologation, wheelbase, aero specials, plates)

> **Milestone — Day 114 Aero Wars:** each factory has a real body with holes
> by track type; the commissioner writes the series-wide book and the
> per-track kit, and can run their own Winston Cup instead of a frozen 1992
> reprint. The live `aero_bias` stub and single `aero-restrict` policy are
> replaced. ✅

### Era 5 — Kit politics
Day 114 gave the commissioner sliders. This era gives those sliders
stakeholders — and lets the office *see* the cars it homologates.

- [x] Day 115 — 16-bit homologated body portraits; commissioner picks this year's coupe per factory
- [x] Day 116 — Named-venue kit overrides (plate this oval, not every superspeedway)
- [x] Day 117 — Homologation count and wheelbase class on the Rulebook desk
- [x] Day 118 — Homologate-to-run as a first-class aero-specials choice
- [x] Day 119 — Factories lobby the winter book (Detroit mail; no auto-rebadge)
- [x] Day 120 — Owners and the garage lobby per-track kits (reuse proposal/lobby)
- [x] Day 121 — Victory-lane politics (one-make runaway hearing; plate-pack controversy)
- [x] Day 122 — Board and factories react on the desk (Win-on-Sunday as a health line)

> **Milestone — Day 122 Kit Politics:** the winter book and the per-track
> kit have stakeholders, not only rewrite buttons. Each racing year shows
> 16-bit body cards the commissioner can pick; named venues can break from
> the type kit; homologation is a desk lever; factories, owners, and the
> garage lobby the package the same way they lobby points.

### Era 6 — Playtest the living office
The first build where era books *and* a writable body book exist. Testers
unpack it and run a career before the office grows another system.

- [x] Day 123 — Playtest loop for the writable book (specials, plates, Chrysler, venue kits)
- [x] Day 124 — Bug pass from the Aero Wars desk (save/load book, era rewind vs custom book)
- [x] Day 125 — Packaged playtest zip with the writable book
- [x] Day 126 — Known-issues note and a tester career pass (meters, Superbirds, plates)

> **Milestone — Day 126 Playable Aero Wars:** a playtester can unpack a zip,
> sit at the desk, and run their own Winston Cup — legalize specials, pull
> plates, invite Chrysler — without Git. ✅

### Era — Commissioner Cup desk (this version)
Re-evaluate from Day 1 through Day 126. Keep the job: lead commissioner
of a Winston Cup-style series. Hide politics and prospects. Restore the
commissioner business books. Fill a forty-car Cup. Put the race file on
the desk.

- [x] Day 127 — Strip the desk: Cup roster, weekly Advance, winter book.
  No prospect page, no council/board/HOF rail, no Beyond picker.
  Hearings stay rules, safety, garage complaints, rivalries.
- [x] Day 128 — Steam screenshot pack of the stripped office and playtest
  copy aimed at first public interest.
- [x] Day 129 — Restore Treasury, Television, Sponsors. Forty independent
  Cup entries, forty named drivers, one driver per car. 16-bit car
  portraits on Standings, Entries, and Drivers. Multi-car orgs later.
- [x] Day 130 — Reports: attendance, TV, wrecks, driver form. Winter-book
  specials and plates swing those numbers (Baseball Mogul-style).
- [x] Day 131 — Steam shots in OOTP / Mogul report style; current bug list.

> **Milestone — Day 131 Commissioner Cup desk:** forty cars, the winter
> book, TV and the gate, and a race file the commissioner can read.
> Players tell us whether to bring back multi-car shops, prospects, or
> Beyond. ✅

### Era 7 — Beyond the peak
Parked. Same commissioner brain, a later inherited world — when players
ask for it. Not a second game. Not a franchise.

- [p] Day 127 — Beyond opening world: fatter commercial load, louder board
- [p] Day 128 — Tighter default templates in Beyond (identity remains a commissioner write)
- [p] Day 129 — Four-door street car raced as a coupe (Taurus analog) only if allowed
- [p] Day 130 — Custom sliders persist on a Beyond career (inherited, not frozen)
- [p] Day 131 — Later-era garage, media, and schedule flavor
- [p] Day 132 — Decade balance pass on the later book
- [p] Day 133 — Playable Beyond career on the same desk

> **Milestone — Day 133 Beyond the Peak:** parked until this basics desk
> has player feedback.

### Era 8 — League-office density
Parked. The OOTP / Front Office Football / Baseball Mogul bar for
reports, race files, and a season you can finish at Mogul speed.
Do not skip the basics desk for a team-owner mode that will not exist.

- [p] Day 134 — Sortable report screens (standings, schedule, history)
- [p] Day 135 — Race file you can reopen (running order, cautions, investigation)
- [p] Day 136 — Weekly desk inbox (this week's work, not a first-weekend tour)
- [p] Day 137 — News and records as an encyclopedia (leaders, splits, decades)
- [p] Day 138 — Commissioner writes the calendar (add, drop, or rotate a date)
- [p] Day 139 — Multi-car team organizations (one owner, two cars)
- [p] Day 140 — Playable density career: finish a season at Mogul speed

> **Milestone — Day 140 League-Office Density:** parked. Bring back when
> the basics loop is fun enough that players want more encyclopedia.
