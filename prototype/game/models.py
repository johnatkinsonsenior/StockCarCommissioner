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

SPONSOR_INDUSTRIES = (
    "Automotive",
    "Energy",
    "Finance",
    "Retail",
    "Telecom",
    "Beverage",
    "Tools",
    "Insurance",
    "Electronics",
    "Logistics",
)

SPONSOR_SATISFACTION_LABELS = (
    (80, "thrilled"),
    (65, "pleased"),
    (50, "content"),
    (35, "restless"),
    (0, "unhappy"),
)

SPONSOR_RENEWAL_MIN_SATISFACTION = 38

NETWORK_KINDS = (
    "National",
    "Cable",
    "Regional",
    "Motorsport",
)


def sponsor_satisfaction_label(satisfaction):
    """Return a mood label for a 0-100 sponsor satisfaction score."""

    for threshold, label in SPONSOR_SATISFACTION_LABELS:
        if satisfaction >= threshold:
            return label

    return "unhappy"


def sponsor_pay_multiplier(satisfaction):
    """Return this year's check multiplier from sponsor mood."""

    if satisfaction >= 80:
        return 1.12
    if satisfaction >= 65:
        return 1.06
    if satisfaction >= 50:
        return 1.00
    if satisfaction >= 35:
        return 0.90
    return 0.78


def apply_objective_review(deal, delivery, breakdown):
    """Update a deal's satisfaction from a 0-100 delivery score."""

    previous = deal.get("satisfaction", 55)
    delta = round((delivery - 50) / 7)

    if delivery >= 75:
        delta += 1
    elif delivery <= 30:
        delta -= 1

    deal["satisfaction"] = _clamp(previous + delta)
    deal["last_delivery"] = delivery
    deal["last_objectives"] = dict(breakdown)
    return previous, deal["satisfaction"], delta


def apply_controversy_shock(deal, amount):
    """Cut deal satisfaction after a scandal. Return previous, current, delta."""

    previous = deal.get("satisfaction", 55)
    delta = -abs(int(amount))
    deal["satisfaction"] = _clamp(previous + delta)
    return previous, deal["satisfaction"], delta

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


TRACK_TYPE_CAPACITY = {
    "Superspeedway": 118_000,
    "Intermediate": 76_000,
    "Short Track": 36_000,
    "Road Course": 48_000,
}

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


