# Known issues — Stock Car Commissioner 0.4.0-aero

Playtest zip for the **writable Aero Wars book** (Era 6, Days 123–126).
Read this beside `PLAYTEST.md`. This is a commissioner-only office. There
is no team-owner or GM career.

## Launch

- **Windows:** `play_ui.bat` needs Python 3.10+ *and* Godot 4.4. If the
  window flashes, run it from Command Prompt — it now pauses on failure.
  Set `GODOT_BIN` if Godot is not on `PATH` (Downloads of
  `Godot_v4.4-stable_win64.exe` are searched automatically).
- **Continue desk:** opening `play_ui` again resumes `saves/office.json`.
  It does not wipe a custom winter book. **New career** is the rewind.
- Git is not required. Export templates are not required.
- Headless Linux (no `DISPLAY`) opens Godot without a window and quits
  after a short tour. That is expected on a cloud box, not on a desktop.

## Winter book

- **Invite Chrysler** adds Valiant to the factory list. It does **not**
  rebadge Harbor Racing. Harbor stays Vanguard on the pinnacle book.
  1970s / 1980s / Beyond still badge Harbor Valiant from the era book.
- **Superbirds** run when aero specials are legal *or* homologate-to-run
  *and* Chrysler is invited so Valiant sits on the factory list. Banned
  specials keep the wing in the garage.
- **Pull plates** is series-wide. Plate *one* oval from **Named venues**
  (Thunder Valley, Atlantic Speedway, Coastal Superspeedway) without
  plating every superspeedway.
- **New career** rewinds the winter book to that era's inherited defaults.
  A custom Superbird / no-plate / Chrysler book lives in the save slot you
  wrote. **Load** restores it, including Valiant on the roster.
- Balance simulation (main menu item 6) does not rewrite the winter book.
  Factory and kit lobby mail still arrive; the auto-commissioner holds.

## Meters and career

- Legal specials raise fan interest and controversy. That is the Aero Wars
  trade. Watch controversy if you leave Superbirds legal for a decade.
- Win on Sunday is a health line on Dashboard, Board, and Rulebook — not
  flavor text. It stays quiet until a Cup race has a winner.
- History is empty until a championship is filed. Hall of Fame hangs
  retirees who won a title, 15 races, or 4,000 points.

## Not in this zip (later eras)

- **Beyond** four-door-as-coupe (Taurus analog) is Era 7.
- Sortable reports, a reopenable race file, and a weekly work inbox are
  Era 8 (league-office density).
- There will not be a franchise / team-owner mode.

## How this zip was checked

`python3 prototype/playtest_aero.py` runs the writable-book loop, a
save/load plus era-rewind pass, and a twelve-week tester career
(meters in range, Superbirds still legal, plates still pulled, Harbor
still Vanguard).
