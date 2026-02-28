from sys import argv


from PySide6.QtCore import Qt
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *



from src.core.constants import (
    APP_TITLE, 
    APP_AUTHOR, 
    APP_VERSION,
    version_str
)

from src.core.db.models import SeasonDB, LeagueDB
from src.core.db.league_db_functions import get_league_table_data
from src.core.db.game_worker import GameDBWorker, WorldState, WorldStateEngine

from src.gui.db_widgets.game_engine_object import GameEngineObject

from src.gui.db_widgets.generic_widgets import TitleLabel
from src.gui.db_widgets.object_views import (
    StaffTreeWidget,
    PlayerTreeWidget,
    CompetitionListWidget
)


from src.gui.db_widgets.fixture_result_widgets import FixtureResultList

from src.gui.db_widgets.league_views import LeagueView
from src.gui.db_widgets.club_widget import ClubWidget


from .utils import set_white_bg
from .generic_widgets import BusyPage


# class DBObject(QObject):
#     def __init__(self, parent=None):
#         super().__init__(parent=parent)
#         self.db_worker = GameDBWorker()

#     def create_new_game(self, delete_existing=True):
#         self.db_worker.create_new_database(delete_existing=delete_existing)
#         self.create_new_season()

#     def create_new_season(self):
#         self.db_worker.do_new_season()

#     def process_current_week(self):
#         self.db_worker.process_current_week()

#     def current_date(self):
#         return self.db_worker.current_date()


# class ClubsListWithView(QWidget):
#     def __init__(self, parent=None):
#         super().__init__(parent=parent)
#         self.setAutoFillBackground(True)

#         self._club_List = QListWidget(self)
#         self._club_List.currentItemChanged.connect(self.on_club_changed)
#         self._club_view = ClubWidget(self)

#         self._club = None

#         layout = QHBoxLayout(self)
#         layout.addWidget(self._club_List, 0, Qt.AlignTop | Qt.AlignLeft)
#         layout.addWidget(self._club_view, 100)

#     def set_club(self, club):
#         self._club = club

#     def invalidate(self, db_worker: DBObject | None):
#         if db_worker is not None:
#             clubs = db_worker.db_worker.worker.get_clubs()
#             self._club_List.clear()
#             for club in clubs:
#                 item = QListWidgetItem(club.name)
#                 item.setData(Qt.UserRole, club)
#                 self._club_List.addItem(item)
#         else:
#             self._club_List.clear()
#             self._club = None

#     def on_club_changed(
#         self, current: QListWidgetItem | None, previous: QListWidgetItem | None
#     ):
#         print("Club changed !")
#         if current is not None:
#             club = current.data(Qt.UserRole)

#             self.set_club(club)
#             self._club_view.club = self._club
#         else:
#             self.set_club(None)
#             self._club_view.club = None


# class HomePage(QFrame):
#     def __init__(self, parent=None):
#         super().__init__(parent=parent)
#         self.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)

#         self._league_1 = LeagueView()
#         self._league_2 = LeagueView()

#         league_layout = QHBoxLayout()
#         league_layout.addWidget(self._league_1)
#         league_layout.addWidget(self._league_2)

#         layout = QVBoxLayout(self)
#         layout.addLayout(league_layout)

#     def invalidate(self):
#         pass

#     def set_league_1(self, league: LeagueDB, season: SeasonDB):
#         self._league_1.set_league(league, season)

#     def set_league_2(self, league: LeagueDB, season: SeasonDB):
#         self._league_2.set_league(league, season)

#     def clear(self):
#         self._league_1.clear()
#         self._league_2.clear()


# class DBMainGameView(QWidget):
#     continue_game = Signal(name="advanced_game")
#     main_menu = Signal(name="main_menu")

#     def __init__(self, parent=None):
#         super().__init__(parent=parent)
#         self.setAutoFillBackground(True)

#         self.tabView = QTabWidget()

#         self.date_label = TitleLabel(size=12)
#         self.date_label.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)

