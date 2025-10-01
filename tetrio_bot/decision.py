"""Common decision data structures for bot engines."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence


@dataclass
class Decision:
    """Represents an ordered list of actions to execute."""

    actions: Sequence[str]


__all__ = ["Decision"]

