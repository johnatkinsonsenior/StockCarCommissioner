from game.models import Driver, Network, Owner, Sponsor, Team, Track


def create_initial_teams():
    """Return a fresh list of teams for a new career."""

    return [
        Team(
            name="Liberty Racing",
            manufacturer="Vanguard",
            car_rating=82,
            crew_rating=78,
            reliability=84,
            starting_budget=5_000_000,
            owner=Owner(
                name="Helen Voss",
                personality="Patient",
                wealth=72,
                patience=80,
                priority="stability",
            ),
            prestige=70,
            engineering=74,
        ),
        Team(
            name="Pioneer Motorsports",
            manufacturer="Apex",
            car_rating=86,
            crew_rating=74,
            reliability=76,
            starting_budget=5_500_000,
            owner=Owner(
                name="Marcus Hale",
                personality="Aggressive",
                wealth=78,
                patience=40,
                priority="wins",
            ),
            prestige=76,
            engineering=80,
        ),
        Team(
            name="Summit Racing",
            manufacturer="Falcon",
            car_rating=79,
            crew_rating=84,
            reliability=88,
            starting_budget=4_800_000,
            owner=Owner(
                name="Ruth Calder",
                personality="Cost-Cutter",
                wealth=58,
                patience=55,
                priority="cost-control",
            ),
            prestige=64,
            engineering=71,
        ),
    ]


def create_team_applicants():
    """Return named owners waiting for a premier charter."""

    return [
        {
            "owner_name": "Ivy Navarro",
            "team_name": "Harbor Racing",
            "personality": "Hands-On",
            "wealth": 64,
            "patience": 62,
            "priority": "prestige",
            "manufacturer": "Independent",
            "car_rating": 72,
            "crew_rating": 70,
            "reliability": 74,
            "budget": 3_800_000,
            "prestige": 48,
            "engineering": 62,
        },
        {
            "owner_name": "Grant Holcomb",
            "team_name": "Ironwood Motorsports",
            "personality": "Hands-On",
            "wealth": 70,
            "patience": 58,
            "priority": "wins",
            "manufacturer": "Independent",
            "car_rating": 70,
            "crew_rating": 68,
            "reliability": 72,
            "budget": 4_200_000,
            "prestige": 44,
            "engineering": 60,
        },
    ]


