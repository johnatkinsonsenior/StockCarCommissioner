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

        return int(round(value / 25_000) * 25_000)

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

    def __str__(self):
        return self.name
