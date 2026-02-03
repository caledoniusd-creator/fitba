

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *



class ViewBase(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        