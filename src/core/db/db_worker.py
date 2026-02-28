from __future__ import annotations
import logging
from random import shuffle, randint, seed as rnd_seed
from sqlalchemy import select, desc, asc

from src.core.utils import random_seed
from src.core.game_types import (
    WeekType,
    ReputationLevel,
    Position,
    StaffRole,
    ContractType,
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


from src.core.utils import timer

from .league_db_functions import (
    league_30_fixtures,
    create_league_fixtures,
    get_league_table_data,
)
from .utils import create_session, create_tables


class DatabaseWorker:
    def __init__(self, db_path: str):
        self._db_path = db_path
        self._session = None

    @property
    def session(self):
        if self._session is None:
            self._session = create_session(self._db_path)
        return self._session

    def close_session(self):
        if self._session:
            self._session.close()
            self._session = None

    def get_seasons(self):
        return self.session.scalars(select(SeasonDB).order_by(asc(SeasonDB.year))).all()

    def get_current_season(self):
        return self.session.scalars(
            select(SeasonDB).order_by(desc(SeasonDB.year))
        ).first()

    def get_world(self):
        return self.session.scalars(select(WorldDB)).first()

    def get_week(self, week_num: int):
        return self.session.scalars(
            select(WeekDB).where(WeekDB.week_num == week_num)
        ).first()

    def get_current_week(self):
        world = self.get_world()
        if world:
            return world.current_week
        return None

    def advance_week(self):
        world = self.get_world()
        if world:
            world.current_week += 1
            self.session.commit()

    def get_clubs(self):
        return self.session.scalars(select(ClubDB)).all()

    def get_competitions(self):
        return self.session.scalars(select(CompetitionDB)).all()

    def get_people(self):
        return self.session.scalars(select(PersonDB)).all()

    def get_staff(self):
        return self.session.scalars(select(StaffDB)).all()

    def get_players(self):
        return self.session.scalars(select(PlayerDB)).all()

    def get_leagues(self):
        return self.session.scalars(select(LeagueDB)).all()

    def get_leagues_from_competitions(self):
        return self.session.scalars(
            select(CompetitionDB).where(
                CompetitionDB.competition_type == CompetitionType.LEAGUE
            )
        ).all()

    def get_cups(self):
        return self.session.scalars(select(CupDB)).all()

    def get_compition_registrations(self, season: SeasonDB):
        return self.session.scalars(
            select(CompetitionRegisterDB).where(
                CompetitionRegisterDB.season_id == season.id
            )
        ).all()

    def get_fixtures_for_current_week(self):

        world = self.get_world()
        if world:
            logging.info(f"Get Fixtures for week: {world.current_week}")
            return self.session.scalars(
                select(FixtureDB)
                .where(FixtureDB.season_id == world.season_id)
                .where(FixtureDB.season_week == world.current_week)
                .where(FixtureDB.result == None)
            ).all()
        return []

    def get_results_for_current_week(self):

        world = self.get_world()
        if world:
            logging.info(f"Get Fixtures for week: {world.current_week}")
            fixtures = self.session.scalars(
                select(FixtureDB)
                .where(FixtureDB.season_id == world.season_id)
                .where(FixtureDB.season_week == world.current_week)
                .where(FixtureDB.result != None)
            ).all()

            return [f.result for f in fixtures]

        return []

    def get_clubs_not_in_leagues_for_season(self, season: SeasonDB | None = None):
        season = season or self.get_current_season()
        league_ids = self.session.scalars(select(LeagueDB.id)).all()
        clubs = self.session.scalars(
            select(ClubDB).where(
                ~ClubDB.id.in_(
                    select(CompetitionRegisterDB.club_id)
                    .where(CompetitionRegisterDB.season_id == season.id)
                    .where(CompetitionRegisterDB.competition_id.in_(league_ids))
                )
            )
        ).all()
        return clubs

    def get_league_registrations_for_current_season(self):
        season = self.get_current_season()
        if not season:
            return []

        league_ids = self.session.scalars(select(LeagueDB.id)).all()
        registrations = self.session.scalars(
            select(CompetitionRegisterDB)
            .where(CompetitionRegisterDB.season_id == season.id)
            .where(CompetitionRegisterDB.competition_id.in_(league_ids))
        ).all()
        return registrations

    def get_next_season_league_registrations(self):
        promoted_count = 3
        relegated_count = 3
        current_season = self.get_current_season()
        all_leagues = self.get_leagues_from_competitions()

        changes = dict()
        for ix, league in enumerate(all_leagues):
            league_data = get_league_table_data(league, current_season)
            if ix > 0:
                # Promote from league
                for p in league_data[0:promoted_count]:
                    changes[p["club"].id] = all_leagues[ix - 1].id

            # Relegate from league
            league_below = all_leagues[ix + 1] if ix < len(all_leagues) - 1 else None

            for r in league_data[-relegated_count:]:
                changes[r["club"].id] = league_below.id if league_below else None

            if league_below is None:
                new_clubs = self.get_clubs_not_in_leagues_for_season()
                shuffle(new_clubs)
                for p in new_clubs[0:promoted_count]:
                    changes[p.id] = league.id

        new_registrations = []
        for club_id, new_league_id in changes.items():
            if new_league_id is not None:
                new_registrations.append((club_id, new_league_id))

        for reg in self.get_league_registrations_for_current_season():
            if reg.club_id in changes.keys():
                pass
            else:
                new_registrations.append((reg.club_id, reg.competition_id))
        return new_registrations

    @timer
    def create_next_season(self):
        seasons = self.get_seasons()
        year = 1 if not seasons else seasons[-1].year + 1
        logging.info(f"Creating Season for Year: {year}")

        new_season = SeasonDB(year=year)
        self.session.add(new_season)
        self.session.commit()
        return new_season

    def add_result(self, fixture, score):
        result = ResultDB(id=fixture.id, home_score=score[0], away_score=score[1])
        self.session.add(result)
        self.session.commit()
        return result

    def add_results(self, fixtures_and_scores):
        all_results = [
            ResultDB(id=fs[0].id, home_score=fs[1][0], away_score=fs[1][1])
            for fs in fixtures_and_scores
        ]
        self.session.add_all(all_results)
        self.session.commit()
        return all_results

    # @timer
    def do_post_season_setup(self):
        logging.info("Post Season Setup...")
        current_season = self.get_current_season()

        if current_season:
            next_season_registrations = self.get_next_season_league_registrations()

        else:
            club_copy = list(self.get_clubs())
            shuffle(club_copy)

            next_season_registrations = []
            for league in self.get_leagues():
                for _ in range(league.required_teams):
                    next_season_registrations.append((club_copy.pop(0).id, league.id))

        # create next season
        next_season = self.create_next_season()

        new_regs = list()
        for reg in next_season_registrations:
            if reg[1] is None:
                continue
            new_regs.append(
                CompetitionRegisterDB(
                    season_id=next_season.id,
                    competition_id=reg[1],
                    club_id=reg[0],
                )
            )

        if new_regs:
            self.session.add_all(new_regs)
            self.session.commit()

        clubs_for_cup = []
        for league in self.get_leagues():
            clubs_for_cup.extend(league.get_clubs_for_season(next_season))

        if clubs_for_cup:
            logging.info("Do cup registration")
            cup_regs = []
            for cup in self.get_cups():
                club_copy = list(clubs_for_cup)
                shuffle(club_copy)

                for club in club_copy:
                    reg = CompetitionRegisterDB(
                        season_id=next_season.id, competition_id=cup.id, club_id=club.id
                    )
                    cup_regs.append(reg)

            if cup_regs:
                self.session.add_all(cup_regs)
                self.session.commit()

    @timer
    def do_new_season(self):
        logging.info("New Season Setup...")

        current_season = self.get_current_season()
        world = self.get_world()
        if current_season and world:
            world.season_id = current_season.id
            world.current_week = 1
            self.session.commit()
        else:
            raise RuntimeError(f"Expected World({world}) and season({current_season})")

        # get all leagues
        for league in self.session.scalars(select(LeagueDB)).all():
            logging.info(f"Create fixtures for {league}")

            # get registered teams
            league_clubs = league.get_clubs_for_season(season=current_season)

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

            self.session.add_all(fixture_objects)
            self.session.commit()

            logging.info(
                f"#Num Rounds {len(fixtures)} #Num Fixtures: {sum([len(f) for f in fixtures])}"
            )


def contract_expiry():
    return WEEKS_IN_YEAR * randint(1, 4)


class DatabaseCreator(DatabaseWorker):
    """
    Database setup worker
    """

    def __init__(self, db_path: str, delete_existing: bool = True):
        super().__init__(db_path=db_path)
        self._delete_existsing = delete_existing
        self._game_seed = random_seed()

    def _pre_populate_db(self):
        logging.info("Pre-populate DB with static data")
        weeks = []
        for week in range(1, WEEKS_IN_YEAR + 1):
            if not self.session.scalars(
                select(WeekDB).where(WeekDB.week_num == week)
            ).first():
                if week <= 5:
                    role = WeekType.Preseason
                elif week <= 48:
                    role = WeekType.Regular_Season
                else:
                    role = WeekType.Postseason

                weeks.append(WeekDB(week_num=week, role=role))
        if weeks:
            self.session.add_all(weeks)
        self.session.commit()

        weeks = self.session.scalars(select(WeekDB)).all()
        logging.info(f"Weeks in DB: {len(weeks)}")

    @timer
    def create_db(self):
        self._game_seed = random_seed()
        logging.info(
            f"Create New Database '{self._db_path}', delete existing: {self._delete_existsing}, seed:{hex(self._game_seed)}"
        )
        create_tables(self._db_path, self._delete_existsing)

        self._pre_populate_db()

        rnd_seed(self._game_seed)

        world = WorldDB(game_seed=self._game_seed)
        self.session.add(world)
        self.session.commit()

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

    @timer
    def _create_db_clubs(self):
        names = list(CLUB_NAMES)
        logging.info(f"Creating {len(CLUB_NAMES)} clubs")

        shuffle(names)
        clubs = [ClubDB(name=name) for name in names]
        self.session.add_all(clubs)
        self.session.commit()

        return len(self.session.scalars(select(ClubDB)).all())

    @timer
    def _create_db_competitions(self):
        logging.info("Creating competitions")

        league_group = LeagueGroupDB(name="Test FA")
        self.session.add(league_group)
        self.session.commit()

        self.session.add(
            LeagueDB(
                name="Premier League",
                short_name="PL",
                league_group_id=league_group.id,
                league_ranking=1,
                required_teams=16,
            )
        )
        self.session.add(
            LeagueDB(
                name="Championship",
                short_name="CH",
                league_group_id=league_group.id,
                league_ranking=2,
                required_teams=16,
            )
        )
        self.session.add(CupDB(name="League Cup", short_name="LC"))
        self.session.commit()

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
        self.session.add_all(all_persons)
        self.session.flush()  # Flush to get IDs
        for person, db_staff in all_staff:
            db_staff.person_id = person.id
            self.session.add(db_staff)
        self.session.commit()

        return len(self.session.scalars(select(StaffDB)).all())

    @timer
    def _create_players(self, num_clubs: int):
        num_players = 15 * num_clubs * 2
        logging.info(f"Creating {num_players} players...")

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
        self.session.add_all(all_persons)
        self.session.flush()
        for person, player_db in all_players:
            player_db.person_id = person.id
            self.session.add(player_db)
        self.session.commit()
        return len(self.session.scalars(select(PlayerDB)).all())

    @timer
    def _allocate_staff(self):
        logging.info("Allocating Staff...")
        clubs = self.session.scalars(select(ClubDB)).all()

        managers = self.session.scalars(
            select(StaffDB).where(StaffDB.role == StaffRole.Manager)
        ).all()
        coaches = self.session.scalars(
            select(StaffDB).where(StaffDB.role == StaffRole.Coach)
        ).all()
        scouts = self.session.scalars(
            select(StaffDB).where(StaffDB.role == StaffRole.Scout)
        ).all()
        physios = self.session.scalars(
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
        self.session.add_all(contracts)
        self.session.commit()

        return len(
            self.session.scalars(
                select(ContractDB).where(
                    ContractDB.contract_type == ContractType.Staff_Contract
                )
            ).all()
        )

    @timer
    def _allocate_players(self):
        logging.info("Allocating Players...")
        clubs = self.session.scalars(select(ClubDB)).all()

        goalkeepers = self.session.scalars(
            select(PlayerDB).where(PlayerDB.position == Position.Goalkeeper)
        ).all()
        defenders = self.session.scalars(
            select(PlayerDB).where(PlayerDB.position == Position.Defender)
        ).all()
        midfielders = self.session.scalars(
            select(PlayerDB).where(PlayerDB.position == Position.Midfielder)
        ).all()
        attackers = self.session.scalars(
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
        self.session.add_all(contracts)
        self.session.commit()

        return len(
            self.session.scalars(
                select(ContractDB).where(
                    ContractDB.contract_type == ContractType.Player_Contract
                )
            ).all()
        )
