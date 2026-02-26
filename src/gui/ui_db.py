from sys import argv


from PySide6.QtCore import Qt
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


from .utils import set_white_bg
from .generic_widgets import BusyPage


from src.core.db.models import (
    SeasonDB,
    LeagueDB
)
from src.core.db.league_db_functions import get_league_table_data

from src.core.db.game_worker import GameDBWorker


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


class TitleLabel(QLabel):
    def __init__(self, title: str, size: int = 16, parent=None):
        super().__init__(parent=parent)
        self.setText(title)
        self.setAlignment(Qt.AlignCenter)
        self.setFont(QFont("DejaVu Sans", size, QFont.Bold))


class TitledTreeWidget(QFrame):
    def __init__(self, title: str, parent=None):
        super().__init__(parent=parent)
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        self.setAutoFillBackground(True)

        self._tree = QTreeWidget(self)
    
        layout = QVBoxLayout(self)
        layout.addWidget(TitleLabel(title, 12), 0, Qt.AlignTop | Qt.AlignHCenter)
        layout.addWidget(self._tree, 100)

    @property
    def tree(self):
        return self._tree
    
    def clear(self):
        self._tree.clear()


class TitledListWidget(QFrame):
    def __init__(self, title: str, parent=None):
        super().__init__(parent=parent)
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        self.setAutoFillBackground(True)

        self._list_widget = QListWidget(self)
    
        layout = QVBoxLayout(self)
        layout.addWidget(TitleLabel(title, 12), 0, Qt.AlignTop | Qt.AlignHCenter)
        layout.addWidget(self._list_widget, 100)

    @property
    def list_widget(self):
        return self._list_widget
    
    def clear(self):
        self._list_widget.clear()



class StaffTreeWidget(TitledTreeWidget):
    def __init__(self, parent=None):
        super().__init__(title="Staff", parent=parent)
        self.tree.setHeaderLabels(["Role", "Name", "Ability", "Reputation", "Personality"])

    def set_staff(self, staff_list):
        self.tree.clear()
        for staff in staff_list:
            item = QTreeWidgetItem([
                staff.role.name,
                staff.person.full_name,
                str(staff.ability),
                staff.reputation_type.name,
                staff.person.personality.name
            ])
            self.tree.addTopLevelItem(item)


class PlayerTreeWidget(TitledTreeWidget):
    def __init__(self, parent=None):
        super().__init__(title="Players", parent=parent)
        self.tree.setHeaderLabels(["Position", "Name", "Ability", "Personality"])

    def set_players(self, player_list):
        self.tree.clear()
        for player in player_list:
            item = QTreeWidgetItem([
                player.position.name,
                player.person.full_name,
                str(player.ability),
                player.person.personality.name
            ])
            self.tree.addTopLevelItem(item)


class CompetitionListWidget(TitledListWidget):
    def __init__(self, parent=None):
        super().__init__(title="Competitions", parent=parent)

    def set_competitions(self, comp_list):
        self.list_widget.clear()
        for comp in comp_list:
            item = QListWidgetItem(comp.name)
            item.setData(Qt.UserRole, comp)
            self.list_widget.addItem(item)


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
        if self ._club is not None:
            self._title.setText(f"{self._club.name}")
            self._staff_list.set_staff(self._club.staff_members())
            self._player_list.set_players(self._club.players())
            self._comp_list.set_competitions(self._club.competitions())


        else:
            self._title.setText(ClubWidget.DEFAULT_TITLE)
            self._staff_list.clear()
            self._player_list.clear()
            self._comp_list.clear()


