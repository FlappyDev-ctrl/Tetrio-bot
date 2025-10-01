"""Utilities for finding and focusing the TETR.IO window."""
from __future__ import annotations

from typing import Optional

import pygetwindow as gw


def find_tetrio_window() -> Optional[gw.Window]:
    candidates = [window for window in gw.getAllWindows() if "tetr.io" in window.title.lower()]
    if not candidates:
        return None
    # Prefer a visible, unminimised window
    candidates.sort(key=lambda win: (not win.isActive, not win.isMaximized))
    return candidates[0]


def focus_tetrio_window() -> bool:
    window = find_tetrio_window()
    if not window:
        return False
    try:
        window.activate()
    except Exception:  # pragma: no cover - platform dependent
        try:
            window.minimize()
            window.restore()
        except Exception:
            return False
    return True
