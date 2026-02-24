from argparse import ArgumentParser
import logging
from random import shuffle, randint
from sqlalchemy import select
from time import perf_counter
from traceback import format_exc
from typing import List
from src.core.game_types import (
    WeekType, 
    ReputationLevel, 
    Position, 
    StaffRole, 
    ContractType
)

from src.core.world_time import WEEKS_IN_YEAR

from src.core.ability import random_ability
from src.core.club import CLUB_NAMES
from src.core.competition import CompetitionType
from src.core.people import PersonFactory
from src.core.db.models import (
    WeekDB,
    SeasonDB,
    PersonDB,
    StaffDB,
    PlayerDB,
    ClubDB,
    ContractDB,
    CompetitionDB,
    LeagueGroupDB,
    LeagueDB,
    CupDB,
    CompetitionRegisterDB,
    FixtureDB,
    ResultDB,
    WorldDB,
)
from src.core.db.utils import create_session, create_tables

from src.core.utils import timer


def contract_expiry():
    return WEEKS_IN_YEAR * randint(1, 4)


league_30_fixtures = [
6, 7, 8,
10, 11, 12,
14, 15, 16,
18, 19, 20,
22, 23, 24,
27, 28, 29,
31, 32, 33,
35, 36, 37,
39, 40, 41,
43, 44, 45,
]


def create_league_fixtures(clubs: List, reverse_fixtures: bool = False):
    club_count = len(clubs)
    fixtures = []
    num_rounds = club_count - 1
    club_list = list(clubs)
    shuffle(club_list)

    if len(club_list) % 2 != 0:
        club_list.append(None)  # Add a dummy club for bye

    half_size = len(club_list) // 2

    # Generate fixtures using the round-robin algorithm
    for round_num in range(num_rounds):
        round_fixtures = []
        for i in range(half_size):
            club1 = club_list[i]
            club2 = club_list[(half_size + i)]
            if round_num % 2 != 0:
                club1, club2 = club2, club1
            if club1 is not None and club2 is not None:
                fixture = (round_num + 1, club1, club2)
                round_fixtures.append(fixture)

        fixtures.append(round_fixtures)
        club_list.append(club_list.pop(1))

    if reverse_fixtures:
        reverse_rounds = []
        for round_fixtures in fixtures:
            reverse_round = []
            for fixture in round_fixtures:
                reverse_fixture = (
                    fixture[0] + num_rounds,
                    fixture[2],
                    fixture[1],
                )
                reverse_round.append(reverse_fixture)
            reverse_rounds.append(reverse_round)
        fixtures.extend(reverse_rounds)
    return fixtures


