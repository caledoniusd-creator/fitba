from PySide6.QtCore import Qt
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


from .generic_widgets import TitleLabel
from .object_views import StaffTreeWidget, PlayerTreeWidget, CompetitionListWidget


class ClubWidget(QWidget):
    DEFAULT_TITLE = "No club selected"

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._club = None
        self.setAutoFillBackground(True)

        self._title = TitleLabel(ClubWidget.DEFAULT_TITLE)

        self._staff_list = StaffTreeWidget()
        self._player_list = PlayerTreeWidget()
        self._comp_list = CompetitionListWidget()

        person_frame = QFrame()
        person_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)

        left_layout = QVBoxLayout()
        left_layout.addWidget(self._staff_list)
        left_layout.addWidget(self._comp_list)

        person_layout = QHBoxLayout(person_frame)
        person_layout.addLayout(left_layout)
        person_layout.addWidget(self._player_list)

        layout = QVBoxLayout(self)
        layout.addWidget(self._title, 0, Qt.AlignTop | Qt.AlignHCenter)
        layout.addWidget(person_frame, 100)

        self.invalidate()

    @property
    def club(self):
        return self._club

    @club.setter
    def club(self, club):
        self._club = club
        self.invalidate()

    def invalidate(self):
        if self._club is not None:
            self._title.setText(f"{self._club.name} ({self._club.id})")
            self._staff_list.set_staff(self._club.staff_members())
            self._player_list.set_players(self._club.players())
            self._comp_list.set_competitions(self._club.competitions())

        else:
            self._title.setText(ClubWidget.DEFAULT_TITLE)
            self._staff_list.clear()
            self._player_list.clear()
            self._comp_list.clear()
