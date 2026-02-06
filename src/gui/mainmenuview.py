
from PySide6.QtCore import Qt
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


from .utils import change_font, hline, set_dark_bg


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

        btn_font = QFont("DejaVu Sans", 16, QFont.Bold)
        for btn in [new_game_btn, load_game_btn, quit_game_btn]:
            # change_font(btn, 8, True)
            btn.setFont(btn_font)
            btn.setFixedSize(QSize(320, 48))

        btn_frame = QFrame()
        btn_frame.setAutoFillBackground(True)
        btn_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        set_dark_bg(btn_frame)

        button_layout = QVBoxLayout(btn_frame)
        button_layout.setContentsMargins(QMargins(64, 64, 64, 64))
        button_layout.setSpacing(8)
        button_layout.addWidget(new_game_btn, 0, Qt.AlignHCenter | Qt.AlignTop)
        button_layout.addWidget(load_game_btn, 0, Qt.AlignHCenter | Qt.AlignTop)
        button_layout.addWidget(quit_game_btn, 0, Qt.AlignHCenter | Qt.AlignTop)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(QMargins(32, 32, 32, 32))
        layout.addWidget(title, 0, Qt.AlignHCenter | Qt.AlignTop)
        layout.addWidget(hline())
        layout.addStretch(25)
        layout.addWidget(btn_frame, 0, Qt.AlignHCenter | Qt.AlignTop)
        layout.addStretch(50)