from dataclasses import dataclass
from typing import List, Optional


from .game_types import ReputationLevel, StaffRole
from .people import Person
from .ability import random_ability


@dataclass
class StaffMember:
    person: Person
    role: StaffRole
    reputation: Optional[ReputationLevel] = None
    ability: Optional[int] = None

    def __post_init__(self):
        self.reputation = self.reputation or ReputationLevel.random()
        self.ability = self.ability or random_ability(0.15)

    def __str__(self):
        return f"{self.person.name.short_name} {str(self.role)} {self.reputation} ({self.ability})"

    def __hash__(self):
        return hash(str(self))


class StaffMemberFactory:
    @staticmethod
    def random_staff_member(person: Person, role: StaffRole):
        return StaffMember(person, role, ReputationLevel.random(), random_ability())


