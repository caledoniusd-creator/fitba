from PySide6.QtCore import Qt
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from src.core.game_types import (
    StaffRole,
    Position
)

from src.gui.utils import hline

from src.core.db.models import SeasonDB
from src.core.workers.club_worker import ClubWorker, ClubAnalysisWorker

from .generic_widgets import TitleLabel, GeneralGamePage
from .object_views import StaffTreeWidget, PlayerTreeWidget, CompetitionListWidget

from .game_engine_object import GameEngineObject


class SimpleTeamWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        self.setContentsMargins(QMargins(4, 4, 4, 4))
        self._formation = TitleLabel("", size=14)
        self._layout_widgets = []
  

        positions = [p for p in Position]
        for p in positions[::-1]:
            row_layout = QHBoxLayout()
            row_layout.setSpacing(48)
            row_layout.setContentsMargins(QMargins(8, 4, 8, 4))
            self._layout_widgets.append((p, row_layout, []))

        layout = QVBoxLayout(self)
        for lw in self._layout_widgets:
            layout.addLayout(lw[1]) 

        layout.addWidget(hline())
        layout.addWidget(self._formation, 0, Qt.AlignHCenter | Qt.AlignBottom)

    def clear(self):
        self._formation.clear()
        for lw in self._layout_widgets:
            for w in lw[2]:
                lw[1].removeWidget(w)
                w.deleteLater()
            lw[2].clear()

    def set_team(self, formation, team):
        self.clear()
        self._formation.setText(str(formation))

        layout = None
        widgets = None
        font = QFont("DejaVu Sans", 12)
        for row in team[0]:
            row_pos = row[0]
            for lw in self._layout_widgets:
                if lw[0] == row_pos:
                    layout = lw[1]
                    widgets = lw[2]
            if layout is None or widgets is None:
                raise RuntimeError("No Layout or widgets")
            
            for p in row[1]:
                lbl = QLabel(f"<b>{row_pos.short_name}</b><br>{p.person.short_name}")
                lbl.setFont(font)
                lbl.setAlignment(Qt.AlignCenter)

                layout.addWidget(lbl, 1, Qt.AlignCenter)
                widgets.append(lbl)


class ClubWidget(GeneralGamePage):
    DEFAULT_TITLE = "No club selected"

    def __init__(self, game_engine: GameEngineObject, parent=None):
        super().__init__(game_engine=game_engine, parent=parent)
        self._club_id = 0
        self._club_worker = None
        self.setAutoFillBackground(True)

        self._title = TitleLabel(ClubWidget.DEFAULT_TITLE)

        self._staff_list = StaffTreeWidget()
        self._player_list = PlayerTreeWidget()
        self._comp_list = CompetitionListWidget()

        self._sqaud_remarks = QLabel()
        self._sqaud_remarks.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        font = QFont("Consolas", 12)
        self._sqaud_remarks.setFont(font)
        self._team_sheet = SimpleTeamWidget()

        person_frame = QFrame()
        person_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)

        left_layout = QVBoxLayout()
        left_layout.addWidget(self._staff_list)
        left_layout.addWidget(self._comp_list)

        sqaud_layout = QVBoxLayout()
        sqaud_layout.addWidget(self._player_list, 2)

        remark_layout = QVBoxLayout()

        remark_layout.addWidget(self._sqaud_remarks, 1, Qt.AlignLeft | Qt.AlignTop)
        remark_layout.addWidget(self._team_sheet, 1, Qt.AlignCenter)
        sqaud_layout.addLayout(remark_layout, 1)

        person_layout = QHBoxLayout(person_frame)
        person_layout.addLayout(left_layout)
        person_layout.addLayout(sqaud_layout)

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
            # self.update_data()
    
    def _get_club(self):
        if self.game_engine.db_worker is None:
            club = None
        else:
            club = self.game_engine.db_worker.get_club(self._club_id)

            if self._club_worker is None:
                self._club_worker = ClubWorker(self._club_id, self.game_engine.db_worker)
            else:
                self._club_worker.club_id = self._club_id
        return club
    
    def update_data(self):
        club = self._get_club()
        if club is not None:
            season = self.game_engine.world_time[0]

            club_data = ClubAnalysisWorker(club).analyse(season=season)
            # print(f"Club Analysis {club_data}")

            self._title.setText(f"{club_data['name']} ({club_data['club_id']})")
            self._staff_list.set_staff(club_data['staff'])
            self._player_list.set_players(club_data['players'])
            self._comp_list.set_competitions(club_data['competitions'])


            positions = [Position.Goalkeeper, Position.Defender, Position.Midfielder, Position.Attacker]
            def player_text(temp_p):
                return f"{temp_p.person.short_name} ({temp_p.person.age}) {temp_p.ability}"
        
            text = []

            for p in positions:
                p_players = club_data["position_groups"][p]
                text.append(f"<b>Best {p.short_name}</b> {player_text(p_players[0])}" if p_players else "No players")
             
            b_player = club_data['best_player']
            text.append(f"<b>Best Player</b> {player_text(b_player)} <b>{b_player.position.short_name}</b>")
            text.append("<hr>")
            manager = club_data["manager"]
            if manager:
                text.append(
                    f"<b>Manager</b>:{manager.person.full_name} ({manager.person.age})" \
                    f" ability={manager.ability}" \
                    f" prf-frmtn={manager.prefered_formation}"
                )
            else:
                text.append("No Manager!!!")
            text.append("<hr>")
            squad_avg, squad_dev, squad_max = club_data['squad']['avg'], club_data['squad']['d_avg'], club_data['squad']['max_a']
            text.append(f"Squad Ability: max={squad_max:2d}, avg={squad_avg:2.02f}, avg dev={squad_dev:2.02f}")

            team_avg, team_dev, team_max = club_data["team_analysis"]
            text.append(
                f"Team Ability: max={team_max:2d}, avg={team_avg:2.02f}, avg dev={team_dev:2.02f}a"
            )
            all_text = ""

            for ix, t in enumerate(text):
                
                try:
                    next_t = text[ix+1]
                except IndexError:
                    next_t = None
                if t != "<hr>" and next_t and next_t != "<hr>":
                    all_text += t + "<br>"
                else:
                    all_text += t
        
            self._sqaud_remarks.setText(all_text)
            self._team_sheet.set_team(club_data["formation"], club_data["best_team"])

        else:
            self._title.setText(ClubWidget.DEFAULT_TITLE)
            self._staff_list.clear()
            self._player_list.clear()
            self._comp_list.clear()
            self._sqaud_remarks.clear()
            self._team_sheet.clear()