class Sponsor:
    """A company that might back teams, drivers, or the league."""

    def __init__(
        self,
        name,
        industry,
        wealth,
        risk_tolerance,
        prestige_preference,
        performance_preference,
        popularity_preference,
        conduct_preference,
        manufacturer_affinity=None,
        preferred_track_types=None,
    ):
        self.name = name
        self.industry = industry
        self.wealth = _clamp(wealth)
        self.risk_tolerance = _clamp(risk_tolerance)
        self.prestige_preference = _clamp(prestige_preference)
        self.performance_preference = _clamp(performance_preference)
        self.popularity_preference = _clamp(popularity_preference)
        self.conduct_preference = _clamp(conduct_preference)
        self.manufacturer_affinity = manufacturer_affinity
        self.preferred_track_types = list(preferred_track_types or [])

    def spending_power(self):
        """Return a dollar scale derived from wealth."""

        return int(200_000 + self.wealth * 12_000)

    def preference_summary(self):
        """Return the two strongest tastes plus a risk posture."""

        ranked = sorted(
            [
                ("prestige", self.prestige_preference),
                ("performance", self.performance_preference),
                ("exposure", self.popularity_preference),
                ("conduct", self.conduct_preference),
            ],
            key=lambda item: item[1],
            reverse=True,
        )
        top = [label for label, value in ranked[:2] if value >= 55]

        tastes = ", ".join(top) if top else "balanced"
        return f"{tastes}; {self.risk_posture()}"

    def risk_posture(self):
        """Return cautious, measured, or bold from risk tolerance."""

        if self.risk_tolerance >= 65:
            return "bold"
        if self.risk_tolerance <= 40:
            return "cautious"
        return "measured"

    def controversy_sensitivity(self):
        """Return 0-1 how badly scandal bothers this brand."""

        caution = (100 - self.risk_tolerance) / 100.0
        conduct = self.conduct_preference / 100.0
        return 0.35 * caution + 0.65 * conduct

    def conflict_walk_threshold(self):
        """Return the conflict heat needed to pull a live deal."""

        return round(18 + self.risk_tolerance * 0.40)

    def objective_profile(self):
        """Return normalized weights for performance, exposure, and conduct."""

        weights = {
            "performance": self.performance_preference,
            "exposure": self.popularity_preference,
            "conduct": self.conduct_preference,
        }
        total = sum(weights.values()) or 1
        return {key: value / total for key, value in weights.items()}

    def primary_objective(self):
        """Return the brand's strongest season objective."""

        profile = self.objective_profile()
        return max(profile, key=profile.get)

    def score_objectives(self, performance, exposure, conduct):
        """Return 0-100 delivery against this brand's season objectives."""

        profile = self.objective_profile()
        return round(
            _clamp(
                performance * profile["performance"]
                + exposure * profile["exposure"]
                + conduct * profile["conduct"]
            )
        )

    def description(self):
        """Return a short label for reports and the dashboard."""

        affinity = (
            f", prefers {self.manufacturer_affinity}"
            if self.manufacturer_affinity
            else ""
        )
        return f"{self.name} ({self.industry}{affinity})"

    def _driver_averages(self, team_drivers):
        """Return popularity, reputation, credibility, and aggression means."""

        if not team_drivers:
            return 55, 55, 55, 50

        count = len(team_drivers)
        popularity = sum(driver.popularity for driver in team_drivers) / count
        reputation = sum(driver.reputation for driver in team_drivers) / count
        credibility = sum(driver.credibility for driver in team_drivers) / count
        aggression = sum(driver.aggression for driver in team_drivers) / count
        return popularity, reputation, credibility, aggression

    def interest_in_team(self, team, team_drivers=None, season_wins=0):
        """Return 0-100 interest in a team based on this brand's tastes."""

        popularity, reputation, credibility, aggression = self._driver_averages(
            list(team_drivers or [])
        )

        score = 45
        score += (
            (self.prestige_preference / 100.0)
            * (team.prestige - 50)
            * 0.45
        )

        performance_signal = _clamp(
            50
            + season_wins * 8
            + team.championships * 6
            + team.performance_trend * 8
            + (team.car_rating - 80)
        )
        score += (
            (self.performance_preference / 100.0)
            * (performance_signal - 50)
            * 0.40
        )
        score += (
            (self.popularity_preference / 100.0)
            * (popularity - 55)
            * 0.35
        )

        conduct_signal = (reputation + credibility) / 2
        score += (
            (self.conduct_preference / 100.0)
            * (conduct_signal - 55)
            * 0.40
        )

        distress = team.financial_distress_level

        if distress >= 2:
            score -= ((100 - self.risk_tolerance) / 100.0) * 18
            score -= 4
        elif distress == 0:
            score += ((100 - self.risk_tolerance) / 100.0) * 6

        if aggression >= 75:
            score += (self.risk_tolerance - 50) * 0.12
            score -= (self.conduct_preference / 100.0) * 6

        if (
            self.manufacturer_affinity
            and team.manufacturer == self.manufacturer_affinity
        ):
            score += 10

        return round(_clamp(score))

    def interest_in_driver(self, driver):
        """Return 0-100 interest in a driver (foundation for endorsements)."""

        score = 45
        score += (
            (self.popularity_preference / 100.0)
            * (driver.popularity - 55)
            * 0.45
        )
        conduct = (driver.reputation + driver.credibility) / 2
        score += (
            (self.conduct_preference / 100.0)
            * (conduct - 55)
            * 0.40
        )

        if driver.aggression >= 75:
            score += (self.risk_tolerance - 50) * 0.15
            score -= (self.conduct_preference / 100.0) * 8

        score += (
            (self.popularity_preference / 100.0)
            * (driver.media_skill - 50)
            * 0.15
        )
        score += (
            (self.performance_preference / 100.0)
            * (
                min(driver.career_wins, 12) * 1.2
                + driver.championships * 6
                + (driver.overall_rating() - 75) * 0.15
            )
        )
        return round(_clamp(score))

    def interest_in_league(self, league_state):
        """Return 0-100 interest in backing the series itself."""

        score = 42
        score += (self.prestige_preference / 100.0) * 22
        score += (self.wealth / 100.0) * 14
        score += (self.conduct_preference / 100.0) * 10
        score += (self.popularity_preference / 100.0) * 8
        score += (league_state.get("integrity", 70) - 50) * 0.12
        score += (league_state.get("fan_interest", 65) - 50) * 0.10
        caution = (100 - self.risk_tolerance) / 100.0
        score -= league_state.get("controversy", 20) * 0.16 * caution
        return round(_clamp(score))

    def __str__(self):
        return self.name


