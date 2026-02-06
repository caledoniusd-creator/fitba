from enum import Enum, auto, unique


from .club import Club


@unique
class CompetitionType(Enum):
    FRIENDLY = auto()
    LEAGUE = auto()
    KNOCKOUT = auto()


class Competition:
    def __init__(
        self, name: str, shortname: str, ranking: int, comp_type: CompetitionType
    ):
        self.name = name
        self.shortname = shortname
        self.ranking = ranking
        self.type = comp_type

        self.clubs = []

    def __str__(self):
        return f"{self.name} ({self.shortname}) [{self.type.name}], #Clubs: {len(self.clubs)} Rank: {self.ranking}"

    @property
    def club_count(self):
        return len(self.clubs)

    def contains(self, club: Club):
        return club in self.clubs


class Friendly(Competition):
    def __init__(self, name: str, shortname: str = ""):
        super().__init__(name, shortname, 1000, CompetitionType.FRIENDLY)
        self.clubs = []


class League(Competition):
    def __init__(self, name: str, shortname: str, ranking: int):
        super().__init__(name, shortname, ranking, CompetitionType.LEAGUE)
        self.clubs = []


class Cup(Competition):
    def __init__(self, name, shortname, ranking: int):
        super().__init__(name, shortname, ranking, CompetitionType.KNOCKOUT)
