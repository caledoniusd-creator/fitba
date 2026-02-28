from sys import argv


from PySide6.QtCore import Qt
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


from src.core.constants import APP_TITLE, version_str

from src.core.db.game_worker import WorldState

from src.gui.db_widgets.game_engine_object import GameEngineObject

from src.gui.db_widgets.generic_widgets import TitleLabel, LogWindow

from src.gui.db_widgets.club_widget import ClubWidget

from src.gui.db_widgets.world_state_widgets import (
    BaseGameWidget,
    BlankGameWidget,
    PlaceholderGamePage,
    BaseFixturesWidget,
)

from src.gui.db_widgets.game_widgets import DateLabel, ContinueBtn, TwinLeagueView

from .utils import set_white_bg
from .generic_widgets import BusyPage


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


class GeneralPage(QWidget):
    def __init__(self, game_engine: GameEngineObject, parent=None):
        super().__init__(parent=parent)
        self._game_engine = game_engine

    @property
    def game_engine(self):
        return self._game_engine

    def update_data(self):
        pass


class HomePage(GeneralPage):
    def __init__(self, game_engine: GameEngineObject, parent=None):
        super().__init__(game_engine, parent=parent)

        self._league_views = TwinLeagueView()
        layout = QVBoxLayout(self)
        layout.addWidget(self._league_views, 100)

    def update_data(self):
        print("Update date for HomePage")

        self._league_views.clear()
        if self.game_engine.is_active:
            season = self.game_engine.world_time[0]
            leagues = self.game_engine.db_worker.get_leagues()
            if not season:
                raise RuntimeError("Invalid Season")
            self._league_views.update_leagues(leagues[0], leagues[1], season)


class ClubPage(GeneralPage):
    def __init__(self, game_engine: GameEngineObject, parent=None):
        super().__init__(game_engine, parent=parent)

        self._club_list = QListWidget()
        self._club_list.currentItemChanged.connect(self.on_current_item_changed)
        self._current_club = 0

        self._club_widget = ClubWidget()

        layout = QHBoxLayout(self)
        layout.addWidget(self._club_list, 2)
        layout.addWidget(self._club_widget, 8)

    @property
    def current_club(self):
        return self._current_club

    @current_club.setter
    def current_club(self, new_club_id):
        self._current_club = new_club_id

    def clear(self):
        self._club_list.clear()
        self._club_widget.club = None

    def update_club_data(self):
        club = self.game_engine.db_worker.get_club(self._current_club)
        self._club_widget.club = club

    def update_data(self):
        print("Update date for ClubPage")
        if self.game_engine.is_active:
            if self._club_list.count() == 0:
                clubs = self.game_engine.db_worker.get_clubs()
                for ix, c in enumerate(clubs):
                    text = str(ix + 1).ljust(8) + c.name
                    item = QListWidgetItem(text)
                    item.setData(Qt.UserRole, c.id)
                    self._club_list.addItem(item)

            if self.current_club is not None:
                self.update_club_data()
            else:
                self._club_widget.club = None
        else:
            self.clear()
            self._club_widget.club = None

    def on_current_item_changed(self, current, previous):
        data = current.data(Qt.UserRole)
        text = current.text()
        print(f"Club: {text}({data}) selected")
        self.current_club = data
        self.update_club_data()


class NewSeasonWidget(PlaceholderGamePage):
    def __init__(self, parent=None):
        super().__init__("New Season", parent=parent)


class PostSeasonWidget(BaseGameWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._league_views = TwinLeagueView()
        center_label = TitleLabel("Post Season")
        layout = QVBoxLayout(self)
        layout.addWidget(center_label, 0, Qt.AlignHCenter | Qt.AlignTop)
        layout.addWidget(self._league_views, 100)

    def update_data(self, game_engine: GameEngineObject):
        print("Update date for PostSeasonWidget")

        self._league_views.clear()
        if game_engine.is_active:
            season = game_engine.world_time[0]
            leagues = game_engine.state_engine.game_worker.worker.get_leagues()
            if not season:
                raise RuntimeError("Invalid Season")
            self._league_views.update_leagues(leagues[0], leagues[1], season)


class PreFixturesWidget(BaseFixturesWidget):
    def __init__(self, parent=None):
        super().__init__("Pre Fixtures", parent=parent)


class ProcessingFixturesWidget(PlaceholderGamePage):
    def __init__(self, parent=None):
        super().__init__("Processing Fixtures", parent=parent)


class PostFixturesWidget(BaseFixturesWidget):
    def __init__(self, parent=None):
        super().__init__("Post Fixtures", parent=parent)


class AwaitingContinueWidget(BaseGameWidget):
    def __init__(self, game_engine: GameEngineObject, parent=None):
        super().__init__(parent=parent)
        self._game_engine = game_engine

        self._nav_frame = QFrame()
        self._nav_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)

        home_btn = QPushButton("Home")
        home_btn.clicked.connect(self.on_home_clicked)

        club_btn = QPushButton("Club")
        club_btn.clicked.connect(self.on_club_clicked)

        nav_frame_layout = QHBoxLayout(self._nav_frame)
        nav_frame_layout.addWidget(home_btn, 0, Qt.AlignLeft | Qt.AlignVCenter)
        nav_frame_layout.addWidget(club_btn, 0, Qt.AlignLeft | Qt.AlignVCenter)
        nav_frame_layout.addStretch(100)

        self._pages = {
            "home": HomePage(self._game_engine),
            "club": ClubPage(self._game_engine),
        }
        self._view_stack = QStackedWidget()
        for v in self._pages.values():
            self._view_stack.addWidget(v)

        self._view_stack.setCurrentWidget(self._pages["home"])

        layout = QVBoxLayout(self)
        layout.addWidget(TitleLabel("Awaiting Continue"), 0, Qt.AlignLeft | Qt.AlignTop)
        layout.addWidget(self._nav_frame)
        layout.addWidget(self._view_stack, 100)

    @property
    def game_engine(self):
        return self._game_engine

    def on_home_clicked(self):
        self._view_stack.setCurrentWidget(self._pages["home"])

    def on_club_clicked(self):
        self._view_stack.setCurrentWidget(self._pages["club"])

    def update_data(self, game_engine: GameEngineObject):
        print("Update date for AwaitingContinueWidget")

        for v in self._pages.values():
            if isinstance(v, GeneralPage):
                v.update_data()


