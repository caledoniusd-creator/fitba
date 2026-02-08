from random import randint


MAX_ABILITY = 100


def random_ability(margin: float = 0.1):
    margin_value = MAX_ABILITY * margin
    min_value, max_value = (
        int(round(margin_value)),
        int(round(MAX_ABILITY - margin_value)),
    )
    return randint(min_value, max_value)
