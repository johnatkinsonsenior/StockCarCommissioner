# Stock Car Commissioner

## Vision

Create the deepest stock car league management simulation ever built.

The player does not drive.

The player runs the league.

## Player Fantasy

• Commissioner
• League President
• Competition Director
• Business Executive

## Core Gameplay

Build the schedule

↓

Run races

↓

Handle incidents

↓

Issue penalties

↓

Grow the league

↓

Repeat

## Commissioner Discipline System

Following reviewable race incidents, the commissioner may choose from several disciplinary actions:

1. No action
2. Official warning
3. Financial fine
4. Championship points penalty
5. Race suspension

Post-race investigation packets (evidence, assigned blame, involved cars) feed this same review. There is no second investigation screen.

Each ruling affects different stakeholders and league metrics.

### Commissioner Metrics

- League Integrity
- Fan Interest
- Controversy
- Fines Collected

### Driver Consequences

- Morale changes
- Warnings
- Fines
- Points penalties
- Suspensions

There is no universally correct disciplinary decision. Lenient rulings may increase excitement but damage league integrity. Severe rulings may strengthen integrity while reducing fan interest and angering drivers or teams.

## Driver Personalities and Relationships

Drivers have individual personality types that influence how they react to commissioner decisions.

### Personality Types

- Professional
- Veteran
- Temperamental
- Rookie
- Aggressive
- Popular

Those types still drive commissioner-ruling reactions. Each driver also has numerical traits on top of the type:

- Temperament
- Loyalty
- Ambition
- Media skill
- Risk tolerance

Traits shade how strongly a type reacts. They do not replace the type.

### Happiness

Driver morale is the happiness track. It is pulled toward:

- Team satisfaction
- Contract satisfaction
- Competitive frustration

There is no second mood meter. Labels such as Content, Settled, Restless, and Unhappy are read from morale.

### Reputation

Popularity is fan fame. Reputation is paddock standing. Credibility is whether the garage believes the driver. Reckless incidents hurt credibility; race wins raise reputation.

### Commissioner Trust

Each driver maintains a commissioner trust rating from 0 to 100.

Trust may increase or decrease based on:

- Warnings
- Fines
- Points penalties
- Suspensions
- Leniency toward rivals
- Consistency of league enforcement

Low trust may eventually cause drivers to:

- Publicly criticize the commissioner
- Appeal penalties
- Threaten to leave the series
- Encourage other drivers to protest
- Refuse promotional appearances

### Rivalries, Feuds, and Friendships

Drivers keep a named primary rival with a numerical intensity that escalates after contact, arguments, and lenient rulings, and decays in quiet offseasons. Rookie rival assignment and retired-rival cleanup still use that name field.

Heated rivalries can become long-term feuds that persist across races and seasons, with intensity and status (active, cooling, dormant) stored in career saves.

Drivers also have allies, teammate bonds, and friendship strength. A commissioner's ruling on one driver can move a rival and an ally.

Rivalry contact, garage arguments, and feud reviews use the same decision-event framework as owner and driver complaints. They do not add a separate crash-physics system.

## Season History and Awards

At the end of each season, the game creates a permanent season record.

### Season Awards

- Series Champion
- Most Race Wins
- Most Popular Driver
- Most Reliable Team
- Commissioner Performance Grade

### Commissioner Grade

The commissioner receives an overall grade based on:

- League Integrity: 45%
- Fan Interest: 35%
- Controversy Management: 20%

### Historical Records

Each season report includes:

- Race results
- Driver standings
- Team finances
- Disciplinary actions
- Driver relationships
- League health
- Season award winners

Future versions will use historical reports to create multi-season records, career statistics, hall-of-fame selections, and league evolution.

## Career Mode

Career mode allows the commissioner to manage the racing series across multiple seasons.

### Persistent Driver Information

The following information continues between seasons:

- Career starts
- Career wins
- Career DNFs
- Career points
- Career earnings
- Championships
- Popularity
- Reputation and credibility
- Morale and happiness components
- Personality type and numerical traits
- Track-type skills (short track, road course, intermediate, superspeedway)
- Commissioner trust
- Rival name and rivalry intensity
- Feuds
- Allies, friendships, and teammate bonds
- Prospect-pool names, pathways, and readiness

