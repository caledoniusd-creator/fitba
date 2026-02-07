from enum import Enum, unique

from random import choice


@unique
class ReputationLevel(Enum):
    Unknown = 0
    Poor = 1
    Good = 2
    Very_Good = 3
    Superb = 4

    @staticmethod
    def random():
        return choice([r for r in ReputationLevel])

    def __str__(self):
        return str(self.name).replace("_", " ")


@unique
class PersonalityType(Enum):
    Withdrawn = 1
    Passive = 2
    Selfish = 3
    Unselfish = 4
    Rebellious = 5
    Responsible = 6
    Arrogant = 7
    Confident = 8
    Thoughtful = 9
    Rash = 10

    @staticmethod
    def random():
        return choice([r for r in PersonalityType])
