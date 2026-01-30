
from typing import List

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *


from core.world_time import DAYS_IN_WEEK, WEEKS_IN_YEAR, WorldTime
from core.fixture import Fixture, Result


from .utils import change_font


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


class WidgetList(QWidget):
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self._widgets = []
        self.widget_layout = QVBoxLayout()

        title_lbl = QLabel(title)
        change_font(title_lbl, 2, True)
        
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(title_lbl, 0, Qt.AlignmentFlag.AlignCenter)
        main_layout.addLayout(self.widget_layout)
        main_layout.addStretch(10)

    @property
    def has_widgets(self):
        return True if self._widgets else False

    def clear_widgets(self):
        for w in self._widgets:
            self.widget_layout.removeWidget(w)
            w.deleteLater()
        self._widgets.clear()

    def set_widgets(self, widgets: List[QWidget]=[]):
        self.clear_widgets()
        for w in widgets:
            self._widgets.append(w)
            self.widget_layout.addWidget(w, 0, Qt.AlignmentFlag.AlignHCenter| Qt.AlignmentFlag.AlignTop)
        self.setVisible(True if self.has_widgets else False)


class FixtureList(WidgetList):
    def __init__(self, parent=None):
        super().__init__("Fixtures", parent)

    def set_fixtures(self, fixtures: List[Fixture]=[]):
        self.set_widgets([FixtureLabel(f) for f in fixtures])  
        

class ResultsList(WidgetList):
    def __init__(self, parent=None):
        super().__init__("Results", parent)

    def set_results(self, results: List[Result]=[]):
        self.set_widgets([ResultLabel(r) for r in results])  

                
