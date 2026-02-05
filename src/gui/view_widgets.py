from typing import List

from PySide6.QtCore import Qt
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *



from core.world_time import WorldTime
from core.club import Club
from core.competition import League
from core.fixture import Fixture, Result


from .utils import change_font
from .generic_widgets import WidgetList


class WorldTimeLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        change_font(self, 8, True)
        # self.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        # self.setAutoFillBackground(True)
        # self.setContentsMargins(QMargins(16, 8, 16, 8))

    def set_time(self, time: WorldTime | None):
        if time is not None:
            text = f"Season {time.year} Week {time.week}"
        else:
            text = "N/A"
        self.setText(text)


class FixtureLabel(QFrame):
    def __init__(self, fixture: Fixture, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        change_font(self, 4)

        palette = QPalette(self.palette())
        palette.setColor(QPalette.ColorRole.Window, QColor(255, 255, 255))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        comp_label = QLabel(fixture.competition.shortname)
        comp_label.setAlignment(
            Qt.AlignLeft | Qt.AlignVCenter
        )
        comp_label.setFixedWidth(96)
        change_font(comp_label, 2, True)

        home_team = QLabel(fixture.club1.name)
        home_team.setAlignment(
            Qt.AlignRight | Qt.AlignVCenter
        )
        home_team.setFixedWidth(255)

        self.vs_label = QLabel("v")
        self.vs_label.setAlignment(Qt.AlignCenter)
        self.vs_label.setFixedWidth(128)
        change_font(self.vs_label, 2, True)

        away_team = QLabel(fixture.club2.name)
        away_team.setAlignment(
            Qt.AlignLeft | Qt.AlignVCenter
        )
        away_team.setFixedWidth(255)

        layout = QHBoxLayout(self)
        layout.addStretch(10)
        layout.addWidget(
            comp_label, 0, Qt.AlignLeft | Qt.AlignVCenter
        )
        layout.addWidget(
            home_team, 0, Qt.AlignLeft | Qt.AlignVCenter
        )
        layout.addWidget(
            self.vs_label, 0, Qt.AlignLeft | Qt.AlignVCenter
        )
        layout.addWidget(
            away_team, 0, Qt.AlignLeft | Qt.AlignVCenter
        )
        layout.addStretch(10)


class ResultLabel(FixtureLabel):
    def __init__(self, result: Result, parent=None):
        super().__init__(result, parent)
        self.vs_label.setText(f" {result.home_score} - {result.away_score} ")


class FixtureList(WidgetList):
    def __init__(self, title: str = "Fixtures", auto_hide: bool = False, parent=None):
        super().__init__(title=title, auto_hide=auto_hide, parent=parent)

    def set_fixtures(self, fixtures: List[Fixture] = []):
        self.set_widgets([FixtureLabel(f) for f in fixtures])


class ResultsList(WidgetList):
    def __init__(self, title: str = "Results", auto_hide: bool = False, parent=None):
        super().__init__(title=title, auto_hide=auto_hide, parent=parent)

    def set_results(self, results: List[Result] = []):
        self.set_widgets([ResultLabel(r) for r in results])


class LeagueTableWidget(QFrame):
    def __init__(self, competition: League, table_data: List, parent=None):
        super().__init__(parent)
        change_font(self, 4)
        self.setFrameStyle(QFrame.Box | QFrame.Plain)
        table_layout = QGridLayout()
        table_layout.setHorizontalSpacing(16)

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

        def title_label(text: str):
            lbl = QLabel(text)
            lbl.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            change_font(lbl, 4, True)
            return lbl

        row_ix = 0

        headers = [
            ("Ply", played),
            ("W", won),
            ("D", draw),
            ("L", loss),
            ("GF", gf),
            ("GA", ga),
            ("GD", gd),
            ("Pts", points),
        ]
        for header in headers:
            table_layout.addWidget(
                title_label(header[0]),
                row_ix,
                header[1],
                Qt.AlignLeft | Qt.AlignVCenter,
            )

        for ix, row in enumerate(table_data):
            club_lbl = QLabel(row.club.name)
            club_lbl.setAlignment(
                Qt.AlignRight | Qt.AlignVCenter
            )
            club_lbl.setFixedWidth(255)
            row_ix += 1
            table_layout.addWidget(
                title_label(str(ix + 1)),
                row_ix,
                num_col,
                Qt.AlignLeft | Qt.AlignVCenter,
            )
            table_layout.addWidget(
                club_lbl,
                row_ix,
                club_col,
                Qt.AlignRight | Qt.AlignVCenter,
            )

            row_items = [
                (row.played, played),
                (row.won, won),
                (row.drawn, draw),
                (row.lost, loss),
                (row.goals_for, gf),
                (row.goals_against, ga),
                (row.goal_diff, gd),
                (row.points, points),
            ]
            for item in row_items:
                table_layout.addWidget(
                    QLabel(str(item[0])),
                    row_ix,
                    item[1],
                    Qt.AlignCenter,
                )

        row_ix += 1
        table_layout.setRowStretch(row_ix, 100)
        table_layout.setColumnStretch(left_edge, 100)
        table_layout.setColumnStretch(right_edge, 100)

        league_title_label = QLabel(competition.name)
        league_title_label.setAlignment(
            Qt.AlignHCenter | Qt.AlignTop
        )
        change_font(league_title_label, 2, True)

        layout = QVBoxLayout(self)
        layout.addWidget(
            league_title_label,
            0,
            Qt.AlignHCenter | Qt.AlignTop,
        )
        layout.addLayout(table_layout)


class ClubsTableListWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.Box | QFrame.Plain)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self._num_cols = 4
        self._widgets = []
        self._widgets_layout = QGridLayout(self)
        self._widgets_layout.setColumnStretch(0, 100)
        self._widgets_layout.setColumnStretch(self._num_cols + 1, 100)
        self.update_visibility()

    def clear_widgets(self):
        for w in self._widgets:
            self._widgets_layout.removeWidget(w)
            w.deleteLater()
        self._widgets.clear()

    def set_clubs(self, clubs: List[Club] | None = None):
        self.clear_widgets()

        if clubs:
            for ix, club in enumerate(clubs):
                row, col = ix // self._num_cols, (ix % self._num_cols) + 1

                lbl = QLabel(club.name)
                lbl.setAlignment(
                    Qt.AlignLeft | Qt.AlignVCenter
                )
                change_font(lbl, 4, True)

                self._widgets_layout.addWidget(
                    lbl,
                    row,
                    col,
                    Qt.AlignLeft | Qt.AlignVCenter,
                )
                self._widgets.append(lbl)
        self.update_visibility()

    @property
    def has_widgets(self):
        return True if self._widgets else False

    def update_visibility(self):
        self.setVisible(True if self.has_widgets else False)


class ClubListView(QTreeWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.update_visibility()

    def set_clubs(self, clubs: List[Club] | None = None):
        self.clear()

        if clubs:
            self.setHeaderLabels(["Club", "Squard Rating"])

            for club in clubs:
                item = QTreeWidgetItem()
                item.setText(0, club.name)
                item.setText(1, str(club.squad.rating))
                self.addTopLevelItem(item)

            for i in range(self.columnCount()):
                self.resizeColumnToContents(i)

        self.update_visibility()

    @property
    def has_indexes(self):
        count = self.topLevelItemCount()
        return True if count > 0 else False

    def update_visibility(self):
        self.setVisible(True if self.has_indexes else False)
