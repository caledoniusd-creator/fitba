from dataclasses import dataclass
from enum import Enum, auto, unique
from os import system, name
from pyexpat.errors import messages
from random import choices, shuffle
from traceback import format_exc
from typing import Optional, List, Dict


from core.club import Club, ClubFactory, ClubPool
from core.competition import CompetitionType, Competition, Friendly, League, Cup
from core.fixture import Fixture, Result
from core.league_table import LeagueTableWorker

from cli.cli import clear_console



league_30_fixtures = [8, 9, 10, 11, 12, 14, 15, 16, 17, 18, 21, 22, 23, 24, 25, 28, 29, 30, 31, 32, 35, 36, 37, 38, 39, 42, 43, 44, 45, 46]
cup_32_fixtures = [19,26, 33, 40, 48]

@dataclass
class WorldTime:
    year: int
    week: int

    def __post_init__(self):
        if self.week < 1 or self.week > 52:
            raise ValueError("Week must be between 1 and 52")
        if self.year < 1:
            raise ValueError("Year must be a positive integer")
        
    def __str__(self):
        return f"Year: {self.year:2d}, Week: {self.week:2d}"
    
    def advance_week(self):
        if self.week == 52:
            self.week = 1
            self.year += 1
        else:
            self.week += 1


@dataclass
class CalendarBase:
    year: int
    weeks: Optional[Dict] = None

    def __post_init__(self):
        self.weeks = self.weeks or {i + 1: [] for i in range(WEEKS_IN_YEAR)}

    @property
    def num_weeks(self):
        return len(self.weeks.keys())
    
    @property
    def count(self):
        return sum(len(objects) for objects in self.weeks.values())
    
    def add_objects(self, week: int, objects):
        if week not in self.weeks:
            raise ValueError(f"Week {week} is not valid in year {self.year}")
        self.weeks[week].extend(objects)
    

@dataclass
class FixtureCalendar(CalendarBase):
    
    def clear_fixtures(self, week: int):
        if week not in self.weeks:
            raise ValueError(f"Week {week} is not valid in year {self.year}")
        self.weeks[week].clear()
        

@dataclass
class ResultCalendar(CalendarBase):
   pass


def create_league_fixtures(league: League, reverse_fixtures: bool = False):
    fixtures = []
    num_rounds = league.club_count - 1
    club_list = list(league.clubs)
    shuffle(club_list)

    if len(club_list) % 2 != 0:
        club_list.append(None)  # Add a dummy club for bye

    half_size = len(club_list) // 2

    # Generate fixtures using the round-robin algorithm
    for round_num in range(num_rounds):
        round_fixtures = []
        for i in range(half_size):
            club1 = club_list[i]
            club2 = club_list[(half_size + i)]
            if round_num % 2 != 0:
                club1, club2 = club2, club1
            if club1 is not None and club2 is not None:
                fixture = Fixture(club1, club2, league, round_num + 1)
                round_fixtures.append(fixture)

        fixtures.append(round_fixtures)
        club_list.append(club_list.pop(1))

    if reverse_fixtures:
        reverse_rounds = []
        for round_fixtures in fixtures:
            reverse_round = []
            for fixture in round_fixtures:
                reverse_fixture = Fixture(
                    fixture.club2, fixture.club1, fixture.competition, fixture.round_num + num_rounds
                )
                reverse_round.append(reverse_fixture)
            reverse_rounds.append(reverse_round)
        fixtures.extend(reverse_rounds)
    return fixtures


@dataclass
class Season:
    year: int
    fixture_calendar: Optional[FixtureCalendar] = None
    match_results: Optional[ResultCalendar] = None

    def __post_init__(self):
        self.fixture_calendar = self.fixture_calendar or FixtureCalendar(self.year)
        self.match_results = self.match_results or ResultCalendar(self.year)

    def __str__(self):
        return f"Season {self.year} #num fixtures: {self.fixture_calendar.count}, #results: {self.match_results.count}"


@dataclass
class World:
    world_time: WorldTime
    current_season: Optional[Season] = None
    previous_seasons: Optional[List[Season]] = None

    club_pool: Optional[ClubPool] = None
    competitions: Optional[List[Competition]] = None


    def __post_init__(self):
        self.previous_seasons = self.previous_seasons or []
        self.club_pool = self.club_pool or ClubPool()
        self.competitions = self.competitions or []

    def __str__(self):
        return f"World Time -> {self.world_time}"


