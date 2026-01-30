
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *


from core.competition import CompetitionType
from core.league_table import LeagueTableWorker
from core.world import WorldState, WorldStateEngine


from .utils import change_font
from .generic_widgets import PagesDialog
from .view_widgets import WorldTimeLabel, FixtureList, ResultsList, LeagueTableWidget
from .week_view import SeasonWeekScroll


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

    show_tables = pyqtSignal(name="show tables")

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Sunken)

        self.clubs_btn = QPushButton("Clubs")
        self.competition_btn = QPushButton("Competitions")
        self.table_btn = QPushButton("Tables")
        self.table_btn.clicked.connect(self.show_tables)
        # self.clubs_btn = QPushButton("Clubs")

        btn_frame = QFrame()
        btn_frame.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Plain)
        button_layout = QHBoxLayout(btn_frame)

        for w in [self.clubs_btn, self.competition_btn, self.table_btn]:
            button_layout.addWidget(w, 0, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        button_layout.addStretch(100)
        btn_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        
        self._fixtures = FixtureList(auto_hide=True)
        self._results = ResultsList(auto_hide=True)

        self._main_layout = QVBoxLayout(self)
        self._main_layout.addWidget(btn_frame, 0, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self._main_layout.addWidget(self._fixtures, 0, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self._main_layout.addWidget(self._results, 0, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self._main_layout.addStretch(10)

    def invalidate(self, world_engine: WorldStateEngine | None):
        if world_engine.state.value == WorldState.AwaitingContinue.value:
            current_fixtures = world_engine.world_worker.get_current_fixtures()
            self._fixtures.set_fixtures(current_fixtures)
            self._results.clear_widgets()

        elif world_engine.state.value == WorldState.NewSeason.value:
            self._fixtures.clear_widgets()
            self._results.clear_widgets()

        elif world_engine.state.value == WorldState.PostSeason.value:
            self._fixtures.clear_widgets()
            self._results.clear_widgets()

        elif world_engine.state.value == WorldState.PreFixtures.value:
            self._fixtures.set_fixtures(world_engine.fixtures)
            self._results.clear_widgets()

        elif world_engine.state.value == WorldState.PostFixtures.value:
            self._results.set_results(world_engine.results)
            self._fixtures.clear_widgets()



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
        self.central_view.show_tables.connect(self.on_show_tables)
        
       
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

    def on_show_tables(self):
        print("show tables")

        widgets = []
        leagues = [comp for comp in self._world_engine.world.competitions if comp.type.value == CompetitionType.LEAGUE.value]
        for league in leagues:
            try:
                ltw = LeagueTableWorker(league, self._world_engine.world_worker.results_for_competition(league))
                table_data = ltw.get_sorted_table()
                widget = LeagueTableWidget(league, table_data)
                widgets.append(widget)
            except KeyError:
                pass

        if widgets:
            dlg = PagesDialog("Leagues", widgets, self)
            dlg.exec()

        