class DatabaseWorker:
    def __init__(self, db_path: str):
        self._db_path = db_path

    def get_session(self):
        return create_session()

    def get_seasons(self):
        return (
            self.get_session().scalars(select(SeasonDB).order_by(SeasonDB.year)).all()
        )

    def get_clubs(self):
        return self.get_session().scalars(select(ClubDB)).all()

    def get_leagues(self):
        return self.get_session().scalars(select(LeagueDB)).all()

    def get_leagues_from_competitions(self):
        session = self.get_session()
        return session.scalars(
            select(CompetitionDB).where(
                CompetitionDB.competition_type == CompetitionType.LEAGUE
            )
        ).all()

    def get_cups(self):
        return self.get_session().scalars(select(CupDB)).all()

    def get_compition_registrations(self, season: SeasonDB):
        return (
            self.get_session()
            .scalars(
                select(CompetitionRegisterDB).where(
                    CompetitionRegisterDB.season_id == season.id
                )
            )
            .all()
        )

    def get_clubs_in_league_for_season(self, season: SeasonDB, league: LeagueDB):
        session = self.get_session()
        clubs = session.scalars(
            select(ClubDB)
            .join(CompetitionRegisterDB, ClubDB.id == CompetitionRegisterDB.club_id)
            .where(CompetitionRegisterDB.season_id == season.id)
            .where(CompetitionRegisterDB.competition_id == league.id)
        ).all()
        return clubs

    def get_clubs_in_leagues_for_season(self, season: SeasonDB):
        session = self.get_session()
        league_ids = session.scalars(select(LeagueDB.id)).all()
        clubs = session.scalars(
            select(ClubDB)
            .join(CompetitionRegisterDB, ClubDB.id == CompetitionRegisterDB.club_id)
            .where(CompetitionRegisterDB.season_id == season.id)
            .where(CompetitionRegisterDB.competition_id.in_(league_ids))
        ).all()
        return clubs

    def get_current_league_clubs(self):
        season = self.get_current_season()
        if season:
            return self.get_clubs_in_leagues_for_season(season)
        return []

    def get_current_season(self):
        seasons = self.get_seasons()
        if seasons:
            return seasons[-1]
        return None

    def get_current_week(self):
        session = self.get_session()
        world = session.scalars(select(WorldDB)).first()
        if world:
            return world.current_week
        return None

    def get_fixtures_for_current_week(self):
        session = self.get_session()
        world = session.scalars(select(WorldDB)).first()
        if world:
            return session.scalars(
                select(FixtureDB)
                .where(FixtureDB.season_id == world.season_id)
                .where(FixtureDB.season_week == world.current_week)
            ).all()
        return []

    def advance_week(self):
        session = self.get_session()
        world = session.scalars(select(WorldDB)).first()
        if world:
            world.current_week += 1
            session.commit()

    def get_results_for_club_in_competition(
        self, season: SeasonDB, competition: CompetitionDB, club: ClubDB
    ):
        session = self.get_session()
        return session.scalars(
            select(ResultDB)
            .join(FixtureDB, ResultDB.id == FixtureDB.id)
            .where(FixtureDB.season_id == season.id)
            .where(FixtureDB.competition_id == competition.id)
            .where(
                (FixtureDB.home_club_id == club.id)
                | (FixtureDB.away_club_id == club.id)
            )
        ).all()

    def get_fixture_from_result(self, result: ResultDB):
        session = self.get_session()
        return session.scalars(
            select(FixtureDB).where(FixtureDB.id == result.id)
        ).first()

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

    def add_result(self, fixture, score):
        session = self.get_session()
        result = ResultDB(id=fixture.id, home_score=score[0], away_score=score[1])
        session.add(result)
        session.commit()

    def add_results(self, fixtures_and_scores):
        session = self.get_session()
        results = [ResultDB(id=fs[0].id, home_score=fs[1][0], away_score=fs[1][1]) for fs in fixtures_and_scores]
        session.add_all(results)
        session.commit()

    @timer
    def do_post_season_setup(self):
        logging.info("Post Season Setup...")
        current_season = self.get_current_season()
        next_season = self.create_next_season()

        clubs_for_cup = []
        session = self.get_session()
        regs = []
        if not current_season:
            logging.info("No current season random league allocation")

            clubs = self.get_clubs()
            leagues = self.get_leagues()

            club_copy = list(clubs)
            shuffle(club_copy)

            for league in leagues:
                for _ in range(league.required_teams):
                    club = club_copy.pop(0)
                    reg = CompetitionRegisterDB(
                        season_id=next_season.id,
                        competition_id=league.id,
                        club_id=club.id,
                    )
                    regs.append(reg)
                    clubs_for_cup.append(club.id)
            session.add_all(regs)
            session.commit()

        else:
            logging.info(f"{next_season} - do promotion and relegation")

            leagues = self.get_leagues()
            leagues_ids = [l.id for l in leagues]
            last_season_reg = self.get_compition_registrations(current_season)
            for reg in last_season_reg:
                if reg.competition_id in leagues_ids:
                    new_reg = CompetitionRegisterDB(
                        season_id=next_season.id,
                        competition_id=reg.competition_id,
                        club_id=reg.club_id,
                    )
                    regs.append(new_reg)
                    clubs_for_cup.append(new_reg.club_id)
            session.add_all(regs)
            session.commit()

        if clubs_for_cup:
            logging.info("Do cup registration")
            cup_regs = []
            for cup in self.get_cups():
                club_copy = list(clubs_for_cup)
                shuffle(club_copy)

                for club in club_copy:
                    reg = CompetitionRegisterDB(
                        season_id=next_season.id, competition_id=cup.id, club_id=club
                    )
                    cup_regs.append(reg)
            session.add_all(cup_regs)
            session.commit()

    @timer
    def do_new_season(self):
        logging.info("New Season Setup...")

        current_season = self.get_current_season()

        # get all leagues
        leagues = self.get_leagues()

        session = self.get_session()

        world = None
        if current_season:
            world = session.scalars(select(WorldDB)).all()
            if not world:
                world = WorldDB(season_id=current_season.id)
                session.add(world)
            else:
                world = world[0]
                world.season_id = current_season.id
            session.commit()

        for league in leagues:
            logging.info(f"Create fixtures for {league}")

            # get registered teams
            league_clubs = self.get_clubs_in_league_for_season(current_season, league)
            names = [c.name for c in league_clubs]
            logging.info(f"{len(league_clubs)} Clubs " + ", ".join(names))

            fixtures = create_league_fixtures(league_clubs, True)
            fixture_objects = []
            for ix, r_fixtures in enumerate(fixtures):
                for f in r_fixtures:
                    fixture = FixtureDB(
                        home_club_id=f[1].id,
                        away_club_id=f[2].id,
                        competition_id=league.id,
                        competition_round=f[0],
                        season_id=current_season.id,
                        season_week=league_30_fixtures[ix],
                    )
                    fixture_objects.append(fixture)
            session.add_all(fixture_objects)
            session.commit()

            total = sum([len(f) for f in fixtures])
            logging.info(f"#Num Rounds {len(fixtures)} #Num Fixtures: {total}")

        all_fixtures = session.scalars(select(FixtureDB)).all()
        logging.info(f"All league fixtures added: {len(all_fixtures)}")

        if world:
            world.current_week = 1
            session.commit()


