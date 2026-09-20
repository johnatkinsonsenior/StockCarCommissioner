# Known issues — Stock Car Commissioner 0.6.0-cup

Playtest zip for the **commissioner Cup desk** (Days 127–131).
Read this beside `PLAYTEST.md`. This is a commissioner-only office. There
is no team-owner or GM career.

## Current bug list

### Launch and packaging

- **Windows:** unpack the zip and double-click **Double-click to play.bat**.
  First launch downloads a private Python 3.12 and Godot 4.4 into `tools/`
  next to that file. The Microsoft Store `python.exe` shortcut is skipped
  on purpose — it cannot run the office and used to make the window flash
  closed. You need internet the first time. `play_ui.bat` is the same
  launcher.
- Git is not required. Export templates are not required.
- Headless Linux (no `DISPLAY`) opens Godot without a window and quits
  after a short tour. That is expected on a cloud box, not on a desktop.
- The Godot window title may append `(DEBUG)` because the office runs
  the editor binary, not an exported release. Cosmetic.

### Desk chrome

- **Continue desk** opening the office again resumes `saves/office.json`.
  It does not wipe a custom winter book. **New career** is the rewind.
- Mail badge counts unread letters. Opening a letter marks it read in
  this session; the JSON snapshot still treats a fresh load as unread
  until the letter is opened again.
- Standings before the first Advance show 0 points, 0 wins, and avg
  finish as —. That is preseason, not a missing table.
- History is empty until a championship is filed.
- Reports, Television last rating, and last gate are empty until you
  Advance a Cup weekend.
- Forty-row lists (Standings, Entries, Drivers, Sponsors) are long on
  purpose. Sortable columns are not in this zip.

### Winter book

- **Invite Chrysler** adds Valiant to the factory list. It does **not**
  rebadge Harbor Racing. Harbor stays Vanguard on the pinnacle book.
  1970s / 1980s still badge Harbor Valiant from the era book. Testers
  often expect the invite to swap Harbor’s badge.
- **Superbirds** run when aero specials are legal *or* homologate-to-run
  *and* Chrysler is invited so Valiant sits on the factory list. Banned
  specials keep the wing in the garage.
- **Pull plates** is series-wide. Plate *one* oval from **Named venues**
  (Thunder Valley, Atlantic Speedway, Coastal Superspeedway) without
  plating every superspeedway.
- **New career** rewinds the winter book to that era's inherited defaults.
  Load restores a custom book you saved.

### Simulation / analytics

- Legal specials raise TV, gate, and wreck risk. Banned specials keep
  the field even. Open superspeedways lift ratings and the wreck book;
  plates pack the show and cap it. The swing is visible on Reports and
  Television. It is not a full Baseball Mogul demand model yet — no
  per-track attendance history chart, no sortable splits.
- A 40-car field scales incident chance so a weekend does not become a
  40-car wreckfest every week. Big packs still happen; they are rarer
  than a naive 40× scale.
- Win on Sunday still prints on Dashboard and Rulebook after a Cup race
  has a winner.

### Not in this zip (parked)

- Prospect pool, development series, councils, board, Hall of Fame,
  Beyond era, four-door-as-coupe.
- Multi-car team organizations (one owner, two cars). This grid is
  forty independent entries. Multi-car shops return on the roadmap.
- Sortable report columns and a reopenable full race file (running
  order, lap-by-lap). Reports is the first race-file page.
- There will not be a franchise / team-owner mode.

## How this zip was checked

`python3 prototype/test_basics_desk.py` asserts the Cup rail (Reports,
Treasury, Television, Sponsors), forty unique entries and drivers,
portraits, era clamp, and a race log after Advance.
`python3 prototype/playtest_aero.py` still runs the writable-book loop.
