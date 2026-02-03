
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *


from .utils import change_font


from .viewbase import ViewBase


class MainMenuView(ViewBase):
    new_game = pyqtSignal(name="new game")
    load_game = pyqtSignal(name="load game")
    quit_game = pyqtSignal(name="quit")

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Main Menu")

        title = QLabel(self.windowTitle())
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        change_font(title, 16, True)

        new_game_btn = QPushButton("New Game")
        new_game_btn.clicked.connect(self.new_game)

        load_game_btn = QPushButton("Load Game")
        load_game_btn.clicked.connect(self.load_game)

        quit_game_btn = QPushButton("Quit")
        quit_game_btn.clicked.connect(self.quit_game)

        for btn in [new_game_btn, load_game_btn, quit_game_btn]:
            change_font(btn, 8, True)
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