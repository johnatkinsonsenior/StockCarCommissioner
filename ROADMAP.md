# Stock Car Commissioner — Development Roadmap

Version-controlled progress tracker. Mirrors feature status in
[`docs/Backlog.md`](docs/Backlog.md).

- **Primary goal:** a deep, replayable stock car *commissioner* simulation.
  The player runs the sanctioning body, not a race team.
- **Era and look:** default book is the **pinnacle** Winston Cup (late
  ’80s–early/mid ’90s). Also runnable: 1970s, 1980s, and settings to push
  **beyond** that peak. Crimson, gold, and white. 16-bit sports-sim desk.
- **Aero Wars:** homologated two-door coupes (Ford / GM / Chrysler
  families) with strengths and holes per track type; the commissioner
  writes series-wide body rules and per-track packages, and can run a
  custom Winston Cup.
- **Desk flow:** Football Commissioner layout (nav, mail, checklist,
  Advance) plus the best of OOTP (era start, inspectable world, news,
  history) and Front Office Football (weekly cadence between events).
- **Calendar:** a season and an offseason, Advanced **week by week** (race
  week, off week, offseason week). Godot is the office; Python simulates.
- **Working method:** each day ends with a working build, a quick test, and a
  Git commit.

**Current position:** Days 1–95 complete. Next coding day:
**Day 96 — Business screens (treasury, TV, sponsors)**.

Legend: `[x]` done · `[ ]` not started · `[~]` in progress

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
| 97 | Commissioner Office | ⬜ Pending |
| 112 | Era Books | ⬜ Pending |
| 114 | Aero Wars | ⬜ Pending |

## Post-Alpha — Commissioner Office

The 90-day plan proved the sim. This era turns it into a Winston Cup
commissioner desk: the **pinnacle** late-’80s–mid-’90s book by default,
with 1970s / 1980s / beyond as settings; crimson, gold, and white; 16-bit
sports-sim chrome; Football Commissioner flow; OOTP-style era start and
inspection; Front Office Football weeks; **Aero Wars** as the factory
story the office actually manages. The player stays the commissioner.
A team-owner career is a later era, not this one.

### Era 1 — The Desk
- [x] Day 91 — Commissioner office shell (sidebar, status bar, Advance, mail, checklist)
- [x] Day 92 — Live mail inbox (hearings and league letters in the center pane)
- [x] Day 93 — Advance one week from the office (race week or off week)
- [x] Day 94 — Standings, schedule, and race recap screens
- [x] Day 95 — Teams, drivers, and prospect pages
- [ ] Day 96 — Business screens (treasury, TV, sponsors)
- [ ] Day 97 — Rulebook, councils, and board on the desk

> Screens in this era use the Winston Cup palette (crimson, gold, white) and
> 16-bit sports-sim chrome. Day 91's charcoal/blue shell is the layout
> prototype only; later desk days restyle as they land.

> **Milestone — Day 97 Commissioner Office:** the player sits in an office and
> Advances a week at a time; they do not scroll a season log.

### Era 2 — Player-paced career
- [ ] Day 98 — Hearing choices in the office write back to the sim
- [ ] Day 99 — Save and load from the office
- [ ] Day 100 — New career and continue from the office (including era book)
- [ ] Day 101 — Offseason as desk weeks, not a print dump
- [ ] Day 102 — Race-weekend recap card (qualifying, cautions, investigation)
- [ ] Day 103 — Alerts arrive as mail
- [ ] Day 104 — Windows play path (no Git required for testers)

> **Milestone — Day 104 Playable Office Career:** a commissioner career can be
> started, advanced, saved, and resumed from the Godot desk.

### Era 3 — Full paddock
- [ ] Day 105 — Full premier grid (more teams and a Cup-sized field)
- [ ] Day 106 — Clickable driver and team profiles
- [ ] Day 107 — Historical season database you can reopen
- [ ] Day 108 — Hall of Fame
- [ ] Day 109 — News ticker and beat-writer headlines on the desk
- [ ] Day 110 — Balance pass so meters hold for a decade
- [ ] Day 111 — Packaged office build for playtesters
- [ ] Day 112 — Era books: 1970s, 1980s, pinnacle (late ’80s–mid ’90s), and beyond

> **Milestone — Day 112 Living Office:** the desk sits on a full-sized paddock
> with history you can inspect, and a new career can start in the pinnacle
> Winston Cup or rewind the same model into the 1970s, 1980s, or beyond.

### Era 4 — Aero Wars
- [ ] Day 113 — Homologated two-door coupe bodies and manufacturer track maps (Ford / GM / Chrysler families; aero + driver skill)
- [ ] Day 114 — Per-track rules packages and a customizable Winston Cup rulebook (homologation, wheelbase, aero specials, plates)

> **Milestone — Day 114 Aero Wars:** each factory has a real body with holes
> by track type; the commissioner writes the series-wide book and the
> per-track kit, and can run their own Winston Cup instead of a frozen 1992
> reprint. The live `aero_bias` stub and single `aero-restrict` policy are
> replaced.
