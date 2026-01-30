
from typing import List

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *


from core.world_time import DAYS_IN_WEEK, WEEKS_IN_YEAR, WorldTime
from core.competition import League
from core.fixture import Fixture, Result


from .utils import change_font
from .generic_widgets import WidgetList


class WorldTimeLabel(QLabel):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        change_font(self, 4, True)

    def set_time(self, time: WorldTime | None):
        if time is not None:
            text = f"{time} ".replace("Year", "Season")
        else: 
            text = "N/A"
        self.setText(text)


class FixtureLabel(QFrame):

    def __init__(self, fixture: Fixture, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Plain)

        comp_label = QLabel(fixture.competition.shortname)
        comp_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        comp_label.setFixedWidth(64)
        change_font(comp_label, 0, True)

        home_team  = QLabel(fixture.club1.name)
        home_team.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        home_team.setFixedWidth(128)

        self.vs_label = QLabel("v")
        self.vs_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.vs_label.setFixedWidth(96)
        change_font(self.vs_label, 0, True)

        away_team = QLabel(fixture.club2.name)
        away_team.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        away_team.setFixedWidth(128)

        layout = QHBoxLayout(self)
        layout.addStretch(10)
        layout.addWidget(comp_label, 0, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(home_team, 0, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(self.vs_label, 0, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(away_team, 0, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        layout.addStretch(10)


class ResultLabel(FixtureLabel):
    def __init__(self, result: Result, parent=None):
        super().__init__(result, parent)
        self.vs_label.setText(f" {result.home_score} - {result.away_score} ")


class FixtureList(WidgetList):
    def __init__(self, auto_hide: bool=False, parent=None):
        super().__init__("Fixtures", auto_hide=auto_hide, parent=parent)

    def set_fixtures(self, fixtures: List[Fixture]=[]):
        self.set_widgets([FixtureLabel(f) for f in fixtures])  
        

class ResultsList(WidgetList):
    def __init__(self, auto_hide: bool=False, parent=None):
        super().__init__("Results", auto_hide=auto_hide, parent=parent)

    def set_results(self, results: List[Result]=[]):
        self.set_widgets([ResultLabel(r) for r in results])  

                

class LeagueTableWidget(QFrame):
    def __init__(self, competition: League, table_data: List, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Plain)
        table_layout = QGridLayout()

        change_font(self, 2)

        left_edge = 0
        num_col = 1
        club_col = 2
        played = 3
        won = 4
        draw = 5
        loss = 6
        gf = 7
        ga = 8
        gd = 9
        points = 10
        right_edge = 11 

        def number_label(num: int):
            lbl = QLabel(str(num))
            lbl.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            change_font(lbl, 0, True)
            return lbl
        
        def title_label(text: str):
            lbl = QLabel(text)
            lbl.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            change_font(lbl, 0, True)
            return lbl

        table_layout.addWidget(title_label("Ply"), 0, played, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        table_layout.addWidget(title_label("W"), 0, won, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        table_layout.addWidget(title_label("D"), 0, draw, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        table_layout.addWidget(title_label("L"), 0, loss, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        table_layout.addWidget(title_label("GF"), 0, gf, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        table_layout.addWidget(title_label("GA"), 0, ga, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        table_layout.addWidget(title_label("GD"), 0, gd, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        table_layout.addWidget(title_label("Pts}"), 0, points, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        row_ix = 0
        for ix, row in enumerate(table_data):
            club_lbl = QLabel(row.club.name)
            club_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            row_ix += 1
            table_layout.addWidget(number_label(ix + 1), row_ix, num_col, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            table_layout.addWidget(club_lbl, row_ix, club_col, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            table_layout.addWidget(QLabel(str(row.played)), row_ix, played, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            table_layout.addWidget(QLabel(str(row.won)), row_ix, won, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            table_layout.addWidget(QLabel(str(row.drawn)), row_ix, draw, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            table_layout.addWidget(QLabel(str(row.lost)), row_ix, loss, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            table_layout.addWidget(QLabel(str(row.goals_for)), row_ix, gf, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            table_layout.addWidget(QLabel(str(row.goals_against)), row_ix, ga, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            table_layout.addWidget(QLabel(str(row.goal_diff)), row_ix, gd, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            table_layout.addWidget(QLabel(str(row.points)), row_ix, points, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        row_ix += 1
        table_layout.setRowStretch(row_ix, 100)
        table_layout.setColumnStretch(left_edge, 100)
        table_layout.setColumnStretch(right_edge, 100)

        league_title_label = QLabel(competition.name)
        league_title_label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        change_font(league_title_label, 2, True)

        layout = QVBoxLayout(self)
        layout.addWidget(league_title_label, 0, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        layout.addLayout(table_layout)


