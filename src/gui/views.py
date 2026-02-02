from typing import List

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *


from core.competition import CompetitionType
from core.fixture import FixtureWorker, ResultWorker
from core.league_table import LeagueTableWorker
from core.world import WorldState, WorldStateEngine


from .utils import change_font
from .generic_widgets import PagesWidget
from .view_widgets import (
    WorldTimeLabel,
    FixtureList,
    ResultsList,
    LeagueTableWidget,
    ClubListWidget,
    ClubListView,
)
from .week_view import SeasonWeekScroll


class ViewBase(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)


class MainMenuView(ViewBase):
    new_game = pyqtSignal(name="new game")
    load_game = pyqtSignal(name="load game")
    quit_game = pyqtSignal(name="quit")

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Main Menu")

        title = QLabel(self.windowTitle())
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        change_font(title, 16, True)

        new_game_btn = QPushButton("New Game")
        new_game_btn.clicked.connect(self.new_game)

        load_game_btn = QPushButton("Load Game")
        load_game_btn.clicked.connect(self.load_game)

        quit_game_btn = QPushButton("Quit")
        quit_game_btn.clicked.connect(self.quit_game)

        for btn in [new_game_btn, load_game_btn, quit_game_btn]:
            change_font(btn, 8, True)
        button_layout = QVBoxLayout()
        button_layout.addWidget(title)
        button_layout.addStretch(10)
        button_layout.addWidget(new_game_btn, 0)
        button_layout.addWidget(load_game_btn)
        button_layout.addWidget(quit_game_btn)
        button_layout.addStretch(10)

        layout = QHBoxLayout(self)

        layout.addStretch(10)
        layout.addLayout(button_layout)
        layout.addStretch(10)


class GameViewTopBar(QFrame):
    game_continue = pyqtSignal(name="game continue")

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Plain)

        self.world_time_lbl = WorldTimeLabel()
        self.state_lbl = QLabel()

        continue_btn = QPushButton("Continue")
        continue_btn.clicked.connect(self.game_continue)
        change_font(continue_btn, 2, True)

        layout = QHBoxLayout(self)
        layout.addWidget(
            self.world_time_lbl,
            0,
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
        )
        layout.addStretch(100)
        layout.addWidget(
            self.state_lbl,
            0,
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
        )
        layout.addWidget(
            continue_btn, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )

    def invalidate(self, world_engine: WorldStateEngine):
        if world_engine:
            self.world_time_lbl.set_time(world_engine.world_time)
            self.state_lbl.setText(
                f"{world_engine.state.name} ({world_engine.state.value})"
            )
        else:
            self.world_time_lbl.set_time(None)
            self.state_lbl.clear()


class GameTabBase(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._world_engine: WorldStateEngine | None = None

        self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Plain)

    @property
    def world_engine(self):
        return self._world_engine

    @world_engine.setter
    def world_engine(self, new_world_engine: WorldStateEngine | None):
        if new_world_engine != self._world_engine:
            self._world_engine = new_world_engine

            self.set_data()

    def set_data(self):
        pass

    def invalidate(self):
        pass


class GameLeagueTableView(GameTabBase):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._stack = PagesWidget("League Tables")
        layout = QVBoxLayout(self)
        layout.addWidget(self._stack)

    def invalidate(self):
        pages = []
        if self._world_engine:
            leagues = [
                comp
                for comp in self._world_engine.world.competitions
                if comp.type.value == CompetitionType.LEAGUE.value
            ]
            for league in leagues:
                try:
                    ltw = LeagueTableWorker(
                        league,
                        self._world_engine.world_worker.results_for_competition(league),
                    )
                    pages.append(LeagueTableWidget(league, ltw.get_sorted_table()))
                except KeyError:
                    pass
        self._stack.set_pages(pages)


class GameClubsView(GameTabBase):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self._club_list = ClubListWidget()
        self._clubs_widget = ClubListView()

        layout = QVBoxLayout(self)
        layout.addWidget(self._club_list)
        layout.addWidget(self._clubs_widget)

    def set_data(self):
        if self._world_engine:
            clubs = self._world_engine.world.club_pool.get_all_clubs()
        else:
            clubs = []
        for w in [self._club_list, self._clubs_widget]:
            w.set_clubs(clubs)

    def invalidate(self):
        pass


class GameHomeWidget(GameTabBase):
    game_continue = pyqtSignal(name="game continue")

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.top_bar = GameViewTopBar()
        self.top_bar.game_continue.connect(self.game_continue)

        self.world_time_lbl = WorldTimeLabel()

        self.season_scroll = SeasonWeekScroll()

        self.central_view = QWidget()

        mid_layout = QHBoxLayout()
        mid_layout.addWidget(self.season_scroll, Qt.AlignmentFlag.AlignLeft)
        mid_layout.addWidget(self.central_view, 100)

        layout = QVBoxLayout(self)
        layout.addWidget(self.top_bar)
        layout.addLayout(mid_layout, 100)

    # def set_data(self):
    #     self.central_view.world_engine = self.world_engine

    def invalidate(self):
        self.top_bar.invalidate(self.world_engine)
        if self._world_engine:
            self.season_scroll.set_current_week(self._world_engine.world_time.week)
        # self.central_view.invalidate()


