from dataclasses import dataclass
from typing import Optional, Dict


from .world_time import WEEKS_IN_YEAR


@dataclass
class CalendarBase:
    year: int
    weeks: Optional[Dict] = None

    def __post_init__(self):
        self.weeks = self.weeks or {i + 1: [] for i in range(WEEKS_IN_YEAR)}

    @property
    def num_weeks(self):
        return len(self.weeks.keys())

    @property
    def count(self):
        return sum(len(objects) for objects in self.weeks.values())

    def add_objects(self, week: int, objects):
        if week not in self.weeks:
            raise ValueError(f"Week {week} is not valid in year {self.year}")
        self.weeks[week].extend(objects)


@dataclass
class FixtureCalendar(CalendarBase):
    def clear_fixtures(self, week: int):
        if week not in self.weeks:
            raise ValueError(f"Week {week} is not valid in year {self.year}")
        self.weeks[week].clear()


@dataclass
class ResultCalendar(CalendarBase):
    pass


@dataclass
class Season:
    year: int
    fixture_calendar: Optional[FixtureCalendar] = None
    match_results: Optional[ResultCalendar] = None

    def __post_init__(self):
        self.fixture_calendar = self.fixture_calendar or FixtureCalendar(self.year)
        self.match_results = self.match_results or ResultCalendar(self.year)

    def __str__(self):
        return f"Season {self.year} #num fixtures: {self.fixture_calendar.count}, #results: {self.match_results.count}"