#         self.btn_continue = QPushButton("Continue")
#         self.btn_continue.clicked.connect(self.continue_game)

#         btn_main_menu = QPushButton("Main Menu")
#         btn_main_menu.clicked.connect(self.main_menu)

#         top_layout = QHBoxLayout()
#         top_layout.addWidget(self.date_label, 0, Qt.AlignTop | Qt.AlignLeft)
#         top_layout.addWidget(self.btn_continue, 0, Qt.AlignTop | Qt.AlignLeft)
#         top_layout.addWidget(btn_main_menu, 0, Qt.AlignTop | Qt.AlignRight)

#         self.home_view = HomePage()
#         self._club_view = ClubsListWithView()

#         self._club_list = QListView()
#         self._comp_list = QListView()

#         list_widgets = QWidget()
#         list_layout = QHBoxLayout(list_widgets)
#         list_layout.addWidget(self._club_list)
#         list_layout.addWidget(self._comp_list)

#         self.tabView.addTab(self.home_view, "Home")
#         self.tabView.addTab(self._club_view, "Clubs")
#         self.tabView.addTab(list_widgets, "All Data")

#         self.tabView.setCurrentIndex(0)

#         layout = QVBoxLayout(self)
#         layout.addLayout(top_layout)
#         layout.addWidget(self.tabView, 100)

#         set_white_bg(self)

#         self._db_worker: DBObject | None = None
#         self.invalidate()

#     def showEvent(self, event):
#         super().showEvent(event)
#         self.invalidate()

#     def set_db_worker(self, db_worker: DBObject | None):
#         if self._db_worker != db_worker:
#             self._db_worker = db_worker
#             self.invalidate()

#     def invalidate(self):
#         if self._db_worker is not None:
#             season, week = self._db_worker.current_date()
#             self.date_label.setText(f"{season} - {week}")
#             db_worker = self._db_worker.db_worker.worker

#             clubs = [
#                 f"{ix + 1:3d}: {c.name}" for ix, c in enumerate(db_worker.get_clubs())
#             ]
#             self._club_list.setModel(QStringListModel(clubs))

#             comps = [
#                 f"{ix + 1:3d}: {c.name}"
#                 for ix, c in enumerate(db_worker.get_competitions())
#             ]
#             self._comp_list.setModel(QStringListModel(comps))

#             leagues = self._db_worker.db_worker.worker.get_leagues()
#             if len(leagues) > 1:
#                 self.home_view.set_league_1(leagues[0], season)
#                 self.home_view.set_league_2(leagues[1], season)
#             else:
#                 self.home_view.clear()

#         else:
#             self.date_label.clear()
#             self._club_list.setModel(QStringListModel())
#             self._comp_list.setModel(QStringListModel())
#             self.home_view.clear()

#         self._club_view.invalidate(self._db_worker)

#     def has_db_worker(self):
#         return self._db_worker is not None




class DateLabel(TitleLabel):
    def __init__(self, title = None, size = 12, parent=None):
        super().__init__(title, size, parent)

    def set_date(self, season, week):
        if season is None:
            season = "Invalid Season"
        if week is None:
            week = "Invalid Week"
        self.setText(f"{season}: {week}")


class ContinueBtn(QPushButton):
    def __init__(self, parent=None):
        super().__init__("Continue")
        self.setFont(QFont("DejaVu Sans", 14, QFont.Bold))


class BlankGameWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)


class PlaceholderGamePage(QWidget):
    def __init__(self, text: str="", parent=None):
        super().__init__(parent=parent)
        center_label = TitleLabel(text)
        layout = QVBoxLayout(self)
        layout.addWidget(center_label, 0, Qt.AlignCenter)


class NewSeasonWidget(PlaceholderGamePage):
    def __init__(self, parent=None):
        super().__init__("New Season", parent=parent)


class PostSeasonWidget(PlaceholderGamePage):
    def __init__(self, parent=None):
        super().__init__("Post Season", parent=parent)

