from dataclasses import dataclass
from typing import Dict, List, Optional


from .world_time import WEEKS_IN_YEAR
from .fixture import Result


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

    def clear_objects(self, week: int):
        if week not in self.weeks:
            raise ValueError(f"Week {week} is not valid in year {self.year}")
        self.weeks[week].clear()


@dataclass
class SeasonFixtureShedule(CalendarBase):
    def add_fixtures(self, week: int, fixtures: List):
        self.add_objects(week=week, objects=fixtures)

    def set_results(self, week: int, results: List):
        self.clear_objects(week=week)
        self.add_objects(week=week, objects=results)

    def get_fixtures(self, with_week: bool = False):
        all_fixtures = []
        for week, entries in self.weeks.items():
            if with_week:
                all_fixtures.extend(
                    [
                        (week, entry)
                        for entry in entries
                        if not isinstance(entry, Result)
                    ]
                )
            else:
                all_fixtures.extend(
                    [entry for entry in entries if not isinstance(entry, Result)]
                )
        return all_fixtures

    def get_results(self, with_week: bool = False):
        all_results = []
        for week, entries in self.weeks.items():
            if with_week:
                all_results.extend(
                    [(week, entry) for entry in entries if isinstance(entry, Result)]
                )
            else:
                all_results.extend(
                    [entry for entry in entries if isinstance(entry, Result)]
                )
        return all_results

    def get_fixtures_for_week(self, week):
        fixtures = []
        if week in self.weeks:
            fixtures.extend([f for f in self.weeks[week] if not isinstance(f, Result)])
        return fixtures

    def get_results_for_week(self, week):
        results = []
        if week in self.weeks:
            results.extend([r for r in self.weeks[week] if isinstance(r, Result)])
        return results

    @property
    def fixture_count(self):
        return len(self.get_fixtures())

    @property
    def result_count(self):
        return len(self.get_results())


@dataclass
class Season:
    year: int
    fixture_schedule: Optional[SeasonFixtureShedule] = None

    def __post_init__(self):
        self.fixture_schedule = self.fixture_schedule or SeasonFixtureShedule(self.year)

    def __str__(self):
        return (
            f"Season {self.year} "
            f"#num fixtures: {self.fixture_schedule.fixture_count}, "
            f"#results: {self.fixture_schedule.result_count}"
        )