class DBMainGameView(QWidget):
    continue_game = Signal(name="advanced_game")
    goto_end_of_season = Signal(name="goto end of season")
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
            "awaiting_continue": AwaitingContinueWidget(self._game_engine),
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

        self._continue_end_of_season_btn = QPushButton("To End of Season")
        self._continue_end_of_season_btn.clicked.connect(self.goto_end_of_season)

        self._extra_continue_frame = QFrame()
        self._extra_continue_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        extra_continue_frame_layout = QHBoxLayout(self._extra_continue_frame)
        extra_continue_frame_layout.addWidget(
            self._continue_end_of_season_btn, 0, Qt.AlignLeft | Qt.AlignVCenter
        )

        self.top_bar_frame = QFrame()
        self.top_bar_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
        top_bar_layout = QHBoxLayout(self.top_bar_frame)
        top_bar_layout.addWidget(self._date_lbl, 0, Qt.AlignLeft | Qt.AlignTop)
        top_bar_layout.addWidget(self._main_menu_btn, 0, Qt.AlignRight | Qt.AlignTop)

        self.bottom_bar_frame = QFrame()
        self.bottom_bar_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
        bottom_bar_layout = QHBoxLayout(self.bottom_bar_frame)
        bottom_bar_layout.addWidget(
            self._extra_continue_frame, 0, Qt.AlignLeft | Qt.AlignVCenter
        )
        bottom_bar_layout.addWidget(
            self._continue_btn, 0, Qt.AlignRight | Qt.AlignVCenter
        )

        layout = QVBoxLayout(self)
        layout.addWidget(self.top_bar_frame)
        layout.addWidget(stack_frame, 100)
        layout.addWidget(self.bottom_bar_frame)

        self.invalidate()

    def on_state_engine_changed(self):
        self.invalidate()

    def on_game_advanced(self):
        self.invalidate()

    def invalidate(self):
        new_page = None
        if self._game_engine.state == WorldState.NewSeason:
            self.top_bar_frame.setVisible(False)
            self._extra_continue_frame.setVisible(False)
            new_page = self._pages["new_season"]

        elif self._game_engine.state == WorldState.PostSeason:
            self.top_bar_frame.setVisible(False)
            self._extra_continue_frame.setVisible(False)
            new_page = self._pages["post_season"]

        elif self._game_engine.state == WorldState.PreFixtures:
            self.top_bar_frame.setVisible(False)
            self._extra_continue_frame.setVisible(False)
            new_page = self._pages["pre_fixtures"]
            new_page.set_fixtures(self._game_engine.current_fixtures())

        elif self._game_engine.state == WorldState.ProcessingFixtures:
            self.top_bar_frame.setVisible(False)
            self._extra_continue_frame.setVisible(False)
            new_page = self._pages["processing_fixtures"]

        elif self._game_engine.state == WorldState.PostFixtures:
            self.top_bar_frame.setVisible(False)
            self._extra_continue_frame.setVisible(False)
            new_page = self._pages["post_fixtures"]
            new_page.set_fixtures(self._game_engine.current_result_fixtures())

        elif self._game_engine.state == WorldState.AwaitingContinue:
            self.top_bar_frame.setVisible(True)
            self._extra_continue_frame.setVisible(True)
            new_page = self._pages["awaiting_continue"]
            new_page.on_home_clicked()

        else:
            print(f"Unhandelled state {self._game_engine.state}")
            self.top_bar_frame.setVisible(True)
            self._extra_continue_frame.setVisible(True)
            new_page = self._pages["blank"]

        if isinstance(new_page, BaseGameWidget):
            new_page.update_data(self._game_engine)
            self._game_view_stack.setCurrentWidget(new_page)

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


class MainView(QStackedWidget):
    """
    Main App View
    """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._game_engine_object = GameEngineObject()
        self._game_engine_object.state_engine_changed.connect(
            self.on_state_engine_changed
        )

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
        self._views["game_view"].goto_end_of_season.connect(self.on_goto_end_of_season)
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
        print("Load Game !")
        self.run_thread_function(
            self._game_engine_object.load_game,
            self.on_show_game_view,
            "Creating Game...",
        )

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
            widget.set_can_continue(self._game_engine_object.is_active)
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

    def on_goto_end_of_season(self):
        print("Advance to end of Season !")
        widget = self.currentWidget()
        if widget is not None and isinstance(widget, DBMainGameView):
            self.run_thread_function(
                self._game_engine_object.advance_to_end_of_season,
                self.on_advanced_game_done,
                "Advancing to end of Season...",
            )


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
        self.log_toggle_action.triggered.connect(self.toggle_log_dock)
        self.addAction(self.log_toggle_action)

    def toggle_log_dock(self):
        if self._log_docked_widget.isVisible():
            self._log_docked_widget.hide()
        else:
            self._log_docked_widget.show()


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
