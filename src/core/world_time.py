from dataclasses import dataclass


DAYS_IN_WEEK = 7
WEEKS_IN_YEAR = 52


@dataclass
class WorldTime:
    """
    World time object
    """

    year: int
    week: int
    day: int = 1

    def __post_init__(self):
        if self.day < 1 or self.day > DAYS_IN_WEEK:
            raise ValueError(f"Day must be between 1 and {DAYS_IN_WEEK}")
        if self.week < 1 or self.week > WEEKS_IN_YEAR:
            raise ValueError(f"Week must be between 1 and {WEEKS_IN_YEAR}")
        if self.year < 1:
            raise ValueError("Year must be a positive integer")

    def __str__(self):
        return f"Year: {self.year:2d}, Week: {self.week:2d}, Day: {self.day:1d}"

    def advance_day(self):
        if self.day == DAYS_IN_WEEK:
            self.day == 1
            self.advance_week()
        else:
            self.day += 1

    def advance_week(self):
        if self.week == WEEKS_IN_YEAR:
            self.week = 1
            self.year += 1
        else:
            self.week += 1
