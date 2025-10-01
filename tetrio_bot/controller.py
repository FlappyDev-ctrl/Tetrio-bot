"""Keyboard controller for sending moves to the TETR.IO window."""
from __future__ import annotations

import time
from typing import Iterable, Mapping

from pynput.keyboard import Controller, Key


class InputController:
    def __init__(self, keymap: Mapping[str, str]):
        self._controller = Controller()
        self._keymap = {action: self._normalise_key(key) for action, key in keymap.items()}

    @staticmethod
    def _normalise_key(key: str):
        if len(key) == 1:
            return key.lower()
        special = {
            "left": Key.left,
            "right": Key.right,
            "up": Key.up,
            "down": Key.down,
            "space": Key.space,
            "shift": Key.shift,
            "ctrl": Key.ctrl,
        }
        return special.get(key.lower(), key)

    def tap(self, key):
        self._controller.press(key)
        time.sleep(0.01)
        self._controller.release(key)

    def execute_actions(self, actions: Iterable[str]) -> None:
        for action in actions:
            key = self._keymap.get(action)
            if not key:
                continue
            self.tap(key)
            time.sleep(0.01)
