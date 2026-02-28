import logging

from PySide6.QtCore import Qt
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


class TitleLabel(QLabel):
    """
    Simple Label to act as title
    """

    def __init__(self, title: str | None = None, size: int = 16, parent=None):
        super().__init__(parent=parent)
        self.setText(title if title else "N/A")
        self.setAlignment(Qt.AlignCenter)
        self.setFont(QFont("DejaVu Sans", size, QFont.Bold))


class TitledTreeWidget(QFrame):
    """
    Tree Widget with Title Label
    """

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
    """
    List Widget with Title Label
    """

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


class QtLogEmitter(QObject):
    message = Signal(str)


class QTextEditHandler(logging.Handler):
    """
    A logging handler that safely forwards log messages to a QTextEdit via Qt signals.
    """

    def __init__(self, emitter: QtLogEmitter):
        super().__init__()
        self.emitter = emitter

    def emit(self, record: logging.LogRecord) -> None:
        try:
            msg = self.format(record)
        except Exception:
            self.handleError(record)
            return
        self.emitter.message.emit(msg)


class LogWindow(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        # self.setWindowFlags(Qt.Tool)
        self.setReadOnly(True)
        self.setLineWrapMode(QTextEdit.NoWrap)
        self.setMinimumSize(256, 96)

        # Emitter + handler
        self._emitter = QtLogEmitter()
        self._emitter.message.connect(self._append_log)

        self.qt_handler = QTextEditHandler(self._emitter)
        self.qt_handler.setLevel(logging.DEBUG)
        self.qt_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s"
            )
        )

        # Add handler to root logger (or use a named logger, your call)
        root = logging.getLogger()
        root.setLevel(logging.DEBUG)
        root.addHandler(self.qt_handler)

        # Optional: keep console logging too
        if not any(isinstance(h, logging.StreamHandler) for h in root.handlers):
            console = logging.StreamHandler()
            console.setLevel(logging.DEBUG)
            console.setFormatter(self.qt_handler.formatter)
            root.addHandler(console)

    def _append_log(self, msg: str) -> None:
        # Append and keep view pinned to bottom
        self.append(msg)
        self.moveCursor(QTextCursor.End)
