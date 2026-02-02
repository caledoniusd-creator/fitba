from typing import List


from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *


from .utils import change_font


class WidgetList(QWidget):
    """
    A custom QWidget container that manages a list of widgets with a title and optional auto-hiding.
    This widget provides a vertical layout with a title label at the top, followed by a
    customizable list of child widgets. It can automatically hide itself when empty if
    auto_hide is enabled.
    Attributes:
        widget_layout (QVBoxLayout): The layout containing the managed widgets.
    Properties:
        has_widgets (bool): Returns True if the widget list contains any widgets, False otherwise.
    """

    def __init__(
        self,
        title: str,
        orientation: Qt.Orientation = Qt.Orientation.Vertical,
        auto_hide: bool = False,
        parent=None,
    ):
        super().__init__(parent)
        self._auto_hide = auto_hide
        self._widgets = []
        self.widget_layout = (
            QVBoxLayout() if orientation == Qt.Orientation.Vertical else QHBoxLayout()
        )

        title_lbl = QLabel(title)
        title_lbl.setAlignment(
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop
        )
        change_font(title_lbl, 2, True)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(
            title_lbl, 0, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop
        )
        main_layout.addLayout(self.widget_layout)
        main_layout.addStretch(10)

        self.update_visibility()

    @property
    def has_widgets(self):
        return True if self._widgets else False

    def update_visibility(self):
        if self._auto_hide is True:
            self.setVisible(True if self.has_widgets else False)

    def clear_widgets(self, update_is_visible: bool = True):
        for w in self._widgets:
            self.widget_layout.removeWidget(w)
            w.deleteLater()
        self._widgets.clear()

        if update_is_visible:
            self.update_visibility()

    def set_widgets(self, widgets: List[QWidget] = []):
        self.clear_widgets(False)
        for w in widgets:
            self._widgets.append(w)
            self.widget_layout.addWidget(
                w, 0, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop
            )

        self.update_visibility()


class PagesWidget(QWidget):
    def __init__(self, title: str, pages: List[QWidget]=list(), parent=None):
        super().__init__(parent=parent)
        self._title = title
        self._pages = list(pages)

        self._stack = QStackedWidget()

        btn_back = QToolButton()
        btn_back.setText("\u2b05")
        btn_back.clicked.connect(self.on_back)

        btn_next = QToolButton()
        btn_next.setText("\u27a1")
        btn_next.clicked.connect(self.on_next)

        for btn in [btn_back, btn_next]:
            change_font(btn, 8, True)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch(100)
        btn_layout.addWidget(btn_back)
        btn_layout.addWidget(btn_next)

        self.setWindowTitle(self._title)
        title_lbl = QLabel(self._title)
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        change_font(title_lbl, 4, True)

        layout = QVBoxLayout(self)
        layout.addWidget(
            title_lbl, 0, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop
        )
        layout.addWidget(self._stack, 100)
        layout.addLayout(btn_layout)

        self.set_pages(pages)

    def on_back(self):
        ix = (self._stack.currentIndex() - 1) % self._stack.count()
        self._stack.setCurrentIndex(ix)

    def on_next(self):
        ix = (self._stack.currentIndex() + 1) % self._stack.count()
        self._stack.setCurrentIndex(ix)

    def set_pages(self, pages: List[QWidget] | None = None):
        for w in self._pages:
            self._stack.removeWidget(w)
            w.deleteLater()

        self._pages.clear()

        for p in pages:
            self._pages.append(p)
            self._stack.addWidget(p)

        if self._stack.count():
            self._stack.setCurrentIndex(0)
        self.setEnabled(True if self._stack.count() > 0 else False)


class PagesDialog(QDialog):
    def __init__(self, title: str, pages: List[QWidget], parent=None):
        super().__init__(parent=parent)
        self.pages = PagesWidget(title=title, pages=pages)

        layout = QVBoxLayout(self)
        layout.addWidget(self.pages, 1)