### Persistent Team Information

The following team information continues between seasons:

- Team budget
- Career prize money
- Career victories
- Championships
- Owner personality, wealth, patience, and priorities
- Prestige and reputation
- Performance trends
- Facility level
- Engineering strength
- Pit crew rating
- Financial health

### Season Resets

At the start of each new season, these values reset:

- Championship points
- Season wins
- Season earnings
- Season starts
- Season DNFs
- Warnings
- Fines
- Points penalties
- Suspensions

### Championship History

Every completed season records:

- Champion
- Championship team
- Final points
- Race wins
- Commissioner grade
- League health
- Final standings
- Race results

## Driver Aging and Career Progression

Drivers age by one year after each completed season.

### Development Stages

- Young Prospect: rapid improvement
- Prime Driver: modest improvement
- Veteran: increased consistency with limited growth
- Aging Veteran: gradual performance decline
- Late Career: significant decline and retirement risk

### Retirement

Retirement probability is influenced by:

- Age
- Championships
- Morale
- Commissioner trust

When a driver retires, the open team seat is filled by a generated rookie.

### Rookie Drivers

Generated rookies receive:

- A unique name
- An age between 19 and 23
- Starting performance ratings
- A personality type and numerical traits
- Popularity, reputation, and credibility
- A team assignment
- A possible initial rivalry with intensity

Retired drivers remain in career history and retain their final statistics.

### Prospect Pool

Named drivers exist **off the premier grid**. They race Super Lates, Late Models, Modifieds, dirt late models, or touring series and wait in a talent book with a scouting **readiness** grade. Those names fill the **National Development Series**, an eight-race feeder championship with its own calendar, points, and champion. The commissioner can read the pool and the feeder standings. After the feeder season, waiting drivers **progress**: they age a year and their readiness (and a little raw speed) moves with how they finished. A premier-ready prospect (readiness 80+) earns the next open premier seat when a driver retires, instead of a generated rookie. The graduate keeps their pathway as origin, signs a rookie deal, and a new name refills the waiting book. If nobody is ready, a generated rookie still fills the seat. A thin pool raises a dashboard alert. An empty pool leaves the feeder with no field. The book persists across seasons and saves.

### Development Series

The National Development Series is the lower-level championship under the premier grid. Prospects race eight feeder venues (short tracks and modest intermediates) on the same weekends as the first eight premier races. Scoring is a fixed ten-place table, independent of the premier points policy. Crashes still finish the race on half points. The dashboard shows the leader or champion and how many of eight are complete. Postseason reprints the feeder table and files it in career history. This is not a second television product.

### Prospect Progression

Feeder results write the next offseason's scouting book. The champion jumps the most; a podium, a top-five, and the rest of the field take smaller readiness ticks. The champion also gains a little speed and consistency. When a premier seat opens, the highest-readiness graduate who has crossed the premier-ready floor is called up. The dashboard stores the last call-up. Ready names waiting for a seat raise an alert.

### New Team Entry

Named owners apply for a premier charter. Two shops wait in the opening book: **Ivy Navarro** at **Harbor Racing**, then **Grant Holcomb** at **Ironwood Motorsports**. Both arrive as Independent manufacturers. Offseason, after retirements and call-ups, the commissioner hears the next applicant on the same decision framework: **grant a charter**, **defer the application**, or **deny the application**.

A grant admits the shop, staffs two seats from the prospect pool (or generated rookies), and raises fan interest while incumbent owners feel the squeeze. The owner council gains the new seat automatically. Defer keeps the applicant first in line. Deny drops them from the book. The field caps at five teams; an empty book or a full grid skips the hearing. Legacy saves without an applicant list load an empty book. An insolvent shop can lose its charter in the offseason.

### Team Closure

Insolvent teams face a **charter review** after offseason finances. Three answers sit on the same decision framework: **withdraw the charter** (the shop folds, drivers are released into the prospect pool as Premier-ready names, fan interest falls, remaining owners ease), **extend a bridge loan** (league treasury cash lifts the shop off Insolvent; integrity takes a hit and incumbents resent the rescue), or **defer the hearing** (they stay insolvent another year). The field cannot drop below two teams; at that floor an insolvent shop remains on the grid. The dashboard shows the last review and the live field size. An insolvent shop raises an alert.

