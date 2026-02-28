from PySide6.QtCore import Qt
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


from src.gui.db_widgets.generic_widgets import TitleLabel

label_height = 24

class ClubNameLabel(QLabel):    
    def __init__(self, name, max_width: int, alignment: Qt.AlignmentFlag = Qt.AlignLeft):
        super().__init__(name)
        self.setAlignment(alignment | Qt.AlignVCenter)
        self.setFont(QFont("DejaVu Sans", 12, QFont.Bold))
        self.setFixedSize(QSize(max_width, label_height))


class ScoreVersusLabel(QLabel):
    def __init__(self, result, max_width: int):
        super().__init__("v" if result is None else f"{result.home_score} - {result.away_score}")
        self.setAlignment(Qt.AlignCenter)
        self.setFont(QFont("Consolas", 12))
        self.setFixedSize(QSize(max_width, label_height))


class CompetitionLabel(QLabel):
    def __init__(self, competition, comp_round, max_width: int):

        text = f"{competition.short_name} ({comp_round})"
        super().__init__(text)
        self.setAlignment(Qt.AlignCenter)
        self.setFont(QFont("Consolas", 10))
        self.setFixedSize(QSize(max_width, label_height))


class FixtureResultRow(QFrame):
    def __init__(self, fixture, parent=None):
        super().__init__(parent=parent)
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        comp = CompetitionLabel(fixture.competition, fixture.competition_round, 64)
        home = ClubNameLabel(fixture.home_club.name, 228, Qt.AlignRight)
        vs = ScoreVersusLabel(fixture.result, 64)
        away = ClubNameLabel(fixture.away_club.name, 228, Qt.AlignLeft)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(QMargins(2, 2, 2, 2))
        layout.addStretch(10)
        layout.addWidget(comp, 0, Qt.AlignLeft | Qt.AlignVCenter)
        layout.addWidget(home, 0, Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(vs, 0, Qt.AlignCenter)
        layout.addWidget(away, 0, Qt.AlignLeft | Qt.AlignVCenter)
        layout.addStretch(10)


class FixtureResultList(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self._title = TitleLabel("Fixtures/Results", 14)

        self._widgets = list()
        self._widgets_layout = QVBoxLayout()

        layout = QVBoxLayout(self)
        layout.addWidget(self._title, 0, Qt.AlignHCenter | Qt.AlignTop)
        layout.addLayout(self._widgets_layout, 10)
        layout.addStretch(10)

    def set_fixtures(self, fixtures):
        
        for w in self._widgets:
            self._widgets_layout.removeWidget(w)
            w.deleteLater()

        self._widgets.clear()
        results_count = 0
        fixture_count = 0
        for f in fixtures:
            w = FixtureResultRow(f)
            self._widgets.append(w)
            self._widgets_layout.addWidget(w, 0, Qt.AlignCenter)
            if f.result != None:
                results_count += 1
            else:
                fixture_count += 1

        if results_count != 0 and fixture_count != 0:
            self._title.setText("Fixtures/Results")
        elif results_count == 0:
            self._title.setText("Fixtures")
        elif fixture_count == 0:
            self._title.setText("Results")
        else:
            self._title.setText("Fixtures/Results")

