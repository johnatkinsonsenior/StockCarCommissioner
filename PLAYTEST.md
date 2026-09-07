# Playtest guide — Stock Car Commissioner 0.3.0-aero

This build is a packaged **commissioner office**. Play it to judge whether
running the sanctioning body from the desk is fun, whether a ten-team Cup
field feels alive, and where balance breaks down across a career.

## Setup

You need Python 3.10+. Git is not required. Unpack the zip (or use this
repository) and run the Godot desk:

    ./play_ui.sh

Windows: double-click `play_ui.bat`, or from Command Prompt:

    play_ui.bat

Godot 4.4 editor or binary on `PATH` (or `GODOT_BIN`) opens the office.
Export templates are not required. If Godot is missing, the terminal loop
still works:

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
   per-track kit. **Advance** then runs a week: the next Cup race, a Race
   Control recap, and new mail.
3. Click a shop or driver for a full card. **History** is empty until a
   championship is filed. **Hall of Fame** hangs retirees who won a title,
   15 races, or 4,000 points.
4. Settings: **Save desk career** writes `desk.json`. **Load** restores a
   slot onto the office session. **New career** rewinds the desk (difficulty,
   length, autosave, era book) — grid, factories, and TV change with the
   book. **Continue desk** reloads `office.json`.
5. Hearing choices write back to the same sim as the terminal. The hearing
   leaves the inbox once it is resolved.

The pinnacle book seats Liberty, Pioneer, Summit, Harbor, Ironwood,
Redline, Coastal, Midland, Crown, and Blue Ridge — twenty drivers. Silver
Creek, Lakeside, Prairie, Piedmont, and Bayou wait outside for a charter.
**1970s** opens eight shops with Valiant on Harbor and Ironwood and a
thinner TV check. **1980s** opens nine; Valiant is fading at Harbor.
**Beyond** seats twelve (Silver Creek and Lakeside join), invites Valiant
back onto Harbor, and fattens treasury and TV.

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
- Do the ten Cup shops stay distinct through expansion and closures?
- Do money, contracts, TV, sponsors, and manufacturer deals matter?
- Is job security real on Hard without feeling random on Normal?
- Does a decade still feel playable, or do the meters run away?
- Where did you want to quit, and where did you want one more season?

## Notes

- Game version `0.3.0-aero`. Save files are schema `0.0.40`.
- Balance simulation (main menu item 6) is for developers, not required play.
- Item 7 launches the Godot commissioner office; item 8 exits.