### Manufacturers

Named automakers badge the grid. Opening factories are **Vanguard** (Durability), **Apex** (Speed), and **Falcon** (Balance). Expansion shops arrive **Independent** (Unaligned). Each identity slightly shifts race pace and mechanical risk. Teams hold a **factory contract** with years remaining. Offseason, expired or unsigned shops may renew, court a new factory, or stay Independent. A proposed switch goes to the commissioner: **approve the switch**, **hold the current badge**, or **force Independent**. Retooling a live factory costs shop budget. The dashboard shows the last move and the next expiring deal. A last-year contract or an unsigned shop raises an alert.

## Team Finances and Offseason Spending

Teams manage a persistent budget across seasons. Income comes from race prize money and offseason sponsorship deals. Expenses include driver salaries, operating costs, and optional investments.

### Sponsorship Revenue

Offseason sponsorship income is based on:

- Base sponsor support
- Facility level
- Team prestige and sponsor appeal
- Championships
- Season race wins
- Average driver popularity

Struggling and insolvent teams may receive reduced sponsorship offers.

The league also keeps a market of named sponsor companies. Each company has:

- An industry (automotive, energy, finance, retail, telecom, beverage, tools, insurance, electronics, or logistics)
- Spending power derived from wealth
- Preferences for prestige, on-track performance, public exposure, and conduct
- A risk posture (cautious brands avoid struggling or aggressive teams; bold brands tolerate them)
- An optional manufacturer affinity

Offseason team revenue now comes from a named main-sponsor contract when one exists. Signed brands score the season they just backed. A scandal can pull a live deal. The series itself can hold naming rights and official partners. Companies enter and leave the sponsor market over time.

### Team Main Sponsors

Each organization can hold one exclusive main-sponsor contract (the hood/title deal). Brands pick teams using the same preference model, with extra caution toward struggling or insolvent shops. Deal length is two to four years. The annual check is a large slice of that brand's spending power and goes to the **team**. Prestige-first matching assigns leftover brands when a career starts. A brand can title a team and still back a driver personally.

A team **may run with no main sponsor**. Unsponsored entries collect only a contingency stipend (about a third of the old blanket check). Losing a main sponsor costs prestige and raises owner pressure. The dashboard flags `No main sponsor`.

### Driver Endorsements

Drivers can hold one personal endorsement at a time. Brands pick drivers using the same preference model (exposure, conduct, performance, risk). A company backs at most one driver. Deal length is one to three years and the annual check is a slice of that brand's spending power. The money goes to the driver, not the team. Signing a deal lifts morale, contract satisfaction, and popularity slightly. Deals are matched when a career starts, paid and renewed in the offseason, and drop when they expire or a driver retires.

### Sponsor Objectives

Every signed title deal and personal endorsement starts content. After each regular season the brand grades delivery against three objectives, weighted by its own tastes:

- Performance: wins, points, and (for teams) organization results
- Exposure: popularity and media presence
- Conduct: reputation and credibility, reduced by warnings, suspensions, and wrecks

That score moves a 0–100 satisfaction mood (thrilled, pleased, content, restless, unhappy). Mood scales the next offseason check up or down. If a deal expires while the brand is unhappy, it will not immediately re-sign the same team or driver; another company may still step in. The dashboard flags restless title sponsors and restless endorsements.

### Sponsor Conflicts

Cautious and conduct-first brands can pull a live deal when scandal piles up. Conflict heat comes from low satisfaction, poor conduct, warnings, suspensions, insolvent shops, and league controversy. Bold brands tolerate more. A commissioner ruling on a wreck shocks related deals. Personal endorsers can walk immediately after an unpunished incident or a suspension. Title sponsors take the shock and decide after the season, unless they are already unhappy.

Withdrawal cancels the remaining years. The team or driver goes unsponsored, takes a prestige/morale hit, and that brand will not rematch the same party this offseason. The next check is lost. The dashboard flags `Sponsor walked`. Replacements wait until the offseason market.

### League Sponsorship