class WorldWorker:
    def __init__(self, world: World):
        self.world = world

    def create_new_season(self):
        if self.world.current_season is not None:
            self.world.previous_seasons.append(self.world.current_season)
        self.world.current_season = Season(self.world.world_time.year)

        fixture_calendar = self.world.current_season.fixture_calendar
        for competition in self.world.competitions:
            if competition.type == CompetitionType.LEAGUE:
                league_fixtures = create_league_fixtures(competition, reverse_fixtures=True)

                for round_num, round_fixtures in enumerate(league_fixtures):
                    fixture_calendar.add_objects(league_30_fixtures[round_num], round_fixtures)
    
    def get_current_fixtures(self):
        week_num = self.world.world_time.week
        return self.world.current_season.fixture_calendar.weeks.get(week_num, [])
    
    def process_fixtures(self, fixtures: List[Fixture], week: int):
        fixture_calendar = self.world.current_season.fixture_calendar
        match_results = self.world.current_season.match_results
        results = []
        for fixture in fixtures:
            weights_home = [1, 1.25, 0.75, 0.5, 0.25, 0.125]
            weights_away = [1.5, 0.99, 0.66, 0.33, 0.11, 0.033]
            home_score = choices(range(0, 6), weights=weights_home, k=1)[0]
            away_score = choices(range(0, 6), weights=weights_away, k=1)[0]
            result = Result(
                fixture.club1,
                fixture.club2,
                fixture.competition,
                fixture.round_num,
                home_score,
                away_score,
            )
            results.append(result)

        match_results.add_objects(self.world.world_time.week, results)
        fixture_calendar.clear_fixtures(self.world.world_time.week)

        return results


    def results_for_competition(self, competition: Competition):
        all_results = []
        for week_results in self.world.current_season.match_results.weeks.values():
            for result in week_results:
                if result.competition == competition:
                    all_results.append(result)
        return all_results
    
    def get_next_fixtures(self):
        next_week = self.world.world_time.week
        fixtures = self.world.current_season.fixture_calendar.weeks.get(next_week, [])
        while not fixtures and next_week < WEEKS_IN_YEAR:
            next_week += 1
            fixtures = self.world.current_season.fixture_calendar.weeks.get(next_week, [])
        return next_week, fixtures


def create_world() -> World:    
    world = World(WorldTime(1, 1))
    for club in ClubFactory.create_clubs(40):
        world.club_pool.add_club(club)

    all_clubs = world.club_pool.get_all_clubs()
    shuffle(all_clubs)

    league_prem = League("Premier League", "PL")
    league_prem.clubs = all_clubs[:16]
    world.competitions.append(league_prem)

    league_champ = League("Championship", "CH")
    league_champ.clubs = all_clubs[16:32]
    world.competitions.append(league_champ)

    cup = Cup("League Cup", "LC")
    cup.clubs = all_clubs[:32]
    world.competitions.append(cup)

    return world


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