class GameViewTabs(QTabWidget):
    game_continue = pyqtSignal(name="game continue")

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._world_engine: WorldStateEngine | None = None

        self._home_widget = GameHomeWidget()
        self._home_widget.game_continue.connect(self.game_continue)
        self.addTab(self._home_widget, "Home")

        self._clubs_widget = GameClubsView()
        self.addTab(self._clubs_widget, "Clubs")

        self._league_tables_widget = GameLeagueTableView()
        self.addTab(self._league_tables_widget, "League Tables")

        self.invalidate()
        self.setCurrentIndex(0)
        QApplication.instance().processEvents()

    @property
    def world_engine(self):
        return self._world_engine

    @world_engine.setter
    def world_engine(self, new_world_engine: WorldStateEngine | None):
        if new_world_engine != self._world_engine:
            self._world_engine = new_world_engine
            for ix in range(self.count()):
                widget = self.widget(ix)
                widget.world_engine = new_world_engine

            self.invalidate()

    def invalidate(self):
        for ix in range(self.count()):
            widget = self.widget(ix)
            widget.invalidate()


class MajorGameView(QWidget):
    def __init__(self, title: str = "<unamed>", parent=None):
        super().__init__(parent)
        lbl = QLabel(title)
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        change_font(lbl, 12, True)

        layout = QVBoxLayout(self)
        layout.addWidget(lbl, 100, Qt.AlignmentFlag.AlignCenter)


class NextContinueStackedWidget(QWidget):
    game_continue = pyqtSignal(name="game continue")

    def __init__(self, parent=None):
        super().__init__(parent)

        self._stack_widget = QStackedWidget()
        self.next_btn = QPushButton("Next")
        self.next_btn.clicked.connect(self.on_next)
        self.continue_btn = QPushButton("Continue")
        self.continue_btn.clicked.connect(self.game_continue)

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


class GameView(ViewBase):
    main_menu = pyqtSignal(name="main menu")
    world_changed = pyqtSignal(name="world_changed")
    game_continue = pyqtSignal(name="game continue")

    def __init__(self, parent=None):
        super().__init__(parent)
        self._world_engine: WorldStateEngine | None = None

        self.setWindowTitle("Game")

        self.view_stack = QStackedWidget()

        self.game_tabs = GameViewTabs()
        self.game_tabs.game_continue.connect(self.game_continue)

        self.game_alt_stack = NextContinueStackedWidget()
        self.game_alt_stack.game_continue.connect(self.game_continue)

        self.view_stack.addWidget(self.game_tabs)
        self.view_stack.addWidget(self.game_alt_stack)

        self.view_stack.setCurrentWidget(self.game_tabs)

        layout = QVBoxLayout(self)
        layout.addWidget(self.view_stack)

        self.world_changed.connect(self.on_world_changed)
        self.game_continue.connect(self.on_game_continue)

    @property
    def world_engine(self):
        return self._world_engine

    @world_engine.setter
    def world_engine(self, new_world_engine: WorldStateEngine | None):
        if new_world_engine != self._world_engine:
            print("New World")
            self._world_engine = new_world_engine
            self.world_changed.emit()

    def invalidate(self):
        if self._world_engine:
            if self._world_engine.state.value == WorldState.NewSeason.value:
                new_pages = [
                    MajorGameView("New Season"),
                ]
                self.game_alt_stack.set_pages(new_pages)
                self.view_stack.setCurrentWidget(self.game_alt_stack)

            elif self._world_engine.state.value == WorldState.PostSeason.value:
                new_pages = [
                    MajorGameView(f"Post Season {self._world_engine.world_time.year}"),
                ]
                self.game_alt_stack.set_pages(new_pages)
                self.view_stack.setCurrentWidget(self.game_alt_stack)

            elif self._world_engine.state.value == WorldState.PreFixtures.value:
                fixtures = self._world_engine.fixtures
                new_pages = list()
                if fixtures:
                    groups = FixtureWorker(fixtures=fixtures).group_by_competition()
                    for comp_fixtures in groups:
                        title = f"{comp_fixtures[0].name} Fixtures"
                        fixture_list = FixtureList(title=title, auto_hide=False)
                        fixture_list.set_fixtures(comp_fixtures[1])
                        new_pages.append(fixture_list)
                    self.game_alt_stack.set_pages(new_pages)

                self.view_stack.setCurrentWidget(self.game_alt_stack)

            elif self._world_engine.state.value == WorldState.ProcessingFixtures.value:
                new_pages = [
                    MajorGameView("Processing Fixtures"),
                ]
                self.game_alt_stack.set_pages(new_pages)
                self.view_stack.setCurrentWidget(self.game_alt_stack)

            elif self._world_engine.state.value == WorldState.PostFixtures.value:
                results = self._world_engine.results
                new_pages = list()
                if results:
                    groups = ResultWorker(results=results).group_by_competition()
                    for comp_result in groups:
                        title = f"{comp_result[0].name} Results"
                        result_list = ResultsList(title=title, auto_hide=False)
                        result_list.set_results(comp_result[1])
                        new_pages.append(result_list)
                    self.game_alt_stack.set_pages(new_pages)

                self.view_stack.setCurrentWidget(self.game_alt_stack)

            else:
                self.view_stack.setCurrentWidget(self.game_tabs)
        else:
            self.view_stack.setCurrentWidget(self.game_tabs)

        self.game_tabs.invalidate()

    def on_world_changed(self):
        print(f"World changed: {self._world_engine.world}")
        self.game_tabs.world_engine = self._world_engine
        self.invalidate()

    def on_game_continue(self):
        self.world_engine.advance_game()
        self.invalidate()

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key.Key_F12:
            event.setAccepted(True)
            self.main_menu.emit()
        else:
            super().keyReleaseEvent(event)
