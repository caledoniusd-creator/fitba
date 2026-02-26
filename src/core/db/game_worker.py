from __future__ import annotations
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

    def create_new_database(self, delete_existing: bool = True):
        logging.info(
            f"Creating new database at {self._db_path}, delete existing: {delete_existing}"
        )
        DatabaseCreator(
            db_path=self._db_path, delete_existing=delete_existing
        ).create_db()

    @property
    def worker(self):
        return DatabaseWorker(db_path=self._db_path)

    def do_new_season(self):
        logging.info("Do new season setup...")
        db_worker = DatabaseWorker(db_path=self._db_path)
        db_worker.do_new_season()

    def process_current_week(self):
        db_worker = DatabaseWorker(db_path=self._db_path)
        current_season = db_worker.get_current_season()
        current_week = db_worker.get_current_week()
        week_db = db_worker.get_week(current_week)
        logging.info(f"Process Current Week: {week_db}...")

        if current_week >= WEEKS_IN_YEAR:
            logging.info(f"End of season [{current_season}] reached...")
            self.process_end_of_season()
            self.do_new_season()
        else:
            current_fixtures = db_worker.get_fixtures_for_current_week()
            if current_fixtures:
                logging.info(f"# Fixtures: {len(current_fixtures)}")
                fixtures_and_scores = []
                for fixture in current_fixtures:
                    score = create_score()
                    fixtures_and_scores.append((fixture, score))
                db_worker.add_results(fixtures_and_scores=fixtures_and_scores)
            db_worker.advance_week()

    def run_season(self):
        db_worker = DatabaseWorker(db_path=self._db_path)
        current_season = db_worker.get_current_season()
        logging.info(f"Simulating {current_season}....")
        while True:
            current_week = db_worker.get_current_week()
            week_db = db_worker.get_week(current_week)

            if current_week != WEEKS_IN_YEAR:
                current_fixtures = db_worker.get_fixtures_for_current_week()

                text = f"{week_db}" + (
                    f" # fixtures {len(current_fixtures)}" if current_fixtures else ""
                )
                logging.info(text)

                if current_fixtures:
                    fixtures_and_scores = []
                    for fixture in current_fixtures:
                        score = create_score()
                        fixtures_and_scores.append((fixture, score))
                    db_worker.add_results(fixtures_and_scores=fixtures_and_scores)
                db_worker.advance_week()

            else:
                logging.info(f"{week_db}")
                break

    def process_end_of_season(self):
        logging.info("Process End of Season...")
        db_worker = DatabaseWorker(db_path=self._db_path)
        current_season = db_worker.get_current_season()

        for league in db_worker.get_leagues_from_competitions():
            league_data = get_league_table_data(league, current_season)
            logging.info(f"{'\n'.join(league_table_text(league_data))}")

        db_worker.do_post_season_setup()

    def current_date(self):
        db_worker = DatabaseWorker(db_path=self._db_path)
        current_season = db_worker.get_current_season()
        current_week = db_worker.get_week(db_worker.get_current_week())
        return current_season, current_week