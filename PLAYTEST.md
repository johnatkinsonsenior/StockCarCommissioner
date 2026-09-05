# Playtest guide — Stock Car Commissioner 0.1.0-alpha

This build is a packaged career-mode prototype. Play it to judge whether the
commissioner loop is fun, whether the league feels alive, and where balance
breaks down.

## Setup

You need Python 3.10+. Unpack the zip (or use this repository) and run:

    ./play.sh

Windows / no bash:

    python3 prototype/run_season.py

Saves land in a `saves/` folder next to the launchers. They do not travel
inside the zip.

Optional graphical desk (Godot 4.4 editor or binary on `PATH`, or `GODOT_BIN`):

    ./play_ui.sh

The Godot project is a prototype overlay. You do not need export templates.
Play and save through the Python career.

## Career loop

1. **Start new career** from the main menu.
2. Choose **difficulty** (Easy / Normal / Hard), **career length** (3 / 5 / 10
   seasons), and **autosave** (off, after each offseason, or after each race).
3. Each season walks preseason business, the 22-race premier calendar, a
   development-series feeder, incidents, hearings, discipline, owners, media,
   and the offseason.
4. Hearings present numbered choices. There is no universally correct ruling.
   Lenient calls can grow fans and controversy; strict calls can protect
   integrity and anger the grid.
5. Watch the dashboard meters: integrity, fan interest, controversy, owner
   pressure, driver sentiment, treasury, board confidence, and approval.
6. **Save current career** / **Load saved career** any time from the main menu.
   Autosave writes `saves/autosave.json` when enabled.

A shorter smoke path: **Run one quick season** from the main menu.

## What to evaluate

- Does a full career feel like running a league, not just clicking events?
- Do Liberty, Pioneer, and Summit (and later expansion / closures) stay
  distinct?
- Do money, contracts, TV, sponsors, and manufacturer deals matter?
- Is job security real on Hard without feeling random on Normal?
- Where did you want to quit, and where did you want one more season?

## Notes

- Game version `0.1.0-alpha`. Save files are schema `0.0.39`.
- Balance simulation (main menu item 6) is for developers, not required play.
- Item 7 launches the Godot prototype; item 8 exits.
