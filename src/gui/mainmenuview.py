
from PySide6.QtCore import Qt
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


from .utils import change_font, hline


from .viewbase import ViewBase


class MainMenuView(ViewBase):
    new_game = Signal(name="new game")
    load_game = Signal(name="load game")
    quit_game = Signal(name="quit")

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Main Menu")

        title = QLabel(self.windowTitle())
        title.setAlignment(Qt.AlignCenter)
        change_font(title, 16, True)

        new_game_btn = QPushButton("New Game")
        new_game_btn.clicked.connect(self.new_game)

        load_game_btn = QPushButton("Load Game")
        load_game_btn.clicked.connect(self.load_game)

        quit_game_btn = QPushButton("Quit")
        quit_game_btn.clicked.connect(self.quit_game)

        for btn in [new_game_btn, load_game_btn, quit_game_btn]:
            change_font(btn, 8, True)
            btn.setFixedWidth(256)

        button_layout = QVBoxLayout()
        button_layout.addStretch(25)
        button_layout.addWidget(new_game_btn, 0, Qt.AlignHCenter | Qt.AlignTop)
        button_layout.addWidget(load_game_btn, 0, Qt.AlignHCenter | Qt.AlignTop)
        button_layout.addWidget(quit_game_btn, 0, Qt.AlignHCenter | Qt.AlignTop)
        button_layout.addStretch(50)

        layout = QVBoxLayout(self)

        layout.addWidget(title)
        layout.addWidget(hline())
        layout.addLayout(button_layout)