from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from src.core.world_time import WEEKS_IN_YEAR
from src.core.world_state_engine import WorldState, WorldStateEngine


class GameEngineObject(QObject):
    state_engine_changed = Signal()
    game_advanced = Signal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._state_engine: WorldStateEngine | None = None

    @property
    def state_engine(self):
        return self._state_engine

    @state_engine.setter
    def state_engine(self, new_engine: WorldStateEngine | None):
        if self._state_engine != new_engine:
            self._state_engine = new_engine
            self.state_engine_changed.emit()

    @property
    def state(self):
        if self._state_engine:
            return self._state_engine.state
        else:
            None

    @property
    def db_worker(self):
        if self._state_engine:
            return self._state_engine.game_worker.worker
        return None

    @property
    def world_time(self):
        if not self._state_engine:
            return None, None
        return self._state_engine.world_time

    def create_new_game(self):
        new_state_engine = WorldStateEngine()
        if new_state_engine.state == WorldState.NewGame:
            new_state_engine.advance_game()
        self.state_engine = new_state_engine

    def load_game(self):
        new_state_engine = WorldStateEngine()
        new_state_engine.state = WorldState.AwaitingContinue
        self.state_engine = new_state_engine

    def close_state_engine(self):
        if self.state_engine:
            # make sure any open database session is closed to avoid
            # detached-object surprises later on and to release file locks
            try:
                self.state_engine.game_worker.close()
            except Exception:
                # be defensive: if something is wrong we still clear the
                # reference so the engine can be garbage collected
                pass
            self.state_engine = None

    def advance_game(self):
        if not self._state_engine:
            raise RuntimeError("No State Engine to advance")
        self._state_engine.advance_game()
        self.game_advanced.emit()

    def advance_to_end_of_season(self):
        if not self._state_engine:
            raise RuntimeError("No State Engine to advance to end of season")
        self._state_engine.advance_to_post_season()
        self.game_advanced.emit()

    def advance_to_next_week(self):
        if not self._state_engine:
            raise RuntimeError("No State Engine to advance to end of season")
        if self.world_time[1].week_num < WEEKS_IN_YEAR:
            self._state_engine.advance_to_new_week()
            self.game_advanced.emit()

    @property
    def is_active(self):
        return self._state_engine is not None

    def current_fixtures(self):
        if not self._state_engine:
            raise RuntimeError("No State Engine to get current fixtures")

        return self._state_engine.game_worker.current_fixtures()

    def current_result_fixtures(self):
        if not self._state_engine:
            raise RuntimeError("No State Engine to get current result")

        results = self._state_engine.game_worker.current_results()
        return [r.fixture for r in results]
