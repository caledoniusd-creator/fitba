

from enum import Enum
import logging
from random import choices
from collections import Counter


class ResultType(Enum):
    HomeWin = "Home"
    Draw = "Draw"
    HomeLoss = "Away"
    
    
def generate_expected_result(home_ability: int, away_ability: int) -> dict[ResultType, float]:
    """
    Generate probabilities for HomeWin, Draw, HomeLoss based on abilities 0-100.
    - Start from equal 1/3 probabilities.
    - Closer teams increase draw probability (continuous).
    - Advantage for win uses a discrete step per 10-point difference.
    """
    ha = max(0, min(100, int(home_ability)))
    aa = max(0, min(100, int(away_ability)))
    diff = ha - aa
    abs_diff = abs(diff)

    base = 1.0 / 3.0

    # Draw increases the closer the teams are (max extra +0.15 when identical)
    closeness = 1.0 - (abs_diff / 100.0)
    draw = base + (closeness * 0.15)

    # Discrete win boost: each 10-point step gives a small boost to the stronger side
    steps = int(abs_diff // 10)
    win_step = 0.05
    win_boost = steps * win_step

    if diff > 0:
        home = base + win_boost
        away = 1.0 - draw - home
    elif diff < 0:
        away = base + win_boost
        home = 1.0 - draw - away
    else:
        home = base
        away = base

    # Clamp and normalize to ensure valid probabilities
    home = max(0.0, home)
    draw = max(0.0, draw)
    away = max(0.0, away)
    total = home + draw + away
    if total == 0:
        results = [
            (ResultType.HomeWin, 1/3),
            (ResultType.Draw, 1/3),
            (ResultType.HomeLoss, 1/3),
        ]
    else:
        results = [
            (ResultType.HomeWin, home / total),
            (ResultType.Draw, draw / total),
            (ResultType.HomeLoss, away / total),
        ]
        
    results.sort(key=lambda x: x[1], reverse=True)
    return results


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
    ability_diff_ratio = ability_diff / 100  * 0.5
    
    # Base probabilities adjusted by ability difference
    draw_prob = 0.6 - abs(ability_diff_ratio)
    home_prob = 0.2 + ability_diff_ratio
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

    result_count = 10
    for ab in test_abilities:

        probs = calculate_match_probabilities(ab[0], ab[1])
        text = f"{ab[0]} v {ab[1]} - H: {probs[ResultType.HomeWin]:0.2f} " \
            f"D: {probs[ResultType.Draw]:0.2f} A: {probs[ResultType.HomeLoss]:0.2f}"
        
        values = []
        weights = []
        for key, value in probs.items():
            values.append(key)
            weights.append(value)

        expected_result = generate_expected_result(ab[0], ab[1])
        max_prob = expected_result[0][1]
        expected_result = [x for x in expected_result if x[1] == max_prob]
        
        expected_result_text = ", ".join([xr[0].name for xr in expected_result])
        
        simulated_results = choices(values, weights=weights, k=result_count)
        num_results = len(simulated_results)
        
        counts = Counter(simulated_results)
        text += " - " + ", ".join([f"{rt.value}: {counts.get(rt,0)}" for rt in ResultType])  
        
        # r_text = ", ".join([f"{r.value}" for r in simulated_results])
        print(f"expected: {expected_result_text}")
        print(f"{text}")