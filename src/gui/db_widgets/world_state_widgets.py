from PySide6.QtCore import Qt
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *



from .game_engine_object import GameEngineObject
from .generic_widgets import TitleLabel
from .fixture_result_widgets import FixtureResultList


class BaseGameWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

    def update_data(self, game_engine: GameEngineObject):
        pass


class BlankGameWidget(BaseGameWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)


class PlaceholderGamePage(BaseGameWidget):
    def __init__(self, text: str = "", parent=None):
        super().__init__(parent=parent)
        center_label = TitleLabel(text)
        layout = QVBoxLayout(self)
        layout.addWidget(center_label, 0, Qt.AlignCenter)


class BaseFixturesWidget(BaseGameWidget):
    def __init__(self, state_text: str, parent=None):
        super().__init__(parent=parent)
        self._fixture_list = FixtureResultList()

        layout = QVBoxLayout(self)
        layout.addWidget(TitleLabel(state_text), 0, Qt.AlignHCenter | Qt.AlignTop)
        layout.addWidget(self._fixture_list, 100)

    def set_fixtures(self, fixtures):
        self._fixture_list.set_fixtures(fixtures)