# Stock Car Commissioner

A stock car league management simulation. You do not drive. You run the league.

Build the schedule, review incidents, issue penalties, negotiate television and
sponsor deals, keep owners and drivers in line, and try to still have a job
when the board meets.

## Current Version

0.4.1-aero (Playable Aero Wars)

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

That opens the terminal career loop. Start a new career, set difficulty,
length, and era book, then work through seasons of races, hearings, and
league business. See `PLAYTEST.md` for the full loop.

The Godot commissioner office (recommended for playtesters):

    ./play_ui.sh

**Windows: double-click `Double-click to play.bat`.** That is the play
button. `play_ui.bat` does the same. First launch downloads Godot 4.4.

Godot is the commissioner office (sidebar, mail, checklist, Advance). The
look is Winston Cup crimson, gold, and white with a 16-bit sports-sim desk.
The pinnacle book opens on ten Cup shops and twenty drivers. Hearings,
Advance, save/load, and new career all run from the desk. History reopens
completed seasons; the Hall of Fame hangs retiree plaques; a gold ticker
cycles beat-writer headlines. Opening the desk again Continues
`saves/office.json`; it does not wipe a custom winter book. **New career**
rewinds the opening world: 1970s (eight shops, Valiant still badging),
1980s (nine shops, Valiant fading), pinnacle (ten shops), or beyond
(twelve shops, fatter TV).
Each factory fields a homologated two-door coupe with a track map;
driver skill still owns the short tracks, aero owns the superspeedways.
Rulebook shows 16-bit body cards for this racing year — pick the legal
coupe each factory fields. Named superspeedways can break from the type
kit: plate this oval without plating every big track. Homologation count
(200 / 500 / per-dealer), wheelbase class (110 / 115 / mixed), and
aero specials (banned / homologate-to-run / legal) sit on Rulebook as
winter-book levers. Detroit, owners, and the garage lobby that book
by mail. A one-make runaway or a plated wreck-fest files a hearing.
Win on Sunday is a desk health line, not flavor text.
Export templates are not required. Python still simulates the season.

## Package a playtest build

    python3 prototype/package_alpha.py

Writes `dist/stock-car-commissioner-0.4.1-aero.zip`. Pass an output path if
you want the zip somewhere else. The zip includes `PLAYTEST.md` and
`KNOWN_ISSUES.md`. Git is not required to play.

## Development status

Era 6 is the playable Aero Wars zip: legalize specials, pull plates,
invite Chrysler, plate one oval, save, and load that book after an era
rewind. This is a **commissioner-only** product (OOTP world, Front Office
Football weeks, Baseball Mogul reports) — no team-owner career. Next on
the roadmap: Beyond, then league-office density.
