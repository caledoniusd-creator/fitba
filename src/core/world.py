from dataclasses import dataclass
from random import seed as rand_seed

from typing import Optional, List

from .world_time import WorldTime
from .calendars import Season
from .club import ClubPool
from .competition import Competition
from .people import PersonPool
from .staff import StaffPool


@dataclass
class World:
    world_seed: int
    world_time: WorldTime

    current_season: Optional[Season] = None
    previous_seasons: Optional[List[Season]] = None

    club_pool: Optional[ClubPool] = None
    competitions: Optional[List[Competition]] = None

    person_pool: Optional[PersonPool] = None
    staff_pool: Optional[StaffPool] = None

    def __post_init__(self):
        self.previous_seasons = self.previous_seasons or []
        self.club_pool = self.club_pool or ClubPool()
        self.competitions = self.competitions or []
        self.person_pool = self.person_pool or PersonPool()
        self.staff_pool = self.staff_pool or StaffPool()

        rand_seed(self.world_seed)

    def __str__(self):
        return f"World Time -> {self.world_time}"
