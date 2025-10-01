"""Configuration management for the TETR.IO bot."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict

CONFIG_DIR = Path.home() / ".config" / "tetrio-bot"
DEFAULT_CONFIG_PATH = CONFIG_DIR / "config.json"


def _default_keymap() -> Dict[str, str]:
    return {
        "move_left": "Left",
        "move_right": "Right",
        "soft_drop": "Down",
        "hard_drop": "space",
        "rotate_cw": "Up",
        "rotate_ccw": "z",
        "rotate_180": "a",
        "hold": "c",
    }


@dataclass
class Region:
    left: int = 0
    top: int = 0
    width: int = 0
    height: int = 0

    @property
    def right(self) -> int:
        return self.left + self.width

    @property
    def bottom(self) -> int:
        return self.top + self.height

    def to_dict(self) -> Dict[str, int]:
        return {
            "left": self.left,
            "top": self.top,
            "width": self.width,
            "height": self.height,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, int]) -> "Region":
        return cls(
            left=int(data.get("left", 0)),
            top=int(data.get("top", 0)),
            width=int(data.get("width", 0)),
            height=int(data.get("height", 0)),
        )


@dataclass
class Settings:
    board_region: Region = field(default_factory=Region)
    preview_region: Region = field(default_factory=Region)
    tick_rate: float = 0.12
    keymap: Dict[str, str] = field(default_factory=_default_keymap)

    def to_dict(self) -> Dict[str, object]:
        return {
            "board_region": self.board_region.to_dict(),
            "preview_region": self.preview_region.to_dict(),
            "tick_rate": self.tick_rate,
            "keymap": self.keymap,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, object]) -> "Settings":
        return cls(
            board_region=Region.from_dict(data.get("board_region", {})),
            preview_region=Region.from_dict(data.get("preview_region", {})),
            tick_rate=float(data.get("tick_rate", 0.12)),
            keymap=dict(data.get("keymap", _default_keymap())),
        )


def load_settings(path: Path = DEFAULT_CONFIG_PATH) -> Settings:
    if not path.exists():
        return Settings()

    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    return Settings.from_dict(data)


def save_settings(settings: Settings, path: Path = DEFAULT_CONFIG_PATH) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(settings.to_dict(), handle, indent=2)