def create_initial_drivers():
    """Return a fresh list of drivers for a new career."""

    return [
        Driver(
            name="Cole Baker",
            team_name="Liberty Racing",
            age=29,
            speed=84,
            consistency=78,
            aggression=62,
            personality="Professional",
            rival="Mason Reed",
            rivalry_intensity=70,
            ally="Ryan Holt",
            friendship_strength=74,
            teammate_bond=76,
            popularity=72,
            reputation=68,
            credibility=76,
            salary=1_200_000,
            contract_years=2,
            short_track=74,
            road_course=80,
            intermediate=82,
            superspeedway=78,
            feuds=[
                {
                    "opponent": "Mason Reed",
                    "intensity": 68,
                    "started_season": 1,
                    "last_incident": "preseason tension",
                    "status": "active",
                }
            ],
            friendships={"Ryan Holt": 74},
        ),
        Driver(
            name="Ryan Holt",
            team_name="Liberty Racing",
            age=38,
            speed=76,
            consistency=88,
            aggression=55,
            personality="Veteran",
            rival="Derek Lane",
            rivalry_intensity=56,
            ally="Cole Baker",
            friendship_strength=74,
            teammate_bond=76,
            popularity=68,
            reputation=72,
            credibility=80,
            salary=975_000,
            contract_years=1,
            short_track=86,
            road_course=72,
            intermediate=80,
            superspeedway=70,
            friendships={"Cole Baker": 74},
        ),
        Driver(
            name="Mason Reed",
            team_name="Pioneer Motorsports",
            age=27,
            speed=91,
            consistency=69,
            aggression=81,
            personality="Temperamental",
            rival="Cole Baker",
            rivalry_intensity=72,
            teammate_bond=46,
            popularity=84,
            reputation=64,
            credibility=48,
            salary=1_350_000,
            contract_years=3,
            short_track=70,
            road_course=68,
            intermediate=84,
            superspeedway=90,
            feuds=[
                {
                    "opponent": "Cole Baker",
                    "intensity": 68,
                    "started_season": 1,
                    "last_incident": "preseason tension",
                    "status": "active",
                }
            ],
        ),
        Driver(
            name="Tyler Knox",
            team_name="Pioneer Motorsports",
            age=21,
            speed=73,
            consistency=82,
            aggression=70,
            personality="Rookie",
            rival="Austin Vale",
            rivalry_intensity=48,
            teammate_bond=46,
            popularity=61,
            reputation=44,
            credibility=58,
            salary=850_000,
            contract_years=2,
            is_rookie=True,
            short_track=76,
            road_course=64,
            intermediate=70,
            superspeedway=68,
        ),
        Driver(
            name="Derek Lane",
            team_name="Summit Racing",
            age=34,
            speed=88,
            consistency=74,
            aggression=77,
            personality="Aggressive",
            rival="Ryan Holt",
            rivalry_intensity=58,
            ally="Austin Vale",
            friendship_strength=62,
            teammate_bond=60,
            popularity=76,
            reputation=70,
            credibility=55,
            salary=1_175_000,
            contract_years=2,
            short_track=82,
            road_course=70,
            intermediate=85,
            superspeedway=88,
            friendships={"Austin Vale": 62},
        ),
        Driver(
            name="Austin Vale",
            team_name="Summit Racing",
            age=25,
            speed=80,
            consistency=80,
            aggression=60,
            personality="Popular",
            rival="Tyler Knox",
            rivalry_intensity=45,
            ally="Derek Lane",
            friendship_strength=62,
            teammate_bond=60,
            popularity=90,
            reputation=82,
            credibility=70,
            media_skill=92,
            salary=1_100_000,
            contract_years=3,
            short_track=72,
            road_course=84,
            intermediate=78,
            superspeedway=76,
            friendships={"Derek Lane": 62},
        ),
    ]


def create_initial_sponsors():
    """Return the opening sponsor market for a new career.

    These companies are not yet bound by contracts. Each has an industry
    and tastes that score how interested the brand is in a given team or
    driver. Named deals, objectives, conflicts, and market churn attach to
    them during a career.
    """

    return [
        Sponsor(
            name="Ironclad Tools",
            industry="Tools",
            wealth=62,
            risk_tolerance=60,
            prestige_preference=48,
            performance_preference=86,
            popularity_preference=40,
            conduct_preference=44,
            preferred_track_types=["Short Track"],
        ),
        Sponsor(
            name="Harbor Mutual",
            industry="Insurance",
            wealth=78,
            risk_tolerance=22,
            prestige_preference=72,
            performance_preference=38,
            popularity_preference=34,
            conduct_preference=92,
        ),
        Sponsor(
            name="VoltCharge Energy",
            industry="Energy",
            wealth=80,
            risk_tolerance=82,
            prestige_preference=50,
            performance_preference=74,
            popularity_preference=58,
            conduct_preference=28,
            preferred_track_types=["Superspeedway"],
        ),
        Sponsor(
            name="Northstar Capital",
            industry="Finance",
            wealth=88,
            risk_tolerance=28,
            prestige_preference=90,
            performance_preference=56,
            popularity_preference=42,
            conduct_preference=76,
        ),
        Sponsor(
            name="Redline Cola",
            industry="Beverage",
            wealth=70,
            risk_tolerance=72,
            prestige_preference=44,
            performance_preference=52,
            popularity_preference=94,
            conduct_preference=32,
        ),
        Sponsor(
            name="Copperline Logistics",
            industry="Logistics",
            wealth=58,
            risk_tolerance=48,
            prestige_preference=55,
            performance_preference=62,
            popularity_preference=46,
            conduct_preference=58,
            manufacturer_affinity="Falcon",
        ),
        Sponsor(
            name="BrightPath Wireless",
            industry="Telecom",
            wealth=74,
            risk_tolerance=54,
            prestige_preference=60,
            performance_preference=44,
            popularity_preference=82,
            conduct_preference=50,
        ),
        Sponsor(
            name="Ridgeway Outfitters",
            industry="Retail",
            wealth=52,
            risk_tolerance=46,
            prestige_preference=50,
            performance_preference=50,
            popularity_preference=62,
            conduct_preference=60,
        ),
        Sponsor(
            name="Helix Electronics",
            industry="Electronics",
            wealth=76,
            risk_tolerance=58,
            prestige_preference=66,
            performance_preference=72,
            popularity_preference=48,
            conduct_preference=54,
            manufacturer_affinity="Apex",
        ),
        Sponsor(
            name="Vanguard Motor Oil",
            industry="Automotive",
            wealth=68,
            risk_tolerance=50,
            prestige_preference=58,
            performance_preference=70,
            popularity_preference=40,
            conduct_preference=62,
            manufacturer_affinity="Vanguard",
        ),
    ]


