from sys import argv


from PySide6.QtCore import Qt
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


from .utils import set_white_bg
from .generic_widgets import BusyPage


from src.database_main import GameDBWorker


class DBObject(QObject):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.db_worker = GameDBWorker()

    def create_new_game(self, delete_existing=True):
        self.db_worker.create_new_database(delete_existing=delete_existing)
        self.create_new_season()

    def create_new_season(self):
        self.db_worker.do_new_season()

    def process_current_week(self):
        self.db_worker.process_current_week()

    def current_date(self):
        return self.db_worker.current_date()


class DBMainGameView(QWidget):
    continue_game = Signal(name="advanced_game")
    main_menu = Signal(name="main_menu")

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setAutoFillBackground(True)

        self.date_label = QLabel()
        self.date_label.setFrameStyle(QFrame.Panel | QFrame.Plain)
        self.date_label.setAlignment(Qt.AlignCenter)
        self.date_label.setFont(QFont("DejaVu Sans", 16, QFont.Bold))

        self.btn_continue = QPushButton("Continue")
        self.btn_continue.clicked.connect(self.continue_game)

        btn_main_menu = QPushButton("Main Menu")
        btn_main_menu.clicked.connect(self.main_menu)

        top_layout = QHBoxLayout()
        top_layout.addWidget(self.date_label, 0, Qt.AlignTop | Qt.AlignLeft)
        top_layout.addWidget(self.btn_continue, 0, Qt.AlignTop | Qt.AlignLeft)
        top_layout.addWidget(btn_main_menu, 0, Qt.AlignTop | Qt.AlignRight)

        self._club_list = QListView()
        self._comp_list = QListView()
        self._people_list = QListView()
        self._staff_list = QListView()
        self._player_list = QListView()

        list_layout = QHBoxLayout()
        list_layout.addWidget(self._club_list)
        list_layout.addWidget(self._comp_list)
        list_layout.addWidget(self._people_list)
        list_layout.addWidget(self._staff_list)
        list_layout.addWidget(self._player_list)

        layout = QVBoxLayout(self)
        layout.addLayout(top_layout)
        layout.addLayout(list_layout, 100)
        # layout.addStretch(100)

        set_white_bg(self)

        self._db_worker: DBObject | None = None
        self.invalidate()

    def showEvent(self, event):
        super().showEvent(event)
        self.invalidate()

    def set_db_worker(self, db_worker: DBObject | None):
        if self._db_worker != db_worker:
            self._db_worker = db_worker
            self.invalidate()

    def invalidate(self):
        if self._db_worker is not None:
            season, week = self._db_worker.current_date()
            self.date_label.setText(f"{season} - {week}")
            db_worker = self._db_worker.db_worker.worker

            clubs = [
                f"{ix + 1:3d}: {c.name}" for ix, c in enumerate(db_worker.get_clubs())
            ]
            self._club_list.setModel(QStringListModel(clubs))

            comps = [
                f"{ix + 1:3d}: {c.name}"
                for ix, c in enumerate(db_worker.get_competitions())
            ]
            self._comp_list.setModel(QStringListModel(comps))

            people = [
                f"{ix + 1:04d}: {p.full_name} ({p.age}) {p.personality.name}"
                for ix, p in enumerate(db_worker.get_people())
            ]
            self._people_list.setModel(QStringListModel(people))

            staff = [
                f"{ix + 1:04d}: {s.person.full_name} - {s.role.name} (Rep: {s.reputation_type.name}, Abil: {s.ability})"
                for ix, s in enumerate(db_worker.get_staff())
            ]
            self._staff_list.setModel(QStringListModel(staff))

            players = [
                f"{ix + 1:04d}: {p.person.full_name} - {p.position.name} (Abil: {p.ability})"
                for ix, p in enumerate(db_worker.get_players())
            ]
            self._player_list.setModel(QStringListModel(players))

        else:
            self.date_label.clear()
            self._club_list.setModel(QStringListModel())
            self._comp_list.setModel(QStringListModel())
            self._people_list.setModel(QStringListModel())
            self._staff_list.setModel(QStringListModel())
            self._player_list.setModel(QStringListModel())

    def has_db_worker(self):
        return self._db_worker is not None


class DBMainMenuView(QWidget):
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
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setAutoFillBackground(True)
        self.setContentsMargins(QMargins(0, 0, 0, 0))

        self.setMinimumSize(800, 600)
        self.setWindowTitle("Fitba DB GUI")

        self._views = {
            "busy": BusyPage(),
            "main_menu": DBMainMenuView(),
            "game_view": DBMainGameView(),
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

        self._game_worker = DBObject()

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
            self._game_worker.create_new_game,
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
        self.close()

    def on_busy_done(self):
        print("Busy done !")
        self.setCurrentWidget(self._views["main_menu"])

    def on_show_game_view(self):
        print("New Game created !")
        view = self._views["game_view"]
        if isinstance(view, DBMainGameView):
            view.set_db_worker(self._game_worker)
            self.setCurrentWidget(view)

    def on_main_menu(self):
        widget = self._views["main_menu"]
        if widget is not None:
            widget.set_can_continue(self._views["game_view"].has_db_worker())
        self.setCurrentWidget(widget)

    def on_advanced_game(self):
        print("Advance Game !")
        widget = self.currentWidget()
        if widget is not None and isinstance(widget, DBMainGameView):
            self.run_thread_function(
                self._game_worker.process_current_week,
                self.on_advanced_game_done,
                "Processing Advance...",
            )

    def on_advanced_game_done(self):
        print("Game advanced !")
        self.on_show_game_view()


class GUIDBApplication(QApplication):
    def __init__(self, args=argv):
        super().__init__(args)
        self.widget = None

    def run(self):
        print(f"Fonts: {', '.join(QFontDatabase.families())}")
        print("Styles: " + ", ".join(QStyleFactory.keys()))
        # QApplication.setStyle(QStyleFactory.create("Windows"))
        QApplication.setStyle(QStyleFactory.create("Fusion"))

        self.widget = MainView()
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