class PreFixturesWidget(BlankGameWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._fixture_list = FixtureResultList()

        layout = QVBoxLayout(self)
        layout.addWidget(TitleLabel("Pre Fixtures"), 0, Qt.AlignHCenter | Qt.AlignTop)
        layout.addWidget(self._fixture_list, 100)

    def set_fixtures(self, fixtures):
        self._fixture_list.set_fixtures(fixtures)


class ProcessingFixturesWidget(PlaceholderGamePage):
    def __init__(self, parent=None):
        super().__init__("Processing Fixtures", parent=parent)


class PostFixturesWidget(BlankGameWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._fixture_list = FixtureResultList()

        layout = QVBoxLayout(self)
        layout.addWidget(TitleLabel("Post Fixtures"), 0, Qt.AlignHCenter | Qt.AlignTop)
        layout.addWidget(self._fixture_list, 100)

    def set_fixtures(self, fixtures):
        self._fixture_list.set_fixtures(fixtures)

class AwaitingContinueWidget(BlankGameWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        layout = QVBoxLayout(self)
        layout.addWidget(TitleLabel("Awaiting Continue"), 0, Qt.AlignLeft | Qt.AlignTop)



class DBMainGameView(QWidget):
    continue_game = Signal(name="advanced_game")
    main_menu = Signal(name="main_menu")

    def __init__(self, game_engine: GameEngineObject, parent=None):
        super().__init__(parent=parent)

        self._game_engine = game_engine
        self._game_engine.state_engine_changed.connect(self.on_state_engine_changed)
        self._game_engine.game_advanced.connect(self.on_game_advanced)



        self._pages = {
            "blank": BlankGameWidget(),
            "new_season": NewSeasonWidget(),
            "post_season": PostSeasonWidget(),
            "pre_fixtures": PreFixturesWidget(),
            "processing_fixtures": ProcessingFixturesWidget(),
            "post_fixtures": PostFixturesWidget(),
            "awaiting_continue": AwaitingContinueWidget()
        }

        self._game_view_stack = QStackedWidget()
        for value in self._pages.values():
            self._game_view_stack.addWidget(value)
        self._game_view_stack.setCurrentWidget(self._pages["blank"])

        stack_frame = QFrame()
        stack_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
        stack_frame_layout = QVBoxLayout(stack_frame)
        stack_frame_layout.addWidget(self._game_view_stack, 1000)


        self.setAutoFillBackground(True)

        self._date_lbl = DateLabel()

        self._main_menu_btn = QPushButton("Main Menu")
        self._main_menu_btn.clicked.connect(self.main_menu)

        self._continue_btn = ContinueBtn()
        self._continue_btn.clicked.connect(self.continue_game)

        self.top_bar_frame = QFrame()
        self.top_bar_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
        top_bar_layout = QHBoxLayout(self.top_bar_frame)
        top_bar_layout.addWidget(self._date_lbl, 0, Qt.AlignLeft | Qt.AlignTop)
        top_bar_layout.addWidget(self._main_menu_btn, 0, Qt.AlignRight | Qt.AlignTop)
        
        self.bottom_bar_frame = QFrame()
        self.bottom_bar_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
        bottom_bar_layout = QHBoxLayout(self.bottom_bar_frame)
        bottom_bar_layout.addWidget(self._continue_btn, 0, Qt.AlignRight | Qt.AlignVCenter)

        layout = QVBoxLayout(self)
        layout.addWidget(self.top_bar_frame)
        layout.addWidget(stack_frame,100)
        layout.addWidget(self.bottom_bar_frame)
    
    def on_state_engine_changed(self):
        self.invalidate()

    def on_game_advanced(self):
        self.invalidate()

    def invalidate(self):
        if self._game_engine.state == WorldState.NewSeason:
            self.top_bar_frame.setVisible(False)
            self._game_view_stack.setCurrentWidget(self._pages["new_season"])

        elif self._game_engine.state == WorldState.PostSeason:
            self.top_bar_frame.setVisible(False)
            self._game_view_stack.setCurrentWidget(self._pages["post_season"])

        elif self._game_engine.state == WorldState.PreFixtures:
            self.top_bar_frame.setVisible(False)
            current_fixtures = self._game_engine.current_fixtures()
            print(f"Current Fixtures: {len(current_fixtures)}")
            w = self._pages["pre_fixtures"]
            w.set_fixtures(current_fixtures)
            self._game_view_stack.setCurrentWidget(w)

        elif self._game_engine.state == WorldState.ProcessingFixtures:
            self.top_bar_frame.setVisible(False)
            self._game_view_stack.setCurrentWidget(self._pages["processing_fixtures"])

        elif self._game_engine.state == WorldState.PostFixtures:
            self.top_bar_frame.setVisible(False)
            current_fixtures = self._game_engine.current_result_fixtures()
            print(f"Current Fixtures: {len(current_fixtures)}")
            w = self._pages["post_fixtures"]
            w.set_fixtures(current_fixtures)
            self._game_view_stack.setCurrentWidget(w)

        elif self._game_engine.state == WorldState.AwaitingContinue:
            self.top_bar_frame.setVisible(True)
            self._game_view_stack.setCurrentWidget(self._pages["awaiting_continue"])

        else:
            print(f"Unhandelled state {self._game_engine.state}")
            self.top_bar_frame.setVisible(True)
            self._game_view_stack.setCurrentWidget(self._pages["blank"])

        self._date_lbl.set_date(*(self._game_engine.world_time))


class DBMainMenuView(QWidget):
    """
    Main Menu View
    """

    new_game = Signal(name="new_game")
    continue_game = Signal(name="continue_game")
    load_game = Signal(name="load_game")
    exit_game = Signal(name="exit_game")

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setAutoFillBackground(True)

        btn_new_game = QPushButton("New Game")
        btn_new_game.clicked.connect(self.new_game)
        self.btn_continue_game = QPushButton("Continue Game")
        self.btn_continue_game.clicked.connect(self.continue_game)
        self.btn_continue_game.setEnabled(False)

        btn_load_game = QPushButton("Load Game")
        btn_load_game.clicked.connect(self.load_game)
        btn_exit = QPushButton("Exit")
        btn_exit.clicked.connect(self.exit_game)

        btn_layout = QVBoxLayout()
        btn_layout.setContentsMargins(QMargins(64, 64, 64, 64))

        btns = [btn_new_game, self.btn_continue_game, btn_load_game, btn_exit]
        btn_font = QFont("DejaVu Sans", 20, QFont.Bold)
        for btn in btns:
            btn.setFont(btn_font)
            btn.setFixedSize(QSize(320, 48))
            btn_layout.addWidget(btn, 0, Qt.AlignCenter)

        set_white_bg(self)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(QMargins(64, 64, 64, 64))

        title = QLabel("Fitba DB GUI")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("DejaVu Sans", 24, QFont.Bold))

        layout.addWidget(title, 1, Qt.AlignTop | Qt.AlignHCenter)
        layout.addLayout(btn_layout)
        layout.addStretch(100)

    def set_can_continue(self, can_continue: bool):
        if self.btn_continue_game is not None:
            self.btn_continue_game.setEnabled(can_continue)


class LogWindow(QTextEdit):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        # self.setWindowFlags(Qt.Tool)
        self.setReadOnly(True)
        self.setMinimumSize(256, 96)
        

class MainView(QStackedWidget):
    """
    Main App View
    """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._game_engine_object = GameEngineObject()
        self._game_engine_object.state_engine_changed.connect(self.on_state_engine_changed)

        self.setAutoFillBackground(True)
        self.setContentsMargins(QMargins(0, 0, 0, 0))
        self.setMinimumSize(1920, 1080)
        self.setWindowTitle("Fitba DB GUI")

        self._views = {
            "busy": BusyPage(),
            "main_menu": DBMainMenuView(),
            "game_view": DBMainGameView(self._game_engine_object),
        }

        self._views["main_menu"].new_game.connect(self.on_new_game)
        self._views["main_menu"].continue_game.connect(self.on_continue_game)
        self._views["main_menu"].load_game.connect(self.on_load_game)
        self._views["main_menu"].exit_game.connect(self.on_exit_game)
        self._views["game_view"].main_menu.connect(self.on_main_menu)
        self._views["game_view"].advanced_game.connect(self.on_advanced_game)

        for view in self._views.values():
            self.addWidget(view)

        self.setCurrentWidget(self._views["main_menu"])
        # self.grabKeyboard()

    def on_state_engine_changed(self):
        sender = self.sender()
        if isinstance(sender, GameEngineObject):
            print("New State Engine!")

    def run_thread_function(self, funct: callable, on_done: callable, message=""):
        self.set_busy(message)
        thread = QThread(self)
        thread.finished.connect(on_done)
        thread.run = lambda: funct()
        thread.start()

    def set_busy(self, message=""):
        self._views["busy"].set_message(message)
        self.setCurrentWidget(self._views["busy"])

    def on_new_game(self):
        print("New Game !")
        self.run_thread_function(
            self._game_engine_object.create_new_game,
            self.on_show_game_view,
            "Creating Game...",
        )

    def on_continue_game(self):
        self.set_busy("Continue game...")
        self.on_show_game_view()

    def on_load_game(self):
        self.set_busy("Loading game...")
        self.on_show_game_view()

    def on_exit_game(self):
        print("Exit Game !")
        if self.parent():
            self.parent().close()
        else:
            self.close()

    def on_busy_done(self):
        print("Busy done !")
        self.setCurrentWidget(self._views["main_menu"])

    def on_show_game_view(self):
        print("New Game created !")
        view = self._views["game_view"]
        if isinstance(view, DBMainGameView):
            view.invalidate()
            self.setCurrentWidget(view)

    def on_main_menu(self):
        widget = self._views["main_menu"]
        if isinstance(widget, DBMainMenuView):
            widget.set_can_continue(self._game_engine_object.is_active())
        self.setCurrentWidget(widget)

    def on_advanced_game(self):
        print("Advance Game !")
        widget = self.currentWidget()
        if widget is not None and isinstance(widget, DBMainGameView):
            self.run_thread_function(
                self._game_engine_object.advance_game,
                self.on_advanced_game_done,
                "Processing Advance...",
            )

    def on_advanced_game_done(self):
        print("Game advanced !")
        self.on_show_game_view()


class AppMainWindow(QMainWindow):
    """
    App Main Window
    """

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.setWindowTitle(f"{APP_TITLE} {version_str()}")

        self._main_view_stack = MainView()
        self.setCentralWidget(self._main_view_stack)

        self._log_window = LogWindow()

        self._log_docked_widget = QDockWidget("Log")
        self._log_docked_widget.setWidget(self._log_window)
        self._log_docked_widget.setAllowedAreas(Qt.BottomDockWidgetArea)
        self._log_docked_widget.hide()

        self.addDockWidget(Qt.BottomDockWidgetArea, self._log_docked_widget)

        self.log_toggle_action = QAction()
        self.log_toggle_action.setShortcut(QKeySequence(Qt.Key_F1))
        self.log_toggle_action.setShortcutContext(Qt.ApplicationShortcut)
        self.log_toggle_action.triggered.connect(self._log_docked_widget.show)
        self.addAction(self.log_toggle_action)


class GUIDBApplication(QApplication):
    """
    Application Object
    """

    def __init__(self, args=argv):
        super().__init__(args)
        self.widget = None

    def run(self):
        # print(f"Fonts: {', '.join(QFontDatabase.families())}")
        # print("Styles: " + ", ".join(QStyleFactory.keys()))
        # QApplication.setStyle(QStyleFactory.create("Windows"))
        QApplication.setStyle(QStyleFactory.create("Fusion"))

        self.widget = AppMainWindow()
        self.widget.show()

        try:
            rc = self.exec()

            if rc != 0:
                print(f"Exit code non-zero ! {rc}")
        except Exception as e:
            print(format_exc())
            print(e)
            pass


def run_db_gui_application():
    GUIDBApplication().run()
