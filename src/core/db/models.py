from __future__ import annotations


from sqlalchemy import ForeignKey, String, Integer, Enum as SAEnum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


from ..game_types import (
    WeekType,
    PersonalityType,
    StaffRole,
    ReputationLevel,
    ContractType,
    Position,
)

from ..competition import CompetitionType


class Base(DeclarativeBase):
    pass


class WeekDB(Base):
    __tablename__ = "weeks"

    id: Mapped[int] = mapped_column(primary_key=True)
    week_num: Mapped[int] = mapped_column(Integer)
    role: Mapped[WeekType] = mapped_column(SAEnum(WeekType))

    def __str__(self):
        return f"Week {self.week_num:2d}: {self.role}"


class SeasonDB(Base):
    __tablename__ = "seasons"
    id: Mapped[int] = mapped_column(primary_key=True)
    year: Mapped[int] = mapped_column(Integer, unique=True)

    # Reverse relationships
    competition_registrations: Mapped[list[CompetitionRegisterDB]] = relationship(
        "CompetitionRegisterDB", back_populates="season"
    )
    fixtures: Mapped[list[FixtureDB]] = relationship(
        "FixtureDB", back_populates="season"
    )
    world: Mapped[WorldDB] = relationship(
        "WorldDB", back_populates="season", uselist=False
    )

    def __repr__(self) -> str:
        return f"[{id}] Season: {self.year}"

    def __str__(self):
        return f"Season {self.year}"


class PersonDB(Base):
    __tablename__ = "persons"

    id: Mapped[int] = mapped_column(primary_key=True)

    first_name: Mapped[str] = mapped_column(String(50), index=True)
    last_name: Mapped[str] = mapped_column(String(50), index=True)
    age: Mapped[int] = mapped_column(Integer)

    personality: Mapped[PersonalityType] = mapped_column(SAEnum(PersonalityType))

    # Reverse relationships
    staff: Mapped[StaffDB] = relationship(
        "StaffDB", back_populates="person", uselist=False
    )
    player: Mapped[PlayerDB] = relationship(
        "PlayerDB", back_populates="person", uselist=False
    )
    contract: Mapped[ContractDB] = relationship(
        "ContractDB", back_populates="person", uselist=False
    )

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
    person_id: Mapped[int] = mapped_column(
        ForeignKey("persons.id"),
        unique=True,  # 👈 enforce one-to-one at DB level
        primary_key=True,
    )

    role: Mapped[StaffRole] = mapped_column(SAEnum(StaffRole))

    reputation_type: Mapped[ReputationLevel] = mapped_column(SAEnum(ReputationLevel))

    ability: Mapped[int] = mapped_column(Integer)

    # Reverse relationship
    person: Mapped[PersonDB] = relationship("PersonDB", back_populates="staff")


class PlayerDB(Base):
    __tablename__ = "players"

    person_id: Mapped[int] = mapped_column(
        ForeignKey("persons.id"),
        unique=True,  # 👈 enforce one-to-one at DB level
        primary_key=True,
    )
    position: Mapped[Position] = mapped_column(SAEnum(Position))
    ability: Mapped[int] = mapped_column(Integer)

    # Reverse relationship
    person: Mapped[PersonDB] = relationship("PersonDB", back_populates="player")


class ClubDB(Base):
    __tablename__ = "clubs"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, index=True)

    # Reverse relationships
    contracts: Mapped[list[ContractDB]] = relationship(
        "ContractDB", back_populates="club"
    )
    home_fixtures: Mapped[list[FixtureDB]] = relationship(
        "FixtureDB", back_populates="home_club", foreign_keys="FixtureDB.home_club_id"
    )
    away_fixtures: Mapped[list[FixtureDB]] = relationship(
        "FixtureDB", back_populates="away_club", foreign_keys="FixtureDB.away_club_id"
    )
    competition_registrations: Mapped[list[CompetitionRegisterDB]] = relationship(
        "CompetitionRegisterDB", back_populates="club"
    )

    def staff_contracts(self):
        return [c for c in self.contracts if c.person.staff is not None]

    def staff_members(self):
        return [c.person.staff for c in self.contracts if c.person.staff is not None]

    def player_contracts(self):
        return [c for c in self.contracts if c.person.player is not None]   
    
    def players(self):
        all_players = [c.person.player for c in self.contracts if c.person.player is not None]
        all_players.sort(key=lambda p: (p.position.value[0], -p.ability), reverse=False)
        return all_players
    
    
    def competitions(self, season=None):
        if season is None:
            return [reg.competition for reg in self.competition_registrations]
        else:
            return [reg.competition for reg in self.competition_registrations if reg.season_id == season.id]
    
    def fixtures(self, season=None):
        all_fixtures = self.home_fixtures + self.away_fixtures
        if season is not None:
            all_fixtures = [f for f in all_fixtures if f.season_id == season.id]
        all_fixtures.sort(key=lambda f: f.season_week)
        return all_fixtures
    
    def results(self, competition=None, season=None):
        all_results = [f.result for f in self.fixtures(season) if f.result is not None]
        if competition is not None:
            all_results = [r for r in all_results if r.fixture.competition_id == competition.id]
        return all_results
    

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

    # Reverse relationships
    person: Mapped[PersonDB] = relationship("PersonDB", back_populates="contract")
    club: Mapped[ClubDB] = relationship("ClubDB", back_populates="contracts")


