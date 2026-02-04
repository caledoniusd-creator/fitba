
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