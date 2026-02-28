from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


from src.core.db.game_worker import WorldState, WorldStateEngine


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
    def world_time(self):
        if not self._state_engine:
            return None, None
        return self._state_engine.world_time

    def create_new_game(self):
        new_state_engine = WorldStateEngine()
        if new_state_engine.state == WorldState.NewGame:
            new_state_engine.advance_game()
        self.state_engine = new_state_engine

    def close_state_engine(self):
        if self.state_engine:
            self.state_engine = None

    def advance_game(self):
        if not self._state_engine:
            raise RuntimeError("No State Engine to advance")
        self._state_engine.advance_game()
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
