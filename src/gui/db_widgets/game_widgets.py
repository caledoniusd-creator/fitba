from PySide6.QtCore import Qt
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


from .generic_widgets import TitleLabel
from .league_views import LeagueView


class DateLabel(TitleLabel):
    def __init__(self, title=None, size=12, parent=None):
        super().__init__(title, size, parent)

    def set_date(self, season, week):
        if season is None:
            season = "Invalid Season"
        if week is None:
            week = "Invalid Week"
        self.setText(f"{season}: {week}")


class ContinueBtn(QPushButton):
    def __init__(self, parent=None):
        super().__init__("Continue")
        self.setFont(QFont("DejaVu Sans", 14, QFont.Bold))


class TwinLeagueView(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)        
        self._league_1 = LeagueView()
        self._league_2 = LeagueView()
        leagues_layout = QHBoxLayout(self)
        leagues_layout.addWidget(self._league_1)
        leagues_layout.addWidget(self._league_2)

    def clear(self):
        for v in [self._league_1, self._league_2]:
            v.clear()

    def update_leagues(self, league_1, league_2, season):
        views = [self._league_1, self._league_2]
        for v in views:
            v.clear()

        for lg, v in zip([league_1, league_2], views):
            v.set_league(lg, season)
