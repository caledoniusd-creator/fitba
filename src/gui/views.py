
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *


from core.world import World, WorldWorker



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
        font = QFont(title.font())
        font.setBold(True)
        font.setPointSize(font.pointSize() + 4)
        title.setFont(font)

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


class GameView(ViewBase):
    main_menu = pyqtSignal(name="main menu")
    world_changed = pyqtSignal(name="world_changed")

    def __init__(self, parent=None):
        super().__init__(parent)
        self._world: World | None = None
        self._world_worker: WorldWorker | None = None

        self.setWindowTitle("Game")
        self.world_changed.connect(self.on_world_changed)

    @property
    def world(self):
        return self._world
    
    @world.setter
    def world(self, new_world: World | None):
        if new_world != self._world:
            self._world = new_world
            if self._world is None and self._world_worker is not None:
                self._world_worker = None
            else:
                self._world_worker = WorldWorker(self._world)
            self.world_changed.emit()

    def on_world_changed(self):
        print(f"World changed: {self._world}")
        pass

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key.Key_F12:    
            event.setAccepted(True)
            self.main_menu.emit()
        else:
            super().keyReleaseEvent(event)