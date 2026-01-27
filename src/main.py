from dataclasses import dataclass
from enum import Enum, auto, unique
from os import system, name
from pyexpat.errors import messages
from random import choices, shuffle
from traceback import format_exc
from typing import Optional, List, Dict


from core.club import Club, ClubFactory, ClubPool
from core.competition import CompetitionType, Competition, Friendly, League, Cup

WEEKS_IN_YEAR = 52

def clear_console():
    """
    Clears the console screen (OS agnostic).
    """
    system("cls" if name == "nt" else "clear")


# class MatchFixture:
#     def __init__(
#         self, club1: Club, club2: Club, competition: Competition, round_num: int = 0
#     ):
#         self.club1 = club1
#         self.club2 = club2
#         self.competition = competition
#         self.round_num = round_num

#     def __str__(self):
#         text = f"{self.club1.name} vs {self.club2.name} in {self.competition.name}"
#         if self.round_num > 0:
#             text += f" (Round {self.round_num})"
#         return text
    

# class MatchResult(MatchFixture):


# class CalendarWeek:
#     def __init__(self, week_num: int, year: int):
#         self.week_num = week_num
#         self.year = year
#         self.fixtures = []

#     def __str__(self):
#         return f"Week {self.week_num} of {self.year}, #Fixtures: {len(self.fixtures)}"


# class FixtureCalendar:
#     def __init__(self, year: int):
#         self.year = year
#         self.weeks = [CalendarWeek(i + 1, year) for i in range(52)]


# @unique
# class LeagueSesson(Enum):
#     Winter = auto()
#     Spring = auto()
#     Summer = auto()
#     Autumn = auto()


# class Season:
#     def __init__(self, year: int, leagues=None, cups=None):
#         self.year = year
#         self.leagues = leagues or []
#         self.cups = cups or []
#         self.fixture_calendar = FixtureCalendar(year)

#     def __str__(self):
#         return (
#             f"Season: {self.year}, Leagues: {len(self.leagues)}, Cups: {len(self.cups)}"
#         )


# def create_league_fixtures(league: League, reverse_fixtures: bool = False):
#     fixtures = []
#     num_rounds = league.club_count - 1
#     club_list = list(league.clubs)
#     shuffle(club_list)

#     if len(club_list) % 2 != 0:
#         club_list.append(None)  # Add a dummy club for bye

#     half_size = len(club_list) // 2

#     # Generate fixtures using the round-robin algorithm
#     for round_num in range(num_rounds):
#         round_fixtures = []
#         for i in range(half_size):
#             club1 = club_list[i]
#             club2 = club_list[(half_size + i)]
#             if club1 is not None and club2 is not None:
#                 fixture = MatchFixture(club1, club2, league, round_num + 1)
#                 round_fixtures.append(fixture)

#         fixtures.append(round_fixtures)
#         club_list.append(club_list.pop(1))
#     return fixtures



# def create_world():
#     clubs = ClubFactory.create_clubs(12)
#     club_pool = ClubPool()
#     for club in clubs:
#         club_pool.add_club(club)

#     league = League("Premier League")
#     league.clubs = club_pool.get_all_clubs()

#     season = Season(2024, leagues=[league])

#     league_season = LeagueSesson.Winter
#     season_offsets = {
#         LeagueSesson.Winter: 0,
#         LeagueSesson.Spring: 13,
#         LeagueSesson.Summer: 26,
#         LeagueSesson.Autumn: 39,
#     }
#     for league_season, offset in season_offsets.items():
#         fixtures = create_league_fixtures(league)
#         for round_num, round_fixtures in enumerate(fixtures):
#             week_num = offset + round_num + 1
#             week = season.fixture_calendar.weeks[week_num]
#             week.fixtures.extend(round_fixtures)
#         break



# def world_sandbox():

#     club_pool = ClubPool()
#     for club in ClubFactory.create_clubs(12):
#         club_pool.add_club(club)

#     all_clubs = club_pool.get_all_clubs()

#     friendly = Friendly("Charity Match")
#     friendly.clubs = choices(all_clubs, k=2)
#     print(friendly)

