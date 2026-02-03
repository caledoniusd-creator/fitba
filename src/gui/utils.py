from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *


def change_font(widget: QWidget, increment: int, bold: bool = False):
    font = QFont(widget.font())
    font.setBold(bold)
    font.setPointSize(font.pointSize() + increment)
    widget.setFont(font)

def hline():
    frame = QFrame()
    frame.setFrameStyle(QFrame.Shape.HLine | QFrame.Shadow.Plain)
    return frame

def vline():
    frame = QFrame()
    frame.setFrameStyle(QFrame.Shape.VLine | QFrame.Shadow.Plain)
    return frame