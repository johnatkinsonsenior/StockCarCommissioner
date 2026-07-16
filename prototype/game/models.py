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

        # Career statistics
        self.career_prize_money = 0
        self.championships = 0
        self.career_wins = 0

    def start_new_season(self):
        """Prepare the team for another season."""

        # For now, preserve the team's ending budget between seasons.
        # Day 13 will add offseason spending and upgrades.
        pass

    def add_prize_money(self, amount):
        """Add race winnings to the team's budget and career total."""

        self.budget += amount
        self.career_prize_money += amount

    def pay_fine(self, amount):
        """Deduct a commissioner fine from the team budget."""

        self.budget = max(0, self.budget - amount)

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

        # Persistent relationship and reputation values
        self.popularity = popularity
        self.morale = 70
        self.commissioner_trust = 60

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
        """Reset statistics that apply only to the new season."""

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

    def __str__(self):
        return self.name