class Network:
    """A broadcaster that might bid for series television rights."""

    def __init__(
        self,
        name,
        kind,
        reach,
        wealth,
        risk_tolerance,
        prestige_preference,
        excitement_preference,
        star_preference,
        integrity_preference,
        preferred_track_types=None,
    ):
        self.name = name
        self.kind = kind
        self.reach = _clamp(reach)
        self.wealth = _clamp(wealth)
        self.risk_tolerance = _clamp(risk_tolerance)
        self.prestige_preference = _clamp(prestige_preference)
        self.excitement_preference = _clamp(excitement_preference)
        self.star_preference = _clamp(star_preference)
        self.integrity_preference = _clamp(integrity_preference)
        self.preferred_track_types = list(preferred_track_types or [])

    def rights_value(self):
        """Return a dollar scale for a full-season rights package."""

        return int(4_000_000 + self.reach * 90_000 + self.wealth * 50_000)

    def profile_summary(self):
        """Return the two strongest tastes plus a risk posture."""

        ranked = sorted(
            [
                ("prestige", self.prestige_preference),
                ("excitement", self.excitement_preference),
                ("stars", self.star_preference),
                ("integrity", self.integrity_preference),
            ],
            key=lambda item: item[1],
            reverse=True,
        )
        top = [label for label, value in ranked[:2] if value >= 55]
        tastes = ", ".join(top) if top else "balanced"
        return f"{tastes}; {self.risk_posture()}"

    def risk_posture(self):
        """Return cautious, measured, or bold from risk tolerance."""

        if self.risk_tolerance >= 65:
            return "bold"
        if self.risk_tolerance <= 40:
            return "cautious"
        return "measured"

    def description(self):
        """Return a short label for reports and the dashboard."""

        return f"{self.name} ({self.kind})"

    def interest_in_league(self, league_state):
        """Return 0-100 interest in buying series television rights."""

        fan = league_state.get("fan_interest", 65)
        integrity = league_state.get("integrity", 70)
        controversy = league_state.get("controversy", 20)
        excitement = fan * 0.50 + controversy * 0.50
        caution = (100 - self.risk_tolerance) / 100.0

        score = 40
        score += (self.prestige_preference / 100.0) * 18
        score += (self.reach / 100.0) * 12
        score += (self.wealth / 100.0) * 10
        score += (self.integrity_preference / 100.0) * (integrity - 50) * 0.35
        score += (self.star_preference / 100.0) * (fan - 50) * 0.25
        score += (self.excitement_preference / 100.0) * (excitement - 45) * 0.20
        score -= controversy * 0.18 * caution
        score += controversy * 0.08 * (self.excitement_preference / 100.0)
        return round(_clamp(score))

    def interest_in_weekend(self, track):
        """Return 0-100 interest in a specific race weekend."""

        score = 48
        if track.type in self.preferred_track_types:
            score += 14

        spectacle = (
            track.incident_risk * 0.45
            + (100 - track.passing_difficulty) * 0.30
            + min(track.purse / 20_000.0, 50) * 0.25
        )
        score += (self.excitement_preference / 100.0) * (spectacle - 40) * 0.30
        score += (self.prestige_preference / 100.0) * (
            min(track.purse / 15_000.0, 60) - 40
        ) * 0.12
        return round(_clamp(score))

    def score_audience(self, rating, league_state):
        """Grade a 0-100 TV rating against this network's tastes."""

        fan = league_state.get("fan_interest", 65)
        integrity = league_state.get("integrity", 70)
        controversy = league_state.get("controversy", 20)
        performance = _clamp(rating)
        exposure = _clamp(rating * 0.55 + fan * 0.45)
        conduct = _clamp((integrity + (100 - controversy)) / 2)
        weights = {
            "performance": self.prestige_preference,
            "exposure": (
                self.star_preference + self.excitement_preference
            ) / 2.0,
            "conduct": self.integrity_preference,
        }
        total = sum(weights.values()) or 1
        delivery = round(
            _clamp(
                performance * weights["performance"] / total
                + exposure * weights["exposure"] / total
                + conduct * weights["conduct"] / total
            )
        )
        return delivery, {
            "performance": round(performance),
            "exposure": round(exposure),
            "conduct": round(conduct),
        }

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
        manufacturer=None,
    ):
        self.name = name
        self.manufacturer = manufacturer or "Independent"
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
        self.organization_titles = 0
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
        self.primary_sponsor = None

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

    def has_primary_sponsor(self):
        """Return whether the team has a named main-sponsor contract."""

        return bool(
            self.primary_sponsor and self.primary_sponsor.get("sponsor")
        )

    def primary_sponsor_label(self):
        """Return the main-sponsor line for reports, or unsponsored."""

        if not self.has_primary_sponsor():
            return "unsponsored"

        deal = self.primary_sponsor
        year_word = "yr" if deal["years"] == 1 else "yrs"
        mood = sponsor_satisfaction_label(deal.get("satisfaction", 55))
        return (
            f"{deal['sponsor']} "
            f"(${deal['value']:,}/yr, {deal['years']} {year_word}) "
            f"— {mood}"
        )

    def sign_primary_sponsor(self, sponsor_name, value, years, season):
        """Sign a multi-year main-sponsor contract."""

        self.primary_sponsor = {
            "sponsor": sponsor_name,
            "value": int(value),
            "years": int(years),
            "signed_season": season,
            "satisfaction": 55,
        }

    def clear_primary_sponsor(self, penalize=True):
        """Drop the main sponsor. Optional prestige hit if the deal is lost."""

        had_deal = self.has_primary_sponsor()
        self.primary_sponsor = None

        if had_deal and penalize:
            self.prestige = _clamp(self.prestige - 4)
            self.owner.pressure = _clamp(self.owner.pressure + 5)

    def collect_primary_sponsor_pay(self):
        """Pay this year's main-sponsor check into the team budget."""

        if not self.has_primary_sponsor():
            return 0

        amount = int(
            self.primary_sponsor["value"]
            * sponsor_pay_multiplier(
                self.primary_sponsor.get("satisfaction", 55)
            )
        )
        self.add_sponsorship(amount)
        return amount

    def advance_primary_sponsor(self):
        """Tick one year off the contract. Return True if it expired."""

        if not self.has_primary_sponsor():
            return False

        self.primary_sponsor["years"] -= 1

        if self.primary_sponsor["years"] <= 0:
            self.clear_primary_sponsor(penalize=False)
            return True

        return False

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

    def record_organization_title(self):
        """Record an organization (team-points) championship."""

        self.organization_titles += 1

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
        capacity=None,
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
        self.capacity = capacity

    def skill_key(self):
        """Return the driver skill attribute used at this track type."""

        return TRACK_TYPE_SKILL_KEYS.get(self.type, "intermediate")

    def seating_capacity(self):
        """Return grandstand capacity, derived from type and purse when unset."""

        if self.capacity:
            return int(self.capacity)

        base = TRACK_TYPE_CAPACITY.get(self.type, 70_000)
        purse_mod = int((self.purse - 600_000) / 20_000)
        purse_mod = max(-8, min(12, purse_mod))
        return int(base + purse_mod * 1_000)

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
        self.endorsement = None
        self.career_endorsement_income = 0

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
        self.season_endorsement_income = 0

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

    def has_endorsement(self):
        """Return whether the driver has an active personal sponsor."""

        return bool(self.endorsement and self.endorsement.get("sponsor"))

    def endorsement_label(self):
        """Return a short personal-sponsor label for reports."""

        if not self.has_endorsement():
            return "unsponsored"

        deal = self.endorsement
        year_word = "yr" if deal["years"] == 1 else "yrs"
        mood = sponsor_satisfaction_label(deal.get("satisfaction", 55))
        return (
            f"{deal['sponsor']} "
            f"(${deal['value']:,}/yr, {deal['years']} {year_word}) "
            f"— {mood}"
        )

    def sign_endorsement(self, sponsor_name, value, years, season):
        """Sign a personal endorsement deal with a brand."""

        self.endorsement = {
            "sponsor": sponsor_name,
            "value": int(value),
            "years": int(years),
            "signed_season": season,
            "satisfaction": 55,
        }

    def clear_endorsement(self):
        """Drop the current personal sponsor, if any."""

        self.endorsement = None

    def collect_endorsement_pay(self):
        """Pay this year's personal-sponsor check to the driver."""

        if not self.has_endorsement():
            return 0

        amount = int(
            self.endorsement["value"]
            * sponsor_pay_multiplier(
                self.endorsement.get("satisfaction", 55)
            )
        )
        self.season_endorsement_income += amount
        self.career_endorsement_income += amount
        self.career_earnings += amount
        return amount

    def advance_endorsement(self):
        """Tick one year off the deal. Return True if it expired."""

        if not self.has_endorsement():
            return False

        self.endorsement["years"] -= 1

        if self.endorsement["years"] <= 0:
            self.clear_endorsement()
            return True

        return False

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