class DatabaseCreator(DatabaseWorker):
    def __init__(self, db_path: str, delete_existing: bool = True):
        super().__init__(db_path=db_path)
        self._delete_existsing = delete_existing

    def _pre_populate_db(self):
        logging.info("Pre-populate DB with static data if needed")
        session = self.get_session()
        weeks = []
        for week in range(1, WEEKS_IN_YEAR + 1):
            if not session.scalars(select(WeekDB).where(WeekDB.week_num == week)).first():
                if week <= 5:
                    role = WeekType.Preseason
                elif week <= 48:
                    role = WeekType.Regular_Season
                else:
                    role = WeekType.Postseason

                weeks.append(WeekDB(week_num=week, role=role))
        if weeks:
            session.add_all(weeks)
        session.commit()

        weeks = session.scalars(select(WeekDB)).all()
        logging.info(f"Weeks in DB: {len(weeks)}")


    @timer
    def create_db(self):
        logging.info(
            f"Create New Database '{self._db_path}', delete existing: {self._delete_existsing}"
        )
        create_tables(self._db_path, self._delete_existsing)

        self._pre_populate_db()

        self._create_db_competitions()
        num_clubs = self._create_db_clubs()
        num_staff = self._create_staff(num_clubs=num_clubs)
        num_players = self._create_players(num_clubs=num_clubs)
        num_staff_reg = self._allocate_staff()
        num_player_reg = self._allocate_players()

        self.do_post_season_setup()
        comp_reg = len(self.get_compition_registrations(self.get_current_season()))

        logging.info(
            f"# Clubs: {num_clubs}, # Staff: {num_staff}, # Players: {num_players}, "
            f"# Staff Reg: {num_staff_reg}, # Player Reg: {num_player_reg}"
            f", # Comp Reg: {comp_reg}"
        )

        self.do_new_season()

    @timer
    def _create_db_clubs(self):
        names = list(CLUB_NAMES)
        logging.info(f"Creating {len(CLUB_NAMES)} clubs")

        shuffle(names)
        session = self.get_session()
        clubs = [ClubDB(name=name) for name in names]
        session.add_all(clubs)
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
        all_persons = []
        all_staff = []
        for count_data in counts:
            for _ in range(count_data[1]):
                staff = PersonFactory.random_staff()
                person = PersonDB(
                    first_name=staff.name.first_name,
                    last_name=staff.name.last_name,
                    age=staff.age,
                    personality=staff.personality,
                )
                all_persons.append(person)
                db_staff = StaffDB(
                    person_id=person.id,  # This will be set after flush
                    role=count_data[0],
                    reputation_type=ReputationLevel.random(),
                    ability=random_ability(),
                )
                all_staff.append((person, db_staff))
        session.add_all(all_persons)
        session.flush()  # Flush to get IDs
        for person, db_staff in all_staff:
            db_staff.person_id = person.id
            session.add(db_staff)
        session.commit()

        return len(session.scalars(select(StaffDB)).all())

    @timer
    def _create_players(self, num_clubs: int):
        num_players = 15 * num_clubs * 2
        logging.info(f"Creating {num_players} players...")

        session = self.get_session()
        all_persons = []
        all_players = []
        for _ in range(num_players):
            player = PersonFactory.random_player()
            person = PersonDB(
                first_name=player.name.first_name,
                last_name=player.name.last_name,
                age=player.age,
                personality=player.personality,
            )
            all_persons.append(person)
            player_db = PlayerDB(
                person_id=person.id,  # Will be set after flush
                position=Position.random(),
                ability=random_ability(),
            )
            all_players.append((person, player_db))
        session.add_all(all_persons)
        session.flush()
        for person, player_db in all_players:
            player_db.person_id = person.id
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

        contracts = []
        for club in clubs:
            manager = managers.pop(0)
            contract = ContractDB(
                person_id=manager.person_id,
                club_id=club.id,
                expiry_date=contract_expiry(),
                wage=100,
                contract_type=ContractType.Staff_Contract,
            )
            contracts.append(contract)

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
                contracts.append(contract)

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
                contracts.append(contract)

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
            contracts.append(contract)
        session.add_all(contracts)
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

        contracts = []
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
                contracts.append(contract)

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
                    contracts.append(contract)
        session.add_all(contracts)
        session.commit()

        return len(
            session.scalars(
                select(ContractDB).where(
                    ContractDB.contract_type == ContractType.Player_Contract
                )
            ).all()
        )


