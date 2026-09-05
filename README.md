# Stock Car Commissioner

A stock car league management simulation. You do not drive. You run the league.

Build the schedule, review incidents, issue penalties, negotiate television and
sponsor deals, keep owners and drivers in line, and try to still have a job
when the board meets.

## Current Version

0.1.0-alpha (Playable Alpha)

Save schema: 0.0.39

## Requirements

- Python 3.10 or newer
- Optional: [Godot 4.4](https://godotengine.org/download) for the graphical UI prototype

## Play a career

From this folder (or an unpacked playtest zip):

    ./play.sh

That opens the terminal career loop. Start a new career, set difficulty and
length, then work through seasons of races, hearings, and league business.
See `PLAYTEST.md` for the full loop.

The optional Godot desk:

    ./play_ui.sh

Godot is the commissioner office (sidebar, mail, checklist, Advance). Export
templates are not required. The Python career still simulates the season.

## Package a playtest build

    python3 prototype/package_alpha.py

Writes `dist/stock-car-commissioner-0.1.0-alpha.zip`. Pass an output path if
you want the zip somewhere else.

## Development status

The 90-day plan through playable alpha is complete. The career loop can be
played repeatedly and evaluated for balance and fun.
