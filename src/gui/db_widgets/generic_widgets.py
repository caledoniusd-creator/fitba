

from PySide6.QtCore import Qt
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *




class TitleLabel(QLabel):
    def __init__(self, title: str, size: int = 16, parent=None):
        super().__init__(parent=parent)
        self.setText(title)
        self.setAlignment(Qt.AlignCenter)
        self.setFont(QFont("DejaVu Sans", size, QFont.Bold))


class TitledTreeWidget(QFrame):
    def __init__(self, title: str, parent=None):
        super().__init__(parent=parent)
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        self.setAutoFillBackground(True)

        self._tree = QTreeWidget(self)

        layout = QVBoxLayout(self)
        layout.addWidget(TitleLabel(title, 12), 0, Qt.AlignTop | Qt.AlignHCenter)
        layout.addWidget(self._tree, 100)

    @property
    def tree(self):
        return self._tree

    def clear(self):
        self._tree.clear()


class TitledListWidget(QFrame):
    def __init__(self, title: str, parent=None):
        super().__init__(parent=parent)
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        self.setAutoFillBackground(True)

        self._list_widget = QListWidget(self)

        layout = QVBoxLayout(self)
        layout.addWidget(TitleLabel(title, 12), 0, Qt.AlignTop | Qt.AlignHCenter)
        layout.addWidget(self._list_widget, 100)

    @property
    def list_widget(self):
        return self._list_widget

    def clear(self):
        self._list_widget.clear()