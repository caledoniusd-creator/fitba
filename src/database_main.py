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
    SeasonDB,
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

from src.core.utils import timer


def contract_expiry():
    return 52 * randint(1, 4)


class DatabaseWorker:
    def __init__(self, db_path: str):
        self._db_path = db_path

    def get_session(self):
        return create_session()

    def get_seasons(self):
        return self.get_session().scalars(select(SeasonDB).order_by(SeasonDB.year)).all()
    
    def get_clubs(self):
        return self.get_session().scalars(select(ClubDB)).all()
    
    def get_leagues(self):
        return self.get_session().scalars(select(LeagueDB)).all()
    
    def get_cups(self):
        return self.get_session().scalars(select(CupDB)).all()
    
    def get_compition_registrations(self, season:SeasonDB):
        return self.get_session().scalars(select(CompetitionRegisterDB).where(CompetitionRegisterDB.season_id==season.id)).all()
    
    def get_current_season(self):
        seasons = self.get_seasons()
        if seasons:
            return seasons[-1]
        return None
    
    @timer
    def create_next_season(self):
        seasons = self.get_seasons()
        if not seasons:
            year = 1
        else:
            year = seasons[-1].year + 1

        logging.info(f"Creating Season for Year: {year}")

        session = self.get_session()
        new_season = SeasonDB(year=year)
        session.add(new_season)
        session.commit()

        return new_season
    
    @timer
    def do_post_season_setup(self):
        logging.info(f"Post Season Setup...")
        current_season = self.get_current_season()
        next_season = self.create_next_season()

        clubs_for_cup = []
        if not current_season:
            logging.info(f"No current season random league allocation")

            clubs = self.get_clubs()
            leagues = self.get_leagues()

            club_copy = list(clubs)
            shuffle(club_copy)
            
            session = self.get_session()
            for league in leagues:
                for _ in range(league.required_teams):
                    club = club_copy.pop(0)
                    reg = CompetitionRegisterDB(
                        season_id=next_season.id, competition_id=league.id, club_id=club.id
                    )
                    session.add(reg)
                    clubs_for_cup.append(club.id)
            session.commit()

        else:
            logging.info(f"{next_season} - do promotion and relegation")

            leagues = self.get_leagues()
            leagues_ids = [l.id for l in leagues]
            last_season_reg = self.get_compition_registrations(current_season)
            session = self.get_session()
            for reg in last_season_reg:
                if reg.competition_id in leagues_ids:
                    new_reg = CompetitionRegisterDB(
                        season_id=next_season.id, competition_id=reg.competition_id, club_id=reg.club_id
                    )
                    session.add(new_reg)
                    clubs_for_cup.append(new_reg.club_id)
            session.commit()
            
        if clubs_for_cup:
            logging.info("Do cup registration")
            for cup in self.get_cups():
                club_copy = list(clubs_for_cup)
                shuffle(club_copy)
                
                for club in club_copy:
                    reg = CompetitionRegisterDB(
                        season_id=next_season.id, competition_id=cup.id, club_id=club
                    )
                    session.add(reg)
            session.commit()
        
class DatabaseCreator(DatabaseWorker):

    def __init__(self, db_path: str, delete_existing: bool = True):
        super().__init__(db_path=db_path)
        self._delete_existsing = delete_existing

    @timer
    def create_db(self):
        logging.info(f"Create New Database '{self._db_path}', delete existing: {self._delete_existsing}")
        create_tables(self._db_path, self._delete_existsing)
        
        self._create_db_competitions()
        num_clubs = self._create_db_clubs()
        num_staff = self._create_staff(num_clubs=num_clubs)
        num_players = self._create_players(num_clubs=num_clubs)
        num_staff_reg = self._allocate_staff()
        num_player_reg = self._allocate_players()

        self.do_post_season_setup()
        comp_reg = len(self.get_compition_registrations(self.get_current_season()))

       

        logging.info(
            f"# Clubs: {num_clubs}, # Staff: {num_staff}, # Players: {num_players}, " \
            f"# Staff Reg: {num_staff_reg}, # Player Reg: {num_player_reg}" \
            f", # Comp Reg: {comp_reg}" 
        )
            
    @timer
    def _create_db_clubs(self):
        names = list(CLUB_NAMES)
        logging.info(f"Creating {len(CLUB_NAMES)} clubs")
        
        shuffle(names)
        session = self.get_session()
        for name in names:
            new_club = ClubDB(name=name)
            session.add(new_club)
        session.commit()

        return len(session.scalars(select(ClubDB)).all())
    
    @timer
    def _create_db_competitions(self):
        logging.info("Creating competitions")

        session = self.get_session()
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
    def _create_staff(self, num_clubs: int):
        counts = [
            (StaffRole.Manager, num_clubs * 2),
            (StaffRole.Coach, num_clubs * 4),
            (StaffRole.Scout, num_clubs * 4),
            (StaffRole.Physio, num_clubs * 2),
        ]
        for count_data in counts:
            logging.info(f"Creating {count_data[1]} x {count_data[0].name}s...")

        session = self.get_session()
        for count_data in counts:
            persons = []
            for _ in range(count_data[1]):
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
                    role=count_data[0],
                    reputation_type=ReputationLevel.random(),
                    ability=random_ability(),
                )
                session.add(db_staff)
            session.commit()

        return len(session.scalars(select(StaffDB)).all())

    @timer
    def _create_players(self, num_clubs: int):
        num_players = 15 * num_clubs * 2
        logging.info(f"Creating {num_players} players...")

        persons = []

        session = self.get_session()
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
    def _allocate_staff(self):
        logging.info("Allocating Staff...")
        session = self.get_session()
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
    def _allocate_players(self):
        logging.info("Allocating Players...")
        session = self.get_session()
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

  

class GameWorker(DatabaseWorker):
    def __init__(self, db_path: str):
        super().__init__(db_path=db_path)
    
    def new_season(self):
        pass

def db_main():

    logging.basicConfig(
        level=logging.DEBUG,
        format="[%(asctime)s|%(thread)x|%(levelname)s|%(module)s.%(funcName)s] %(message)s"
    )

    try:
        start_time = perf_counter()
        db_path = "var/football.db"
        delete_existsing = True
        DatabaseCreator(db_path=db_path, delete_existing=delete_existsing).create_db()


        # logging.info("TODO! Create New Season...")
        # logging.info("TODO! Create Competition Fixtures...")
        # logging.info("TODO! Simulate Season...")
        # logging.info("TODO! Process End of Season...")

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
