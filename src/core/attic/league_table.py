from typing import List, Dict

from ..club import Club
from .competition import League
from .fixture import Result


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

    @property
    def goal_diff(self):
        return self.goals_for - self.goals_against

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
            f"{self.points:3d}",
        ]
        return "| " + " | ".join(parts) + " |"


class LeagueTableWorker:
    def __init__(self, competition: "League", results: List[Result]):
        self.competition = competition
        self.results = results
        self.table_entries: Dict[Club, LeagueTableEntry] = {}

        for club in competition.clubs:
            self.table_entries[club] = LeagueTableEntry(club)

        self._process_results()

    def _process_results(self):
        if self.results:
            for result in self.results:
                entry_home = self.table_entries[result.club1]
                entry_away = self.table_entries[result.club2]

                entry_home.record_result(result.home_score, result.away_score)
                entry_away.record_result(result.away_score, result.home_score)

    def get_sorted_table(self):
        return sorted(
            self.table_entries.values(),
            key=lambda entry: (
                -entry.points,
                -entry.goal_diff,
                -entry.goals_for,
                entry.club.name,
            ),
            reverse=False,
        )

    def table_text(self):
        if self.results:
            return []

        columns = ["-" * 24, "---", "---", "---", "---", "---", "---", "---"]
        separator = "|-" + "-|-".join(columns) + "-|"
        top_line = separator.replace("|", "-")
        title = f"{self.competition.name}".center(len(top_line), " ")

        titles = ["Club".rjust(24), "Ply", " W ", " D ", " L ", " GF", " GA", "Pts"]
        lines = [title, top_line, "| " + " | ".join(titles) + " |", separator]
        lines.extend([entry.line_text() for entry in self.get_sorted_table()])
        lines.append(top_line)
        return lines
