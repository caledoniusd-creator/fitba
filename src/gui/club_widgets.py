

from typing import List

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *


from .utils import change_font, hline

class ClubsListWidget(QListWidget):

    selected_clubs = pyqtSignal(list, name="selected clubs")

    def __init__(self, parent=None):
        super().__init__(parent)
        self.currentItemChanged.connect(self.on_current_club_changed)
        
    def on_current_club_changed(self, current: QModelIndex, previous: QModelIndex):
        club = None
        if current and current.data(Qt.ItemDataRole.UserRole):
            club = current.data(Qt.ItemDataRole.UserRole)
        self.selected_clubs.emit([club])

    def set_clubs(self, clubs: List=[]):
        self.clear()

        def listItem(text: str, payload: any = None):
            item = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, payload)
            return item

        self.addItem(listItem("None"))
        for club in sorted(clubs, key=lambda c: c.name):
            self.addItem(listItem(club.name, club))
        self.setCurrentRow(0)
        self.setEnabled(True if self.count() > 1 else False)


class ClubInfoWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Plain)


        self._club = None

        self._club_title = QLabel()
        self._club_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        change_font(self._club_title, 12, True)

        self._squad_rating = QLabel()
        self._squad_rating.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        change_font(self._squad_rating, 4)

        squad_rating_title = QLabel("Squad Rating")
        change_font(squad_rating_title, 4, True)

        squad_rating_layout = QHBoxLayout()
        squad_rating_layout.addWidget(squad_rating_title)
        squad_rating_layout.addWidget(self._squad_rating, 0)
        squad_rating_layout.addStretch(100)

        def list_group(title, widget):
            t_label = QLabel(title)
            change_font(t_label, 8, True)
            frame = QFrame()
            frame.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
            frame_layout = QVBoxLayout(frame)
            frame_layout.addWidget(t_label, 0, Qt.AlignmentFlag.AlignCenter)
            frame_layout.addWidget(widget, 1000)
            return frame
        
        self._competition_list = QListWidget()
        self._fixtures_list = QListWidget()
        self._results_list = QListWidget()

        info_frame = QFrame()
        info_frame.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        info_frame_layout = QHBoxLayout(info_frame)
        for t, w in zip(["Competitions", "Fixtures", "Results"], [self._competition_list, self._fixtures_list, self._results_list]):
            info_frame_layout.addWidget(list_group(t, w))
        


        layout = QVBoxLayout(self)
        layout.addWidget(self._club_title, 0, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        layout.addWidget(hline())
        layout.addLayout(squad_rating_layout)
        layout.addWidget(info_frame, 10)
        layout.addStretch(100)

    def set_club(self, club):
        if self._club != club:
            self._club = club
            self.invalidate()

    def invalidate(self):
        if self._club:
            self._club_title.setText(self._club.name)
            self._squad_rating.setText(str(self._club.squad.rating))

        else:
            self._club_title.setText("N/A")
            self._squad_rating.setText("-")
            self._competition_list.clear()
            self._fixtures_list.clear()
            self._results_list.clear()