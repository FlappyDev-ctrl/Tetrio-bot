"""Bot runtime loop."""
from __future__ import annotations

import threading
import time
from typing import Optional

import numpy as np

from .capture import BoardCapture, PreviewCapture
from .config import Settings
from .engines import create_decision_provider
from .controller import InputController
from .window import focus_tetrio_window


class BotRunner:
    def __init__(self, settings: Settings, *, policy_path: str | None = None, engine: str = "zetris"):
        self._settings = settings
        self._policy_path = policy_path
        self._engine = engine
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        if self._thread and self._thread.is_alive():
            self._stop_event.set()
            self._thread.join()

    def _run_loop(self) -> None:
        if not focus_tetrio_window():
            raise RuntimeError("Impossible de trouver une fenêtre TETR.IO active.")

        board_capture = BoardCapture(self._settings.board_region)
        preview_capture = PreviewCapture(self._settings.preview_region)
        controller = InputController(self._settings.keymap)
        decision_provider = create_decision_provider(self._engine, policy_path=self._policy_path)

        while not self._stop_event.is_set():
            board_state = board_capture.capture_board()
            queue = preview_capture.capture_queue(max_pieces=5)
            decision = decision_provider.decide(board_state.grid.astype(np.float32), queue, hold=None)
            controller.execute_actions(decision.actions)
            time.sleep(self._settings.tick_rate)
