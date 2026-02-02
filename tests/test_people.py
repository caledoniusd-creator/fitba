from src.core.people import PersonFactory


def test_people():
    for _ in range(100):
        p = PersonFactory.random_male()
        assert 18 <= p.age <= 65
        print(p)


def test_staff_people():
    for _ in range(100):
        p = PersonFactory.random_staff()
        assert 35 <= p.age <= 60
        print(p)