def create_sponsor_prospects():
    """Return companies waiting to enter the sponsor market."""

    return [
        Sponsor(
            name="Skyline Bank",
            industry="Finance",
            wealth=84,
            risk_tolerance=30,
            prestige_preference=88,
            performance_preference=50,
            popularity_preference=40,
            conduct_preference=80,
        ),
        Sponsor(
            name="Apex Fuel",
            industry="Energy",
            wealth=66,
            risk_tolerance=74,
            prestige_preference=48,
            performance_preference=82,
            popularity_preference=56,
            conduct_preference=36,
            preferred_track_types=["Superspeedway"],
        ),
        Sponsor(
            name="Golden Hour Coffee",
            industry="Beverage",
            wealth=55,
            risk_tolerance=62,
            prestige_preference=46,
            performance_preference=44,
            popularity_preference=90,
            conduct_preference=52,
        ),
        Sponsor(
            name="Sentinel Tires",
            industry="Automotive",
            wealth=72,
            risk_tolerance=50,
            prestige_preference=58,
            performance_preference=76,
            popularity_preference=42,
            conduct_preference=60,
            manufacturer_affinity="Vanguard",
        ),
        Sponsor(
            name="Prairie Hardware",
            industry="Tools",
            wealth=48,
            risk_tolerance=58,
            prestige_preference=40,
            performance_preference=78,
            popularity_preference=38,
            conduct_preference=50,
            preferred_track_types=["Short Track"],
        ),
        Sponsor(
            name="Lakeview Health",
            industry="Insurance",
            wealth=64,
            risk_tolerance=24,
            prestige_preference=68,
            performance_preference=36,
            popularity_preference=32,
            conduct_preference=90,
        ),
        Sponsor(
            name="MetroLink Transit",
            industry="Logistics",
            wealth=60,
            risk_tolerance=46,
            prestige_preference=52,
            performance_preference=58,
            popularity_preference=48,
            conduct_preference=62,
        ),
        Sponsor(
            name="Pulse Mobile",
            industry="Telecom",
            wealth=70,
            risk_tolerance=56,
            prestige_preference=54,
            performance_preference=46,
            popularity_preference=84,
            conduct_preference=48,
        ),
        Sponsor(
            name="Oak & Iron",
            industry="Retail",
            wealth=50,
            risk_tolerance=44,
            prestige_preference=48,
            performance_preference=42,
            popularity_preference=66,
            conduct_preference=72,
        ),
        Sponsor(
            name="Nova Semiconductors",
            industry="Electronics",
            wealth=82,
            risk_tolerance=52,
            prestige_preference=74,
            performance_preference=80,
            popularity_preference=50,
            conduct_preference=58,
            manufacturer_affinity="Apex",
        ),
    ]


