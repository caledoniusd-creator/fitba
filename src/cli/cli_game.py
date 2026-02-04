from dataclasses import dataclass
from enum import Enum, auto, unique
from traceback import format_exc
from typing import Optional, List


from core.world_time import WEEKS_IN_YEAR
from core.competition import CompetitionType
from core.fixture import Fixture, Result
from core.league_table import LeagueTableWorker
from core.workers import create_test_world, WorldWorker

from .cli import clear_console


@unique
class GameState(Enum):
    Continue = auto()
    Current_Fixtures = auto()
    Processing_Results = auto()
    Display_Results = auto()


@unique
class GameView(Enum):
    MainView = auto()
    ClubsView = auto()
    FixtureView = auto()
    ResultView = auto()
    LeagueTableView = auto()


@dataclass
class GameLoopState:
    state: GameState = GameState.Continue
    view: GameView = GameView.MainView
    current_fixtures: Optional[List[Fixture]] = None
    current_results: Optional[List[Result]] = None
    view_data: Optional[dict] = None

    def reset(self):
        self.state = GameState.Continue
        self.view = GameView.MainView
        self.current_fixtures = None
        self.current_results = None
        self.view_data = None


def cli_app_main():
    try:
        # New Game / Load Game Menu
        create_or_load = "create"  # For now, always create new game
        if create_or_load == "create":
            # Create World
            world = create_test_world()

        elif create_or_load == "load":
            # Load World
            world = None  # Placeholder for load functionality

        # fail if no world
        if world is None:
            raise RuntimeError("Failed to create or load world.")

        # UI Constants
        line_length = 80
        max_lines = 25
        seperator, blank_line = "=" * line_length, " " * line_length

        # User Input Loop
        keep_running = True
        world_worker = WorldWorker(world)

        game_loop_state = GameLoopState()
        last_week = None
        while keep_running:
            try:
                # clear
                clear_console()
                messages = []

                # processing
                if world.world_time.week == 1 and last_week != world.world_time.week:
                    # Week 1 of new season
                    world_worker.create_new_season()
                    messages.append(
                        f"New Season {world.world_time.year}"
                        + f", completed: {len(world.previous_seasons)}"
                        if world.previous_seasons
                        else ""
                    )

                elif world.world_time.week == WEEKS_IN_YEAR:
                    # Week 52 - end of season
                    messages.append(
                        f"Season {world.world_time.year} completed! prepare promotion/relegation and new season setup next week."
                    )

                # display messages based on state
                if game_loop_state.state == GameState.Continue:
                    if game_loop_state.view == GameView.MainView:
                        current_fixtures = world_worker.get_current_fixtures()
                        if current_fixtures:
                            messages.append(
                                f"{len(current_fixtures)} fixtures this week"
                            )
                        else:
                            next_week, next_fixtures = world_worker.get_next_fixtures()
                            messages.append("No fixtures scheduled this week.")
                            messages.append(
                                f"Next fixtures in Week {next_week} ({len(next_fixtures)} fixtures)"
                                if next_fixtures
                                else "No more fixtures scheduled this season."
                            )

                    elif game_loop_state.view == GameView.LeagueTableView:
                        league = game_loop_state.view_data.get("league", None)
                        if league:
                            ltw = LeagueTableWorker(
                                league, world_worker.results_for_competition(league)
                            )
                            messages.append(blank_line)
                            messages.extend(
                                [
                                    f" {line} ".ljust(line_length, " ")
                                    for line in ltw.table_text()
                                ]
                            )

                    elif game_loop_state.view == GameView.ClubsView:
                        clubs_in_list = 15
                        all_clubs = world_worker.world.club_pool.get_all_clubs()
                        all_clubs = [str(club.name).ljust(25) for club in all_clubs]
                        club_lists = [
                            all_clubs[i : i + 20]
                            for i in range(0, len(all_clubs), clubs_in_list)
                        ]
                        max_size = max([len(clubs) for clubs in club_lists])

                        for i in range(0, max_size):
                            text = []
                            for clubs in club_lists:
                                try:
                                    name = clubs[i]
                                    text.append(name)
                                except IndexError:
                                    pass
                            messages.append(" ".join(text))

                elif game_loop_state.state == GameState.Current_Fixtures:
                    if game_loop_state.current_fixtures:
                        messages.append(
                            f"Fixtures for Week {world.world_time.week}: {len(game_loop_state.current_fixtures)}"
                        )
                        messages.extend(
                            [
                                f" {fixture} ".center(line_length, " ")
                                for fixture in game_loop_state.current_fixtures
                            ]
                        )

                elif game_loop_state.state == GameState.Processing_Results:
                    if game_loop_state.current_fixtures:
                        messages.append(
                            f"Processing {len(game_loop_state.current_fixtures)} fixtures..."
                        )

                elif game_loop_state.state == GameState.Display_Results:
                    if game_loop_state.current_results:
                        messages.append(
                            f"Results for Week {world.world_time.week}: {len(game_loop_state.current_results)}"
                        )
                        messages.extend(
                            [
                                f" {result} ".center(line_length, " ")
                                for result in game_loop_state.current_results
                            ]
                        )
                else:
                    messages.append(f"Unknown game state: {game_loop_state.state}")

                # display
                title_lines = [
                    " Fitba Manager ".center(line_length, "="),
                    f" {world.world_time} ".replace("Year", "Season").center(
                        line_length, " "
                    ),
                    seperator,
                    blank_line,
                ]

                lines = list(title_lines)
                messages = messages[-max_lines:]

                lines.extend(
                    [f" {message} ".ljust(line_length, " ") for message in messages]
                )
                lines.extend([blank_line for _ in range(max_lines - len(messages))])

                info_line = (
                    f" #Clubs: {world.club_pool.count}, #Comps: {len(world.competitions)}"
                    f", #Fixtures: {world.current_season.fixture_calendar.count}, #Results: {world.current_season.match_results.count} "
                )
                lines.extend(
                    [
                        blank_line,
                        seperator,
                        info_line.ljust(line_length, " "),
                        seperator,
                    ]
                )

                print("\n".join(lines))

                # update
                last_week = world.world_time.week

                # get user input
                user_input = (
                    input("Enter command (q to quit, Enter for next week): ")
                    .strip()
                    .lower()
                )
                if user_input == "q":
                    print("Exiting game. Goodbye!")
                    keep_running = False
                    continue
                else:
                    # State machine transitions
                    if game_loop_state.state == GameState.Continue:
                        if game_loop_state.view == GameView.MainView:
                            if user_input == "t":
                                leagues = [
                                    comp
                                    for comp in world.competitions
                                    if comp.type == CompetitionType.LEAGUE
                                ]
                                league = leagues[0] if leagues else None

                                game_loop_state.view = GameView.LeagueTableView
                                game_loop_state.view_data = {"league": league}

                            elif user_input == "c":
                                game_loop_state.view = GameView.ClubsView
                                game_loop_state.view_data = None

                            elif user_input == "":
                                current_week_fixtures = (
                                    world_worker.get_current_fixtures()
                                )
                                if current_week_fixtures:
                                    game_loop_state.state = GameState.Current_Fixtures
                                    game_loop_state.current_fixtures = (
                                        current_week_fixtures
                                    )
                                else:
                                    game_loop_state.reset()
                                    world.world_time.advance_week()

                        elif game_loop_state.view == GameView.LeagueTableView:
                            try:
                                index = int(user_input)
                                leagues = [
                                    comp
                                    for comp in world.competitions
                                    if comp.type == CompetitionType.LEAGUE
                                ]
                                index = (index - 1) % len(leagues)
                                league = leagues[index] if leagues else None
                                game_loop_state.view_data = {"league": league}

                            except ValueError:
                                game_loop_state.view = GameView.MainView
                                game_loop_state.view_data = None

                        elif game_loop_state.view == GameView.ClubsView:
                            game_loop_state.view = GameView.MainView
                            game_loop_state.view_data = None

                    elif game_loop_state.state == GameState.Current_Fixtures:
                        if game_loop_state.current_fixtures:
                            game_loop_state.state = GameState.Processing_Results
                        else:
                            game_loop_state.reset()

                    elif game_loop_state.state == GameState.Processing_Results:
                        if game_loop_state.current_fixtures:
                            results = world_worker.process_fixtures(
                                game_loop_state.current_fixtures, world.world_time.week
                            )
                            game_loop_state.current_results = results
                            game_loop_state.state = GameState.Display_Results
                        else:
                            game_loop_state.reset()

                    elif game_loop_state.state == GameState.Display_Results:
                        game_loop_state.reset()

                    else:
                        input(
                            "Unknown command. Please try again. Press Enter to continue..."
                        )

            except KeyboardInterrupt:
                print("\nExiting game. Goodbye!")
                keep_running = False

    except Exception as e:
        print(f"An error occurred: {e}")
        print(format_exc())
