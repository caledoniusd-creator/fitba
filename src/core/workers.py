from dataclasses import dataclass
from enum import Enum, unique, auto
from random import choices, shuffle, randrange, seed as rand_seed

from typing import Optional, List

from .world_time import WEEKS_IN_YEAR, WorldTime
from .calendars import Season
from .club import Club, ClubPool, ClubFactory
from .competition import CompetitionType, Competition, League, Cup
from .leagues import league_30_fixtures, create_league_fixtures
from .fixture import Fixture, Result
from .league_table import LeagueTableWorker
from .people import PersonFactory
from .world import World


def random_seed():
    return randrange(2**32)


def create_test_world() -> World:
    world_seed = random_seed()
    print(f"World Seed: {hex(world_seed)}")

    world = World(world_seed, WorldTime(1, 1))
    for club in ClubFactory.create_clubs(48):
        world.club_pool.add_club(club)

    all_clubs = world.club_pool.get_all_clubs()
    shuffle(all_clubs)

    league_prem = League("Premier League", "PL", ranking=1)
    league_prem.clubs = all_clubs[:16]
    world.competitions.append(league_prem)

    league_champ = League("Championship", "CH", ranking=2)
    league_champ.clubs = all_clubs[16:32]
    world.competitions.append(league_champ)

    cup = Cup("League Cup", "LC", ranking=100)
    cup.clubs = all_clubs[:32]
    world.competitions.append(cup)

    people = [PersonFactory.random_male() for _ in range(1000)]
    world.person_pool.add_people(people)

    return world


class WorldWorker:
    """
    A worker class responsible for managing seasonal operations and fixture processing in the game world.

    This class handles the creation of new seasons, processing of post-season activities,
    retrieval and processing of fixtures, and calculation of competition results.

    Attributes:
        world (World): The world instance that this worker manages.
    """

    def __init__(self, world: World):
        self.world = world

    def create_new_season(self):
        if self.world.current_season is not None:
            self.world.previous_seasons.append(self.world.current_season)

        self.world.current_season = Season(self.world.world_time.year)

        fixture_schedule = self.world.current_season.fixture_schedule
        for competition in [
            c for c in self.world.competitions if c.type == CompetitionType.LEAGUE
        ]:
            for ix, round_fixtures in enumerate(
                create_league_fixtures(competition, reverse_fixtures=True)
            ):
                round_week = league_30_fixtures[ix]
                fixture_schedule.add_fixtures(round_week, round_fixtures)

    def _promotion_and_relegation(self):
        all_teams = set(self.world.club_pool.get_all_clubs())
        leagues = [
            comp
            for comp in self.world.competitions
            if comp.type == CompetitionType.LEAGUE
        ]
        league_clubs = []
        for league in leagues:
            league_clubs.extend(league.clubs)

        other_clubs = list(all_teams.difference(set(league_clubs)))
        move_clubs = []

        for ix, league in enumerate(leagues):
            table_data = LeagueTableWorker(
                league, self.results_for_competition(league)
            ).get_sorted_table()

            league_above = None if ix == 0 else leagues[ix - 1]
            league_below = None if ix >= len(leagues) - 1 else leagues[ix + 1]

            # promotion
            winners = table_data[0].club
            if league_above:
                for club in [p.club for p in table_data[:3]]:
                    move_clubs.append((club, league, league_above))

            # relegation
            for club in [r.club for r in table_data[-3:]]:
                move_clubs.append((club, league, league_below))

            print(f"{league.name} winners {winners.name}")

        # non league club promotion
        shuffle(other_clubs)
        league_above = leagues[-1]
        for club in other_clubs[:3]:
            move_clubs.append((club, None, league_above))

        # do club moves
        print("Move clubs")
        for data in move_clubs:
            text = f" - {data[0].name}"
            if data[1]:
                text += f" remove from {data[1].name}"
                data[1].clubs.remove(data[0])
            if data[2]:
                text += f" add to {data[2].name}"
                data[2].clubs.append(data[0])
            print(text)

    def process_post_season(self):
        self._promotion_and_relegation()

    def get_current_fixtures(self):
        week_num = self.world.world_time.week
        if self.world.current_season:
            return self.world.current_season.fixture_schedule.get_fixtures_for_week(week_num)
        return []

    def process_fixtures(self, fixtures: List[Fixture], week: int):
        fixture_schedule = self.world.current_season.fixture_schedule

        results = []
        for fixture in fixtures:
            weights_home = [1, 1.25, 0.75, 0.5, 0.25, 0.125]
            weights_away = [1.5, 0.99, 0.66, 0.33, 0.11, 0.033]
            home_score = choices(range(0, 6), weights=weights_home, k=1)[0]
            away_score = choices(range(0, 6), weights=weights_away, k=1)[0]
            result = Result(
                fixture.club1,
                fixture.club2,
                fixture.competition,
                fixture.round_num,
                home_score,
                away_score,
            )
            results.append(result)
        fixture_schedule.set_results(self.world.world_time.week, results)
        return results

    def results_for_competition(self, competition: Competition):
        all_results = []
        if self.world.current_season:
            fixture_schedule = self.world.current_season.fixture_schedule
            all_results = [r for r in fixture_schedule.get_results() if r.competition == competition]
        
        return all_results

    def get_next_fixtures(self):
        if self.world.current_season:
            fixture_schedule = self.world.current_season.fixture_schedule
            next_week = self.world.world_time.week
            fixtures = fixture_schedule.get_fixtures_for_week(next_week)
            while not fixtures and next_week < WEEKS_IN_YEAR:
                next_week += 1
                fixtures = fixture_schedule.get_fixtures_for_week(next_week)
            if fixtures:
                return next_week, fixtures
        return None
    
    def get_club_season_info(self, club: Club):
        data = {
            "competitions": [],
            "fixtures": [],
            "results": [],
        }

        if not self.world.current_season:
            return data

        current_season = self.world.current_season
        for comp in self.world.competitions:
            if comp.contains(club):
                data["competitions"].append(comp)

        for fixture in current_season.fixture_schedule.get_fixtures(with_week=True):
            if fixture[1].involves(club):
                data["fixtures"].append(fixture)

        for result in current_season.fixture_schedule.get_results(with_week=True):
            if result[1].involves(club):
                data["results"].append(result)
        return data

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#   Main State Engine 
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


