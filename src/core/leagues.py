from random import shuffle

from .competition import League
from .fixture import Fixture


league_30_fixtures = [
    8,
    9,
    10,
    11,
    12,
    14,
    15,
    16,
    17,
    18,
    21,
    22,
    23,
    24,
    25,
    28,
    29,
    30,
    31,
    32,
    35,
    36,
    37,
    38,
    39,
    42,
    43,
    44,
    45,
    46,
]
cup_32_fixtures = [19, 26, 33, 40, 48]


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
                    fixture.club2,
                    fixture.club1,
                    fixture.competition,
                    fixture.round_num + num_rounds,
                )
                reverse_round.append(reverse_fixture)
            reverse_rounds.append(reverse_round)
        fixtures.extend(reverse_rounds)
    return fixtures


