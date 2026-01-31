from dataclasses import dataclass
import names
from random import randint


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
    def random_male():
        name = Name(names.get_first_name(gender="male"), names.get_last_name())
        age = randint(18, 65)

        return Person(name, age)