The series can hold one **naming-rights** partner. That brand's name goes on the series (for example, the Northstar Capital Stock Car Series). The annual check is a large slice of the company's spending power and goes to the **league treasury**, not to a team. Deal length is three to five years. Wealthy, prestige-seeking brands are first in line. The series **may run without a title sponsor**; the dashboard flags `No series sponsor`.

Up to two **official partners** sit alongside naming rights (official insurance, telecom, and so on). Those checks are smaller. A brand can name the series or be an official partner, not both, but it can still title a team or back a driver.

League deals use the same mood, pay, expiry, and withdrawal rules as team and driver contracts. They grade the series on fan interest, integrity, and controversy. Losing naming rights drops fan interest and raises controversy.

### Sponsorship Market

Named companies sit in an active market of eight to fourteen brands. Ten more companies wait as prospects. Each offseason, after existing deals pay and rematch, the idle brand with the lowest league interest leaves if the market is above the floor, and the waiting prospect with the highest interest enters if the market is below the ceiling.

A brand with a live title deal, endorsement, naming-rights contract, or official-partner slot never leaves. A departed company joins the prospect list and can return later. New arrivals immediately bid on leftover unsigned slots. The dashboard shows active, idle, and waiting counts, and flags a thin market or this season's enter/leave moves.

### Operating Expenses

Each offseason teams pay:

- Base operating costs
- Facility maintenance
- Driver salaries

### Facility Upgrades

Teams may upgrade their shop up to facility level 5. The shop rating is derived from that level. Upgrades improve reliability, prestige, and engineering, and increase future sponsorship potential.

### Performance Investment

Profitable teams may invest in car, crew, and engineering development during the offseason, improving race performance.

### Financial Health

Team financial health is tracked across four levels on a single money-status track:

- Profitable
- Stable
- Struggling
- Insolvent

Struggling teams face reduced morale, performance penalties, and limited investment options. Insolvent teams suffer severe performance declines and sponsor discounts but remain entered in the series.

## Television

The league keeps a market of named television networks. Named rights deals attach to them. Each race is rated for television audience. Live gate attendance is a separate book. Each completed weekend files media headlines. Each broadcaster has:

- A kind (national, cable, regional, or motorsport)
- Audience reach and bid power
- Preferences for prestige, on-track excitement, star drivers, and product integrity
- A risk posture (cautious networks want a clean, respectable series; bold networks tolerate spectacle)
- Optional favorite track types

Horizon Sports is the opening national flagship. Peakline Cable and Coastline Media are sports and entertainment cables. Heartland Broadcast is a cautious regional. Redline TV is a smaller motorsport specialist. Interest in the series rises with fan interest and integrity, and falls with controversy for cautious brands.

### TV Contracts

The series can hold one exclusive **television-rights** contract. Networks bid a multi-year package. The annual bid is a large slice of that broadcaster's rights value, scaled by interest in the league. Deal length is three to six years; wealthier, prestige-seeking networks want longer deals. The highest bid wins. The annual check goes to the **league treasury**.

Horizon Sports wins the opening auction (six years). The series **may run without a TV deal**; the dashboard flags `No TV deal`. Losing coverage without a replacement drops fan interest and raises controversy. If a deal expires while the network is unhappy, it will not immediately re-bid; another broadcaster may still step in.

### TV Ratings

Each race produces a television rating (0–100) and an estimated viewer count. The score rises with fan interest, star drivers, cautions, wrecks, and marquee tracks (superspeedways especially). The rights-holder's tastes reshape that number: excitement-first networks lift wreck-filled shows; integrity-first networks prefer a clean, respectable product. Unsigned weekends still get a syndicated estimate.

The dashboard shows the last race, the season average, and a multi-season trend (stable, rising, falling). After the championship the rights holder grades delivery against those ratings. Mood then scales the next offseason TV check. Soft or sliding ratings raise a dashboard alert.

### Race Popularity

Each race weekend also produces a **gate** — how many people bought a ticket, kept separate from the TV rating. Demand is set before the green flag: fan interest, advertised star drivers, track type, purse, and weather. Short tracks pack a smaller house; superspeedways are harder to fill. Cautions and wrecks lift television, not the live crowd. Rain keeps people home more than it hurts the broadcast. Attendance never exceeds seating capacity. A 97% house counts as sold out.

