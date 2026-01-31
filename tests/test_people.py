
from src.core.people import PersonFactory


def test_people():
    p = PersonFactory.random_male()
    print(p)
