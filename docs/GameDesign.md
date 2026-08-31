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

## Save and Load

Career progress can be saved to JSON files in the local `saves/` folder and loaded later to continue play.

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
- Team owners, reputation, trends, facilities, engineering, and pit crews
- Driver traits, happiness, reputation, rivalries, feuds, and friendships

Players may save between seasons or from the main menu. Loaded careers resume mid-season if races remain, or continue with the next scheduled season.

## League Calendar

Each season moves through a fixed league calendar:

- Preseason: the series prepares teams and drivers for the new year
- Regular Season: championship races are run in order
- Postseason: standings, awards, championship, and season records are finalized
- Offseason: drivers develop or decline, retirements are processed, team finances are settled, and paddock rivalries, feuds, and friendships are updated

The calendar phase is saved with career progress. A loaded career resumes in the same phase, including remaining regular-season races.

## Commissioner Management

The commissioner reviews a dashboard at each calendar phase and after every race. The dashboard shows league health, fan interest, controversy, locker-room happiness, reputation, rivalries, feuds, and friendships, team organizations, driver-commissioner relationships, active policies, the next race weekend's track, the last weekend's weather, pole, and cautions, and key alerts.

### Decision Events

Rule, safety, owner, driver, rivalry, and feud matters use one shared decision framework:

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

### Safety Mandates

During the offseason the commissioner may require current, enhanced, or maximum safety equipment. Stronger mandates lower crash risk and raise team costs.

### Owner and Driver Complaints

Named owners lobby through their teams for financial relief and looser technical scrutiny. Each owner has a personality, wealth, patience, and a priority (wins, stability, cost-control, or prestige). Owner complaints and postseason lobbying are tied to those people, not anonymous team pressure. Drivers file grievances about officiating, safety, and trust. Both can appear during the regular season and again after the championship.

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

Each team has an engineering department rating. Stronger engineering reduces mechanical-failure risk, contributes to race pace, and grows through facility upgrades and performance investment.

### Pit Crews

Pit-crew skill uses the existing crew rating. Weaker crews can lose time with in-race mistakes. Profitable and stable teams may train crews in the offseason. Race weekends also pick an automated pit plan (tires, fuel, timing) that uses crew rating, tire wear, weather, and grid position. Component-level pit-road penalties are not part of this system.

### Financial Health

The four-level money track is labeled Profitable, Stable, Struggling, and Insolvent. Insolvent teams stay on the grid.

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