def app_main():

    try:
        # New Game / Load Game Menu
        create_or_load = "create"  # For now, always create new game
        if create_or_load == "create":
            # Create World
            world = create_world()
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
                    messages.append(f"New Season {world.world_time.year}" + f", completed: {len(world.previous_seasons)}" if world.previous_seasons else "")
                
                elif world.world_time.week == WEEKS_IN_YEAR:
                    # Week 52 - end of season
                    messages.append(f"Season {world.world_time.year} completed! prepare promotion/relegation and new season setup next week.")


                # display messages based on state
                if game_loop_state.state == GameState.Continue:
                    
                    if game_loop_state.view == GameView.MainView:
                        current_fixtures = world_worker.get_current_fixtures()
                        if current_fixtures:
                            messages.append(f"{len(current_fixtures)} fixtures this week")
                        else:
                            next_week, next_fixtures = world_worker.get_next_fixtures()
                            messages.append("No fixtures scheduled this week.")
                            messages.append(f"Next fixtures in Week {next_week} ({len(next_fixtures)} fixtures)" if next_fixtures else "No more fixtures scheduled this season.")

                    elif game_loop_state.view == GameView.LeagueTableView:
                        league = game_loop_state.view_data.get("league", None)
                        if league:
                            ltw = LeagueTableWorker(league, world_worker.results_for_competition(league))
                            messages.append(blank_line)
                            messages.extend([f" {line} ".ljust(line_length, " ") for line in ltw.table_text()])     

                    elif game_loop_state.view == GameView.ClubsView:
                        clubs_in_list = 15
                        all_clubs = world_worker.world.club_pool.get_all_clubs()
                        all_clubs =[str(c.name).ljust(25) for c in all_clubs]
                        club_lists = [all_clubs[i:i+20] for i in range(0, len(all_clubs), clubs_in_list)]
                        max_size = max([len(l) for l in club_lists])

                        for i in range(0, max_size):
                            text = []
                            for l in club_lists:
                                try:
                                    name = l[i]
                                    text.append(name)
                                except IndexError:
                                    pass             
                            messages.append(" ".join(text))               

                elif game_loop_state.state == GameState.Current_Fixtures:
                    if game_loop_state.current_fixtures:
                        messages.append(f"Fixtures for Week {world.world_time.week}: {len(game_loop_state.current_fixtures)}")  
                        messages.extend([f" {fixture} ".center(line_length, " ") for fixture in game_loop_state.current_fixtures])

                elif game_loop_state.state == GameState.Processing_Results:
                    if game_loop_state.current_fixtures:
                        messages.append(f"Processing {len(game_loop_state.current_fixtures)} fixtures...")

                elif game_loop_state.state == GameState.Display_Results:
                    if game_loop_state.current_results:
                        messages.append(f"Results for Week {world.world_time.week}: {len(game_loop_state.current_results)}")
                        messages.extend([f" {result} ".center(line_length, " ") for result in game_loop_state.current_results])
                else:
                    messages.append(f"Unknown game state: {game_loop_state.state}")

                # display
                title_lines = [
                    " Fitba Manager ".center(line_length, "="),
                    f" {world.world_time} ".replace("Year", "Season").center(line_length, " "),
                    seperator,
                    blank_line
                ]

                lines = list(title_lines)
                messages = messages[-max_lines:]

                lines.extend([f" {message} ".ljust(line_length, " ") for message in messages])
                lines.extend([blank_line for _ in range(max_lines - len(messages))])
                
                info_line = f" #Clubs: {world.club_pool.count}, #Comps: {len(world.competitions)}" \
                    f", #Fixtures: {world.current_season.fixture_calendar.count}, #Results: {world.current_season.match_results.count} "
                lines.extend([blank_line, seperator, info_line.ljust(line_length, " "), seperator])

                print("\n".join(lines))

                # update
                last_week = world.world_time.week

                # get user input
                user_input = input("Enter command (q to quit, Enter for next week): ").strip().lower()
                if user_input == "q":
                    print("Exiting game. Goodbye!")
                    keep_running = False
                    continue
                else:
                    
                    # State machine transitions
                    if game_loop_state.state == GameState.Continue:
                        if game_loop_state.view == GameView.MainView:
                            if user_input == "t":
                                leagues = [comp for comp in world.competitions if comp.type == CompetitionType.LEAGUE]
                                league = leagues[0] if leagues else None

                                game_loop_state.view = GameView.LeagueTableView
                                game_loop_state.view_data = {"league": league}

                            elif user_input == "c":
                                game_loop_state.view = GameView.ClubsView
                                game_loop_state.view_data = None

                            elif user_input == "":
                                current_week_fixtures = world_worker.get_current_fixtures()
                                if current_week_fixtures:
                                    game_loop_state.state = GameState.Current_Fixtures
                                    game_loop_state.current_fixtures = current_week_fixtures
                                else:
                                    game_loop_state.reset()
                                    world.world_time.advance_week()
                            

                        elif game_loop_state.view == GameView.LeagueTableView:
                            try:
                                index = int(user_input)
                                leagues = [comp for comp in world.competitions if comp.type == CompetitionType.LEAGUE]
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
                            results = world_worker.process_fixtures(game_loop_state.current_fixtures, world.world_time.week)
                            game_loop_state.current_results = results
                            game_loop_state.state = GameState.Display_Results
                        else:
                            game_loop_state.reset()

                    elif game_loop_state.state == GameState.Display_Results:
                        game_loop_state.reset()

                    else:
                        input("Unknown command. Please try again. Press Enter to continue...")

            except KeyboardInterrupt:
                print("\nExiting game. Goodbye!")
                keep_running = False

    except Exception as e:
        print(f"An error occurred: {e}")
        print(format_exc())




if __name__ == "__main__":
    app_main()
