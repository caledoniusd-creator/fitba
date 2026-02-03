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
    """
    A QWidget that displays a collection of pages with navigation controls.
    This widget manages multiple pages (QWidget instances) in a stacked layout,
    providing back and next buttons to navigate between them. Pages cycle around
    when reaching the end or beginning.
    Attributes:
        _title (str): The title of the widget displayed at the top.
        _pages (List[QWidget]): List of page widgets managed by this widget.
        _stack (QStackedWidget): The stacked widget containing all pages.
    Methods:
        __init__(title: str, pages: List[QWidget] = list(), parent=None):
            Initialize the PagesWidget with a title and optional list of pages.
        on_back():
            Navigate to the previous page. Wraps around to the last page if on the first page.
        on_next():
            Navigate to the next page. Wraps around to the first page if on the last page.
        set_pages(pages: List[QWidget] | None = None):
            Replace the current pages with a new list of pages. Cleans up old pages
            and updates the stacked widget. Disables the widget if no pages are provided.
    """
    
    def __init__(self, title: str, pages: List[QWidget] = list(), parent=None):
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


class NextContinueStackedWidget(QWidget):
    continue_pressed = pyqtSignal(name="continue_pressed")

    def __init__(self, parent=None):
        super().__init__(parent)

        self._stack_widget = QStackedWidget()
        self.next_btn = QPushButton("Next")
        self.next_btn.clicked.connect(self.on_next)
        self.continue_btn = QPushButton("Continue")
        self.continue_btn.clicked.connect(self.continue_pressed)

        for btn in [self.next_btn, self.continue_btn]:
            change_font(btn, 2, True)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch(100)
        btn_layout.addWidget(self.next_btn, 0)
        btn_layout.addWidget(self.continue_btn, 0)

        layout = QVBoxLayout(self)
        layout.addLayout(btn_layout)
        layout.addWidget(self._stack_widget, 100)

        self.update_btns()
        self.setEnabled(False)

    def set_pages(self, new_pages: List[QWidget] | None = None):
        widgets = [
            self._stack_widget.widget(i) for i in range(self._stack_widget.count())
        ]
        for w in widgets:
            self._stack_widget.removeWidget(w)
            w.deleteLater()

        if new_pages:
            for page in new_pages:
                self._stack_widget.addWidget(page)

        self.update_btns()

        if self._stack_widget.count() > 0:
            self._stack_widget.setCurrentIndex(0)
            self.setEnabled(True)
        else:
            self.setEnabled(False)

    def update_btns(self):
        num_pages = self._stack_widget.count()
        if num_pages > 0:
            cur_ix = self._stack_widget.currentIndex()
            if cur_ix < num_pages - 1:
                self.next_btn.setVisible(True)
                self.continue_btn.setVisible(False)
            else:
                self.next_btn.setVisible(False)
                self.continue_btn.setVisible(True)
        else:
            self.next_btn.setVisible(False)
            self.continue_btn.setVisible(True)

    def on_next(self):
        num_pages = self._stack_widget.count()
        cur_ix = self._stack_widget.currentIndex()
        next_ix = cur_ix + 1
        if next_ix < num_pages:
            self._stack_widget.setCurrentIndex(next_ix)
        self.update_btns()
