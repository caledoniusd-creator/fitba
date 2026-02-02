from dataclasses import dataclass
from typing import List

from .club import Club
from .competition import Competition


CLUB_NAME_SIZE = 24


@dataclass(frozen=True)
class Fixture:
    club1: Club
    club2: Club
    competition: Competition
    round_num: int = 0

    def competition_text(self):
        competition_str = f"{self.competition.shortname}"
        if self.round_num > 0:
            competition_str += f" Rnd {self.round_num}"
        return competition_str

    def __str__(self):
        return f"{self.competition_text().ljust(12)} {self.club1.name.rjust(CLUB_NAME_SIZE)} vs {self.club2.name.ljust(CLUB_NAME_SIZE)}"


@dataclass(frozen=True)
class Result(Fixture):
    home_score: int = 0
    away_score: int = 0

    def __str__(self):
        return f"{self.competition_text().ljust(12)} {self.club1.name.rjust(CLUB_NAME_SIZE)}  {self.home_score}-{self.away_score}  {self.club2.name.ljust(CLUB_NAME_SIZE)}"


class FixtureWorker:
    def __init__(self, fixtures: List[Fixture]):
        self.fixtures = fixtures

    def group_by_competition(self):
        groups = dict()
        for f in self.fixtures:
            if f.competition not in groups:
                groups[f.competition] = list()
            groups[f.competition].append(f)

        groups = [(competition, fixtures) for competition, fixtures in groups.items()]
        groups.sort(key=lambda x: x[0].ranking)
        return groups


class ResultWorker:
    def __init__(self, results: List[Result]):
        self.results = results

    def group_by_competition(self):
        groups = dict()
        for r in self.results:
            if r.competition not in groups:
                groups[r.competition] = list()
            groups[r.competition].append(r)

        groups = [(competition, results) for competition, results in groups.items()]
        groups.sort(key=lambda x: x[0].ranking)
        return groups
