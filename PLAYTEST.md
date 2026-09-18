# Playtest guide — Stock Car Commissioner 0.4.0-aero

This build is a packaged **commissioner office** with a writable Aero Wars
book. Play it to judge whether running the sanctioning body from the desk
is fun, whether a ten-team Cup field feels alive, and whether *your*
Winston Cup — Superbirds, no plates, Chrysler invited — is the sport you
meant to sell.

Also read `KNOWN_ISSUES.md`.

## Setup

You need Python 3.10+. Git is not required. Unpack the zip (or use this
repository) and run the Godot desk:

    ./play_ui.sh

Windows: double-click `play_ui.bat`, or from Command Prompt:

    play_ui.bat

If the window flashes and closes, run `play_ui.bat` from Command Prompt
so the error stays on screen. You need Python 3.10+ **and** Godot 4.4.
Godot 4.4 editor or binary on `PATH` (or `GODOT_BIN`) opens the office.
Export templates are not required. Opening the desk again **Continues**
`saves/office.json`; it does not wipe a custom winter book. If Godot is
missing, the terminal loop still works:

    ./play.sh

Windows: `play.bat` uses the `py` launcher when installed, otherwise
`python`. Saves land in a `saves/` folder next to the launchers. They do
not travel inside the zip.

## Office loop

1. Open **Mail**. The queued hearing sits as a letter. Dashboard alerts
   arrive as memos. A gold ticker under the status bar carries beat copy.
2. Visit Dashboard, Standings, Teams, Television, Drivers, Rulebook, Board,
   and Mail to fill the first-weekend checklist. **Rulebook** is the winter
   body book: rewrite specials, template, plates, Chrysler, and the
   per-track kit. **Homologation count** (200 / 500 / per-dealer) and
   **wheelbase class** (110-inch downsized, 115-inch intermediates, or
   mixed) sit on Rulebook as desk levers. **Aero specials** is a three-way
   radio: banned, homologate-to-run, or legal. Detroit mail and a kit
   lobby sit in the inbox beside the winter-book hearing. **Named venues**
   can plate one oval without plating every superspeedway. Dashboard,
   Board, and Rulebook show **Win on Sunday** factory health. **Advance**
   then runs a week: the next Cup race, a Race Control recap, and new mail.
3. Click a shop or driver for a full card. **History** is empty until a
   championship is filed. **Hall of Fame** hangs retirees who won a title,
   15 races, or 4,000 points.
4. Settings: **Save desk career** writes `desk.json`. **Load** restores a
   slot onto the office session. **New career** rewinds the desk (difficulty,
   length, autosave, era book) — grid, factories, TV, *and the winter book*
   change with the era. A custom Superbird book does not ride into a 1970s
   rewind; Load the slot you saved. **Continue desk** reloads `office.json`.
5. Hearing choices write back to the same sim as the terminal. The hearing
   leaves the inbox once it is resolved.

The pinnacle book seats Liberty, Pioneer, Summit, Harbor, Ironwood,
Redline, Coastal, Midland, Crown, and Blue Ridge — twenty drivers. Silver
Creek, Lakeside, Prairie, Piedmont, and Bayou wait outside for a charter.
**1970s** opens eight shops with Valiant on Harbor and Ironwood and a
thinner TV check. **1980s** opens nine; Valiant is fading at Harbor.
**Beyond** seats twelve (Silver Creek and Lakeside join), invites Valiant
back onto Harbor, and fattens treasury and TV.

## Writable book (Era 6)

This is the pass that decides whether the office is playable as a custom
Winston Cup, not only as a frozen 1992 reprint.

1. **Legalize specials** (or homologate-to-run) on Rulebook. Superbirds
   become a legal Valiant coupe once Chrysler is in the book.
2. **Pull restrictor plates** for a series-wide open superspeedway, or
   plate **Thunder Valley** alone from Named venues.
3. **Invite Chrysler**. Valiant joins the factory list. Harbor Racing
   stays Vanguard on the pinnacle book — the invite is not a rebadge.
4. Save the desk. Start a **1970s** New career. The inherited book comes
   back (specials banned, Harbor on Valiant, no Thunder Valley override).
5. **Load** the slot from step 4. Specials, plates, Chrysler, and the
   venue kit should return with Valiant still on the roster.

Developer check (optional):

    python3 prototype/playtest_aero.py

## Terminal loop

1. **Start new career** from the main menu.
2. Choose **difficulty** (Easy / Normal / Hard), **career length** (3 / 5 / 10
   seasons), and **autosave** (off, after each offseason, or after each race).
3. Each season walks preseason business, the 22-race premier calendar, a
   development-series feeder, incidents, hearings, discipline, owners, media,
   and the offseason.
4. A shorter smoke path: **Run one quick season**.

## What to evaluate

- Does a full career feel like running a league, not just clicking events?
- Did you ever want to “take over a team,” or did the office job hold?
- Can you tell your Winston Cup from the inherited era book?
- Did Invite Chrysler rebadge Harbor? It should not.
- Did Superbirds show once specials were legal and Chrysler was in?
- Did Load restore a custom book after a 1970s New career?
- Do the ten Cup shops stay distinct through expansion and closures?
- Do money, contracts, TV, sponsors, and manufacturer deals matter?
- Is job security real on Hard without feeling random on Normal?
- Does a decade still feel playable, or do the meters run away?
- Where did you want to quit, and where did you want one more season?

## Notes

- Game version `0.4.0-aero`. Save files are schema `0.0.41`.
- Balance simulation (main menu item 6) is for developers, not required play.
- Item 7 launches the Godot commissioner office; item 8 exits.