#     fixture = MatchFixture(
#         friendly.clubs[0], friendly.clubs[1], friendly
#     )
#     print(fixture)



# def mainold():
    # club = Club("Celtic")
    # clubs = ClubFactory.create_clubs(12)
    # print(club)
    # for club in clubs:
    #     print(club)

    # league = League("Premier League")
    # league.clubs = clubs

    # print(league)

    # season = Season(2024, leagues=[league])
    # print(season)

    # league_season = LeagueSesson.Winter
    # season_offsets = {
    #     LeagueSesson.Winter: 0,
    #     LeagueSesson.Spring: 13,
    #     LeagueSesson.Summer: 26,
    #     LeagueSesson.Autumn: 39,
    # }
    # for league_season, offset in season_offsets.items():
    #     fixtures = create_league_fixtures(league)
    #     for round_num, round_fixtures in enumerate(fixtures):
    #         week_num = offset + round_num + 1
    #         week = season.fixture_calendar.weeks[week_num]
    #         week.fixtures.extend(round_fixtures)
    #     break

    # current_week = 1
    # while current_week <= 52:
    #     current_fixtures = season.fixture_calendar.weeks[current_week - 1].fixtures
    #     print(f"Fixtures for Week {current_week}: {len(current_fixtures)}")
    #     if not current_fixtures:
    #         current_week += 1
    #     else:
    #         break

    # for week in season.fixture_calendar.weeks[:26]:
    #     print(week)
    # fixtures = create_league_fixtures(league)
    # for round_num, round_fixtures in enumerate(fixtures):
    #     print(f"Fixtures for Round {round_num + 1}:")
    #     for fixture in round_fixtures:
    #         print(f"  {fixture}")



league_30_fixtures = [8, 9, 10, 11, 12, 14, 15, 16, 17, 18, 21, 22, 23, 24, 25, 28, 29, 30, 31, 32, 35, 36, 37, 38, 39, 42, 43, 44, 45, 46]





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


@dataclass(frozen=True)
class Fixture:
    club1: Club
    club2: Club
    competition: Competition
    round_num: int = 0
    
    def competition_text(self):
        competition_str = f"{self.competition.shortname}"
        if self.round_num > 0:
            competition_str += f" Rnd {self.round_num}"
        return competition_str

    def __str__(self):
        return f"{self.competition_text()} {self.club1.name.rjust(16)} vs {self.club2.name.ljust(16)}"


@dataclass(frozen=True)
class Result(Fixture):
    home_score: int = 0
    away_score: int = 0

    def __str__(self):
        return f"{self.competition_text()} {self.club1.name.rjust(16)} {self.home_score} - {self.away_score} {self.club2.name.ljust(16)}"


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

                # num_round = len(league_fixtures)
                # half_way = (num_round // 2)
                # start_week = 4
                for round_num, round_fixtures in enumerate(league_fixtures):
                    # fixture_week = start_week + round_num
                    # if (round_num + 1) > half_way: 
                    #      fixture_week += 2  # Skip 2 weeks at mid-season
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
    
    
class LeagueTableEntry:
    def __init__(self, club: Club):
        self.club = club
        self.played = 0
        self.won = 0
        self.drawn = 0
        self.lost = 0
        self.goals_for = 0
        self.goals_against = 0
        self.points = 0

    def record_result(self, goals_for: int, goals_against: int):
        self.played += 1
        self.goals_for += goals_for
        self.goals_against += goals_against

        if goals_for > goals_against:
            self.won += 1
            self.points += 3
        elif goals_for == goals_against:
            self.drawn += 1
            self.points += 1
        else:
            self.lost += 1

    def line_text(self):
        parts = [
            self.club.name[:24].rjust(24),
            f"{self.played:3d}",
            f"{self.won:3d}",
            f"{self.drawn:3d}",
            f"{self.lost:3d}",
            f"{self.goals_for:3d}",
            f"{self.goals_against:3d}",
            f"{self.points:3d}"
        ]
        return "| " + " | ".join(parts) + " |"


