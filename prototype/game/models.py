FACILITY_MAX_LEVEL = 5
CREW_TRAINING_COST = 80_000
TREND_HISTORY_SEASONS = 4

FACILITY_UPGRADE_COSTS = {
    2: 400_000,
    3: 650_000,
    4: 900_000,
    5: 1_200_000,
}

FINANCIAL_STATUS_LABELS = {
    0: "Profitable",
    1: "Stable",
    2: "Struggling",
    3: "Insolvent",
}

TREND_LABELS = {
    2: "Rising Fast",
    1: "Rising",
    0: "Stable",
    -1: "Falling",
    -2: "Falling Fast",
}

PERSONALITY_TRAIT_DEFAULTS = {
    "Professional": {
        "temperament": 72,
        "loyalty": 78,
        "ambition": 65,
        "media_skill": 70,
        "risk_tolerance": 48,
    },
    "Veteran": {
        "temperament": 80,
        "loyalty": 82,
        "ambition": 55,
        "media_skill": 68,
        "risk_tolerance": 42,
    },
    "Temperamental": {
        "temperament": 35,
        "loyalty": 50,
        "ambition": 78,
        "media_skill": 45,
        "risk_tolerance": 75,
    },
    "Rookie": {
        "temperament": 58,
        "loyalty": 62,
        "ambition": 80,
        "media_skill": 40,
        "risk_tolerance": 68,
    },
    "Aggressive": {
        "temperament": 45,
        "loyalty": 55,
        "ambition": 82,
        "media_skill": 52,
        "risk_tolerance": 85,
    },
    "Popular": {
        "temperament": 70,
        "loyalty": 60,
        "ambition": 70,
        "media_skill": 88,
        "risk_tolerance": 55,
    },
}

HAPPINESS_LABELS = (
    (75, "Content"),
    (55, "Settled"),
    (40, "Restless"),
    (0, "Unhappy"),
)


def trait_defaults_for(personality):
    """Return numerical trait defaults for a personality type."""

    return dict(
        PERSONALITY_TRAIT_DEFAULTS.get(
            personality,
            PERSONALITY_TRAIT_DEFAULTS["Professional"],
        )
    )


TRACK_TYPE_SKILL_KEYS = {
    "Short Track": "short_track",
    "Road Course": "road_course",
    "Intermediate": "intermediate",
    "Superspeedway": "superspeedway",
}


def default_track_skills(speed, consistency, aggression):
    """Return track-type skills derived from core driver ratings."""

    return {
        "short_track": _clamp(
            round(aggression * 0.40 + consistency * 0.60)
        ),
        "road_course": _clamp(
            round(speed * 0.35 + consistency * 0.65)
        ),
        "intermediate": _clamp(
            round(speed * 0.50 + consistency * 0.50)
        ),
        "superspeedway": _clamp(
            round(
                speed * 0.55
                + aggression * 0.25
                + consistency * 0.20
            )
        ),
    }


def _clamp(value, minimum=0, maximum=100):
    return max(minimum, min(value, maximum))


class Owner:
    """Represents the person who owns a racing team."""

    def __init__(
        self,
        name,
        personality,
        wealth,
        patience,
        priority,
    ):
        self.name = name
        self.personality = personality
        self.wealth = _clamp(wealth)
        self.patience = _clamp(patience)
        self.priority = priority
        self.pressure = 25

    @classmethod
    def default_for_team(cls, team_name):
        """Build a generic owner when a save or team has none."""

        return cls(
            name=f"{team_name} Ownership",
            personality="Hands-On",
            wealth=50,
            patience=50,
            priority="stability",
        )

    def description(self):
        """Return a short owner label for prompts and reports."""

        return f"{self.name} ({self.personality}, {self.priority})"

    def __str__(self):
        return self.name


