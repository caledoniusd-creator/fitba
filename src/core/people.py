from dataclasses import dataclass
from faker import Faker
from random import gauss
from typing import List


from .game_types import PersonalityType


@dataclass
class Name:
    first_name: str
    last_name: str

    @staticmethod
    def random_male_name():
        return Name(
            PersonFactory.fake.first_name_male(), PersonFactory.fake.last_name()
        )

    def __str__(self):
        return self.full_name

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def short_name(self):
        return f"{self.first_name[:1]}. {self.last_name}"


class Person:
    def __init__(self, name: Name, age, personality: PersonalityType):
        self.name = name
        self.age = age
        self.personality = personality

    def __str__(self):
        return f"{self.name} ({self.age}) [{self.personality.name}]"


class PersonFactory:
    fake = Faker("en_GB")

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
        age = PersonFactory.generate_age(
            min_age=min_age, max_age=max_age, average=average
        )

        return Person(Name.random_male_name(), age, PersonalityType.random())

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
