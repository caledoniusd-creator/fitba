from typing import List

from PySide6.QtCore import Qt
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


from core.competition import CompetitionType
from core.fixture import FixtureWorker, ResultWorker
from core.league_table import LeagueTableWorker
from core.workers import WorldState, WorldStateEngine


from .utils import change_font, set_dark_bg
from .generic_widgets import PagesWidget, NextContinueStackedWidget
from .view_widgets import (
    WorldTimeLabel,
    FixtureList,
    ResultsList,
    LeagueTableWidget,
    ClubsTableListWidget,
    ClubListView,
)
from .club_widgets import ClubsListWidget, ClubInfoWidget
from .week_view import SeasonWeekScroll
from .viewbase import ViewBase


class GameViewTopBar(QFrame):

    game_continue = Signal(name="game continue")
    run_to_post_season = Signal(name="run to post season")
    advance_new_week = Signal(name="advance new week")

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)

        self.world_time_lbl = WorldTimeLabel()
        self.state_lbl = QLabel()

        continue_btn = QPushButton("\u21a6")
        continue_btn.setToolTip("Continue")
        continue_btn.clicked.connect(self.game_continue)

        new_week_btn = QPushButton("\u21d2")
        new_week_btn.setToolTip("To new week")
        new_week_btn.clicked.connect(self.advance_new_week)

        end_season_btn = QPushButton("\u21db")
        end_season_btn.setToolTip("To end of Season")
        end_season_btn.clicked.connect(self.run_to_post_season)

        btn_frame = QFrame()
        btn_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        btn_frame.setAutoFillBackground(True)
        set_dark_bg(btn_frame)
        btn_layout = QHBoxLayout(btn_frame)
        btn_layout.setContentsMargins(QMargins(4, 4, 4, 4))
        btn_layout.setSpacing(4)
        btn_layout.addStretch(100)

        for btn in [end_season_btn, new_week_btn, continue_btn]:
            change_font(btn, 16, True)
            btn.setFixedSize(64, 24)
            btn_layout.addWidget(btn, 0, Qt.AlignRight | Qt.AlignVCenter)

        layout = QHBoxLayout(self)
        layout.addWidget(
            self.world_time_lbl,
            0,
            Qt.AlignRight | Qt.AlignVCenter,
        )
        layout.addStretch(100)
        layout.addWidget(
            self.state_lbl,
            0,
            Qt.AlignRight | Qt.AlignVCenter,
        )
        layout.addWidget(
            btn_frame, 0, Qt.AlignRight | Qt.AlignVCenter
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

        self.setFrameStyle(QFrame.Box | QFrame.Plain)

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

        self._club_list = ClubsTableListWidget()
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


class GameClubView(GameTabBase):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self._club_list = ClubsListWidget()
        self._club_list.selected_clubs.connect(self.on_current_club_changed)

        self._club_info = ClubInfoWidget()

        layout = QHBoxLayout(self)
        layout.addWidget(self._club_list, 0, Qt.AlignLeft)
        layout.addWidget(self._club_info, 1000)
        

    def set_data(self):
        clubs = self._world_engine.world.club_pool.get_all_clubs() if self._world_engine else []
        self._club_list.set_clubs(clubs)
        
        item = self._club_list.currentItem()
        self._club_info.set_club(item.data(Qt.ItemDataRole.UserRole) if item else None)

    def invalidate(self):
        self._club_info.invalidate()
    
    def on_current_club_changed(self, clubs):
        self._club_info.set_club(clubs[0])


class GameHomeWidget(GameTabBase):
    game_continue = Signal(name="game continue")
    run_to_post_season = Signal(name="run to post season")
    advance_new_week = Signal(name="advance new week")

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.top_bar = GameViewTopBar()
        self.top_bar.game_continue.connect(self.game_continue)
        self.top_bar.run_to_post_season.connect(self.run_to_post_season)
        self.top_bar.advance_new_week.connect(self.advance_new_week)

        self.world_time_lbl = WorldTimeLabel()

        self.season_scroll = SeasonWeekScroll()

        self.messages_list = QListWidget()
        change_font(self.messages_list, 4)

        mid_layout = QHBoxLayout()
        mid_layout.addWidget(self.season_scroll, Qt.AlignLeft)
        mid_layout.addWidget(self.messages_list, 100)

        layout = QVBoxLayout(self)
        layout.addWidget(self.top_bar)
        layout.addLayout(mid_layout, 100)

    def invalidate(self):
        self.top_bar.invalidate(self.world_engine)
        if self._world_engine:
            self.season_scroll.set_current_week(self._world_engine.world_time.week)
        
        self._update_messages()

    def _get_messages(self):
        messages = []
        if self._world_engine:
            current_season = self._world_engine.world.current_season
            if current_season:
                 messages.append(f"{current_season.fixture_schedule.fixture_count} remaining Fixtures, {current_season.fixture_schedule.result_count} completed Results")

            current_fixtures = self._world_engine.world_worker.get_current_fixtures()
            if current_fixtures:
                messages.append(f"{len(current_fixtures)} fixtures pending.")

           
        else:
            messages.append("WARNING: No world engine !!!!")

        return messages

    def _update_messages(self):
        self.messages_list.clear()
        for message in self._get_messages():
            self.messages_list.addItem(QListWidgetItem(message))


class GameViewTabs(QTabWidget):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._world_engine: WorldStateEngine | None = None

        self._home_widget = GameHomeWidget()
        self.addTab(self._home_widget, "Home")

        self._club_view_widget = GameClubView()
        self.addTab(self._club_view_widget, "Club")

        self._league_tables_widget = GameLeagueTableView()
        self.addTab(self._league_tables_widget, "League Tables")

        self._clubs_widget = GameClubsView()
        self.addTab(self._clubs_widget, "Clubs")


        self.invalidate()
        # self.setCurrentIndex(0)
        # QApplication.instance().processEvents()

    @property
    def world_engine(self):
        return self._world_engine
    
    @property
    def home_widget(self):
        return self._home_widget

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
        lbl.setAlignment(Qt.AlignCenter)
        change_font(lbl, 12, True)

        layout = QVBoxLayout(self)
        layout.addWidget(lbl, 100, Qt.AlignCenter)


class GameView(ViewBase):
    main_menu = Signal(name="main menu")
    world_changed = Signal(name="world_changed")
    game_continue = Signal(name="game continue")

    def __init__(self, parent=None):
        super().__init__(parent)
        self._world_engine: WorldStateEngine | None = None

        self.setWindowTitle("Game")

        self.view_stack = QStackedWidget()

        self.game_tabs = GameViewTabs()
        self.game_tabs.home_widget.game_continue.connect(self.game_continue)

        self.game_alt_stack = NextContinueStackedWidget()
        self.game_alt_stack.continue_pressed.connect(self.game_continue)

        self.view_stack.addWidget(self.game_tabs)
        self.view_stack.addWidget(self.game_alt_stack)

        self.view_stack.setCurrentWidget(self.game_tabs)

        layout = QVBoxLayout(self)
        layout.addWidget(self.view_stack)

        self.world_changed.connect(self.on_world_changed)
        self.game_continue.connect(self.on_game_continue)
        self.game_tabs.home_widget.run_to_post_season.connect(self.on_run_to_post_season)
        self.game_tabs.home_widget.advance_new_week.connect(self.on_advance_new_week)

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

    def _processing_update(self, message: str, funct: callable):
        widget = MajorGameView(message)
        current_index = self.view_stack.currentIndex()
        self.view_stack.addWidget(widget)
        self.view_stack.setCurrentWidget(widget)
        self.setEnabled(False)
        QGuiApplication.processEvents()

        funct()

        self.view_stack.removeWidget(widget)
        self.view_stack.setCurrentIndex(current_index)
        self.setEnabled(True)
        self.invalidate()

    def on_run_to_post_season(self):
        self._processing_update("Run to end of season!", self.world_engine.advance_to_post_season)

    def on_advance_new_week(self):
        self._processing_update("Run to new week!", self.world_engine.advance_to_new_week)

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_F1:
            event.setAccepted(True)
            self.main_menu.emit()
        else:
            super().keyReleaseEvent(event)
