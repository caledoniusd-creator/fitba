from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *


from core.world_time import DAYS_IN_WEEK, WEEKS_IN_YEAR


from .utils import change_font


class DayView(QFrame):
    size = QSize(32, 32)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.Shape.Panel | QFrame.Shadow.Plain)
        self.setFixedSize(DayView.size)

    def sizeHint(self):
        return DayView.size


class WeekView(QFrame):
    selected_week = pyqtSignal(int, name="selected")

    def __init__(self, week_number: int, parent=None):
        super().__init__(parent)
        self.week_number = week_number
        self._selected = False
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Plain)
        self.setAutoFillBackground(True)

        self.week_number_label = QLabel(str(self.week_number))
        change_font(self.week_number_label, 2, True)
        self.week_number_label.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )

        self.days = [DayView() for _ in range(DAYS_IN_WEEK)]

        layout = QHBoxLayout(self)
        layout.addWidget(
            self.week_number_label,
            0,
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
        )
        for day in self.days:
            layout.addWidget(
                day, 0, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
            )
        layout.addSpacerItem(QSpacerItem(16, 16))
        self.update_frame()

    @property
    def selected(self):
        return self._selected

    @selected.setter
    def selected(self, is_selected: bool):
        if is_selected != self._selected:
            self._selected = is_selected
            self.update_frame()
            if self._selected is True:
                self.selected_week.emit(self.week_number)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.selected = not self.selected

    def update_frame(self):
        self.setFrameStyle(
            QFrame.Shape.Panel
            | (QFrame.Shadow.Raised if not self.selected else QFrame.Shadow.Sunken)
        )


class SeasonView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._weeks = [WeekView(i + 1) for i in range(WEEKS_IN_YEAR)]
        self._weeks[0].selected = True

        layout = QVBoxLayout(self)
        for week in self._weeks:
            layout.addWidget(
                week, 0, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
            )
            week.selected_week.connect(self.on_selected_week)

    def on_selected_week(self, week_number):
        for week in self._weeks:
            if week.week_number != week_number:
                week.selected = False

    def set_current_week(self, week: int):
        if 0 > week > WEEKS_IN_YEAR:
            raise ValueError("invalid week")
        ix = week - 1
        self._weeks[ix].selected = True

    def week_widget(self):
        for w in self._weeks:
            if w.selected is True:
                return w
        return None


class SeasonWeekScroll(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._season_view = SeasonView()
        self.setWidget(self._season_view)

        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)

    def set_current_week(self, week: int):
        self._season_view.set_current_week(week)
        widget = self._season_view.week_widget()
        if widget:
            self.ensureWidgetVisible(widget)


