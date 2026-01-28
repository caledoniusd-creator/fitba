from dataclasses import dataclass

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