def create_driver_prospects():
    """Return named drivers waiting outside the premier series."""

    return [
        Driver(
            name="Tessa Quinn",
            team_name="Heartland Super Lates",
            age=21,
            speed=77,
            consistency=74,
            aggression=66,
            personality="Popular",
            rival=None,
            popularity=62,
            salary=0,
            contract_years=0,
            is_rookie=True,
            pathway="Super Late",
            readiness=82,
        ),
        Driver(
            name="Dane Holloway",
            team_name="Carolina Late Models",
            age=20,
            speed=74,
            consistency=70,
            aggression=72,
            personality="Aggressive",
            rival=None,
            popularity=54,
            salary=0,
            contract_years=0,
            is_rookie=True,
            pathway="Late Model",
            readiness=78,
        ),
        Driver(
            name="Micah Prado",
            team_name="Lakeside Modifieds",
            age=22,
            speed=71,
            consistency=76,
            aggression=58,
            personality="Professional",
            rival=None,
            popularity=48,
            salary=0,
            contract_years=0,
            is_rookie=True,
            pathway="Modified",
            readiness=74,
        ),
        Driver(
            name="Sloane Avery",
            team_name="Red Clay Dirt",
            age=19,
            speed=73,
            consistency=64,
            aggression=78,
            personality="Temperamental",
            rival=None,
            popularity=50,
            salary=0,
            contract_years=0,
            is_rookie=True,
            pathway="Dirt Late Model",
            readiness=71,
        ),
        Driver(
            name="Reid Langford",
            team_name="Atlantic Touring",
            age=23,
            speed=68,
            consistency=78,
            aggression=52,
            personality="Professional",
            rival=None,
            popularity=46,
            salary=0,
            contract_years=0,
            is_rookie=True,
            pathway="Touring",
            readiness=69,
        ),
        Driver(
            name="Ivy Brennan",
            team_name="Heartland Super Lates",
            age=18,
            speed=70,
            consistency=62,
            aggression=70,
            personality="Rookie",
            rival=None,
            popularity=44,
            salary=0,
            contract_years=0,
            is_rookie=True,
            pathway="Super Late",
            readiness=66,
        ),
        Driver(
            name="Colton Briggs",
            team_name="Carolina Late Models",
            age=21,
            speed=66,
            consistency=68,
            aggression=60,
            personality="Professional",
            rival=None,
            popularity=42,
            salary=0,
            contract_years=0,
            is_rookie=True,
            pathway="Late Model",
            readiness=64,
        ),
        Driver(
            name="Maren Shaw",
            team_name="Red Clay Dirt",
            age=20,
            speed=68,
            consistency=60,
            aggression=74,
            personality="Aggressive",
            rival=None,
            popularity=40,
            salary=0,
            contract_years=0,
            is_rookie=True,
            pathway="Dirt Late Model",
            readiness=61,
        ),
        Driver(
            name="Pax Ellison",
            team_name="Lakeside Modifieds",
            age=19,
            speed=64,
            consistency=66,
            aggression=62,
            personality="Rookie",
            rival=None,
            popularity=38,
            salary=0,
            contract_years=0,
            is_rookie=True,
            pathway="Modified",
            readiness=58,
        ),
        Driver(
            name="Harlan Crowe",
            team_name="Atlantic Touring",
            age=24,
            speed=62,
            consistency=70,
            aggression=48,
            personality="Veteran",
            rival=None,
            popularity=36,
            salary=0,
            contract_years=0,
            is_rookie=True,
            pathway="Touring",
            readiness=54,
        ),
    ]


