from argparse import ArgumentParser
import logging

from src.database_main import game_state_engine
from src.gui.ui_db import run_db_gui_application

from src.sandbox.game_result_sandbox import game_result_function
from src.sandbox.player_ability_sandbox import test_player_ability


if __name__ == "__main__":
    parser = ArgumentParser("Fitba")
    parser.add_argument(
        "-g", "--gui", action="store_true", default=True, help="Running GUI mode"
    )
    args = parser.parse_args()

    if args.gui:
        # run_db_gui_application()
        # game_result_function()
        test_player_ability()
        
    else:
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s | %(levelname)s | %(message)s",
        )
        game_state_engine(seasons=2)
