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