@unique
class WorldState(Enum):
    NewSeason = auto()
    PostSeason = auto()
    PreFixtures = auto()
    ProcessingFixtures = auto()
    PostFixtures = auto()
    AwaitingContinue = auto()


class WorldStateEngine:
    def __init__(self, world: World):
        self._world_worker = WorldWorker(world)
        self._state = WorldState.NewSeason

        self._fixtures = None
        self._results = None

    def clear_fixtures_and_results(self):
        self._fixtures = None
        self._results = None

    @property
    def fixtures(self):
        return self._fixtures

    @property
    def results(self):
        return self._results

    @property
    def world_worker(self):
        return self._world_worker

    @property
    def world(self):
        return self._world_worker.world

    @property
    def world_time(self):
        return self.world.world_time

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, new_state: WorldState):
        self._state = new_state

    def _do_process_fixtures(self):
        self._results = self.world_worker.process_fixtures(self._fixtures, self.world_time.week)

    def _process_state(self):
        if self.state == WorldState.NewSeason:
            self.world_worker.create_new_season()
            print(f"New Season {self.world_time.year}")
            self.state = WorldState.AwaitingContinue

        elif self.state == WorldState.PostSeason:
            print(
                f"Post Season {self.world_time.year} completed! prepare promotion/relegation and new season setup next week."
            )
            self.world_worker.process_post_season()
            print("Advance Week")
            self.world_time.advance_week()
            self.state = WorldState.NewSeason

        elif self.state == WorldState.PreFixtures:
            print("Pre Fixtures")
            self.state = WorldState.ProcessingFixtures

        elif self.state == WorldState.ProcessingFixtures:
            print("Processing Fixtures")
            self._do_process_fixtures()
            self.state = WorldState.PostFixtures

        elif self.state == WorldState.PostFixtures:
            print("Post Fixtures")
            self.state = WorldState.AwaitingContinue

        elif self.state == WorldState.AwaitingContinue:
            current_week_fixtures = self.world_worker.get_current_fixtures()
            if current_week_fixtures:
                self._fixtures = current_week_fixtures
                self.state = WorldState.PreFixtures
            else:
                print("Advance Week")
                self.clear_fixtures_and_results()
                self.world_time.advance_week()
                if self.world_time.week == WEEKS_IN_YEAR:
                    self.state = WorldState.PostSeason

        else:
            raise RuntimeError(f"Unknown state: {self.state}")

    def advance_game(self):
        self._process_state()

    def advance_to_post_season(self):
        current_week = self.world_time.week
        print(f"Advancing to PostSeason current week: {current_week}")
        while self.state != WorldState.PostSeason:
            self.advance_game()
            if current_week != self.world_time.week:
                current_week = self.world_time.week
                print(f"New week: {current_week}")
        print("Post Season!")

    def advance_to_new_week(self):
        if self.state in [WorldState.PostSeason, WorldState.NewSeason]:
            print(f"Invalid state '{self.state.name}' to advance to new week")
            return
        current_week = self.world_time.week
        print(f"Advancing to new week current week: {current_week}")
        while self.state != WorldState.PostSeason and current_week == self.world_time.week:
            self.advance_game()