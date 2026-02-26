from __future__ import annotations
from argparse import ArgumentParser
import logging
from time import perf_counter, sleep
from traceback import format_exc

from src.core.db.game_worker import GameDBWorker


def db_main():

    logging.basicConfig(
        level=logging.DEBUG,
        format="[%(asctime)s|%(thread)x|%(levelname)s|%(module)s.%(funcName)s] %(message)s",
    )

    try:
        start_time = perf_counter()

        game_worker = GameDBWorker()

        max_seasons = 3
        
        game_worker.create_new_database(delete_existing=True)
        count = 0
        while count < max_seasons:
            game_worker.do_new_season()
            game_worker.run_season()
            game_worker.process_end_of_season()
            sleep(1.00)
            count += 1

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