class CompetitionDB(Base):
    __tablename__ = "competitions"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    short_name: Mapped[str] = mapped_column(String(6), unique=True, index=True)

    # support legacy lowercase string values stored in the DB (e.g. 'league')
    competition_type: Mapped[CompetitionType] = mapped_column(SAEnum(CompetitionType))

    # Reverse relationships
    fixtures: Mapped[list[FixtureDB]] = relationship(
        "FixtureDB", back_populates="competition"
    )
    competition_registrations: Mapped[list[CompetitionRegisterDB]] = relationship(
        "CompetitionRegisterDB", back_populates="competition"
    )

    __mapper_args__ = {
        "polymorphic_on": "competition_type",
    }

    def get_clubs_for_season(self, season: SeasonDB):
        all_registrations = self.competition_registrations
        clubs = []
        for reg in all_registrations:
            if reg.season_id == season.id:
                clubs.append(reg.club)  
        return clubs
    


class LeagueGroupDB(Base):
    __tablename__ = "league_groups"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[String] = mapped_column(String(50), unique=True, index=True)

    # Reverse relationship
    leagues: Mapped[list[LeagueDB]] = relationship(
        "LeagueDB", back_populates="league_group"
    )


class LeagueDB(CompetitionDB):
    __tablename__ = "leagues"

    id: Mapped[int] = mapped_column(ForeignKey("competitions.id"), primary_key=True)

    league_group_id: Mapped[int] = mapped_column(ForeignKey("league_groups.id"))

    league_ranking: Mapped[int] = mapped_column(Integer)
    required_teams: Mapped[int] = mapped_column(Integer)

    # Reverse relationship
    league_group: Mapped[LeagueGroupDB] = relationship(
        "LeagueGroupDB", back_populates="leagues"
    )

    __mapper_args__ = {
        "polymorphic_identity": CompetitionType.LEAGUE,
    }

    def __str__(self):
        return self.name


class CupDB(CompetitionDB):
    __tablename__ = "cups"

    id: Mapped[int] = mapped_column(ForeignKey("competitions.id"), primary_key=True)

    __mapper_args__ = {
        "polymorphic_identity": CompetitionType.KNOCKOUT,
    }


class CompetitionRegisterDB(Base):
    __tablename__ = "competition_registry"
    id: Mapped[int] = mapped_column(primary_key=True)
    season_id: Mapped[int] = mapped_column(ForeignKey("seasons.id"), nullable=False)
    competition_id: Mapped[int] = mapped_column(
        ForeignKey("competitions.id"),
    )

    club_id: Mapped[int] = mapped_column(
        ForeignKey("clubs.id"),
    )

    # Reverse relationships
    season: Mapped[SeasonDB] = relationship(
        "SeasonDB", back_populates="competition_registrations"
    )
    competition: Mapped[CompetitionDB] = relationship(
        "CompetitionDB", back_populates="competition_registrations"
    )
    club: Mapped[ClubDB] = relationship(
        "ClubDB", back_populates="competition_registrations"
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

    competition_round: Mapped[int] = mapped_column(Integer)

    season_id: Mapped[int] = mapped_column(
        ForeignKey("seasons.id"),
    )

    season_week: Mapped[int] = mapped_column(Integer)

    # discriminator column for fixture subclasses (joined-table polymorphism)
    fixture_type: Mapped[str] = mapped_column(String(20), default="fixture")

    # Reverse relationships
    home_club: Mapped[ClubDB] = relationship(
        "ClubDB", back_populates="home_fixtures", foreign_keys=[home_club_id]
    )
    away_club: Mapped[ClubDB] = relationship(
        "ClubDB", back_populates="away_fixtures", foreign_keys=[away_club_id]
    )
    competition: Mapped[CompetitionDB] = relationship(
        "CompetitionDB", back_populates="fixtures"
    )
    season: Mapped[SeasonDB] = relationship("SeasonDB", back_populates="fixtures")
    result: Mapped[ResultDB] = relationship(
        "ResultDB", back_populates="fixture", uselist=False
    )

    __mapper_args__ = {
        "polymorphic_on": "fixture_type",
        "polymorphic_identity": "fixture",
    }


class ResultDB(Base):
    __tablename__ = "results"

    id: Mapped[int] = mapped_column(ForeignKey("fixtures.id"), primary_key=True)

    home_score: Mapped[int] = mapped_column(Integer)
    away_score: Mapped[int] = mapped_column(Integer)

    # Reverse relationship
    fixture: Mapped[FixtureDB] = relationship("FixtureDB", back_populates="result")


class WorldDB(Base):
    __tablename__ = "world"

    id: Mapped[int] = mapped_column(primary_key=True)
    season_id: Mapped[int] = mapped_column(
        ForeignKey("seasons.id"),
    )
    current_week: Mapped[int] = mapped_column(Integer, default=1)

    # Reverse relationship
    season: Mapped[SeasonDB] = relationship("SeasonDB", back_populates="world")
