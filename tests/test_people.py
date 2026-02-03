from src.core.people import Name, Person, PersonFactory


def test_names():
    examples = [
        ("Andrew", "Baxter"),
        ("Chris", "Derry"),
        ("Eric", "Freshman")
    ]

    for example in examples:
        name = Name(example[0], example[1])
        assert(name)
        assert(name.first_name == example[0])
        assert(name.last_name == example[1])
        assert(str(name) == f"{example[0]} {example[1]}")
        assert(name.short_name == f"{example[0][0:1]}. {example[1]}")


def test_person():
    examples = [
        (("Andrew", "Baxter"), 34),
        (("Chris", "Derry"), 45),
        (("Eric", "Freshman"), 16)
    ]

    for example in examples:
        person = Person(Name(example[0][0], example[0][1]), example[1])
        assert(person)
        assert(person.name.first_name == example[0][0])
        assert(person.name.last_name == example[0][1])
        assert(person.age == example[1])
        assert(str(person) == f"{example[0][0]} {example[0][1]} ({example[1]})")


def test_people():
    for _ in range(100):
        p = PersonFactory.random_male()
        assert(p)
        assert(str(p) != "")
        assert 18 <= p.age <= 65

def test_staff_people():
    for _ in range(100):
        p = PersonFactory.random_staff()
        assert(p)
        assert(str(p) != "")
        assert(35 <= p.age <= 60)


def test_player_people():
    for _ in range(100):
        p = PersonFactory.random_player()
        assert(p)
        assert(str(p) != "")
        assert(18 <= p.age <= 30)
