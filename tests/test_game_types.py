import pytest


from src.core.game_types import ReputationLevel


def test_reputation_level():
    enums = [e for e in ReputationLevel]
    for e in enums:
        assert(e)
        with pytest.raises(ValueError):
            str(e).index("_")

    for _ in range(100):
        e = ReputationLevel.random()
        assert(e)
        assert(e in ReputationLevel)