The dashboard shows the last house, the season-average fill, and a multi-season attendance trend. Soft or sliding gates raise a dashboard alert. Television and gate stay on separate books.

### Media Stories

Each completed weekend files one to three **media stories**: a lead headline plus optional follow-ups. Copy is generated from the facts already on the race — winner, cautions, wrecks, weather, TV rating, and gate — and attributed to the rights holder (or the wire services when the series is unsigned). A wreckfest lead is spicy; a packed house is upbeat; a soft rating or empty grandstand is downbeat. Stewards opening a file produces a serious investigation brief. Newsworthy weekends call a press conference. A mishandled podium can boil into a media controversy.

The dashboard lists last weekend's headlines and the season story count. Postseason prints a kind recap.

### Press Conferences

After a newsworthy weekend — wrecks, steward files, rain, or downbeat copy — the commissioner takes the podium. The prompt quotes the lead headline. Three answers sit on the same decision framework as owner and driver complaints: **stay on script** (dry, protects integrity), **celebrate the show** (feeds fans and controversy), or **promise a review** (the garage hears the league is watching). A quiet, clean win does not call a presser. Answers are logged. Celebrating wrecks or stonewalling a steward file can spark a public scandal; promising a review keeps the weekend contained.

### Media Controversies

A mishandled podium boils into a second decision on the same framework. Celebrating a wreckfest produces **"League Cheers the Chaos"**. Staying on script after a steward file produces **"League Accused of Stonewalling"**. Promising a review defuses the weekend. If controversy is already high and the papers are still on a wreck or investigation, **"Public Pressure Mounts on the Series"** can land without those answers.

Three responses: **deny everything** (the story grows and signed brands flinch), **apologize** (fans cool, owners call it a fold), or **launch a public inquiry** (integrity recovers, the board starts calling). The dashboard stores the last scandal. An active scandal raises an alert.

## Save and Load

Career progress is a **complete world snapshot**. One JSON file in `saves/` stores every live collection, the league book, the calendar, and the policies. Writes go to a temp file and replace the destination so a crash cannot leave a half-written career. The load menu lists each file with season, phase, and field size. Legacy 0.0.37 files still load; missing collections fill from the opening book, while an empty list stays empty.

Saved data includes:

- Active drivers and teams
- Retired drivers
- Series tracks
- League metrics
- Race history for the current season
- Completed season history
- Current season number and career length
- League policies
- Commissioner decision log
- Race investigations and wreck summaries
- Team owners, reputation, trends, facilities, engineering, and pit crews
- Driver traits, happiness, reputation, rivalries, feuds, and friendships
- Sponsor companies, industries, and preferences
- Driver endorsement deals and personal-sponsor income
- Team main-sponsor contracts, including unsponsored entries
- Sponsor deal satisfaction, last delivery, and objective breakdowns
- Sponsor withdrawals and brands blocked from rematching the same party
- Series naming rights, official partners, and the league treasury
- Sponsor prospect companies waiting to enter the market
- Sponsor market enter/leave log
- Television networks, kinds, reach, and broadcast tastes
- Series television rights, bids, and TV income
- Television ratings, viewer counts, and ratings trend
- Race-weekend gate attendance, fill, and attendance trend
- Generated media headlines and narratives
- Press-conference answers
- Media-controversy answers and scandal headlines
- Owner-council seats, chair, and rebuke votes
- Driver-council seats, chair, and feedback
- Stakeholder rule proposals and the docket
- Owner-council rule votes and applied policy changes
- Owner coalitions and paddock lobbying
- Commissioner approval with fans, owners, and drivers
- Board confidence, dismissal risk, and career-ending dismissals
- Prospect-pool drivers waiting outside the premier series
- Development-series calendar, standings, and champion
- Prospect call-ups onto open premier seats
- Manufacturer factory contracts, years remaining, and switch history
- Nested calendar (season, career length, phase) and a load-menu summary card
- Game settings: difficulty, career length, and autosave

Players may save between seasons or from the main menu. Loaded careers resume mid-season if races remain, or continue with the next scheduled season.

## Game Settings

A new career asks for **difficulty**, **career length**, and **autosave**. The same three live on the main-menu settings screen and on the commissioner dashboard.

