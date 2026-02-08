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


class StaffPool:
    def __init__(self):
        self._staff = set()

    def get_all_staff(self):
        return list(self._staff)

    @property
    def count(self):
        return len(self._staff)

    def add_staff_person(self, staff_person: StaffMember):
        self._staff.add(staff_person)

    def add_staff_people(self, staff_people: List[StaffMember]):
        self._staff.update(staff_people)

    def clear(self):
        self._staff.clear()

    def remove_staff_person(self, staff_person: StaffMember):
        self._staff.discard(staff_person)
