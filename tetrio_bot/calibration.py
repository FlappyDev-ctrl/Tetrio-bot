"""Utilities to calibrate the capture regions."""
from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from typing import Callable, Optional

import pyautogui
from pynput import keyboard

from .config import Region, Settings, save_settings

pyautogui.FAILSAFE = False


@dataclass
class CalibrationResult:
    board_region: Region
    preview_region: Region


class _HotkeyWaiter:
    def __init__(self, target_key: keyboard.Key | keyboard.KeyCode):
        self._target_key = target_key
        self._event = threading.Event()

    def __enter__(self) -> "_HotkeyWaiter":
        self._listener = keyboard.Listener(on_press=self._on_press)
        self._listener.start()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self._listener.stop()

    def _on_press(self, key) -> None:
        if key == self._target_key:
            self._event.set()

    def wait(self, timeout: Optional[float] = None) -> bool:
        return self._event.wait(timeout)


def _capture_point(prompt: str, *, target_key: keyboard.Key, on_update: Optional[Callable[[tuple[int, int]], None]] = None) -> tuple[int, int]:
    print(prompt)
    with _HotkeyWaiter(target_key) as waiter:
        while not waiter.wait(0.05):
            position = pyautogui.position()
            if on_update:
                on_update((position.x, position.y))
            time.sleep(0.05)
    pos = pyautogui.position()
    print(f"Position enregistrée: {pos.x}, {pos.y}")
    return pos.x, pos.y


def calibrate(settings: Settings, *, status_callback: Optional[Callable[[str], None]] = None) -> CalibrationResult:
    """Interactively calibrate the capture regions.

    The user is asked to place their mouse on the top-left and bottom-right corners
    of the TETR.IO matrix as well as the preview box. They must press F8 to record
    each point.
    """

    def notify(message: str) -> None:
        print(message)
        if status_callback:
            status_callback(message)

    notify("Placez le curseur sur la CASE en haut à gauche du plateau puis appuyez sur F8.")
    top_left_x, top_left_y = _capture_point("-> En attente du point haut gauche (F8)", target_key=keyboard.Key.f8)

    notify("Placez le curseur sur la CASE en bas à droite du plateau puis appuyez sur F8.")
    bottom_right_x, bottom_right_y = _capture_point("-> En attente du point bas droite (F8)", target_key=keyboard.Key.f8)

    board_region = Region(
        left=min(top_left_x, bottom_right_x),
        top=min(top_left_y, bottom_right_y),
        width=abs(bottom_right_x - top_left_x),
        height=abs(bottom_right_y - top_left_y),
    )

    notify("Placez le curseur sur l'aperçu des prochaines pièces (haut gauche) et appuyez sur F8.")
    preview_top_left_x, preview_top_left_y = _capture_point("-> En attente du point haut gauche de l'aperçu (F8)", target_key=keyboard.Key.f8)

    notify("Placez le curseur sur le coin bas droite de l'aperçu et appuyez sur F8.")
    preview_bottom_right_x, preview_bottom_right_y = _capture_point("-> En attente du point bas droite de l'aperçu (F8)", target_key=keyboard.Key.f8)

    preview_region = Region(
        left=min(preview_top_left_x, preview_bottom_right_x),
        top=min(preview_top_left_y, preview_bottom_right_y),
        width=abs(preview_bottom_right_x - preview_top_left_x),
        height=abs(preview_bottom_right_y - preview_top_left_y),
    )

    settings.board_region = board_region
    settings.preview_region = preview_region
    save_settings(settings)

    notify("Calibration terminée et enregistrée.")
    return CalibrationResult(board_region=board_region, preview_region=preview_region)