def create_score():
    min_goals, max_goals = 0, 5
    return randint(min_goals, max_goals), randint(min_goals, max_goals)


def create_league_table_data(club: ClubDB, results: List, db_worker: DatabaseWorker):
    data = {
        "club": club,
        "ply": 0,
        "w": 0,
        "d": 0,
        "l": 0,
        "gf": 0,
        "ga": 0,
        "gd": 0,
        "pts": 0,
    }

    for result in results:
        fixture = db_worker.get_fixture_from_result(result)
        if fixture.home_club_id == club.id:
            home = True
        elif fixture.away_club_id == club.id:
            home = False

        else:
            raise RuntimeError(f"{club.name} not in fixture: {fixture}")

        data["ply"] += 1

        if result.home_score == result.away_score:
            data["d"] += 1
            data["gf"] += result.home_score
            data["ga"] += result.away_score
        else:
            if result.home_score > result.away_score:
                if home:
                    data["w"] += 1
                else:
                    data["l"] += 1
            else:
                if home:
                    data["l"] += 1
                else:
                    data["w"] += 1
            data["gf"] += result.home_score
            data["ga"] += result.away_score

    data["gd"] = data["gf"] - data["ga"]
    data["pts"] = (data["w"] * 3) + data["d"]
    return data


def get_league_table_data(league: LeagueDB, current_season: SeasonDB, db_worker: DatabaseWorker):
    clubs = db_worker.get_clubs_in_league_for_season(
        season=current_season, league=league
    )
    league_data = list()
    for club in clubs:
        results = db_worker.get_results_for_club_in_competition(
            season=current_season, competition=league, club=club
        )
        league_data.append(create_league_table_data(club, results, db_worker))

    league_data.sort(
        key=lambda d: (-d["pts"], -d["gf"], -d["gd"], d["club"].name)
    )
    return league_data


def league_table_text(league_data):
    league_table_text = ["", ("-" * 80), f"League Table"]

    for ld in league_data:
        text = [
            ld["club"].name.ljust(30),
            str(ld["ply"]).center(3),
            str(ld["w"]).center(3),
            str(ld["d"]).center(3),
            str(ld["l"]).center(3),
            str(ld["gf"]).center(3),
            str(ld["ga"]).center(3),
            str(ld["gd"]).center(3),
            str(ld["pts"]).center(3),
        ]
        league_table_text.append(f"{'|'.join(text)}")
    league_table_text.append(("-" * 80))
    return league_table_text


class GameDBWorker:

    DEFAULT_DB_PATH = "var/football.db"

    def __init__(self, db_path: str | None = None):
        self._db_path = db_path or self.DEFAULT_DB_PATH 


    def create_new_database(self, delete_existing: bool = True):
        logging.info(f"Creating new database at {self._db_path}, delete existing: {delete_existing}")
        DatabaseCreator(db_path=self._db_path, delete_existing=delete_existing).create_db()

    def run_season(self):
        logging.info("Simulate Season...")
        db_worker = DatabaseWorker(db_path=self._db_path)
        while True:
            current_week = db_worker.get_current_week()

            if current_week != WEEKS_IN_YEAR:
                current_fixtures = db_worker.get_fixtures_for_current_week()
                logging.info(
                    f"Current Week: {current_week} # fixtures {len(current_fixtures)}"
                )
                if current_fixtures:
                    fixtures_and_scores = []
                    for fixture in current_fixtures:
                        score = create_score()
                        fixtures_and_scores.append((fixture, score))
                    db_worker.add_results(fixtures_and_scores=fixtures_and_scores)
                db_worker.advance_week()

            else:
                break
    
    def process_end_of_season(self):
        logging.info("Process End of Season...")
        db_worker = DatabaseWorker(db_path=self._db_path)
        current_season = db_worker.get_current_season()
        leagues = db_worker.get_leagues_from_competitions()
        for league in leagues:
            league_data = get_league_table_data(league, current_season, db_worker)  
            text = league_table_text(league_data)
            logging.info(f"{'\n'.join(text)}")

def db_main():

    logging.basicConfig(
        level=logging.DEBUG,
        format="[%(asctime)s|%(thread)x|%(levelname)s|%(module)s.%(funcName)s] %(message)s",
    )

    try:
        start_time = perf_counter()

        game_worker = GameDBWorker()
        
        game_worker.create_new_database(delete_existing=True)
        game_worker.run_season()
        game_worker.process_end_of_season()


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
