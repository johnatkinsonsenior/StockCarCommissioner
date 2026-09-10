# Stock Car Commissioner

A stock car league management simulation. You do not drive. You run the league.

Build the schedule, review incidents, issue penalties, negotiate television and
sponsor deals, keep owners and drivers in line, and try to still have a job
when the board meets.

## Current Version

0.3.0-aero (Aero Wars)

Save schema: 0.0.41

## Requirements

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

Windows: double-click `play_ui.bat`.

Godot is the commissioner office (sidebar, mail, checklist, Advance). The
look is Winston Cup crimson, gold, and white with a 16-bit sports-sim desk.
The pinnacle book opens on ten Cup shops and twenty drivers. Hearings,
Advance, save/load, and new career all run from the desk. History reopens
completed seasons; the Hall of Fame hangs retiree plaques; a gold ticker
cycles beat-writer headlines. A new career rewinds the opening world:
1970s (eight shops, Valiant still badging), 1980s (nine shops, Valiant
fading), pinnacle (ten shops), or beyond (twelve shops, fatter TV).
Each factory fields a homologated two-door coupe with a track map;
driver skill still owns the short tracks, aero owns the superspeedways.
Rulebook shows 16-bit body cards for this racing year — pick the legal
coupe each factory fields. Named superspeedways can break from the type
kit: plate this oval without plating every big track.
Export templates are not required. Python still simulates the season.

## Package a playtest build

    python3 prototype/package_alpha.py

Writes `dist/stock-car-commissioner-0.3.0-aero.zip`. Pass an output path if
you want the zip somewhere else.

## Development status

Era 4 ships Aero Wars: named coupes, track maps, and a commissioner-written
winter book. Named venues can override the type kit. Next on the roadmap:
homologation on the desk, then Detroit and garage lobby, then a playtest zip,
then Beyond.
