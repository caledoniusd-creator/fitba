from enum import Enum, unique, auto
from datetime import datetime
from sys import argv
from traceback import format_exc

from PySide6.QtCore import Qt
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


from src.__version__ import __version__
from src.core.world import World
from src.core.workers import create_test_world, WorldStateEngine

from .mainmenuview import MainMenuView
from .game_views import GameView

from .utils import change_font, set_white_bg

@unique
class AppState(Enum):
    MainMenu = auto()
    GameView = auto()


class BusyPage(QWidget):
    def __init__(self, message: str="", parent=None):
        super().__init__(parent=parent)
        self.setAutoFillBackground(True)

        set_white_bg(self)
        self._update_timer = 0

        self._busy = QProgressBar()
        self._busy.setRange(0, 0)
        
        self._message = QLabel(message)
        self._message.setAlignment(Qt.AlignCenter)
        change_font(self._message, 8, True)

        self._timer_lbl = QLabel()
        
        font = QFont("DejaVu Sans Mono", 12, QFont.Bold)
        self._timer_lbl.setFont(font)

        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(QMargins(64, 64, 64, 64))
        layout.addWidget(self._message, 100)
        layout.addWidget(self._timer_lbl, 0, Qt.AlignLeft| Qt.AlignBottom)
        layout.addWidget(self._busy, 0, Qt.AlignBottom)


        self.cur_time = datetime.now()

    def set_message(self, message):
        self._message.setText(message)

    def clear_message(self):
        self._message.clear()

    def showEvent(self, event):
        self.reset_current_time()
        self.start_timer()
        super().showEvent(event)

    def hideEvent(self, event):
        self.stop_timer()
        print((f"Busy for {self.delta_time():.2f} seconds"))
        super().hideEvent(event)
    
    def start_timer(self):
        self.stop_timer()
        self._update_timer = self.startTimer(10)

    def stop_timer(self):
        if self._update_timer:
            self.killTimer(self._update_timer)
            self._update_timer = 0

    def reset_current_time(self):
        self.cur_time = datetime.now()

    def delta_time(self):
        return (datetime.now() - self.cur_time).total_seconds()
    
    def update_time_label(self):
        self._timer_lbl.setText(f"{self.delta_time():.2f} seconds")

    def timerEvent(self, event):
        if self._update_timer and event.timerId() == self._update_timer:
            self.update_time_label()
            event.accept()
        else:
            super().timerEvent(event)


class NewGameThread(QThread):
    def __init__(self, funct: callable, parent=None):
        super().__init__(parent=parent)
        self._funct = funct
        self.world: World | None = None

    def run(self):
        self.world = self._funct()
        


class AppMainWindow(QStackedWidget):
    def __init__(self, window_size: QSize = QSize(1920, 1024), parent=None):
        super().__init__(parent=parent)
        self.setFixedSize(window_size)
        self.setWindowTitle(f"Fitba - {__version__}")

        self._main_menu = MainMenuView()
        self._main_menu.new_game.connect(self._on_new_game)
        self._main_menu.load_game.connect(self.on_load_game)
        self._main_menu.quit_game.connect(self.close)

        self._game_menu = GameView()
        self._game_menu.main_menu.connect(self.on_main_menu)
        
        self._busy_view = BusyPage()
        
        main_menu_ix = self.addWidget(self._main_menu)
        self.addWidget(self._game_menu)
        self.addWidget(self._busy_view)
        

        self.setCurrentIndex(main_menu_ix)

        self.show()
        self.center_on_screen()

    def center_on_screen(self):
        screen = QGuiApplication.primaryScreen().availableGeometry()
        frame = self.frameGeometry()
        frame.moveCenter(screen.center())
        self.move(frame.topLeft())

    def _on_new_game(self):
        
        self._busy_view.set_message("Creating New Game")
        self.setCurrentWidget(self._busy_view)

        thread = NewGameThread(create_test_world, self)
        thread.finished.connect(self._on_new_game_ready)
        thread.start()

    def _on_new_game_ready(self):
        new_game_thread = self.sender()
        if new_game_thread and new_game_thread.world:
            self._game_menu.world_engine = WorldStateEngine(new_game_thread.world)
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
        print(f"Fonts: {', '.join(QFontDatabase.families())}")
        print("Styles: " + ", ".join(QStyleFactory.keys()))
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


def run_gui_application():
    GUIApplication().run()
