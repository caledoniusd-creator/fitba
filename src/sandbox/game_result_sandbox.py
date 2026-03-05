

from enum import Enum
import logging
from random import choices


class ResultType(Enum):
    HomeWin = "Home"
    Draw = "Draw"
    HomeLoss = "Away"


def calculate_match_probabilities(home_ability: int, away_ability: int) -> dict[ResultType, float]:
    """
    Calculate the probability of each match result based on team abilities.
    
    Args:
        home_ability: Home team ability (0-100)
        away_ability: Away team ability (0-100)
    
    Returns:
        Dictionary with probabilities for each ResultType
    """
    ability_diff = home_ability - away_ability
    ability_diff_ratio = ability_diff / 250
    
    # Base probabilities adjusted by ability difference
    draw_prob = 0.34 - abs(ability_diff_ratio)
    home_prob = 0.33 + ability_diff_ratio
    away_prob = 1 - draw_prob - home_prob
    
    # Normalize to ensure valid probabilities
    total = home_prob + draw_prob + away_prob
    
    return {
        ResultType.HomeWin: max(0, min(1, home_prob / total)),
        ResultType.Draw: max(0, min(1, draw_prob / total)),
        ResultType.HomeLoss: max(0, min(1, away_prob / total)),
    }


def game_result_function():
    test_abilities = [
        (50, 50),
        (75, 25),
        (60, 40),
        (40, 60),
        (90, 74),
        (85, 83),
        (20, 75),
        (3, 6)
    ]

    result_count = 5
    for ab in test_abilities:

        probs = calculate_match_probabilities(ab[0], ab[1])
        text = f"{ab[0]} v {ab[1]} - H: {probs[ResultType.HomeWin]:0.2f} " \
            f"D: {probs[ResultType.Draw]:0.2f} A: {probs[ResultType.HomeLoss]:0.2f}"
        
        values = []
        weights = []
        for key, value in probs.items():
            values.append(key)
            weights.append(value)

        simulated_results = choices(values, weights=weights, k=result_count)
        r_text = ", ".join([f"{r.value}" for r in simulated_results])
        print(f"{text} - {r_text}")