def create_initial_networks():
    """Return the opening broadcast market for a new career.

    These companies are not yet bound by rights contracts. Each has a
    footprint, bid power, and tastes that score how interested the
    network is in the series and in a given race weekend. Named deals
    and ratings attach to them in later days.
    """

    return [
        Network(
            name="Horizon Sports",
            kind="National",
            reach=90,
            wealth=88,
            risk_tolerance=32,
            prestige_preference=86,
            excitement_preference=48,
            star_preference=70,
            integrity_preference=78,
            preferred_track_types=["Intermediate", "Superspeedway"],
        ),
        Network(
            name="Peakline Cable",
            kind="Cable",
            reach=76,
            wealth=80,
            risk_tolerance=55,
            prestige_preference=62,
            excitement_preference=70,
            star_preference=74,
            integrity_preference=50,
            preferred_track_types=["Superspeedway"],
        ),
        Network(
            name="Heartland Broadcast",
            kind="Regional",
            reach=58,
            wealth=54,
            risk_tolerance=24,
            prestige_preference=70,
            excitement_preference=36,
            star_preference=44,
            integrity_preference=88,
            preferred_track_types=["Short Track"],
        ),
        Network(
            name="Redline TV",
            kind="Motorsport",
            reach=48,
            wealth=50,
            risk_tolerance=68,
            prestige_preference=44,
            excitement_preference=86,
            star_preference=60,
            integrity_preference=38,
            preferred_track_types=["Short Track", "Road Course", "Superspeedway"],
        ),
        Network(
            name="Coastline Media",
            kind="Cable",
            reach=64,
            wealth=66,
            risk_tolerance=62,
            prestige_preference=52,
            excitement_preference=58,
            star_preference=92,
            integrity_preference=42,
            preferred_track_types=["Road Course", "Superspeedway"],
        ),
    ]


teams = create_initial_teams()
drivers = create_initial_drivers()
sponsors = create_initial_sponsors()
sponsor_prospects = create_sponsor_prospects()
driver_prospects = create_driver_prospects()
team_applicants = create_team_applicants()
networks = create_initial_networks()


