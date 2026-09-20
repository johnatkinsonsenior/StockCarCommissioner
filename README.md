# Stock Car Commissioner

A stock car league management simulation. You do not drive. You run the
league — lead commissioner of a Winston Cup-style series in the
seventies, eighties, and nineties.

Write the winter book. Advance one week. Read the mail. Inspect the
forty-car Cup. Watch how the package you wrote hits TV, the gate, and
the wreck book. That is the game.

## Current Version

0.6.0-cup (Commissioner Cup desk)

Save schema: 0.0.41

## Requirements

Windows: unpack the zip and double-click **Double-click to play.bat**.
The first launch installs a private Python and Godot 4.4 into `tools/`.
You do not need to install either yourself.

Mac / Linux / developers:

- Python 3.10 or newer
- Optional: [Godot 4.4](https://godotengine.org/download) for the graphical office desk

## Play a career

From this folder (or an unpacked playtest zip). Git is not required.

    ./play.sh

Windows: double-click `play.bat`.

That opens the terminal career loop. See `PLAYTEST.md` for the full loop.

The Godot commissioner office (recommended):

    ./play_ui.sh

**Windows: double-click `Double-click to play.bat`.** That is the play
button. `play_ui.bat` does the same. First launch downloads Godot 4.4.

Godot is the commissioner office (sidebar, mail, checklist, Advance).
The look is Winston Cup crimson, gold, and white with a 16-bit sports-sim
desk. Every era book opens **forty Cup cars and forty named drivers** —
one driver per entry. Multi-car team organizations come later.
**New career** rewinds the opening world: 1970s, 1980s, or pinnacle
(late ’80s–mid ’90s). Each factory fields a homologated two-door coupe
with a 16-bit car portrait on Standings, Entries, Drivers, and Reports.
Rulebook is the winter book: pick the legal coupe, set homologation and
wheelbase, legalize or ban aero specials, plate a named oval. Mail
carries rules, safety, and garage hearings. Advance runs the next week.

**Reports** is the race file — attendance, TV rating, wrecks, driver
form. The winter book you write moves those numbers, Baseball Mogul
style. **Treasury**, **Television**, and **Sponsors** sit on the Business
rail because they are commissioner work.

This build hides prospects, councils, the board, and the Hall of Fame.
The sim still has them; the desk does not. There is no team-owner career.

## Package a playtest build

    python3 prototype/package_alpha.py

Writes `dist/stock-car-commissioner-0.6.0-cup.zip`. Pass an output
path if you want the zip somewhere else. The zip includes `PLAYTEST.md`
and `KNOWN_ISSUES.md`. Git is not required to play.

## Development status

This version is the commissioner Cup desk: forty single-car entries,
weekly Advance, winter book, TV / gate / wreck analytics. Design peers
are OOTP, Front Office Football, and Baseball Mogul — league office,
not franchise. Multi-car shops, prospects, and Beyond stay parked.