- Easy: more fan goodwill, a $500,000 league treasury, extra shop budget, quieter race weekends, and a patient board (dismissal floor 27).
- Normal: the standard opening brief.
- Hard: hotter politics, thinner wallets, more incident risk, and a restless board (dismissal floor 43).
- Career length is 3, 5, or 10 seasons. It cannot be shortened below the season already in progress.
- Autosave can be off, after each offseason, or after each race. The reserved slot is `autosave.json`.

Difficulty and autosave are stored on the career save (0.0.39). Legacy 0.0.38 files load as Normal, three seasons, autosave off.

## Balance Simulation

Main menu item 6 runs a batch of AI careers so the opening book can be measured before playtesting. The auto-commissioner answers every numbered hearing and post-race ruling, skips save prompts, and silences the season printout.

- Board hearings present the season. Charter reviews extend a bridge loan. Factory hearings hold the current badge. New-team hearings defer. Other events take the middle option. Discipline follows the investigation packet (warning when confidence is low, a fine in ordinary cases, points when the file is severe and controversy is already high).
- A 50-season batch is 10 careers of 5 seasons. A 100-season batch is 20 careers of 5. Difficulty stays Normal and autosave stays off for the run, then the live career is restored.
- The JSON report lands in `season_reports/` with champions, commissioner grades, league health, closures, entries, factory switches, call-ups, retirements, and budgets. It is not written into the career save.

## League Calendar

Each season moves through a fixed league calendar:

- Preseason: the series prepares teams and drivers for the new year
- Regular Season: championship races are run in order; the development series races its own calendar alongside the first eight weekends
- Postseason: standings, awards, championship, feeder champion, and season records are finalized
- Offseason: drivers develop or decline, prospects progress from feeder results, retirements are processed and may call up a premier-ready prospect, team finances are settled, factory contracts tick and may switch, the sponsor market churns, television rights are paid, the prospect pool and development book remain on file, and paddock rivalries, feuds, and friendships are updated

The calendar phase is saved with career progress. A loaded career resumes in the same phase, including remaining regular-season races.

## Commissioner Management

The commissioner reviews a dashboard at each calendar phase and after every race. The dashboard shows league health, fan interest, controversy, locker-room happiness, reputation, rivalries, feuds, and friendships, team organizations, series naming rights, television rights, TV ratings, gate attendance, media headlines, last press-conference answer, last media scandal, owner-council chair and last rebuke vote, driver-council chair and last feedback, the rule-proposal docket, owner coalitions, last paddock lobbying, the last owner-council rule vote, commissioner approval with fans, owners, and drivers, board confidence and dismissal risk, the prospect pool waiting outside the premier series, the National Development Series leader or champion, the last prospect call-up, last factory switch and next expiring factory deal, difficulty, career length, and autosave, main-sponsor contracts, sponsor withdrawals, the sponsor market (active, idle, and waiting companies), the broadcast market, driver-commissioner relationships, active policies, the next race weekend's track and seating capacity, the last weekend's weather, pole, cautions, wrecks, investigation blame, last TV rating, last gate, and last headlines, and key alerts.

### Decision Events

Rule, safety, owner, driver, rivalry, feud, press-conference, media-controversy, owner-council, driver-council, rule-proposal, lobbying, rule-vote, board-confidence, team-entry, team-closure, and manufacturer-switch matters use one shared decision framework:

- A prompt and numbered choices
- Immediate consequences
- Weighted secondary outcomes

Decisions are logged and stored in career saves.

### Rule Changes

During preseason the commissioner may set:

- Championship points structure
- Race format
- Penalty standards
- Technical rules

These policies persist between seasons and affect scoring, incident risk, fines, and operating costs. Stage points, when the format is stage racing, are taken from the same championship points table rather than a separate scoring system.

Owners and drivers can also **introduce** rule proposals after the championship. The commissioner dockets, tables, or kills the paper. A later owner-council vote decides whether the policy actually changes.

### Rule Proposals

Postseason, a stakeholder puts a rule change on the table. The owner-council chair files from that owner's priority (wins, stability, cost-control, or prestige). The driver-council chair files garage paper (safety, stricter enforcement, or heavier inspection). A concerned garage protest steers the paper to the drivers; a passed owner rebuke steers it to the owners. Otherwise the sponsor rotates by season.

