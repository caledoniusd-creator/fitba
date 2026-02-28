from PySide6.QtCore import Qt
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


from src.core.db.models import SeasonDB, LeagueDB
from src.core.db.league_db_functions import get_league_table_data


from .generic_widgets import TitleLabel


class LeagueView(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)

        self.title = TitleLabel("", 12)
        self.tree_widget = QTreeWidget()
        self.tree_widget.setFont(QFont("DejaVu Sans", 12))

        layout = QVBoxLayout(self)
        layout.addWidget(self.title, 0, Qt.AlignHCenter | Qt.AlignTop)
        layout.addWidget(self.tree_widget, 100)

    def set_league(self, league: LeagueDB, season: SeasonDB):
        self.title.setText(league.name)

        table_data = get_league_table_data(league, season)
        self.tree_widget.clear()
        self.tree_widget.setHeaderLabels(
            ["Pos", "Club", "Ply", "W", "D", "L", "GF", "GA", "GD", "Pts"]
        )
        for ix, d in enumerate(table_data):
            pos = ix + 1
            item = QTreeWidgetItem(
                [
                    str(pos),
                    d["club"].name,
                    str(d["ply"]),
                    str(d["w"]),
                    str(d["d"]),
                    str(d["l"]),
                    str(d["gf"]),
                    str(d["ga"]),
                    str(d["gd"]),
                    str(d["pts"]),
                ]
            )
            self.tree_widget.addTopLevelItem(item)

        for c in range(self.tree_widget.columnCount()):
            self.tree_widget.resizeColumnToContents(c)

    def clear(self):
        self.title.clear()
