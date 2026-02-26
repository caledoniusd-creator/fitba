from __future__ import annotations
from random import shuffle, randint
from typing import List


from src.core.world_time import WEEKS_IN_YEAR

from src.core.db.models import (
    SeasonDB,
    ClubDB,
    LeagueDB,
)



def contract_expiry():
    return WEEKS_IN_YEAR * randint(1, 4)


league_30_fixtures = [
    6, 7, 8, 10, 11, 12, 14, 15,16, 18, 19, 20, 22, 23, 24,
    27, 28, 29, 31, 32, 33, 35, 36, 37, 39, 40, 41, 43, 44, 45,
]


def create_league_fixtures(clubs: List, reverse_fixtures: bool = False):
    club_count = len(clubs)
    fixtures = []
    num_rounds = club_count - 1
    club_list = list(clubs)
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
                fixture = (round_num + 1, club1, club2)
                round_fixtures.append(fixture)

        fixtures.append(round_fixtures)
        club_list.append(club_list.pop(1))

    if reverse_fixtures:
        reverse_rounds = []
        for round_fixtures in fixtures:
            reverse_round = []
            for fixture in round_fixtures:
                reverse_fixture = (
                    fixture[0] + num_rounds,
                    fixture[2],
                    fixture[1],
                )
                reverse_round.append(reverse_fixture)
            reverse_rounds.append(reverse_round)
        fixtures.extend(reverse_rounds)
    return fixtures


def create_league_table_data(club: ClubDB, results: List):
    data = {
        "club": club,
        "ply": 0,
        "w": 0,
        "d": 0,
        "l": 0,
        "gf": 0,
        "ga": 0,
        "gd": 0,
        "pts": 0,
    }

    for result in results:
        fixture = result.fixture
        if fixture.home_club_id == club.id:
            home = True
        elif fixture.away_club_id == club.id:
            home = False
        else:
            raise RuntimeError(f"{club.name} not in fixture: {fixture}")

        data["ply"] += 1

        if result.home_score == result.away_score:
            data["d"] += 1
            data["gf"] += result.home_score
            data["ga"] += result.away_score
        else:
            if result.home_score > result.away_score:
                if home:
                    data["w"] += 1
                else:
                    data["l"] += 1
            else:
                if home:
                    data["l"] += 1
                else:
                    data["w"] += 1
            data["gf"] += result.home_score
            data["ga"] += result.away_score

    data["gd"] = data["gf"] - data["ga"]
    data["pts"] = (data["w"] * 3) + data["d"]
    return data


def get_league_table_data(league: LeagueDB, current_season: SeasonDB):
    clubs = league.get_clubs_for_season(season=current_season)
    league_data = list()
    for club in clubs:
        results = club.results(competition=league, season=current_season)
        league_data.append(create_league_table_data(club, results))

    league_data.sort(key=lambda d: (-d["pts"], -d["gf"], -d["gd"], d["club"].name))
    return league_data