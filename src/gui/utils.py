
from PySide6.QtCore import Qt
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


def change_font(widget: QWidget, increment: int, bold: bool = False):
    font = QFont(widget.font())
    font.setBold(bold)
    font.setPointSize(font.pointSize() + increment)
    widget.setFont(font)

def hline():
    frame = QFrame()
    frame.setFrameStyle(QFrame.HLine | QFrame.Plain)
    return frame

def vline():
    frame = QFrame()
    frame.setFrameStyle(QFrame.VLine | QFrame.Plain)
    return frame

def set_dark_bg(widget):
    palette = QPalette(widget.palette())
    palette.setColor(QPalette.ColorRole.Window, QColor(224, 224, 224))
    widget.setPalette(palette)

def set_white_bg(widget):
    palette = QPalette(widget.palette())
    palette.setColor(QPalette.ColorRole.Window, QColor(255, 255, 255))
    widget.setPalette(palette)