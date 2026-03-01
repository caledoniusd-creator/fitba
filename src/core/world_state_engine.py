
from __future__ import annotations
from enum import Enum, auto, unique
import logging
from random import randint


from src.core.world_time import WEEKS_IN_YEAR

from .db.league_db_functions import get_league_table_data
from .db.db_worker import DatabaseWorker, DatabaseCreator

from .db.game_worker import create_score, GameDBWorker

@unique
class WorldState(Enum):
    NewGame = auto()
    NewSeason = auto()
    PostSeason = auto()
    PreFixtures = auto()
    ProcessingFixtures = auto()
    PostFixtures = auto()
    AwaitingContinue = auto()


class WorldStateEngine:
    def __init__(self, db_path: str | None = None):
        db_path = db_path if db_path is not None else GameDBWorker.DEFAULT_DB_PATH
        self._game_worker = GameDBWorker(db_path=db_path)

        self._state = WorldState.NewGame
        self._results = None

    def clear_results(self):
        self._results = None

    @property
    def results(self):
        return self._results

    @property
    def game_worker(self):
        return self._game_worker

    @property
    def world_time(self):
        return self.game_worker.current_date()

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, new_state: WorldState):
        self._state = new_state

    def _do_process_fixtures(self):
        current_fixtures = self.game_worker.current_fixtures()
        if not current_fixtures:
            logging.warning("Processing fixtures for no fixtures?")
            return

        logging.info(f"Processing {len(current_fixtures)} fixtures")
        self._results = self.game_worker.worker.add_results(
            fixtures_and_scores=[
                (fixture, create_score()) for fixture in current_fixtures
            ]
        )

    def _process_state(self):
        if self.state == WorldState.NewGame:
            logging.info("New Game...")
            self.game_worker.create_new_database(delete_existing=True)
            self.state = WorldState.NewSeason

        elif self.state == WorldState.NewSeason:
            self.game_worker.do_new_season()
            logging.info(f"New Season {self.world_time[0].year}")
            self.state = WorldState.AwaitingContinue

        elif self.state == WorldState.PostSeason:
            logging.info(
                f"Post Season {self.world_time[0].year} completed! prepare promotion/relegation and new season setup next week."
            )
            self._game_worker.process_end_of_season()
            self.state = WorldState.NewSeason

        elif self.state == WorldState.PreFixtures:
            logging.info("Pre Fixtures")
            self.state = WorldState.ProcessingFixtures

        elif self.state == WorldState.ProcessingFixtures:
            logging.info("Processing Fixtures")
            self._do_process_fixtures()
            self.state = WorldState.PostFixtures

        elif self.state == WorldState.PostFixtures:
            logging.info("Post Fixtures")
            self.state = WorldState.AwaitingContinue

        elif self.state == WorldState.AwaitingContinue:
            current_week_fixtures = self.game_worker.current_fixtures()
            if current_week_fixtures:
                self.state = WorldState.PreFixtures
            else:
                logging.info("Advance Week")
                self.clear_results()
                self.game_worker.worker.advance_week()
                if self.world_time[1].week_num == WEEKS_IN_YEAR:
                    self.state = WorldState.PostSeason

        else:
            raise RuntimeError(f"Unknown state: {self.state}")

    def advance_game(self):
        self._process_state()

    def advance_to_post_season(self):
        current_week = self.world_time[1].week_num
        logging.info(f"Advancing to PostSeason current week: {current_week}")
        while self.state != WorldState.PostSeason:
            self.advance_game()
            if current_week != self.world_time[1].week_num:
                current_week = self.world_time[1].week_num
                logging.info(f"New week: {current_week}")
        logging.info("Post Season!")

    def advance_to_new_week(self):
        if self.state in [WorldState.PostSeason, WorldState.NewSeason]:
            logging.info(f"Invalid state '{self.state.name}' to advance to new week")
            return
        current_week = self.world_time[1].week_num
        logging.info(f"Advancing to new week current week: {current_week}")
        while (
            self.state != WorldState.PostSeason
            and current_week == self.world_time[1].week_num
        ):
            self.advance_game()
    