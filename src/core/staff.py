
from dataclasses import dataclass
from enum import Enum, unique
from random import randint
from typing import List, Optional


from .game_types import ReputationLevel
from .people import Person


MAX_RATING = 100


def random_rating(margin: float = 0.1):
    margin_value = MAX_RATING * margin
    min_value, max_value = int(round(margin_value)), int(round(MAX_RATING - margin_value))
    return randint(min_value, max_value)


@unique
class StaffRole(Enum):
    Undefined = 0
    Manager = 1
    Coach = 2
    Scout = 3
    Physio = 4



@dataclass
class StaffMember:
    person: Person
    role: StaffRole
    reputation: Optional[ReputationLevel] = None
    rating: Optional[int] = None

    def __post_init__(self):
        self.reputation = self.reputation or ReputationLevel.random()
        self.rating = self.rating or random_rating(0.15)

    def __str__(self):
        return f"{self.person.name.short_name} {str(self.role)} {self.reputation} ({self.rating})"
    
    def __hash__(self):
        return hash(str(self))

class StaffMemberFactory:

    @staticmethod
    def random_staff_member(person: Person, role: StaffRole):
        return StaffMember(person, role, ReputationLevel.random(), random_rating())
    


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
