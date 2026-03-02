from __future__ import annotations
from enum import Enum, auto, unique
import logging
from random import randint


from src.core.world_time import WEEKS_IN_YEAR

from .league_db_functions import get_league_table_data
from .db_worker import DatabaseWorker, DatabaseCreator


def create_score():
    min_goals, max_goals = 0, 5
    return randint(min_goals, max_goals), randint(min_goals, max_goals)


def league_table_text(league_data):
    league_table_text = ["", ("-" * 80), "League Table"]

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
        # keep a single worker instance so that sessions stay alive when
        # objects returned by the API are still being used by the caller.
        self._worker: DatabaseWorker | None = None

    def create_new_database(self, delete_existing: bool = True):
        logging.info(
            f"Creating new database at {self._db_path}, delete existing: {delete_existing}"
        )
        DatabaseCreator(
            db_path=self._db_path, delete_existing=delete_existing
        ).create_db()

    @property
    def worker(self):
        if self._worker is None:
            self._worker = DatabaseWorker(db_path=self._db_path)
        return self._worker

    def close(self):
        """Close any open session held by the cached worker."""
        if self._worker:
            self._worker.close_session()
            self._worker = None

    def do_new_season(self):
        logging.info("Do new season setup...")
        self.worker.do_new_season()

    def process_end_of_season(self):
        logging.info("Process End of Season...")
        current_season = self.worker.get_current_season()

        for league in self.worker.get_leagues_from_competitions():
            league_data = get_league_table_data(league, current_season)
            logging.info(f"{'\n'.join(league_table_text(league_data))}")

        self.worker.do_post_season_setup()

    def current_date(self):
        current_season = self.worker.get_current_season()
        current_week = self.worker.get_week(self.worker.get_current_week())
        return current_season, current_week

    def current_fixtures(self):
        return self.worker.get_fixtures_for_current_week()

    def current_results(self):
        return self.worker.get_results_for_current_week()