class LeagueTableWorker:
    def __init__(self, competition: League, results: List[Result]):
        self.competition = competition
        self.results = results
        self.table_entries: Dict[Club, LeagueTableEntry] = {}

        for club in competition.clubs:
            self.table_entries[club] = LeagueTableEntry(club)

        self._process_results()

    def _process_results(self):
        for result in self.results:
            entry_home = self.table_entries[result.club1]
            entry_away = self.table_entries[result.club2]

            entry_home.record_result(result.home_score, result.away_score)
            entry_away.record_result(result.away_score, result.home_score)

    def get_sorted_table(self):
        return sorted(
            self.table_entries.values(),
            key=lambda entry: (entry.points, entry.goals_for - entry.goals_against, entry.goals_for),
            reverse=True
        )
    
    def table_text(self):
        columns = ["-" * 24, "---", "---", "---", "---", "---", "---", "---"]
        separator = "|-" + "-|-".join(columns) + "-|"
        top_line = separator.replace("|", "-")


        titles = ["Club".rjust(24), "Ply", " W ", " D ", " L ", " GF", " GA", "Pts"]
        lines = [top_line, "| " + " | ".join(titles) + " |", separator]
        lines.extend([entry.line_text() for entry in self.get_sorted_table()])
        lines.append(top_line)
        return lines
    

def app_main():

    try:
        # New Game / Load Game Menu

        # Create or Load Game

        world = World(WorldTime(1, 1))
        for club in ClubFactory.create_clubs(40):
            world.club_pool.add_club(club)

        all_clubs = world.club_pool.get_all_clubs()
        shuffle(all_clubs)

        league_prem = League("Premier League", "PL")
        league_prem.clubs = all_clubs[:16]
        world.competitions.append(league_prem)

        # league_champ = League("Championship", "CH")
        # league_champ.clubs = all_clubs[16:32]
        # world.competitions.append(league_champ)

        # UI Constants
        line_length = 80
        max_lines = 20
        seperator, blank_line = "=" * line_length, " " * line_length
        
        # User Input Loop
        keep_running = True
        world_worker = WorldWorker(world)
        while keep_running:

            try:
                # clear
                clear_console()

                messages = []

                # process
                if world.world_time.week == 1:
                    world_worker.create_new_season()
                    messages.append(f"New Season {world.world_time.year}" + f", completed: {len(world.previous_seasons)}" if world.previous_seasons else "")

                # fixtures
                current_week_fixtures = world_worker.get_current_fixtures()
                if current_week_fixtures:
                    messages.append(f"Fixtures for Week {world.world_time.week}: {len(current_week_fixtures)}")
                    messages.extend([f" {fixture} ".center(line_length, " ") for fixture in current_week_fixtures])

                
                # results
                if current_week_fixtures:
                    results = world_worker.process_fixtures(current_week_fixtures, world.world_time.week)
                    messages.append(f"Results for Week {world.world_time.week}: {len(results)}")
                    messages.extend([f" {result} ".center(line_length, " ") for result in results])
                   
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

                # get user input
                user_input = input("Enter command (q to quit, Enter for next week): ").strip().lower()
                if user_input == "q":
                    print("Exiting game. Goodbye!")
                    keep_running = False
                    continue
                elif user_input == "t":
                    clear_console()
                    lines = list(title_lines)

                    leagues = [comp for comp in world.competitions if comp.type == CompetitionType.LEAGUE]
                    league = leagues[0] if leagues else None
                    if league:
                        ltw = LeagueTableWorker(league, world_worker.results_for_competition(league))
                        lines.append(blank_line)
                        lines.extend([f" {line} ".ljust(line_length, " ") for line in ltw.table_text()])
                    
                    print("\n".join(lines))
                    user_input = input(">").strip().lower()
                    continue

                elif user_input == "":
                    world.world_time.advance_week()

                else:
                    print("Unknown command. Please try again.")
                    input("Press Enter to continue...")

            except KeyboardInterrupt:
                print("\nExiting game. Goodbye!")
                keep_running = False

    except Exception as e:
        print(f"An error occurred: {e}")
        print(format_exc())




if __name__ == "__main__":
    app_main()
