from dataclasses import dataclass
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
        return self.world.current_season.fixture_calendar.weeks.get(week_num, [])

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



