from enum import Enum, unique

from random import choice, randint


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

    def str(self):
        return " ".join([t[0:1].upper() + t[1:].lower() for t in self.name.split("_")])


@unique
class StaffRole(Enum):
    Undefined = 0
    Manager = 1
    Coach = 2
    Scout = 3
    Physio = 4


@unique
class ContractType(Enum):
    Staff_Contract = 1
    Player_Contract = 2


@unique
class Position(Enum):
    Goalkeeper = (1, "GK", "Goalkeeper")
    Defender = (2, "DF", "Defender")
    Midfielder = (3, "MD", "Midfielder")
    Attacker = (4, "AT", "Attacker")

    @staticmethod
    def outfeild_positions():
        return [Position.Defender, Position.Midfielder, Position.Attacker]

    @staticmethod
    def random(goalkeeper_ratio=1 / 7):
        prob = int(round(1 / goalkeeper_ratio))
        if randint(1, prob) == prob:
            return Position.Goalkeeper
        return choice(Position.outfeild_positions())
