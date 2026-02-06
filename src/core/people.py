from dataclasses import dataclass
import names
from random import gauss
from typing import List


@dataclass
class Name:
    first_name: str
    last_name: str

    def __str__(self):
        return self.full_name

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def short_name(self):
        return f"{self.first_name[:1]}. {self.last_name}"


class Person:
    def __init__(self, name: Name, age):
        self.name = name
        self.age = age

    def __str__(self):
        return f"{self.name} ({self.age})"


class PersonFactory:
    @staticmethod
    def generate_age(
        min_age: int, max_age: int, average: float, std_dev: float | None = None
    ) -> int:
        """
        Generate an age using a bell curve (normal distribution),
        constrained to [min_age, max_age].

        - average: the mean of the distribution
        - std_dev: spread; defaults to a sensible value based on the range
        """

        if std_dev is None:
            # Rule of thumb: ~99.7% of values fall within ±3σ
            std_dev = (max_age - min_age) / 6

        while True:
            age = gauss(average, std_dev)
            if min_age <= age <= max_age:
                return round(age)

    @staticmethod
    def random_male(min_age=18, max_age=65, average=40):
        name = Name(names.get_first_name(gender="male"), names.get_last_name())
        age = PersonFactory.generate_age(
            min_age=min_age, max_age=max_age, average=average
        )

        return Person(name, age)

    @staticmethod
    def random_staff(min_age=35, max_age=60, average=42):
        return PersonFactory.random_male(
            min_age=min_age, max_age=max_age, average=average
        )

    @staticmethod
    def random_player(min_age=18, max_age=30, average=24):
        return PersonFactory.random_male(
            min_age=min_age, max_age=max_age, average=average
        )


class PersonPool:
    def __init__(self):
        self._people = set()

    def add_person(self, person: Person):
        self._people.add(person)

    def add_people(self, new_people: List[Person]):
        self._people.update(new_people)

    def remove_person(self, person: Person):
        self._people.discard(person)

    def get_all_people(self):
        return list(self._people)

    @property
    def count(self):
        return len(self._people)

    def clear(self):
        self._people.clear()


# def persons_main():
#     count = 10
#     people = [PersonFactory.random_male() for _ in range(count)]
#     staff = [PersonFactory.random_staff() for _ in range(count)]
#     players = [PersonFactory.random_player() for _ in range(count)]

#     cols = [[], [], []]

#     for person, employee, players in zip(people, staff, players):
#         cols[0].append(str(person).ljust(30))
#         cols[1].append(str(employee).ljust(30))
#         cols[2].append(str(players).ljust(30))
#     for c1, c2, c3 in zip(cols[0], cols[1], cols[2]):
#         print(f"{c1} | {c2} | {c3}")


# if __name__ == "__main__":
#     persons_main()
