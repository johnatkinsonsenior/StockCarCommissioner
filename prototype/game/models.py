class Team:
    """Represents a stock car racing team."""

    def __init__(
        self,
        name,
        car_rating,
        crew_rating,
        reliability,
        starting_budget,
    ):
        self.name = name
        self.car_rating = car_rating
        self.crew_rating = crew_rating
        self.reliability = reliability
        self.starting_budget = starting_budget
        self.budget = starting_budget

    def reset_season(self):
        """Reset financial values for a new test season."""

        self.budget = self.starting_budget

    def add_prize_money(self, amount):
        self.budget += amount

    def pay_fine(self, amount):
        self.budget -= amount

    def __str__(self):
        return self.name


class Driver:
    """Represents a stock car racing driver."""

    def __init__(
        self,
        name,
        team_name,
        speed,
        consistency,
        aggression,
        personality,
        rival,
        popularity,
    ):
        self.name = name
        self.team_name = team_name
        self.speed = speed
        self.consistency = consistency
        self.aggression = aggression
        self.personality = personality
        self.rival = rival
        self.starting_popularity = popularity

        self.reset_season()

    def reset_season(self):
        """Reset statistics at the beginning of a season."""

        self.points = 0
        self.earnings = 0
        self.starts = 0
        self.finishes = 0
        self.wins = 0
        self.dnfs = 0

        self.morale = 70
        self.popularity = self.starting_popularity
        self.commissioner_trust = 60

        self.warnings = 0
        self.fines = 0
        self.points_penalties = 0
        self.suspensions = 0
        self.suspension_races = 0

    def add_points(self, amount):
        self.points += amount

    def deduct_points(self, amount):
        self.points = max(0, self.points - amount)
        self.points_penalties += amount

    def add_earnings(self, amount):
        self.earnings += amount

    def is_suspended(self):
        return self.suspension_races > 0

    def __str__(self):
        return self.name