class ClubView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setAutoFillBackground(True)

        self._club_List = QListWidget(self)
        self._club_List.currentItemChanged.connect(self.on_club_changed)
        self._club_view = ClubWidget(self)

        self._club = None

        layout = QHBoxLayout(self)
        layout.addWidget(self._club_List, 0, Qt.AlignTop | Qt.AlignLeft)
        layout.addWidget(self._club_view, 100)   
        

    def set_club(self, club):
        self._club = club

    def invalidate(self, db_worker: DBObject | None):
        if db_worker is not None:
            clubs = db_worker.db_worker.worker.get_clubs()
            self._club_List.clear()
            for club in clubs:
                item = QListWidgetItem(club.name)
                item.setData(Qt.UserRole, club)
                self._club_List.addItem(item)
        else:
            self._club_List.clear()
            self._club = None


    def on_club_changed(self, current: QListWidgetItem | None, previous: QListWidgetItem | None):
        print("Club changed !")
        if current is not None:
            club = current.data(Qt.UserRole)
           
            self.set_club(club)
            self._club_view.club = self._club
        else:
            self.set_club(None)
            self._club_view.club = None



class LeagueView(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)

        self.title = TitleLabel("", 12)
        self.tree_widget = QTreeWidget()
        self.tree_widget.setFont(QFont("DejaVu Sans", 12))

        layout = QVBoxLayout(self)
        layout.addWidget(self.title, 0, Qt.AlignHCenter | Qt.AlignTop)
        layout.addWidget(self.tree_widget, 100)

    def set_league(self, league: LeagueDB, season: SeasonDB):
        self.title.setText(league.name)
        
        table_data = get_league_table_data(league, season)
        self.tree_widget.clear()
        self.tree_widget.setHeaderLabels(["Pos", "Club", "Ply", "W", "D", "L", "GF", "GA", "GD", "Pts"])
        for ix, d in enumerate(table_data):
            pos = ix + 1
            item = QTreeWidgetItem(
                [
                    str(pos), d["club"].name, str(d["ply"]), str(d["w"]), str(d["d"]), str(d["l"]),
                    str(d["gf"]), str(d["ga"]), str(d["gd"]), str(d["pts"])
                ]
            )
            self.tree_widget.addTopLevelItem(item)

        for c in range(self.tree_widget.columnCount()):
            self.tree_widget.resizeColumnToContents(c)

    def clear(self):
        self.title.clear()
        self.tree_widget.clear()


class HomePage(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)

        self._league_1 = LeagueView()
        self._league_2 = LeagueView()

        league_layout = QHBoxLayout()
        league_layout.addWidget(self._league_1)
        league_layout.addWidget(self._league_2)

        layout = QVBoxLayout(self)
        layout.addLayout(league_layout)


    def invalidate(self):
        pass

    def set_league_1(self, league: LeagueDB, season: SeasonDB):
        self._league_1.set_league(league, season)

    def set_league_2(self, league: LeagueDB, season: SeasonDB):
        self._league_2.set_league(league, season)

    def clear(self):
        self._league_1.clear()
        self._league_2.clear()


class DBMainGameView(QWidget):
    continue_game = Signal(name="advanced_game")
    main_menu = Signal(name="main_menu")

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setAutoFillBackground(True)


        self.tabView = QTabWidget()

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

        self.home_view = HomePage()
        self._club_view = ClubView()

        self._club_list = QListView()
        self._comp_list = QListView()
   

        list_widgets = QWidget()
        list_layout = QHBoxLayout(list_widgets)
        list_layout.addWidget(self._club_list)
        list_layout.addWidget(self._comp_list)



        self.tabView.addTab(self.home_view, "Home")
        self.tabView.addTab(self._club_view, "Clubs")
        self.tabView.addTab(list_widgets, "All Data")

        self.tabView.setCurrentIndex(0)

        layout = QVBoxLayout(self)
        layout.addLayout(top_layout)
        layout.addWidget(self.tabView, 100)


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


            leagues = self._db_worker.db_worker.worker.get_leagues()
            if len(leagues) > 1:
                self.home_view.set_league_1(leagues[0], season)
                self.home_view.set_league_2(leagues[1], season)
            else:
                self.home_view.clear()

        else:
            self.date_label.clear()
            self._club_list.setModel(QStringListModel())
            self._comp_list.setModel(QStringListModel())
            self.home_view.clear()

        self._club_view.invalidate(self._db_worker)

    def has_db_worker(self):
        return self._db_worker is not None


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
        self.setAutoFillBackground(True)
        self.setContentsMargins(QMargins(0, 0, 0, 0))

        self.setMinimumSize(1920, 1080)
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
