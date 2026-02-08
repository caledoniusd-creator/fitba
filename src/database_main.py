from argparse import ArgumentParser
from functools import wraps
import logging
from random import shuffle, randint
from sqlalchemy import select
from time import perf_counter
from traceback import format_exc

from src.core.game_types import ReputationLevel, Position, StaffRole, ContractType

from src.core.ability import random_ability
from src.core.club import CLUB_NAMES
from src.core.people import PersonFactory
from src.core.db.models import (
    PersonDB,
    StaffDB,
    PlayerDB,
    ClubDB,
    ContractDB,
    LeagueGroupDB,
    LeagueDB,
    CupDB,
    CompetitionRegisterDB,
)
from src.core.db.utils import create_session, create_tables


def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = perf_counter()
        result = func(*args, **kwargs)
        end = perf_counter()
        logging.info(f"{func.__name__} took {end - start:.6f} seconds")
        return result

    return wrapper


def contract_expiry():
    return 52 * randint(1, 4)


@timer
def create_db_competitions():
    session = create_session()

    league_group = LeagueGroupDB(name="Test FA")
    session.add(league_group)
    session.commit()

    session.add(
        LeagueDB(
            name="Premier League",
            short_name="PL",
            league_group_id=league_group.id,
            league_ranking=1,
            required_teams=16,
        )
    )
    session.add(
        LeagueDB(
            name="Championship",
            short_name="CH",
            league_group_id=league_group.id,
            league_ranking=2,
            required_teams=16,
        )
    )
    session.add(CupDB(name="League Cup", short_name="LC"))
    session.commit()


@timer
def create_db_clubs():
    session = create_session()
    names = list(CLUB_NAMES)
    shuffle(names)
    for name in names:
        new_club = ClubDB(name=name)
        session.add(new_club)
    session.commit()

    return len(session.scalars(select(ClubDB)).all())


@timer
def create_staff(num_clubs: int):
    session = create_session()
    counts = [
        (StaffRole.Manager, num_clubs * 2),
        (StaffRole.Coach, num_clubs * 4),
        (StaffRole.Scout, num_clubs * 4),
        (StaffRole.Physio, num_clubs * 2),
    ]

    for count_data in counts:
        role, count = count_data
        logging.info(f"Creating {count} {role.name}s...")

        persons = []
        for _ in range(count):
            staff = PersonFactory.random_staff()
            person = PersonDB(
                first_name=staff.name.first_name,
                last_name=staff.name.last_name,
                age=staff.age,
                personality=staff.personality,
            )
            session.add(person)
            persons.append(person)
        session.commit()

        for person in persons:
            db_staff = StaffDB(
                person_id=person.id,
                role=role,
                reputation_type=ReputationLevel.random(),
                ability=random_ability(),
            )
            session.add(db_staff)
        session.commit()

    return len(session.scalars(select(StaffDB)).all())


@timer
def create_players(num_clubs: int):
    session = create_session()

    num_players = 15 * num_clubs * 2
    logging.info(f"Creating {num_players} players...")

    persons = []
    for _ in range(num_players):
        player = PersonFactory.random_player()
        person = PersonDB(
            first_name=player.name.first_name,
            last_name=player.name.last_name,
            age=player.age,
            personality=player.personality,
        )
        session.add(person)
        persons.append(person)
    session.commit()

    for person in persons:
        player_db = PlayerDB(
            person_id=person.id, position=Position.random(), ability=random_ability()
        )
        session.add(player_db)
    session.commit()
    return len(session.scalars(select(PlayerDB)).all())


@timer
def allocate_staff():
    session = create_session()
    clubs = session.scalars(select(ClubDB)).all()

    managers = session.scalars(
        select(StaffDB).where(StaffDB.role == StaffRole.Manager)
    ).all()
    coaches = session.scalars(
        select(StaffDB).where(StaffDB.role == StaffRole.Coach)
    ).all()
    scouts = session.scalars(
        select(StaffDB).where(StaffDB.role == StaffRole.Scout)
    ).all()
    physios = session.scalars(
        select(StaffDB).where(StaffDB.role == StaffRole.Physio)
    ).all()

    logging.info("Allocate Managers")
    shuffle(clubs)
    shuffle(managers)

    for club in clubs:
        manager = managers.pop(0)
        contract = ContractDB(
            person_id=manager.person_id,
            club_id=club.id,
            expiry_date=contract_expiry(),
            wage=100,
            contract_type=ContractType.Staff_Contract,
        )
        session.add(contract)

    logging.info("Allocate Coaches")

    shuffle(clubs)
    shuffle(coaches)

    for ix, club in enumerate(clubs):
        for _ in range(2):
            coach = coaches.pop(0)
            contract = ContractDB(
                person_id=coach.person_id,
                club_id=club.id,
                expiry_date=contract_expiry(),
                wage=100,
                contract_type=ContractType.Staff_Contract,
            )
            session.add(contract)

    logging.info("Allocate Scouts")
    shuffle(clubs)
    shuffle(scouts)
    for ix, club in enumerate(clubs):
        for _ in range(2):
            scout = scouts.pop(0)
            contract = ContractDB(
                person_id=scout.person_id,
                club_id=club.id,
                expiry_date=contract_expiry(),
                wage=100,
                contract_type=ContractType.Staff_Contract,
            )
            session.add(contract)

    logging.info("Allocate Physios")
    shuffle(clubs)
    shuffle(physios)

    for club in clubs:
        physio = physios.pop(0)
        contract = ContractDB(
            person_id=physio.person_id,
            club_id=club.id,
            expiry_date=contract_expiry(),
            wage=100,
            contract_type=ContractType.Staff_Contract,
        )
        session.add(contract)
    session.commit()

    return len(
        session.scalars(
            select(ContractDB).where(
                ContractDB.contract_type == ContractType.Staff_Contract
            )
        ).all()
    )


