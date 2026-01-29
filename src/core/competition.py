from enum import Enum, auto, unique


@unique
class CompetitionType(Enum):
    FRIENDLY = auto()
    LEAGUE = auto()
    KNOCKOUT = auto()


class Competition:
    def __init__(self, name, shortname, comp_type: CompetitionType):
        self.name = name
        self.shortname = shortname
        self.type = comp_type
        self.clubs = []

    def __str__(self):
        return f"{self.name} ({self.shortname}) [{self.type.name}], #Clubs: {len(self.clubs)}"

    @property
    def club_count(self):
        return len(self.clubs)


class Friendly(Competition):
    def __init__(self, name, shortname=""):
        super().__init__(name, shortname, CompetitionType.FRIENDLY)
        self.clubs = []


class League(Competition):
    def __init__(self, name, shortname):
        super().__init__(name, shortname, CompetitionType.LEAGUE)
        self.clubs = []


class Cup(Competition):
    def __init__(self, name, shortname):
        super().__init__(name, shortname, CompetitionType.KNOCKOUT)