Three answers sit on the same decision framework: **docket it for a later vote** (the paper waits; the sponsor eases), **table it** (a stall), or **kill the proposal** (integrity up, the sponsor leaves angry). Docketing does not change the rulebook. The dashboard shows the docket.

### Rule Voting

Preseason, before the commissioner's own rule-change filing, the owner council votes the **oldest** paper on the docket. An empty docket skips the session.

Three answers sit on the same decision framework: **let the chamber vote** (integrity up, no whip), **whip for passage** (owners notice, integrity down), or **whip against**. Each seat then votes aye or nay from that owner's priority, patience, and personal pressure. Passing applies the policy and lifts the paper; failing rejects it and also clears it from the docket. Votes are recorded. The dashboard shows the last tally. A remaining docket still raises an alert.

### Political Influence

Owners sit in **coalitions** by priority — wins, stability, cost-control, or prestige. When a paper is on the docket the blocs line up for or against it. Preseason, before the floor vote, the paddock lobbies the commissioner.

Three answers sit on the same decision framework: **take every meeting** (even-handed, no extra heat), **cultivate the backing bloc** (they peel the closest swing vote), or **cultivate the opposition** (the paper cools across the chamber). Lobbying does not change the rulebook. It stacks with the later whip. The dashboard shows the coalitions and the last meetings.

### Approval Rating

The commissioner carries a live **approval rating** with three constituencies: fans (from fan interest), owners (from owner pressure, eased by patience), and drivers (from garage sentiment, trust, and morale). Overall approval is the mean of those three. Labels run Popular, Accepted, Mixed, Unpopular, and Hostile. The performance grade stays a separate integrity / fan-interest / controversy score. Slipping approval raises a dashboard alert. Postseason files the reading in career history.

### Job Security

The **board of directors** keeps a confidence score from overall approval, integrity, controversy, and owner approval. A passed owner rebuke, a garage protest, or an active scandal each ding the chair. Dismissal risk is the inverse. Labels run Secure, Steady, Watched, Precarious, and Collapsing.

When confidence leaves Steady, postseason calls a hearing on the same decision framework: **present the season**, **promise reforms**, or **defy the board**. A hearing that leaves confidence Collapsing **dismisses the commissioner** and ends the career. The dashboard shows board confidence and risk. A watching or high-risk board raises an alert.

### Safety Mandates

During the offseason the commissioner may require current, enhanced, or maximum safety equipment. Stronger mandates lower crash risk and raise team costs.

### Owner and Driver Complaints

Named owners lobby through their teams for financial relief and looser technical scrutiny. Each owner has a personality, wealth, patience, and a priority (wins, stability, cost-control, or prestige). Owner complaints and postseason lobbying are tied to those people, not anonymous team pressure. After the championship the owners sit as a council and vote. Drivers file grievances about officiating, safety, and trust, and the garage sits as a driver council to file feedback. Both can appear during the regular season and again after the championship.

### Owner Council

Every team owner holds a seat. The chair is the owner with the most political weight — prestige, personal pressure, impatience, wealth, and financial distress. The council mood is quiet, watchful, or restless from that heat.

Postseason, the chamber gavel a motion to **rebuke the commissioner**. Three answers sit on the same decision framework: **defer to the chamber** (let the votes run), **work the room** (soften ballots, spend integrity), or **stare them down** (integrity up, the room hardens). Each seat then votes aye or nay from patience, pressure, shop health, and league controversy. A passing rebuke raises owner pressure and controversy; a failed rebuke cools the owners. Votes are recorded. The dashboard shows the chair, seat count, and last tally.

### Driver Council

Every driver on the grid holds a seat. The chair is the driver with the most political weight — popularity, reputation, credibility, and media skill. Austin Vale gavels the opening garage. The council mood is settled, watchful, or restless from morale and driver sentiment.

Postseason, after the private grievance, the chamber files **feedback on officiating and safety**. Three answers: **hear the garage** (let every seat talk), **promise a working group** (the garage cools, owners notice), or **dismiss the gripes** (integrity up, the locker room goes cold). Each seat then files satisfied or concerned from morale, trust, and personality. A concerned majority files a protest; a satisfied majority stands down; a tie splits the garage. Feedback is recorded. The dashboard shows the chair, seat count, and last tally.

