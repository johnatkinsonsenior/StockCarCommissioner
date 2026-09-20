# Stock Car Commissioner

A stock car league management simulation. You do not drive. You run the
league — lead commissioner of a Winston Cup-style series in the
seventies, eighties, and nineties.

Write the winter book. Advance one week. Read the mail. Inspect the Cup
roster. That is the game.

## Current Version

0.5.0-basics (Commissioner Basics)

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
desk. The pinnacle book opens on ten Cup shops and twenty drivers.
**New career** rewinds the opening world: 1970s (eight shops, Chrysler
still badging), 1980s (nine shops), or pinnacle (ten shops).
Each factory fields a homologated two-door coupe with a track map.
Rulebook shows 16-bit body cards for this racing year — pick the legal
coupe each factory fields, set homologation and wheelbase, legalize or
ban aero specials, plate a named oval. Mail carries rules, safety, and
garage hearings. Advance runs the next week.

This build hides prospects, councils, the board, TV, sponsors, and the
Hall of Fame. The sim still has them; the desk does not. There is no
team-owner career.

## Package a playtest build

    python3 prototype/package_alpha.py

Writes `dist/stock-car-commissioner-0.5.0-basics.zip`. Pass an output
path if you want the zip somewhere else. The zip includes `PLAYTEST.md`
and `KNOWN_ISSUES.md`. Git is not required to play.

## Development status

This version is the commissioner-basics desk: Cup roster, weekly
Advance, winter book. Design peers are OOTP, Front Office Football, and
Baseball Mogul — league office, not franchise. Next depends on player
feedback. Beyond and extra politics stay parked.
