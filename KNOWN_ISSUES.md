# Known issues — Stock Car Commissioner 0.5.0-basics

Playtest zip for the **commissioner-basics desk** (Days 127–128).
Read this beside `PLAYTEST.md`. This is a commissioner-only office. There
is no team-owner or GM career.

## Launch

- **Windows:** unpack the zip and double-click **Double-click to play.bat**.
  First launch downloads a private Python 3.12 and Godot 4.4 into `tools/`
  next to that file. The Microsoft Store `python.exe` shortcut is skipped
  on purpose — it cannot run the office and used to make the window flash
  closed. You need internet the first time. `play_ui.bat` is the same
  launcher.
- **Continue desk:** opening the office again resumes `saves/office.json`.
  It does not wipe a custom winter book. **New career** is the rewind.
- Git is not required. Export templates are not required.
- Headless Linux (no `DISPLAY`) opens Godot without a window and quits
  after a short tour. That is expected on a cloud box, not on a desktop.

## This desk

- Nav is Dashboard, Mail, Standings, Schedule, Teams, Drivers, Rulebook,
  History, Settings. Prospects, Board, Treasury, Television, Sponsors,
  Hearings (as a page), and Hall of Fame are hidden.
- New career eras are **1970s**, **1980s**, and **pinnacle**. Beyond is
  parked. Picking Beyond from an old save path clamps to pinnacle.
- Hearings in Mail are rules, safety, owner/driver complaints, and
  rivalries. Factory lobby, kit lobby, councils, and charter fights
  stay off this inbox.
- The Cup roster is the roster. Young-driver / prospect pages are gone.

## Winter book

- **Invite Chrysler** adds Valiant to the factory list. It does **not**
  rebadge Harbor Racing. Harbor stays Vanguard on the pinnacle book.
  1970s / 1980s still badge Harbor Valiant from the era book.
- **Superbirds** run when aero specials are legal *or* homologate-to-run
  *and* Chrysler is invited so Valiant sits on the factory list. Banned
  specials keep the wing in the garage.
- **Pull plates** is series-wide. Plate *one* oval from **Named venues**
  (Thunder Valley, Atlantic Speedway, Coastal Superspeedway) without
  plating every superspeedway.
- **New career** rewinds the winter book to that era's inherited defaults.
  Load restores a custom book you saved.

## Meters and career

- Legal specials raise fan interest and controversy. That is the Aero Wars
  trade.
- History is empty until a championship is filed.
- Win on Sunday still prints on Dashboard and Rulebook after a Cup race
  has a winner.

## Not in this zip (parked)

- Prospect pool, development series, councils, board, TV desk, sponsors
  desk, Hall of Fame, Beyond era, four-door-as-coupe.
- Sortable reports and a reopenable race file (later density work).
- There will not be a franchise / team-owner mode.

## How this zip was checked

`python3 prototype/test_basics_desk.py` asserts the stripped rail, filtered
hearings, empty prospect book, and era clamp.
`python3 prototype/playtest_aero.py` still runs the writable-book loop.
