from argparse import ArgumentParser
import logging
from traceback import format_exc

from cli.cli_game import cli_app_main

from src.core.club import CLUB_NAMES
from src.core.db.models import Club, LeagueGroup, League, Cup
from src.core.db.utils import create_session, create_tables


def create_db_competitions():
    session = create_session()()

    league_group = LeagueGroup(name="Test FA")
    session.add(league_group)
    session.commit()

    session.add(
        League(
            name="Premier League",
            short_name="PL",
            league_group_id=league_group.id,
            league_ranking=1,
            required_teams=16,
        )
    )
    session.add(
        League(
            name="Championship",
            short_name="CH",
            league_group_id=league_group.id,
            league_ranking=2,
            required_teams=16,
        )
    )
    session.add(Cup(name="League Cup", short_name="LC"))
    session.commit()


def create_db_clubs():
    session = create_session()()
    for name in CLUB_NAMES:
        new_club = Club(name=name)
        session.add(new_club)
    session.commit()


def db_main():

    logging.basicConfig(level=logging.DEBUG)
    try:
        logging.info("Create Tables")
        create_tables()
        create_db_competitions()
        create_db_clubs()

    except Exception as e:
        logging.debug(format_exc())
        logging.exception(e)
        logging.error(e)


if __name__ == "__main__":
    parser = ArgumentParser("Fitba")
    parser.add_argument(
        "-g", "--gui", action="store_true", default=True, help="Running GUI mode"
    )
    args = parser.parse_args()

    if args.gui:
        # run_gui_application()
        db_main()
    else:
        cli_app_main()
