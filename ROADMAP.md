# Stock Car Commissioner — 90-Day Development Roadmap

Version-controlled progress tracker for the path from Python prototype to a
playable commissioner-management alpha. Mirrors the 90-day plan and stays in
sync with the feature status in [`docs/Backlog.md`](docs/Backlog.md).

- **Primary goal:** a deep, replayable stock car racing *commissioner*
  simulation (the player runs the sanctioning body, not a race team).
- **Foundation:** prove the Python simulation first; serious UI work comes late.
- **Working method:** each day ends with a working build, a quick test, and a
  Git commit.

**Current position:** Days 1–54 complete. Next coding day: **Day 55 — Team
standings**.

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
- [ ] Day 55 — Team standings (organization championship)
- [ ] Day 56 — Historical records (all-time wins, championships, streaks)

## Week 9 — Sponsors and Commercial Model
- [ ] Day 57 — Sponsor entities (companies, industries, preferences)
- [ ] Day 58 — Driver sponsors (endorsement deals)
- [ ] Day 59 — Team sponsors (multi-year contracts, revenue)
- [ ] Day 60 — Sponsor objectives (performance, exposure, conduct)
- [ ] Day 61 — Sponsor conflicts (controversies, withdrawals)
- [ ] Day 62 — League sponsorship (naming rights, league-wide partners)
- [ ] Day 63 — Sponsorship market (companies enter/leave over time)

> **Milestone — Day 63 Business Ecosystem:** teams, sponsors, and league
> finances connect to performance and decisions.

## Week 10 — Television and Media
- [ ] Day 64 — TV networks (broadcasters and profiles)
- [ ] Day 65 — TV contracts (rights bids, length, negotiations)
- [ ] Day 66 — Ratings (audience simulation and trends)
- [ ] Day 67 — Race popularity (event audience and attendance)
- [ ] Day 68 — Media stories (generated headlines and narratives)
- [ ] Day 69 — Press conferences (commissioner response choices)
- [ ] Day 70 — Media controversies (scandals, public pressure)

## Week 11 — League Politics
- [ ] Day 71 — Owner council (representation and voting)
- [ ] Day 72 — Driver council (representation and feedback)
- [ ] Day 73 — Rule proposals (stakeholder-introduced changes)
- [ ] Day 74 — Voting system (approve/reject rules, record votes)
- [ ] Day 75 — Political influence (lobbying, coalitions)
- [ ] Day 76 — Approval rating (fans, owners, drivers)
- [ ] Day 77 — Job security (board confidence, dismissal risk)

> **Milestone — Day 77 Political Career:** the commissioner has approval
> ratings, political pressure, and job-security risk.

## Week 12 — World Expansion
- [ ] Day 78 — Prospect pool (drivers outside the premier series)
- [ ] Day 79 — Development series (lower-level feeder championship)
- [ ] Day 80 — Prospect progression (young drivers earn promotion)
- [ ] Day 81 — New team entry (owners apply to enter)
- [ ] Day 82 — Team closure (failed teams leave the sport)
- [ ] Day 83 — Manufacturers (automakers with performance identities)
- [ ] Day 84 — Manufacturer contracts (team deals and switching)

> **Milestone — Day 84 Living Racing World:** prospects, new teams, failed
> teams, and manufacturers evolve independently.

## Final Six Days — Alpha Preparation
- [ ] Day 85 — Complete save architecture (serialize the full career world)
- [ ] Day 86 — Game settings (difficulty, season length, autosave)
- [ ] Day 87 — Balance simulation (run 50–100 AI seasons)
- [ ] Day 88 — Bug fixing (rosters, finances, contracts, saves, edge cases)
- [ ] Day 89 — UI prototype (begin the graphical interface, preferably in Godot)
- [ ] Day 90 — Playable alpha (packaged career-mode build for playtesting)

> **Milestone — Day 90 Playable Alpha:** the complete career loop can be played
> repeatedly and evaluated for balance and fun.

## Milestone Summary
| Day | Name | Status |
| --- | --- | --- |
| 14 | Career Foundation | ✅ Done |
| 21 | Commissioner Loop | ✅ Done |
| 35 | Emergent Personalities | ✅ Done |
| 49 | Race Simulation Depth | ✅ Done |
| 63 | Business Ecosystem | ⬜ Pending |
| 77 | Political Career | ⬜ Pending |
| 84 | Living Racing World | ⬜ Pending |
| 90 | Playable Alpha | ⬜ Pending |
