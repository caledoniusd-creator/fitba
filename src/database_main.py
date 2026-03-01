from __future__ import annotations
from argparse import ArgumentParser
import logging
import sys
from time import perf_counter, sleep
from traceback import format_exc

from src.core.world_state_engine import  WorldState, WorldStateEngine


def game_state_engine(seasons: int = 3):
    """
    non interactive game loop
    """
    state_engine = WorldStateEngine()
    if state_engine.state == WorldState.NewGame:
        state_engine.advance_game()

    for _ in range(seasons):
        state_engine.advance_game()
        state_engine.advance_to_post_season()

        sleep(1)
        state_engine.advance_game()


def game_with_state_engine_test_run():
    """
    Console UI game loop
    """
    state_engine = WorldStateEngine()

    while True:
        if state_engine.state == WorldState.AwaitingContinue:
            date_text = f"{state_engine.world_time[0]} {state_engine.world_time[1]}"
        else:
            date_text = "n/a"

        logging.info(f"Game State: {state_engine.state.name} - {date_text}")

        if state_engine.state == WorldState.PreFixtures:
            logging.info("Next Fixtures:")
            current_fixtures = state_engine.game_worker.current_fixtures()
            for f in current_fixtures:
                text = [
                    str(f.competition.short_name).ljust(8),
                    str(f.competition_round).center(3),
                    str(f.home_club.name).rjust(30),
                    str("v").center(5),
                    str(f.away_club.name).ljust(30),
                ]
                logging.info("".join(text))

        elif state_engine.state == WorldState.PostFixtures:
            logging.info("Previous Results:")
            results = state_engine.game_worker.current_results()
            for r in results:
                text = [
                    str(r.fixture.competition.short_name).ljust(8),
                    str(r.fixture.competition_round).center(3),
                    str(r.fixture.home_club.name).rjust(30),
                    str(r.home_score).rjust(3),
                    str("-"),
                    str(r.away_score).ljust(3),
                    str(r.fixture.away_club.name).ljust(30),
                ]
                logging.info("".join(text))

        sys.stdout.flush()
        user_input = input(">")

        if user_input.lower() == "q":
            break

        if user_input.lower() == "e":
            logging.info("Advancing to Post Season")
            state_engine.advance_to_post_season()

        else:
            logging.info("Advance!")
            state_engine.advance_game()


def db_main():
    """
    Test DB Main function
    simulates a a number of seasons with out a UI
    """
    logging.basicConfig(
        level=logging.DEBUG,
        format="[%(asctime)s|%(thread)x|%(levelname)s|%(module)s.%(funcName)s] %(message)s",
    )

    try:
        start_time = perf_counter()

        game_state_engine(seasons=3)
        # game_with_state_engine_test_run()

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