def create_track_pool():
    """Return the full catalog of venues the series can visit.

    The pool is larger than a single season's calendar so the schedule
    generator can rotate venues in and out from year to year. It contains a
    realistic mix of superspeedways, intermediates, short tracks, and road
    courses. "Grand National Speedway" is reserved as the marquee finale.
    """

    return [
        Track(
            name="Atlantic Speedway",
            track_type="Superspeedway",
            purse=750_000,
            incident_risk=18,
            length=2.5,
            banking=31,
            surface="asphalt",
            tire_wear=45,
            passing_difficulty=35,
        ),
        Track(
            name="Carolina Motor Speedway",
            track_type="Intermediate",
            purse=600_000,
            incident_risk=10,
            length=1.5,
            banking=24,
            surface="asphalt",
            tire_wear=62,
            passing_difficulty=55,
        ),
        Track(
            name="Granite Hills Speedway",
            track_type="Short Track",
            purse=480_000,
            incident_risk=20,
            length=0.6,
            banking=18,
            surface="concrete",
            tire_wear=80,
            passing_difficulty=68,
        ),
        Track(
            name="Cypress Point",
            track_type="Road Course",
            purse=660_000,
            incident_risk=13,
            length=2.4,
            banking=7,
            surface="asphalt",
            tire_wear=56,
            passing_difficulty=76,
        ),
        Track(
            name="Meridian Motor Speedway",
            track_type="Intermediate",
            purse=610_000,
            incident_risk=11,
            length=1.5,
            banking=20,
            surface="asphalt",
            tire_wear=60,
            passing_difficulty=54,
        ),
        Track(
            name="Thunder Valley",
            track_type="Superspeedway",
            purse=700_000,
            incident_risk=20,
            length=2.0,
            banking=28,
            surface="asphalt",
            tire_wear=50,
            passing_difficulty=40,
        ),
        Track(
            name="Ironwood Speedway",
            track_type="Intermediate",
            purse=590_000,
            incident_risk=12,
            length=1.33,
            banking=22,
            surface="asphalt",
            tire_wear=64,
            passing_difficulty=58,
        ),
        Track(
            name="Pine Ridge Raceway",
            track_type="Short Track",
            purse=500_000,
            incident_risk=16,
            length=0.5,
            banking=14,
            surface="concrete",
            tire_wear=78,
            passing_difficulty=70,
        ),
        Track(
            name="Sierra Raceway",
            track_type="Road Course",
            purse=640_000,
            incident_risk=14,
            length=2.6,
            banking=6,
            surface="asphalt",
            tire_wear=58,
            passing_difficulty=78,
        ),
        Track(
            name="Delta Downs Speedway",
            track_type="Intermediate",
            purse=620_000,
            incident_risk=11,
            length=1.5,
            banking=26,
            surface="asphalt",
            tire_wear=63,
            passing_difficulty=56,
        ),
        Track(
            name="Copper Canyon Speedway",
            track_type="Intermediate",
            purse=600_000,
            incident_risk=12,
            length=2.0,
            banking=22,
            surface="asphalt",
            tire_wear=66,
            passing_difficulty=60,
        ),
        Track(
            name="Liberty Bowl Speedway",
            track_type="Short Track",
            purse=460_000,
            incident_risk=22,
            length=0.75,
            banking=24,
            surface="asphalt",
            tire_wear=82,
            passing_difficulty=66,
        ),
        Track(
            name="Heartland Motor Speedway",
            track_type="Intermediate",
            purse=615_000,
            incident_risk=10,
            length=1.5,
            banking=20,
            surface="asphalt",
            tire_wear=61,
            passing_difficulty=55,
        ),
        Track(
            name="Bayside Speedway",
            track_type="Superspeedway",
            purse=720_000,
            incident_risk=19,
            length=2.66,
            banking=33,
            surface="asphalt",
            tire_wear=42,
            passing_difficulty=33,
        ),
        Track(
            name="Maple Grove Speedway",
            track_type="Short Track",
            purse=470_000,
            incident_risk=21,
            length=0.53,
            banking=12,
            surface="concrete",
            tire_wear=85,
            passing_difficulty=72,
        ),
        Track(
            name="Horizon Raceway",
            track_type="Intermediate",
            purse=605_000,
            incident_risk=11,
            length=1.5,
            banking=24,
            surface="asphalt",
            tire_wear=62,
            passing_difficulty=57,
        ),
        Track(
            name="Lone Star Circuit",
            track_type="Road Course",
            purse=650_000,
            incident_risk=12,
            length=2.3,
            banking=8,
            surface="asphalt",
            tire_wear=55,
            passing_difficulty=75,
        ),
        Track(
            name="Kingsport Speedway",
            track_type="Short Track",
            purse=490_000,
            incident_risk=18,
            length=0.625,
            banking=16,
            surface="concrete",
            tire_wear=79,
            passing_difficulty=69,
        ),
        Track(
            name="Falls City Speedway",
            track_type="Intermediate",
            purse=630_000,
            incident_risk=10,
            length=1.5,
            banking=22,
            surface="asphalt",
            tire_wear=63,
            passing_difficulty=56,
        ),
        Track(
            name="Summit Point Circuit",
            track_type="Road Course",
            purse=645_000,
            incident_risk=13,
            length=2.2,
            banking=9,
            surface="asphalt",
            tire_wear=54,
            passing_difficulty=77,
        ),
        Track(
            name="Emerald Coast Speedway",
            track_type="Intermediate",
            purse=640_000,
            incident_risk=11,
            length=1.5,
            banking=20,
            surface="asphalt",
            tire_wear=60,
            passing_difficulty=54,
        ),
        Track(
            name="Grand National Speedway",
            track_type="Superspeedway",
            purse=900_000,
            incident_risk=18,
            length=2.5,
            banking=30,
            surface="asphalt",
            tire_wear=46,
            passing_difficulty=36,
        ),
        Track(
            name="Daybreak Superspeedway",
            track_type="Superspeedway",
            purse=710_000,
            incident_risk=19,
            length=2.4,
            banking=29,
            surface="asphalt",
            tire_wear=47,
            passing_difficulty=38,
        ),
        Track(
            name="Coastal Superspeedway",
            track_type="Superspeedway",
            purse=730_000,
            incident_risk=20,
            length=2.55,
            banking=32,
            surface="asphalt",
            tire_wear=44,
            passing_difficulty=34,
        ),
        Track(
            name="Riverside Motor Speedway",
            track_type="Intermediate",
            purse=612_000,
            incident_risk=11,
            length=1.5,
            banking=23,
            surface="asphalt",
            tire_wear=62,
            passing_difficulty=56,
        ),
        Track(
            name="Highland Speedway",
            track_type="Intermediate",
            purse=598_000,
            incident_risk=12,
            length=1.25,
            banking=18,
            surface="asphalt",
            tire_wear=66,
            passing_difficulty=59,
        ),
        Track(
            name="Prairie Motor Speedway",
            track_type="Intermediate",
            purse=625_000,
            incident_risk=10,
            length=1.5,
            banking=21,
            surface="asphalt",
            tire_wear=61,
            passing_difficulty=55,
        ),
        Track(
            name="Old Dominion Speedway",
            track_type="Short Track",
            purse=475_000,
            incident_risk=19,
            length=0.58,
            banking=15,
            surface="asphalt",
            tire_wear=81,
            passing_difficulty=69,
        ),
        Track(
            name="Cedar Creek Speedway",
            track_type="Short Track",
            purse=485_000,
            incident_risk=20,
            length=0.66,
            banking=20,
            surface="concrete",
            tire_wear=83,
            passing_difficulty=67,
        ),
        Track(
            name="Glen Haven Circuit",
            track_type="Road Course",
            purse=655_000,
            incident_risk=13,
            length=2.5,
            banking=7,
            surface="asphalt",
            tire_wear=57,
            passing_difficulty=77,
        ),
        Track(
            name="Northgate Circuit",
            track_type="Road Course",
            purse=635_000,
            incident_risk=14,
            length=2.1,
            banking=10,
            surface="asphalt",
            tire_wear=53,
            passing_difficulty=74,
        ),
    ]


