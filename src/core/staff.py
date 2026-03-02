from dataclasses import dataclass
from typing import Optional


from .game_types import ReputationLevel, StaffRole, MatchFormation
from .people import Person
from .ability import random_ability


@dataclass
class StaffMember:
    person: Person
    role: StaffRole
    reputation: Optional[ReputationLevel] = None
    ability: Optional[int] = None
    preferred_formation: Optional[MatchFormation] = None

    def __post_init__(self):
        self.reputation = self.reputation or ReputationLevel.random()
        self.ability = self.ability or random_ability(0.15)
        self.preferred_formation or MatchFormation.random()

    def __str__(self):
        return f"{self.person.name.short_name} {str(self.role)} {self.reputation} ({self.ability})"

    def __hash__(self):
        return hash(str(self))


class StaffMemberFactory:
    @staticmethod
    def random_staff_member(person: Person, role: StaffRole):
        return StaffMember(person, role, ReputationLevel.random(), random_ability())
