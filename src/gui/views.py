
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *


from core.world import WorldState, WorldStateEngine

from .utils import change_font
from .view_widgets import WorldTimeLabel, SeasonWeekScroll, FixtureList, ResultsList


class ViewBase(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)


class MainMenuView(ViewBase):

    new_game = pyqtSignal(name="new game")
    load_game = pyqtSignal(name="load game")
    quit_game = pyqtSignal(name="quit")

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Main Menu")

        title = QLabel(self.windowTitle())
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        change_font(title, 4, True)

        new_game_btn = QPushButton("New Game")
        new_game_btn.clicked.connect(self.new_game)

        load_game_btn = QPushButton("Load Game")
        load_game_btn.clicked.connect(self.load_game)

        quit_game_btn = QPushButton("Quit")
        quit_game_btn.clicked.connect(self.quit_game)

        button_layout = QVBoxLayout()
        button_layout.addWidget(title)
        button_layout.addStretch(10)
        button_layout.addWidget(new_game_btn, 0)
        button_layout.addWidget(load_game_btn)
        button_layout.addWidget(quit_game_btn)
        button_layout.addStretch(10)

        layout = QHBoxLayout(self)
        
        layout.addStretch(10)
        layout.addLayout(button_layout)
        layout.addStretch(10)





class GameViewTopBar(QFrame):
    game_continue = pyqtSignal(name="game continue")

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Plain)

        self.world_time_lbl = WorldTimeLabel()
        self.state_lbl = QLabel()

        continue_btn = QPushButton("Continue")
        continue_btn.clicked.connect(self.game_continue)
        change_font(continue_btn, 2, True)

        layout = QHBoxLayout(self)
        layout.addWidget(self.world_time_lbl, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        layout.addStretch(100)
        layout.addWidget(self.state_lbl, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(continue_btn, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

    def invalidate(self, world_engine: WorldStateEngine):
        if world_engine:
            self.world_time_lbl.set_time(world_engine.world_time)
            self.state_lbl.setText(f"{world_engine.state.name} ({world_engine.state.value})")
        else:
            self.world_time_lbl.set_time(None)
            self.state_lbl.clear()


class GameCenterWidget(QFrame):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Sunken)
        self._fixtures = FixtureList()
        self._results = ResultsList()
        
        self._fixtures.setVisible(False)
        self._results.setVisible(False)

        self._main_layout = QVBoxLayout(self)
        self._main_layout.addWidget(self._fixtures)
        self._main_layout.addWidget(self._results)

    def invalidate(self, world_engine: WorldStateEngine | None):
        if world_engine.state.value == WorldState.AwaitingContinue.value:
            current_fixtures = world_engine.world_worker.get_current_fixtures()
            self._fixtures.set_fixtures(current_fixtures)
            self._results.set_results()

        elif world_engine.state.value == WorldState.NewSeason.value:
            self._fixtures.set_fixtures()
            self._results.set_results()

        elif world_engine.state.value == WorldState.PostSeason.value:
            self._fixtures.set_fixtures()
            self._results.set_results()

        elif world_engine.state.value == WorldState.PreFixtures.value:
            self._fixtures.set_fixtures(world_engine.fixtures)
            self._results.set_results()

        elif world_engine.state.value == WorldState.PostFixtures.value:
            self._results.set_results(world_engine.results)
            self._fixtures.set_fixtures()

        # if world_engine.state.value in [WorldState.AwaitingContinue.value, WorldState.PreFixtures.value]:
        #     current_fixtures =  world_engine.world_worker.get_current_fixtures()
        #     self._fixtures.set_fixtures(current_fixtures)
        # else:
        #     self._fixtures.set_fixtures([])
        #     self._results.set_results([])
        
        # if world_engine.state.value == WorldState.PostFixtures.value:
        #     self._results.set_results(world_engine.results)


class GameCentralView(QStackedWidget):
    def __init__(self, parent =None):
        super().__init__(parent)

    

class GameView(ViewBase):
    main_menu = pyqtSignal(name="main menu")
    world_changed = pyqtSignal(name="world_changed")
    game_continue = pyqtSignal(name="game continue")

    def __init__(self, parent=None):
        super().__init__(parent)
        self._world_engine: WorldStateEngine | None = None

        self.setWindowTitle("Game")

        self.top_bar = GameViewTopBar()
        self.top_bar.game_continue.connect(self.game_continue)
        
        self.world_time_lbl = WorldTimeLabel()
        self.season_scroll = SeasonWeekScroll()
        self.central_view = GameCenterWidget()
        
       
        mid_layout = QHBoxLayout()
        mid_layout.addWidget(self.season_scroll, Qt.AlignmentFlag.AlignLeft)
        mid_layout.addWidget(self.central_view, 100)

        layout = QVBoxLayout(self)
        layout.addWidget(self.top_bar)
        layout.addLayout(mid_layout, 100)
        

        self.world_changed.connect(self.on_world_changed)
        self.game_continue.connect(self.on_game_continue)

    @property
    def world_engine(self):
        return self._world_engine
    
    @world_engine.setter
    def world_engine(self, new_world_engine: WorldStateEngine | None):
        if new_world_engine != self._world_engine:
            print("New World")
            self._world_engine = new_world_engine
            self.world_changed.emit()

    def invalidate_data(self):
        self.top_bar.invalidate(self.world_engine)
        self.season_scroll.set_current_week(self._world_engine.world_time.week)
        self.central_view.invalidate(self._world_engine)

    def on_world_changed(self):
        print(f"World changed: {self._world_engine.world}")
        self.invalidate_data()

    def on_game_continue(self):
        self.world_engine.advance_game()
        self.invalidate_data()

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key.Key_F12:    
            event.setAccepted(True)
            self.main_menu.emit()
        else:
            super().keyReleaseEvent(event)