FINALE_VENUE = "Grand National Speedway"

SEASON_COMPOSITION = {
    "Superspeedway": 4,
    "Intermediate": 9,
    "Short Track": 5,
    "Road Course": 4,
}

SEASON_LENGTH = sum(SEASON_COMPOSITION.values())


def _rotate_pick(items, count, offset):
    """Pick ``count`` venues from ``items`` using a wrapping rotation window.

    Advancing ``offset`` season to season slides the window, rotating venues
    into and out of the calendar while keeping the count stable.
    """

    pool_size = len(items)

    if count >= pool_size:
        return list(items)

    start = offset % pool_size
    return [items[(start + index) % pool_size] for index in range(count)]


def _spread_by_type(tracks_to_order):
    """Reorder venues to avoid back-to-back races of the same track type."""

    buckets = {}

    for track in tracks_to_order:
        buckets.setdefault(track.type, []).append(track)

    ordered = []
    last_type = None
    remaining = len(tracks_to_order)

    while remaining:
        candidates = sorted(
            buckets.items(),
            key=lambda item: len(item[1]),
            reverse=True,
        )

        chosen_type = None

        for track_type, bucket in candidates:
            if bucket and track_type != last_type:
                chosen_type = track_type
                break

        if chosen_type is None:
            for track_type, bucket in candidates:
                if bucket:
                    chosen_type = track_type
                    break

        ordered.append(buckets[chosen_type].pop(0))
        last_type = chosen_type
        remaining -= 1

    return ordered


