from argparse import ArgumentParser
import logging

from src.database_main import game_state_engine
from src.gui.ui_db import run_db_gui_application


if __name__ == "__main__":
    parser = ArgumentParser("Fitba")
    parser.add_argument(
        "-g", "--gui", action="store_true", default=True, help="Running GUI mode"
    )
    args = parser.parse_args()

    if args.gui:
        run_db_gui_application()
    else:
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s | %(levelname)s | %(message)s",
        )
        game_state_engine(seasons=2)
