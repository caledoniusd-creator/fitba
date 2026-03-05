from src.core.db.game_worker import GameDBWorker

class BaseWorker:

    def __init__(self, game_worker: GameDBWorker):
        self._game_worker = game_worker

    @property
    def game_worker(self):
        return self._game_worker
    
    def refresh(self):
        pass

    