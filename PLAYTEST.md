# Playtest guide — Stock Car Commissioner 0.5.0-basics

This build is a packaged **commissioner office** for a Winston Cup-style
series. You are the lead commissioner. You do not drive. You do not own
a shop. Play it to judge whether the weekly desk — mail, Cup roster,
winter book, Advance — is the game you want to sit in.

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
2. Visit Dashboard, Standings, Teams, Drivers, Rulebook, and Mail to fill
   the first-weekend checklist. **Rulebook** is the winter body book:
   rewrite specials, template, plates, Chrysler, and the per-track kit.
   Homologation count, wheelbase class, and aero specials (banned /
   homologate-to-run / legal) sit as desk levers. Named venues can plate
   one oval without plating every superspeedway. **Advance** then runs a
   week: the next Cup race, a Race Control recap, and new mail.
3. Click a shop or driver for a full card. **History** is empty until a
   championship is filed.
4. Settings: **Save desk career** writes `desk.json`. **Load** restores a
   slot. **New career** rewinds the desk into 1970s, 1980s, or pinnacle.
   **Continue desk** reloads `office.json`.
5. Hearing choices write back to the same sim as the terminal. The hearing
   leaves the inbox once it is resolved.

The pinnacle book seats Liberty, Pioneer, Summit, Harbor, Ironwood,
Redline, Coastal, Midland, Crown, and Blue Ridge — twenty drivers.
**1970s** opens eight shops with Valiant still on the grid.
**1980s** opens nine. There is no Beyond picker on this desk.

This version does **not** show Prospects, Hearings as a nav page,
Treasury, Television, Sponsors, Board, or Hall of Fame. The Cup roster
is the roster.

## Writable book

1. **Legalize specials** (or homologate-to-run) on Rulebook. Superbirds
   become a legal Valiant coupe once Chrysler is in the book.
2. **Pull restrictor plates** for a series-wide open superspeedway, or
   plate **Thunder Valley** alone from Named venues.
3. **Invite Chrysler**. Valiant joins the factory list. Harbor Racing
   stays Vanguard on the pinnacle book — the invite is not a rebadge.
4. Save the desk. Start a **1970s** New career. The inherited book comes
   back (specials banned, Harbor on Valiant).
5. **Load** the slot from step 4. Specials, plates, Chrysler, and the
   venue kit should return.

Developer check:

    python3 prototype/test_basics_desk.py
    python3 prototype/playtest_aero.py

## What to evaluate

- Does sitting as commissioner of a Cup series feel like OOTP / Front
  Office Football / Baseball Mogul pointed at stock cars?
- Is the weekly cadence the right speed?
- Can you tell Ford from Pontiac from Plymouth on the winter book?
- Did you miss prospects, TV, or board politics — or were you glad they
  were gone?
- Where should this desk go next?

## Notes

- Game version `0.5.0-basics`. Save files are schema `0.0.41`.
- Balance simulation (main menu item 6) is for developers, not required play.
- Item 7 launches the Godot commissioner office; item 8 exits.
