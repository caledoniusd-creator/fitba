from __future__ import annotations


from sqlalchemy import ForeignKey, String, Integer, Enum as SAEnum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


from ..game_types import (
    PersonalityType,
    StaffRole,
    ReputationLevel,
    ContractType,
    Position,
)

from ..competition import CompetitionType


class Base(DeclarativeBase):
    pass


class PersonDB(Base):
    __tablename__ = "persons"

    id: Mapped[int] = mapped_column(primary_key=True)

    first_name: Mapped[str] = mapped_column(String(50), index=True)
    last_name: Mapped[str] = mapped_column(String(50), index=True)
    age: Mapped[int] = mapped_column(Integer)

    personality: Mapped[PersonalityType] = mapped_column(SAEnum(PersonalityType))

    def __repr__(self) -> str:
        return (
            f"Person(id={self.id}, "
            f"name={self.first_name} {self.last_name}, "
            f"age={self.age}, "
            f"personality={self.personality})"
        )

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def short_name(self):
        return f"{self.first_name[:1]}. {self.last_name}"


class StaffDB(Base):
    __tablename__ = "staff"

    id: Mapped[int] = mapped_column(primary_key=True)
    person_id: Mapped[int] = mapped_column(
        ForeignKey("persons.id"),
        unique=True,  # 👈 enforce one-to-one at DB level
    )

    role: Mapped[StaffRole] = mapped_column(SAEnum(StaffRole))

    reputation_type: Mapped[ReputationLevel] = mapped_column(SAEnum(ReputationLevel))

    ability: Mapped[int] = mapped_column(Integer)


class PlayerDB(Base):
    __tablename__ = "players"

    id: Mapped[int] = mapped_column(primary_key=True)
    person_id: Mapped[int] = mapped_column(
        ForeignKey("persons.id"),
        unique=True,  # 👈 enforce one-to-one at DB level
    )

    position: Mapped[Position] = mapped_column(SAEnum(Position))

    ability: Mapped[int] = mapped_column(Integer)


class ClubDB(Base):
    __tablename__ = "clubs"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, index=True)


class ContractDB(Base):
    __tablename__ = "contracts"

    person_id: Mapped[int] = mapped_column(
        ForeignKey("persons.id"),
        unique=True,  # 👈 enforce one-to-one at DB level
        primary_key=True,
    )

    club_id: Mapped[int] = mapped_column(
        ForeignKey("clubs.id"), nullable=True, default=None
    )

    expiry_date: Mapped[int] = mapped_column(Integer)
    wage: Mapped[int] = mapped_column(Integer)

    contract_type: Mapped[ContractType] = mapped_column(SAEnum(ContractType))


class CompetitionDB(Base):
    __tablename__ = "competitions"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    short_name: Mapped[str] = mapped_column(String(6), unique=True, index=True)

    # support legacy lowercase string values stored in the DB (e.g. 'league')
    competition_type: Mapped[CompetitionType] = mapped_column(
        SAEnum(
            CompetitionType,
            values_callable=lambda enums: [e.name.lower() for e in enums],
        )
    )

    __mapper_args__ = {
        "polymorphic_on": "competition_type",
    }


class LeagueGroupDB(Base):
    __tablename__ = "league_groups"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[String] = mapped_column(String(50), unique=True, index=True)


class LeagueDB(CompetitionDB):
    __tablename__ = "leagues"

    id: Mapped[int] = mapped_column(ForeignKey("competitions.id"), primary_key=True)

    league_group_id: Mapped[int] = mapped_column(ForeignKey("league_groups.id"))

    league_ranking: Mapped[int] = mapped_column(Integer)
    required_teams: Mapped[int] = mapped_column(Integer)

    __mapper_args__ = {
        "polymorphic_identity": CompetitionType.LEAGUE,
    }


class CupDB(CompetitionDB):
    __tablename__ = "cups"

    id: Mapped[int] = mapped_column(ForeignKey("competitions.id"), primary_key=True)

    __mapper_args__ = {
        "polymorphic_identity": CompetitionType.KNOCKOUT,
    }


class CompetitionRegisterDB(Base):
    __tablename__ = "competition_registry"
    id: Mapped[int] = mapped_column(primary_key=True)
    season: Mapped[int] = mapped_column(Integer)
    competition_id: Mapped[int] = mapped_column(
        ForeignKey("competitions.id"),
    )

    club_id: Mapped[int] = mapped_column(
        ForeignKey("clubs.id"),
    )


class FixtureDB(Base):
    __tablename__ = "fixtures"

    id: Mapped[int] = mapped_column(primary_key=True)

    home_club_id: Mapped[int] = mapped_column(
        ForeignKey("clubs.id"),
    )

    away_club_id: Mapped[int] = mapped_column(
        ForeignKey("clubs.id"),
    )

    competition_id: Mapped[int] = mapped_column(
        ForeignKey("competitions.id"),
    )

    ability: Mapped[int] = mapped_column(Integer)

    # discriminator column for fixture subclasses (joined-table polymorphism)
    fixture_type: Mapped[str] = mapped_column(String(20), default="fixture")

    __mapper_args__ = {
        "polymorphic_on": "fixture_type",
        "polymorphic_identity": "fixture",
    }


class ResultDB(FixtureDB):
    __tablename__ = "results"

    id: Mapped[int] = mapped_column(ForeignKey("fixtures.id"), primary_key=True)

    home_score: Mapped[int] = mapped_column(Integer)
    away_score: Mapped[int] = mapped_column(Integer)

    __mapper_args__ = {
        "polymorphic_identity": "result",
    }
