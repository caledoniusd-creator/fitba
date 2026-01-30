from dataclasses import dataclass
from enum import Enum, unique, auto
from random import choices, shuffle
from typing import Optional, List

from .world_time import WEEKS_IN_YEAR, WorldTime
from .calendars import Season
from .club import ClubPool, ClubFactory
from .competition import CompetitionType, Competition, League, Cup
from .leagues import league_30_fixtures, create_league_fixtures
from .fixture import Fixture, Result


@dataclass
class World:
    world_time: WorldTime
    current_season: Optional[Season] = None
    previous_seasons: Optional[List[Season]] = None

    club_pool: Optional[ClubPool] = None
    competitions: Optional[List[Competition]] = None

    def __post_init__(self):
        self.previous_seasons = self.previous_seasons or []
        self.club_pool = self.club_pool or ClubPool()
        self.competitions = self.competitions or []

    def __str__(self):
        return f"World Time -> {self.world_time}"


def create_test_world() -> World:    
    world = World(WorldTime(1, 1))
    for club in ClubFactory.create_clubs(40):
        world.club_pool.add_club(club)

    all_clubs = world.club_pool.get_all_clubs()
    shuffle(all_clubs)

    league_prem = League("Premier League", "PL")
    league_prem.clubs = all_clubs[:16]
    world.competitions.append(league_prem)

    league_champ = League("Championship", "CH")
    league_champ.clubs = all_clubs[16:32]
    world.competitions.append(league_champ)

    cup = Cup("League Cup", "LC")
    cup.clubs = all_clubs[:32]
    world.competitions.append(cup)

    return world






class WorldWorker:
    def __init__(self, world: World):
        self.world = world

    def create_new_season(self):
        if self.world.current_season is not None:
            self.world.previous_seasons.append(self.world.current_season)
        self.world.current_season = Season(self.world.world_time.year)

        fixture_calendar = self.world.current_season.fixture_calendar
        for competition in self.world.competitions:
            if competition.type == CompetitionType.LEAGUE:
                league_fixtures = create_league_fixtures(
                    competition, reverse_fixtures=True
                )

                for round_num, round_fixtures in enumerate(league_fixtures):
                    fixture_calendar.add_objects(
                        league_30_fixtures[round_num], round_fixtures
                    )

    def get_current_fixtures(self):
        week_num = self.world.world_time.week
        if self.world.current_season:
            return self.world.current_season.fixture_calendar.weeks.get(week_num, [])
        return []

    def process_fixtures(self, fixtures: List[Fixture], week: int):
        fixture_calendar = self.world.current_season.fixture_calendar
        match_results = self.world.current_season.match_results
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

        match_results.add_objects(self.world.world_time.week, results)
        fixture_calendar.clear_fixtures(self.world.world_time.week)

        return results

    def results_for_competition(self, competition: Competition):
        all_results = []
        for week_results in self.world.current_season.match_results.weeks.values():
            for result in week_results:
                if result.competition == competition:
                    all_results.append(result)
        return all_results

    def get_next_fixtures(self):
        next_week = self.world.world_time.week
        fixtures = self.world.current_season.fixture_calendar.weeks.get(next_week, [])
        while not fixtures and next_week < WEEKS_IN_YEAR:
            next_week += 1
            fixtures = self.world.current_season.fixture_calendar.weeks.get(
                next_week, []
            )
        return next_week, fixtures


@unique
class WorldState(Enum):
    NewSeason = auto()
    PostSeason = auto()
    PreFixtures = auto()
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

    def _process_state(self):
        if self.state == WorldState.NewSeason:
            self.world_worker.create_new_season()
            print(f"New Season {self.world_time.year}")
            self.state = WorldState.AwaitingContinue

        elif self.state == WorldState.PostSeason:
            print(f"Post Season {self.world_time.year} completed! prepare promotion/relegation and new season setup next week.")
            print("Advance Week")
            self.world_time.advance_week()
            self.state = WorldState.NewSeason

        elif self.state == WorldState.PreFixtures:
            print("Pre Fixtures")
            self._results = self.world_worker.process_fixtures(self._fixtures, self.world_time.week)
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