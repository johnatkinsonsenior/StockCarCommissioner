# Playtest guide — Stock Car Commissioner 0.6.0-cup

This build is a packaged **commissioner office** for a Winston Cup-style
series. You are the lead commissioner. You do not drive. You do not own
a shop. Play it to judge the weekly desk — mail, a forty-car Cup,
winter book, TV and the gate, Advance — and whether the reports feel
like OOTP / Baseball Mogul pointed at stock cars.

Also read `KNOWN_ISSUES.md`.

## Setup

Git is not required.

**Windows — this is the play button.** Unpack the zip and double-click:

    Double-click to play.bat

That is the whole setup. The first launch downloads a private Python and
Godot 4.4 into a `tools` folder next to the bat file. The Microsoft Store
`python.exe` shortcut is ignored (it cannot run the office). You do not
need to install Python or Godot yourself. You need internet the first time.

`play_ui.bat` does the same thing. A black window stays open with progress;
it only waits for a key if something failed.

Mac / Linux:

    ./play_ui.sh

Godot 4.4 on `PATH` (or `GODOT_BIN`) opens the office. Export templates
are not required. Opening the desk again **Continues** `saves/office.json`.

Terminal career (no office window):

    ./play.sh

Windows terminal: `play.bat`. Saves land in a `saves/` folder next to the
launchers. They do not travel inside the zip.

## Office loop

1. Open **Mail**. The welcome letter and any queued hearing sit there.
   Dashboard alerts arrive as memos. A gold ticker under the status bar
   carries beat copy.
2. Visit Dashboard, Standings, Entries, Rulebook, Television, and Mail
   to fill the first-weekend checklist. **Rulebook** is the winter body
   book: rewrite specials, template, plates, Chrysler, and the per-track
   kit. Homologation count, wheelbase class, and aero specials (banned /
   homologate-to-run / legal) sit as desk levers. Named venues can plate
   one oval without plating every superspeedway.
3. **Reports** is the race file. Empty until you Advance. After a weekend
   it shows TV, gate attendance and fill, cautions, wrecks, and driver
   form. The winter-book notes at the top tell you how specials and
   plates are swinging the show.
4. **Entries** and **Drivers** show the 16-bit car for that seat. Forty
   cars, forty named drivers, one driver per entry. Click a name for the
   card. **Treasury**, **Television**, and **Sponsors** are the commercial
   books. **History** is empty until a championship is filed.
5. Settings: **Save desk career** writes `desk.json`. **Load** restores a
   slot. **New career** rewinds the desk into 1970s, 1980s, or pinnacle.
   **Continue desk** reloads `office.json`.
6. Hearing choices write back to the same sim as the terminal. The hearing
   leaves the inbox once it is resolved.

Every era book seats **forty Cup cars**. **1970s** still badges Valiant
(Chrysler) on Harbor and several independent entries. **1980s** leaves
Harbor on Valiant. **Pinnacle** is Ford vs GM unless you invite Chrysler.
There is no Beyond picker on this desk. Multi-car team organizations are
not in this build.

This version does **not** show Prospects, Hearings as a nav page, Board,
or Hall of Fame. The Cup roster is the roster.

## Writable book

1. **Legalize specials** (or homologate-to-run) on Rulebook. Superbirds
   become a legal Valiant coupe once Chrysler is in the book. Reports
   should show a TV / gate / wreck swing.
2. **Pull restrictor plates** for a series-wide open superspeedway, or
   plate **Thunder Valley** alone from Named venues.
3. **Invite Chrysler**. Valiant joins the factory list. Harbor Racing
   stays Vanguard on the pinnacle book — the invite is not a rebadge.
4. Save the desk. Start a **1970s** New career. The inherited book comes
   back (specials banned, Harbor on Valiant, forty cars).
5. **Load** the slot from step 4. Specials, plates, Chrysler, and the
   venue kit should return.

Developer check:

    python3 prototype/test_basics_desk.py
    python3 prototype/playtest_aero.py

## What to evaluate

- Does sitting as commissioner of a forty-car Cup feel like OOTP / Front
  Office Football / Baseball Mogul pointed at stock cars?
- Do the Reports, Television, and Standings screens read like a league
  office — dense tables, TV, gate, wrecks — or like chrome?
- Can you tell Ford from Pontiac from Plymouth on the winter book, and
  see the car on the entry?
- Did the rules package you wrote change ratings and attendance the way
  you expected?
- Did you miss prospects, multi-car teams, or board politics — or were
  you glad they were gone?
- Where should this desk go next?

## Notes

- Game version `0.6.0-cup`. Save files are schema `0.0.41`.
- Balance simulation (main menu item 6) is for developers, not required play.
- Item 7 launches the Godot commissioner office; item 8 exits.