## Teams as Organizations

Teams are organizations, not just car ratings and a budget.

### Owners

Each team has a named owner with:

- Personality
- Wealth
- Patience
- A priority: wins, stability, cost-control, or prestige
- Personal pressure on the commissioner

Impatient or cash-strapped owners are more likely to request meetings. Commissioner rulings change that owner's patience and pressure as well as league-wide owner pressure.

### Reputation

Teams carry prestige that affects attractiveness to drivers and appeal to sponsors. Prestige moves with championships, facility upgrades, results trends, and financial health.

### Performance Trends

Recent championship points (up to four seasons) produce a momentum label: Rising Fast, Rising, Stable, Falling, or Falling Fast. Momentum slightly shifts car rating, engineering, prestige, and owner patience in the offseason.

### Facilities

Shop quality uses the existing facility level 1–5. A derived shop rating feeds sponsorship and driver attractiveness. Upgrades are the same `upgrade_facility` flow.

### Engineering

Each team has an engineering department rating. Stronger engineering reduces mechanical-failure risk, contributes to race pace, and grows through facility upgrades and performance investment. Failures are named parts: engine, transmission, or brakes. Team reliability and engineering remain the durability source.

### Pit Crews

Pit-crew skill uses the existing crew rating. Weaker crews can lose time with in-race mistakes. Mistakes are typed as crew errors or pit-road speeding and can draw a drive-through or stop-and-go under the existing penalty standard. Profitable and stable teams may train crews in the offseason. Race weekends also pick an automated pit plan (tires, fuel, timing) that uses crew rating, tire wear, weather, and grid position.

### Financial Health

The four-level money track is labeled Profitable, Stable, Struggling, and Insolvent. Insolvent teams face a charter review and can leave the grid.

## Race Simulation

Race weekends use a single outcome-level simulation. The commissioner does not drive.

### Tracks

Each venue is a Track object with name, type, purse, incident risk, length, banking, surface, tire wear, and passing difficulty. Track types remain Short Track, Road Course, Intermediate, and Superspeedway.

### Driver Track Skills

Drivers carry a rating for each of those four types. Skills persist on the driver, feed qualifying and race pace, and default from core speed, consistency, and aggression when missing from older saves.

### Qualifying

Each weekend sets a starting grid from qualifying performance. Inspection infractions can drop a car one or two spots, more often under inspection-heavy technical rules. Grid position changes race outcomes, especially at tracks that are hard to pass.

### Stages and Heats

Race format stays on the existing policy. Stage racing awards stage points derived from the active championship points table (one quarter, minimum 1). Heat-and-feature runs a heat that sets the feature grid. There is no second points system.

### Cautions

Yellow flags, restarts, and field compression are applied at race-outcome level. Caution count comes from track incident risk, weather, and crashes. This is not a lap-by-lap wreck chain.

### Pit Strategy

Each car is assigned an automated plan: two-stop, three-stop, fuel-save, short-run, or wet tires. The plan uses tire wear, weather, crew rating, and starting spot. Pit-crew mistakes still use crew rating, with extra risk on more aggressive plans.

### Weather

Race day generates conditions (clear, hot, cloudy, windy, or light rain) that apply to both qualifying and the feature. Weather shifts pace, incident risk, and tire load.

### Tires and Fuel

Tire wear is the existing track rating plus weather. It degrades pace unless the pit plan (especially a three-stop) covers it. There is no second tire number. Fuel is handled on the same pit plan: standard windows, fuel-save conservation, or a late-race gamble that can pay off or run the car dry.

### Contact and Wrecks

Crash chance still decides whether a car is in trouble. Contact then escalates to minor contact, a spin, or a crash. Nearby cars can be collected into a chain-reaction wreck at race-outcome level. This is not a lap-by-lap physics engine.

### Post-Race Investigation

Reckless crashes and wreck initiators generate an investigation packet: evidence, blame, confidence, and involved cars. That packet is printed in the existing commissioner review and stored on the race record and decision log.
