

from argparse import ArgumentParser
from cli.cli_game import cli_app_main
from gui.gui_main import run_gui_application


if __name__ == "__main__":
    
    parser = ArgumentParser("Fitba")
    parser.add_argument("-g", "--gui", action="store_true", default=True, help="Running GUI mode")
    args = parser.parse_args()
    

    if args.gui:
        run_gui_application()
    else:
        cli_app_main()
    
