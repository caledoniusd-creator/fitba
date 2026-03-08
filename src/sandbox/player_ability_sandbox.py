
from dataclasses import dataclass
from enum import Enum, unique
from random import choices, triangular, random
from typing import Optional

@unique
class PlayerRating(Enum):
    Elite = 1
    Very_Good = 2
    Good = 3
    Above_Average = 4
    Average = 5
    Below_Average = 6
    Poor = 7
    Very_Poor = 8
    Inadaquate = 9
    
    @staticmethod
    def random_ability(rating):
        all_ratings = [r for r in PlayerRating]
        rating_count = len(all_ratings)
        
        rating_step = 100 / rating_count
        half_step = rating_step / 2
        rating_level = 9 - (rating.value)
    
        level_range = rating_step * rating_level, rating_step * rating_level + 1
        ability = int(round(triangular(level_range[0], level_range[1], level_range[0] + half_step)))
        return ability
    
    @staticmethod
    def random():
        weights = [1, 2, 4, 8, 16, 8, 4, 2, 1]
        values = [r for r in PlayerRating]
        return choices(values, weights=weights, k=1)[0]
    
    def __str__(self):
        return str(self.name).replace("_", " ")
    
    
    
def calculate_current_ability(age: int, potential_ability: float) -> float:
    """
    Calculate current ability from age (16-40) and potential (0-100).

    - Ages 16-24: linear from initial_at_16 to 80% of potential at 24.
        initial_at_16 is chosen so the per-year gain required between 16 and 24 is < 10.
    - Ages 25-30: linear from 80% to 100% of potential.
    - Ages 31-40: non-linear decline (slow at first, accelerating toward 40).
    """
    # clamp inputs
    age = max(16, min(40, int(age)))
    potential = max(0, min(100.0, potential_ability))

    target_24 = round(0.9 * potential)

    # start at ~40% of potential
    initial_16 = int(max(0, potential * 0.4))

    if age <= 16:
        return initial_16

    if age <= 24:
        # linear interpolation 16 -> 24
        frac = (age - 16) / 8.0
        value = initial_16 + (target_24 - initial_16) * frac
        return int(round(value))

    if age <= 30:
        # linear interpolation 24 -> 30 from 80% to 100% of potential
        frac = (age - 24) / 6.0
        value = target_24 + (potential - target_24) * frac
        return int(round(value))

    # ages 31-40: accelerating decline using a quadratic curve
    # decline_fraction goes 0.1 -> 1.0 for ages 31 -> 40
    decline_fraction = (age - 30) / 10.0
    decay = decline_fraction ** 2  # slow early, faster later
    max_drop_fraction = 0.8  # maximum drop by age 40 (fraction of potential)
    drop = potential * max_drop_fraction * decay
    value = potential - drop
    return int(round(max(0, value)))


@dataclass
class PlayerDataTest:
    age: int
    rating: PlayerRating
    potential_ability: float
    current_ability: int = 0
    abilty_at_21: int = 0
    
    def __post_init__(self):
        self.update_current_ability()
    
    def __str__(self):
        return f"({self.age}) [{self.rating}] => cur: {self.current_ability:3d} pot: {self.potential_ability:2.02f}"
        
    def update_current_ability(self):
        self.current_ability = calculate_current_ability(self.age, self.potential_ability)
        if self.age == 21:
            self.abilty_at_21 = self.current_ability
        
    def should_retire(self):
        return self.age > 21 and self.abilty_at_21 > self.current_ability
        
    def reduce_potential(self):
        reduction_percent = 0.05 * random() 
        reduction_amount = reduction_percent * self.potential_ability
        self.potential_ability -= reduction_amount

    
def test_player_ability():
    age_range = (16, 40)
    for i in range(1):
        rating = PlayerRating.random()
 
        player = PlayerDataTest(age=age_range[0], rating=rating, potential_ability=PlayerRating.random_ability(rating=rating))
        season = 1
        while player.age <= age_range[1]:
            print(f"Season {season:2d} - Player: {player}")
            
            player.age += 1
            season += 1
            
            player.update_current_ability()
            if player.should_retire() is True:
                print(f"Retiring at age: {player.age}")
                break
            else:
                player.reduce_potential()
        