class Team:
    """Represents a stock car racing team."""

    def __init__(
        self,
        name,
        car_rating,
        crew_rating,
        reliability,
        starting_budget,
        owner=None,
        prestige=None,
        engineering=None,
    ):
        self.name = name
        self.car_rating = car_rating
        self.crew_rating = crew_rating
        self.reliability = reliability

        self.starting_budget = starting_budget
        self.budget = starting_budget

        self.owner = owner or Owner.default_for_team(name)
        self.prestige = prestige if prestige is not None else 55
        self.engineering = (
            engineering
            if engineering is not None
            else max(40, (car_rating + crew_rating) // 2)
        )

        # Career statistics
        self.career_prize_money = 0
        self.championships = 0
        self.career_wins = 0

        # Financial statistics
        self.current_payroll = 0
        self.career_salary_expenses = 0
        self.facility_level = 1
        self.season_sponsorship = 0
        self.season_operating_expenses = 0
        self.career_sponsorship_income = 0
        self.career_operating_expenses = 0
        self.career_facility_investment = 0
        self.career_performance_investment = 0
        self.career_crew_training = 0
        self.financial_distress_level = 0

        self.season_points_history = []
        self.performance_trend = 0
        self.season_pit_mistakes = 0

    def start_new_season(self):
        """Reset values that apply only to the upcoming season."""

        self.current_payroll = 0
        self.season_sponsorship = 0
        self.season_operating_expenses = 0
        self.season_pit_mistakes = 0

    def add_prize_money(self, amount):
        """Add race winnings to the team's budget and career total."""

        self.budget += amount
        self.career_prize_money += amount

    def pay_fine(self, amount):
        """Deduct a commissioner fine from the team's budget."""

        self.budget = max(0, self.budget - amount)

    def pay_driver_salary(self, amount):
        """Pay a driver's annual salary."""

        self.budget -= amount
        self.current_payroll += amount
        self.career_salary_expenses += amount

    def can_afford(self, amount, reserve=500_000):
        """Return whether the team can afford an expense and retain reserves."""

        return self.budget - amount >= reserve

    def add_sponsorship(self, amount):
        """Add sponsorship revenue to the team budget."""

        self.budget += amount
        self.season_sponsorship += amount
        self.career_sponsorship_income += amount

    def pay_operating_expense(self, amount):
        """Pay a seasonal operating expense."""

        self.budget -= amount
        self.season_operating_expenses += amount
        self.career_operating_expenses += amount

    def facility_upgrade_cost(self):
        """Return the cost to upgrade to the next facility level."""

        next_level = self.facility_level + 1

        if next_level > FACILITY_MAX_LEVEL:
            return None

        return FACILITY_UPGRADE_COSTS[next_level]

    def facility_rating(self):
        """Return a 0-99 shop rating derived from facility_level."""

        return min(99, 15 + self.facility_level * 17)

    def upgrade_facility(self):
        """Upgrade the team facility if affordable."""

        cost = self.facility_upgrade_cost()

        if cost is None or not self.can_afford(cost):
            return False

        self.budget -= cost
        self.career_facility_investment += cost
        self.facility_level += 1
        self.reliability = _clamp(self.reliability + 2, 0, 99)
        self.prestige = _clamp(self.prestige + 2)
        self.engineering = _clamp(self.engineering + 2, 0, 99)

        return True

    def invest_in_performance(self, amount):
        """Invest in car, crew, and engineering development."""

        if amount <= 0 or not self.can_afford(amount):
            return {
                "car_gain": 0,
                "crew_gain": 0,
                "engineering_gain": 0,
                "spent": 0,
            }

        self.budget -= amount
        self.career_performance_investment += amount

        car_gain = _clamp(amount // 100_000, 1, 3)
        crew_gain = _clamp(amount // 120_000, 1, 2)
        engineering_gain = _clamp(amount // 150_000, 1, 3)

        self.car_rating = _clamp(self.car_rating + car_gain, 0, 99)
        self.crew_rating = _clamp(self.crew_rating + crew_gain, 0, 99)
        self.engineering = _clamp(
            self.engineering + engineering_gain,
            0,
            99,
        )

        return {
            "car_gain": car_gain,
            "crew_gain": crew_gain,
            "engineering_gain": engineering_gain,
            "spent": amount,
        }

    def train_pit_crew(self):
        """Pay for offseason pit-crew training if the team can afford it."""

        if not self.can_afford(CREW_TRAINING_COST):
            return 0

        self.budget -= CREW_TRAINING_COST
        self.career_crew_training += CREW_TRAINING_COST

        gain = 1 if self.crew_rating >= 85 else 2
        self.crew_rating = _clamp(self.crew_rating + gain, 0, 99)

        return gain

    def record_pit_mistake(self):
        """Record a race pit-crew mistake."""

        self.season_pit_mistakes += 1

    def attractiveness(self):
        """Return how attractive the team is to drivers."""

        health = 100 - self.financial_distress_level * 18

        return round(
            _clamp(
                self.prestige * 0.40
                + self.facility_rating() * 0.20
                + health * 0.25
                + self.engineering * 0.15
            )
        )

    def sponsor_appeal(self):
        """Return how attractive the team is to sponsors."""

        return round(
            _clamp(
                self.prestige * 0.45
                + self.facility_rating() * 0.25
                + (3 - self.financial_distress_level) * 12
                + self.championships * 4
            )
        )

    def performance_trend_label(self):
        """Return a readable multi-season momentum label."""

        return TREND_LABELS.get(self.performance_trend, "Stable")

    def record_season_performance(self, points):
        """Store season points and update momentum from recent results."""

        self.season_points_history.append(points)
        self.season_points_history = self.season_points_history[
            -TREND_HISTORY_SEASONS:
        ]

        if len(self.season_points_history) < 2:
            self.performance_trend = 0
            return

        latest = self.season_points_history[-1]
        previous = (
            sum(self.season_points_history[:-1])
            / len(self.season_points_history[:-1])
        )
        delta = latest - previous

        if delta >= 20:
            self.performance_trend = 2
        elif delta >= 8:
            self.performance_trend = 1
        elif delta <= -20:
            self.performance_trend = -2
        elif delta <= -8:
            self.performance_trend = -1
        else:
            self.performance_trend = 0

        self.prestige = _clamp(self.prestige + self.performance_trend)

    def apply_trend_effects(self):
        """Apply modest offseason car and engineering drift from momentum."""

        if self.performance_trend >= 1:
            self.car_rating = _clamp(self.car_rating + 1, 0, 99)
            self.engineering = _clamp(self.engineering + 1, 0, 99)
            self.owner.patience = _clamp(self.owner.patience + 2)
            self.owner.pressure = _clamp(self.owner.pressure - 3)
        elif self.performance_trend <= -1:
            self.car_rating = _clamp(self.car_rating - 1, 0, 99)
            self.engineering = _clamp(self.engineering - 1, 0, 99)
            self.owner.patience = _clamp(self.owner.patience - 4)
            self.owner.pressure = _clamp(self.owner.pressure + 4)

    def apply_owner_financial_mood(self):
        """Adjust owner patience and pressure from financial health."""

        if self.financial_distress_level == 0:
            self.owner.patience = _clamp(self.owner.patience + 3)
            self.owner.pressure = _clamp(self.owner.pressure - 5)
        elif self.financial_distress_level == 2:
            self.owner.patience = _clamp(self.owner.patience - 5)
            self.owner.pressure = _clamp(self.owner.pressure + 8)
        elif self.financial_distress_level == 3:
            self.owner.patience = _clamp(self.owner.patience - 10)
            self.owner.pressure = _clamp(self.owner.pressure + 15)

    def update_financial_distress(self):
        """Update the team's financial health level from its budget."""

        if self.budget >= 1_500_000:
            self.financial_distress_level = 0
        elif self.budget >= 750_000:
            self.financial_distress_level = 1
        elif self.budget >= 250_000:
            self.financial_distress_level = 2
        else:
            self.financial_distress_level = 3

    def financial_status_label(self):
        """Return a readable financial health label."""

        return FINANCIAL_STATUS_LABELS[self.financial_distress_level]

    def record_win(self):
        """Record a race victory for the team."""

        self.career_wins += 1

    def record_championship(self):
        """Record a team championship."""

        self.championships += 1

    def __str__(self):
        return self.name


class Track:
    """Represents a race track. Replaces the old track dictionaries."""

    def __init__(
        self,
        name,
        track_type,
        purse,
        incident_risk,
        length,
        banking,
        surface,
        tire_wear,
        passing_difficulty,
    ):
        self.name = name
        self.type = track_type
        self.purse = purse
        self.incident_risk = incident_risk
        self.length = length
        self.banking = banking
        self.surface = surface
        self.tire_wear = _clamp(tire_wear)
        self.passing_difficulty = _clamp(passing_difficulty)

    def skill_key(self):
        """Return the driver skill attribute used at this track type."""

        return TRACK_TYPE_SKILL_KEYS.get(self.type, "intermediate")

    def description(self):
        """Return a short physical description."""

        return (
            f"{self.length} mi, {self.banking}° {self.surface}, "
            f"wear {self.tire_wear}, pass {self.passing_difficulty}"
        )

    def __str__(self):
        return self.name


class Driver:
    """Represents a stock car racing driver."""

    def __init__(
        self,
        name,
        team_name,
        age,
        speed,
        consistency,
        aggression,
        personality,
        rival,
        popularity,
        salary,
        contract_years,
        is_rookie=False,
        temperament=None,
        loyalty=None,
        ambition=None,
        media_skill=None,
        risk_tolerance=None,
        rivalry_intensity=None,
        ally=None,
        friendship_strength=0,
        teammate_bond=55,
        reputation=None,
        credibility=None,
        team_satisfaction=65,
        contract_satisfaction=65,
        competitive_frustration=30,
        feuds=None,
        friendships=None,
        short_track=None,
        road_course=None,
        intermediate=None,
        superspeedway=None,
    ):
        self.name = name
        self.team_name = team_name
        self.age = age

        self.speed = speed
        self.consistency = consistency
        self.aggression = aggression

        self.personality = personality
        self.rival = rival
        self.popularity = popularity
        self.salary = salary
        self.contract_years = contract_years
        self.previous_team = None
        self.is_free_agent = False
        self.is_rookie = is_rookie

        self.morale = 70
        self.commissioner_trust = 60
        self.is_retired = False

        traits = trait_defaults_for(personality)
        self.temperament = _clamp(
            temperament if temperament is not None else traits["temperament"]
        )
        self.loyalty = _clamp(
            loyalty if loyalty is not None else traits["loyalty"]
        )
        self.ambition = _clamp(
            ambition if ambition is not None else traits["ambition"]
        )
        self.media_skill = _clamp(
            media_skill if media_skill is not None else traits["media_skill"]
        )
        self.risk_tolerance = _clamp(
            risk_tolerance
            if risk_tolerance is not None
            else traits["risk_tolerance"]
        )

        if rivalry_intensity is not None:
            self.rivalry_intensity = _clamp(rivalry_intensity)
        elif rival:
            self.rivalry_intensity = 50
        else:
            self.rivalry_intensity = 0

        self.ally = ally
        self.friendship_strength = _clamp(friendship_strength)
        self.teammate_bond = _clamp(teammate_bond)
        self.friendships = dict(friendships or {})

        if reputation is not None:
            self.reputation = _clamp(reputation)
        else:
            self.reputation = _clamp((popularity + 50) // 2)

        if credibility is not None:
            self.credibility = _clamp(credibility)
        else:
            self.credibility = _clamp(
                (self.temperament + self.loyalty) // 2
            )

        self.team_satisfaction = _clamp(team_satisfaction)
        self.contract_satisfaction = _clamp(contract_satisfaction)
        self.competitive_frustration = _clamp(competitive_frustration)
        self.feuds = list(feuds or [])

        skills = default_track_skills(speed, consistency, aggression)
        self.short_track = _clamp(
            short_track if short_track is not None else skills["short_track"],
            0,
            99,
        )
        self.road_course = _clamp(
            road_course if road_course is not None else skills["road_course"],
            0,
            99,
        )
        self.intermediate = _clamp(
            intermediate if intermediate is not None else skills["intermediate"],
            0,
            99,
        )
        self.superspeedway = _clamp(
            superspeedway
            if superspeedway is not None
            else skills["superspeedway"],
            0,
            99,
        )

        # Career statistics
        self.career_starts = 0
        self.career_finishes = 0
        self.career_wins = 0
        self.career_dnfs = 0
        self.career_points = 0
        self.career_earnings = 0
        self.championships = 0
        self.seasons_completed = 0

        self.reset_season()

    def reset_season(self):
        """Reset statistics that apply only to one season."""

        self.points = 0
        self.earnings = 0
        self.starts = 0
        self.finishes = 0
        self.wins = 0
        self.dnfs = 0

        self.warnings = 0
        self.fines = 0
        self.points_penalties = 0
        self.suspensions = 0
        self.suspension_races = 0

    def complete_season(self):
        """Transfer season statistics into career totals."""

        self.career_starts += self.starts
        self.career_finishes += self.finishes
        self.career_wins += self.wins
        self.career_dnfs += self.dnfs
        self.career_points += self.points
        self.career_earnings += self.earnings
        self.seasons_completed += 1

        if self.is_rookie:
            self.is_rookie = False

    def record_championship(self):
        """Record a driver championship."""

        self.championships += 1

    def add_points(self, amount):
        self.points += amount

    def deduct_points(self, amount):
        actual_deduction = min(self.points, amount)
        self.points -= actual_deduction
        self.points_penalties += actual_deduction

    def add_earnings(self, amount):
        self.earnings += amount

    def is_suspended(self):
        return self.suspension_races > 0

    def overall_rating(self):
        """Return a simple overall driver rating."""

        return round(
            self.speed * 0.45
            + self.consistency * 0.40
            + (100 - self.aggression) * 0.15
        )

    def calculate_market_value(self):
        """Calculate the driver's estimated annual salary value."""

        overall = self.overall_rating()

        value = (
            150_000
            + overall * 11_000
            + self.popularity * 3_000
            + self.career_wins * 20_000
            + self.championships * 250_000
        )

        if self.age <= 23:
            value *= 0.85
        elif self.age >= 38:
            value *= 0.90

        return int(round(value / 25_000) * 25_000        )

    def track_skill_for(self, track_type):
        """Return the driver's rating for a track type."""

        key = TRACK_TYPE_SKILL_KEYS.get(track_type, "intermediate")

        return getattr(self, key)

    def advance_contract(self):
        """Reduce the number of years remaining on the contract."""

        if self.contract_years > 0:
            self.contract_years -= 1

        if self.contract_years == 0:
            self.is_free_agent = True

    def sign_contract(self, team_name, salary, contract_years):
        """Sign a new contract with a team."""

        if self.team_name != team_name:
            self.previous_team = self.team_name

        self.team_name = team_name
        self.salary = salary
        self.contract_years = contract_years
        self.is_free_agent = False

    def contract_description(self):
        """Return a readable description of the driver's contract."""

        if self.is_free_agent:
            return "Free Agent"

        year_word = "year" if self.contract_years == 1 else "years"

        return (
            f"${self.salary:,} per season, "
            f"{self.contract_years} {year_word} remaining"
        )

    def happiness_label(self):
        """Return a readable label derived from morale, not a second mood."""

        for threshold, label in HAPPINESS_LABELS:
            if self.morale >= threshold:
                return label

        return "Unhappy"

    def sync_morale_from_happiness(self):
        """Move morale toward team, contract, and competitive satisfaction."""

        target = round(
            self.team_satisfaction * 0.35
            + self.contract_satisfaction * 0.30
            + (100 - self.competitive_frustration) * 0.35
        )
        self.morale = _clamp(round(self.morale * 0.6 + target * 0.4))

    def set_rival(self, rival_name, intensity=40):
        """Set the primary rival name and intensity."""

        self.rival = rival_name
        self.rivalry_intensity = _clamp(intensity) if rival_name else 0

    def adjust_rivalry(self, amount):
        """Escalate or decay the primary rivalry without clearing the name."""

        if not self.rival:
            return

        self.rivalry_intensity = _clamp(self.rivalry_intensity + amount)

    def decay_rivalry(self, amount=6):
        """Reduce rivalry intensity during quiet stretches."""

        if not self.rival:
            self.rivalry_intensity = 0
            return

        self.rivalry_intensity = _clamp(self.rivalry_intensity - amount)

    def hottest_feud(self):
        """Return the driver's strongest feud dictionary, if any."""

        if not self.feuds:
            return None

        return max(self.feuds, key=lambda feud: feud.get("intensity", 0))

    def feud_with(self, opponent_name):
        """Return the feud record against one opponent, or None."""

        for feud in self.feuds:
            if feud.get("opponent") == opponent_name:
                return feud

        return None

    def record_feud(self, opponent_name, season, delta=8, incident=""):
        """Open or escalate a long-term feud that persists across races."""

        if not opponent_name or opponent_name == self.name:
            return None

        feud = self.feud_with(opponent_name)

        if feud is None:
            feud = {
                "opponent": opponent_name,
                "intensity": _clamp(40 + delta),
                "started_season": season,
                "last_incident": incident,
                "status": "active",
            }
            self.feuds.append(feud)
        else:
            feud["intensity"] = _clamp(feud.get("intensity", 40) + delta)
            if incident:
                feud["last_incident"] = incident

        if feud["intensity"] >= 55:
            feud["status"] = "active"
        elif feud["intensity"] >= 25:
            feud["status"] = "cooling"
        else:
            feud["status"] = "dormant"

        if self.rival == opponent_name:
            self.adjust_rivalry(max(2, delta // 2))

        return feud

    def cool_feuds(self):
        """Decay feud intensity in the offseason."""

        for feud in self.feuds:
            decay = 4 if feud.get("status") == "active" else 8
            feud["intensity"] = _clamp(feud.get("intensity", 0) - decay)

            if feud["intensity"] >= 55:
                feud["status"] = "active"
            elif feud["intensity"] >= 25:
                feud["status"] = "cooling"
            else:
                feud["status"] = "dormant"

    def clear_relationship_with(self, other_name):
        """Drop rival, ally, feud, and friendship ties to a retired driver."""

        if self.rival == other_name:
            self.rival = None
            self.rivalry_intensity = 0

        if self.ally == other_name:
            self.ally = None
            self.friendship_strength = 0

        self.feuds = [
            feud
            for feud in self.feuds
            if feud.get("opponent") != other_name
        ]
        self.friendships.pop(other_name, None)

    def set_ally(self, ally_name, strength=60):
        """Set the primary ally and friendship strength."""

        self.ally = ally_name
        self.friendship_strength = _clamp(strength) if ally_name else 0

        if ally_name:
            self.friendships[ally_name] = self.friendship_strength

    def adjust_friendship(self, other_name, amount):
        """Change friendship strength with another driver."""

        if not other_name or other_name == self.name:
            return

        current = self.friendships.get(other_name, 0)
        updated = _clamp(current + amount)
        self.friendships[other_name] = updated

        if self.ally == other_name:
            self.friendship_strength = updated
        elif self.ally is None and updated >= 65:
            self.set_ally(other_name, updated)

    def friendship_with(self, other_name):
        """Return friendship strength with another driver."""

        if other_name == self.ally:
            return self.friendship_strength

        return self.friendships.get(other_name, 0)

    def __str__(self):
        return self.name