@timer
def allocate_players():
    session = create_session()
    clubs = session.scalars(select(ClubDB)).all()

    goalkeepers = session.scalars(
        select(PlayerDB).where(PlayerDB.position == Position.Goalkeeper)
    ).all()
    defenders = session.scalars(
        select(PlayerDB).where(PlayerDB.position == Position.Defender)
    ).all()
    midfielders = session.scalars(
        select(PlayerDB).where(PlayerDB.position == Position.Midfielder)
    ).all()
    attackers = session.scalars(
        select(PlayerDB).where(PlayerDB.position == Position.Attacker)
    ).all()

    shuffle(clubs)
    shuffle(goalkeepers)
    for _ in range(3):
        shuffle(clubs)
        for club in clubs:
            gk = goalkeepers.pop(0)
            contract = ContractDB(
                person_id=gk.person_id,
                club_id=club.id,
                expiry_date=contract_expiry(),
                wage=100,
                contract_type=ContractType.Player_Contract,
            )
        session.add(contract)

    for plist in [defenders, midfielders, attackers]:
        for _ in range(4):
            shuffle(clubs)
            shuffle(plist)
            for club in clubs:
                player = plist.pop(0)
                contract = ContractDB(
                    person_id=player.person_id,
                    club_id=club.id,
                    expiry_date=contract_expiry(),
                    wage=100,
                    contract_type=ContractType.Player_Contract,
                )
        session.add(contract)
    session.commit()

    return len(
        session.scalars(
            select(ContractDB).where(
                ContractDB.contract_type == ContractType.Player_Contract
            )
        ).all()
    )


@timer
def register_clubs_with_competitions():
    season = 1
    session = create_session()

    clubs = session.scalars(select(ClubDB)).all()
    leagues = session.scalars(select(LeagueDB)).all()
    cups = session.scalars(select(CupDB)).all()

    club_copy = list(clubs)
    shuffle(club_copy)
    clubs_for_cup = []
    for league in leagues:
        logging.info(f"adding clubs ({league.required_teams}) to {league.name}")
        for i in range(league.required_teams):
            club = club_copy.pop(0)
            reg = CompetitionRegisterDB(
                season=season, competition_id=league.id, club_id=club.id
            )
            session.add(reg)
            clubs_for_cup.append(club)
    session.commit()

    for cup in cups:
        logging.info(f"adding clubs to {cup.name}")
        for club in clubs_for_cup:
            reg = CompetitionRegisterDB(
                season=season, competition_id=cup.id, club_id=club.id
            )
            session.add(reg)
    session.commit()

    return len(session.scalars(select(CompetitionRegisterDB)).all())


def db_main():

    logging.basicConfig(level=logging.DEBUG)
    try:
        start_time = perf_counter()
        logging.info("Create Database...")
        create_tables()

        logging.info("Create Competitions...")
        create_db_competitions()

        logging.info("Create Clubs...")
        num_clubs = create_db_clubs()
        logging.info(f"{num_clubs} clubs created")

        logging.info("Create Staff...")
        num_staff = create_staff(num_clubs=num_clubs)
        logging.info(f"{num_staff} staff created")

        logging.info("Create Players...")
        num_players = create_players(num_clubs=num_clubs)
        logging.info(f"{num_players} players created")

        logging.info("Allocating Staff...")
        num_contracts = allocate_staff()
        logging.info(f"{num_contracts} contracts created")

        logging.info("Allocating Players...")
        num_contracts = allocate_players()
        logging.info(f"{num_contracts} contracts created")

        logging.info("Register Clubs with Leagues and Cups...")
        num_regs = register_clubs_with_competitions()
        logging.info(f"{num_regs} registrations created")

        logging.info("TODO! Create New Season...")
        logging.info("TODO! Create Competition Fixtures...")
        logging.info("TODO! Simulate Season...")
        logging.info("TODO! Process End of Season...")

        total_time = perf_counter() - start_time
        logging.info(f"Took {total_time:.6f} seconds")

    except Exception as e:
        logging.debug(format_exc())
        logging.exception(e)
        logging.error(e)


if __name__ == "__main__":
    parser = ArgumentParser("Fitba")
    options = [
        "create",
    ]
    parser.add_argument(
        "-m", "--mode", choices=options, default="create", help="Running mode"
    )
    args = parser.parse_args()

    if args.mode:
        if args.mode == "create":
            db_main()
        else:
            pass
