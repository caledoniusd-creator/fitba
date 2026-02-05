
from typing import List


from PySide6.QtCore import Qt
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


from .utils import change_font, hline


class ClubsListWidget(QListWidget):

    selected_clubs = Signal(list, name="selected clubs")

    def __init__(self, parent=None):
        super().__init__(parent)
        self.currentItemChanged.connect(self.on_current_club_changed)
        
    def on_current_club_changed(self, current: QModelIndex, previous: QModelIndex):
        club = None
        if current and current.data(Qt.UserRole):
            club = current.data(Qt.UserRole)
        self.selected_clubs.emit([club])

    def set_clubs(self, clubs: List=[]):
        self.clear()

        def listItem(text: str, payload: any = None):
            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, payload)
            return item

        self.addItem(listItem("None"))
        for club in sorted(clubs, key=lambda c: c.name):
            self.addItem(listItem(club.name, club))
        self.setCurrentRow(0)
        self.setEnabled(True if self.count() > 1 else False)


class ClubInfoWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.Box | QFrame.Plain)


        self._club = None
        self._world_worker = None

        self._club_title = QLabel()
        self._club_title.setAlignment(Qt.AlignCenter)
        change_font(self._club_title, 12, True)

        self._squad_rating = QLabel()
        self._squad_rating.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
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
            frame.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
            frame_layout = QVBoxLayout(frame)
            frame_layout.addWidget(t_label, 0, Qt.AlignCenter)
            frame_layout.addWidget(widget, 1000)
            return frame
        
        self._competition_list = QListWidget()
        self._fixtures_list = QListWidget()
        self._results_list = QListWidget()

        widget_lists = [self._competition_list, self._fixtures_list, self._results_list]
        for wl in widget_lists:
            change_font(wl, 2)

        info_frame = QFrame()
        info_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        info_frame_layout = QHBoxLayout(info_frame)
        for t, w in zip(["Competitions", "Fixtures", "Results"], widget_lists):
            info_frame_layout.addWidget(list_group(t, w))
        


        layout = QVBoxLayout(self)
        layout.addWidget(self._club_title, 0, Qt.AlignHCenter | Qt.AlignTop)
        layout.addWidget(hline())
        layout.addLayout(squad_rating_layout)
        layout.addWidget(info_frame, 10)
        layout.addStretch(5)

    @property
    def world_worker(self):
        return self._world_worker
    
    @world_worker.setter
    def world_worker(self, new_world_worker):
        if self._world_worker != new_world_worker:
            self._world_worker = new_world_worker
            self.invalidate()

    def set_club(self, club):
        if self._club != club:
            self._club = club
            self.invalidate()

    def _set_competition(self, competitions: List):
        self._competition_list.clear()
        for comp in competitions:
            item = QListWidgetItem(comp.name)
            item.setData(Qt.UserRole, comp)
            self._competition_list.addItem(item)

    def _set_fixtures(self, fixtures: List):
        self._fixtures_list.clear()
        for fixture in fixtures:
 
            home_team = fixture[1].club1 == self._club
            ha_text = "H" if home_team else "A"
            opponent = fixture[1].club2 if home_team else fixture[1].club1

            cmp_txt = f"{fixture[1].competition.shortname} Rd: {fixture[1].round_num}"
            text = f"Week:{fixture[0]} {cmp_txt} {opponent.name} ({ha_text})"
            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, fixture)
            self._fixtures_list.addItem(item)

    def _set_results(self, results: List):
        self._results_list.clear()
        for result in results:

            home_team = result[1].club1 == self._club
            ha_text = "H" if home_team else "A"
            opponent = result[1].club2 if home_team else result[1].club1

            h_score, a_score =result[1].home_score, result[1].away_score
            score_text = f"{h_score} - {a_score}"
            result_text = "D"
            if h_score > a_score:
                result_text = "W" if home_team else "L"
            elif a_score > h_score:
                result_text = "L" if home_team else "W"


            cmp_txt = f"{result[1].competition.shortname} Rd: {result[1].round_num}"
            text = f"Week:{result[0]} {cmp_txt} {opponent.name} ({ha_text}) {score_text} {result_text}"
            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, result)
            self._results_list.addItem(item)


    def invalidate(self):
        if self._club:
            self._club_title.setText(self._club.name)
            self._squad_rating.setText(str(self._club.squad.rating))

            if self._world_worker:
                data = self._world_worker.get_club_season_info(self._club)

                self._set_competition(data["competitions"])
                self._set_fixtures(data["fixtures"])
                self._set_results(data["results"])
                # print(data)
            else:
                self._competition_list.clear()
                self._fixtures_list.clear()
                self._results_list.clear()

        else:
            self._club_title.setText("N/A")
            self._squad_rating.setText("-")
            self._competition_list.clear()
            self._fixtures_list.clear()
            self._results_list.clear()