def generate_season_schedule(season_number=1, pool=None):
    """Build one season's calendar from the venue pool.

    Venues rotate year to year (driven by ``season_number``), while the
    track-type mix, a superspeedway opener, and the marquee finale stay
    consistent. Returns a fresh, ordered list of Track objects.
    """

    if pool is None:
        pool = create_track_pool()

    by_type = {
        "Superspeedway": [],
        "Intermediate": [],
        "Short Track": [],
        "Road Course": [],
    }

    for track in pool:
        by_type.setdefault(track.type, []).append(track)

    offset = max(season_number - 1, 0)

    finale = None
    superspeedways = []

    for track in by_type["Superspeedway"]:
        if finale is None and track.name == FINALE_VENUE:
            finale = track
        else:
            superspeedways.append(track)

    ss_needed = SEASON_COMPOSITION["Superspeedway"]
    reserve_finale = finale is not None
    ss_pick_count = ss_needed - 1 if reserve_finale else ss_needed

    chosen_ss = _rotate_pick(superspeedways, ss_pick_count, offset)
    chosen_intermediate = _rotate_pick(
        by_type["Intermediate"],
        SEASON_COMPOSITION["Intermediate"],
        offset * 3,
    )
    chosen_short = _rotate_pick(
        by_type["Short Track"],
        SEASON_COMPOSITION["Short Track"],
        offset * 2,
    )
    chosen_road = _rotate_pick(
        by_type["Road Course"],
        SEASON_COMPOSITION["Road Course"],
        offset * 2,
    )

    opener = chosen_ss[0] if chosen_ss else None
    middle = chosen_ss[1:] + chosen_intermediate + chosen_short + chosen_road
    middle = _spread_by_type(middle)

    schedule = []

    if opener is not None:
        schedule.append(opener)

    schedule.extend(middle)

    if finale is not None:
        schedule.append(finale)

    return schedule


def create_initial_tracks():
    """Return the opening-season schedule (season 1's generated calendar)."""

    return generate_season_schedule(season_number=1)


def create_development_track_pool():
    """Return the feeder-series venues the prospects race."""

    return [
        Track(
            name="Heartland Oval",
            track_type="Short Track",
            purse=90_000,
            incident_risk=16,
            length=0.5,
            banking=14,
            surface="asphalt",
            tire_wear=70,
            passing_difficulty=62,
            capacity=12_000,
        ),
        Track(
            name="Carolina County Park",
            track_type="Intermediate",
            purse=100_000,
            incident_risk=12,
            length=1.0,
            banking=18,
            surface="asphalt",
            tire_wear=58,
            passing_difficulty=50,
            capacity=18_000,
        ),
        Track(
            name="Lakeside Fairgrounds",
            track_type="Short Track",
            purse=85_000,
            incident_risk=18,
            length=0.4,
            banking=12,
            surface="asphalt",
            tire_wear=74,
            passing_difficulty=66,
            capacity=9_000,
        ),
        Track(
            name="Red Clay Speedway",
            track_type="Short Track",
            purse=80_000,
            incident_risk=20,
            length=0.375,
            banking=10,
            surface="asphalt",
            tire_wear=78,
            passing_difficulty=70,
            capacity=8_000,
        ),
        Track(
            name="Atlantic Marine Park",
            track_type="Intermediate",
            purse=105_000,
            incident_risk=11,
            length=1.25,
            banking=20,
            surface="asphalt",
            tire_wear=55,
            passing_difficulty=48,
            capacity=22_000,
        ),
        Track(
            name="Pine Hollow Speedway",
            track_type="Short Track",
            purse=88_000,
            incident_risk=17,
            length=0.5,
            banking=15,
            surface="asphalt",
            tire_wear=72,
            passing_difficulty=64,
            capacity=11_000,
        ),
        Track(
            name="Midland Motor Park",
            track_type="Intermediate",
            purse=98_000,
            incident_risk=13,
            length=1.0,
            banking=16,
            surface="asphalt",
            tire_wear=60,
            passing_difficulty=52,
            capacity=16_000,
        ),
        Track(
            name="Capital Fairgrounds",
            track_type="Short Track",
            purse=110_000,
            incident_risk=15,
            length=0.5,
            banking=14,
            surface="asphalt",
            tire_wear=68,
            passing_difficulty=60,
            capacity=20_000,
        ),
    ]


def generate_development_schedule(season_number=1):
    """Return this season's feeder calendar, rotating the opener."""

    pool = create_development_track_pool()
    offset = (max(int(season_number), 1) - 1) % len(pool)
    return pool[offset:] + pool[:offset]


tracks = create_initial_tracks()
development_tracks = generate_development_schedule(1)
