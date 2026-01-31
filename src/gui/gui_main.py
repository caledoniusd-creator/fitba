from enum import Enum, unique, auto
from sys import argv
from traceback import format_exc

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *


from .views import MainMenuView, GameView

from src.core.world import create_test_world, WorldStateEngine


@unique
class AppState(Enum):
    MainMenu = auto()
    GameView = auto()


class AppMainWindow(QStackedWidget):
    def __init__(self, window_size: QSize = QSize(1920, 1024), parent=None):
        super().__init__(parent=parent)
        self.setFixedSize(window_size)
        self.setWindowTitle("Fitba")

        self._main_menu = MainMenuView()
        self._main_menu.new_game.connect(self.on_new_game)
        self._main_menu.load_game.connect(self.on_load_game)
        self._main_menu.quit_game.connect(self.close)

        self._game_menu = GameView()
        self._game_menu.main_menu.connect(self.on_main_menu)

        main_menu_ix = self.addWidget(self._main_menu)
        self.addWidget(self._game_menu)

        self.setCurrentIndex(main_menu_ix)

        self.show()
        self.center_on_screen()

    def center_on_screen(self):
        screen = QGuiApplication.primaryScreen().availableGeometry()
        frame = self.frameGeometry()
        frame.moveCenter(screen.center())
        self.move(frame.topLeft())

    def on_new_game(self):
        self._game_menu.world_engine = WorldStateEngine(create_test_world())
        self.setCurrentWidget(self._game_menu)

    def on_load_game(self):
        pass

    def on_main_menu(self):
        self.setCurrentWidget(self._main_menu)


class GUIApplication(QApplication):
    def __init__(self, args=argv):
        super().__init__(args)
        self.widget = None

    def run(self):
        # print("Styles: " + ", ".join(QStyleFactory.keys()))
        # QApplication.setStyle(QStyleFactory.create("Windows"))
        QApplication.setStyle(QStyleFactory.create("Fusion"))

        self.widget = AppMainWindow()
        self.widget.show()

        try:
            rc = self.exec()
        except Exception as e:
            print(format_exc())
            print(e)
            pass


def run_gui_application():
    GUIApplication().run()
