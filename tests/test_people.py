from src.core.people import Name, Person, PersonFactory, PersonPool


def test_names():
    """
    Test Names
    """
    examples = [("Andrew", "Baxter"), ("Chris", "Derry"), ("Eric", "Freshman")]

    for example in examples:
        name = Name(example[0], example[1])
        assert name
        assert name.first_name == example[0]
        assert name.last_name == example[1]
        assert str(name) == f"{example[0]} {example[1]}"
        assert name.short_name == f"{example[0][0:1]}. {example[1]}"


def test_person():
    """
    Test Person
    """
    examples = [
        (("Andrew", "Baxter"), 34),
        (("Chris", "Derry"), 45),
        (("Eric", "Freshman"), 16),
    ]

    for example in examples:
        person = Person(Name(example[0][0], example[0][1]), example[1])
        assert person
        assert person.name.first_name == example[0][0]
        assert person.name.last_name == example[0][1]
        assert person.age == example[1]
        assert str(person) == f"{example[0][0]} {example[0][1]} ({example[1]})"


def test_person_factory():
    """
    Test PersonFactory
    """

    age_count = 20
    person_count = 50

    age_range = 18, 35, 24
    for _ in range(age_count):
        age_no_stddev = PersonFactory.generate_age(
            age_range[0], age_range[1], age_range[2]
        )
        age_stddev = PersonFactory.generate_age(
            age_range[0], age_range[1], age_range[2], (age_range[1] - age_range[0]) / 3
        )
        assert age_range[0] <= age_no_stddev <= age_range[1]
        assert age_range[0] <= age_stddev <= age_range[1]

    def check_person(p, min_age, max_age):
        assert p
        assert min_age <= p.age <= max_age
        assert str(p) != ""

    for _ in range(person_count):
        check_person(PersonFactory.random_male(), 18, 65)
        check_person(PersonFactory.random_staff(), 35, 60)
        check_person(PersonFactory.random_player(), 18, 30)


def test_person_pool():
    """
    Test PersonPool
    """
    count = 10
    pool = PersonPool()
    assert pool

    people = [PersonFactory.random_male() for _ in range(count)]
    assert len(people) == count
    person = people[0]
    assert person
    pool.add_person(person)
    assert pool.count == 1
    assert pool.get_all_people()[0] == person
    pool.remove_person(person)
    assert pool.count == 0
    assert person not in pool.get_all_people()

    pool.add_people(people)
    assert pool.count == len(people)
    for p in people:
        assert person in pool.get_all_people()
    pool.clear()
    assert pool.count == 0
