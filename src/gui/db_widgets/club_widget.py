from PySide6.QtCore import Qt
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from src.core.db.models import SeasonDB

from .generic_widgets import TitleLabel, GeneralGamePage
from .object_views import StaffTreeWidget, PlayerTreeWidget, CompetitionListWidget

from .game_engine_object import GameEngineObject

class ClubWidget(GeneralGamePage):
    DEFAULT_TITLE = "No club selected"

    def __init__(self, game_engine: GameEngineObject, parent=None):
        super().__init__(game_engine=game_engine, parent=parent)
        self._club_id = None
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
        self.update_data()

    @property
    def club_id(self):
        return self._club_id

    @club_id.setter
    def club_id(self, club_id):
        if self._club_id != club_id:
            self._club_id = club_id
            self.update_data()
    
    def update_data(self):
        if self._club_id is not None:
            club = self.game_engine.db_worker.get_club(self._club_id)
        else:
            club = None
        
        if club is not None:
            season = self.game_engine.world_time[0]
            self._title.setText(f"{club.name} ({club.id})")
            self._staff_list.set_staff(club.staff_members())
            self._player_list.set_players(club.players())
            self._comp_list.set_competitions(club.competitions(season=season))

        else:
            self._title.setText(ClubWidget.DEFAULT_TITLE)
            self._staff_list.clear()
            self._player_list.clear()
            self._comp_list.clear()


