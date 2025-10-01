"""Wrapper around the Zetris AI inference API."""
from __future__ import annotations

import importlib
from typing import Iterable, List

import numpy as np

from .decision import Decision


class ZetrisAdapter:
    """Thin wrapper that delegates to the Zetris AI implementation.

    The adapter tries to import the official Zetris package. If it is not
    available a descriptive error is raised.
    """

    def __init__(self, *, policy_path: str | None = None) -> None:
        try:
            self._module = importlib.import_module("zetris")
        except ModuleNotFoundError as exc:  # pragma: no cover - depends on external package
            raise RuntimeError(
                "Le module 'zetris' est introuvable. Installez-le via 'pip install git+https://github.com/ZetrisAI/Zetris'."
            ) from exc

        # The public API exposes a `load_policy` helper which returns an agent
        # capable of producing move sequences for a given board state. We import
        # the helper lazily to avoid importing heavy dependencies when this
        # module is only used for type checking.
        try:
            load_policy = getattr(self._module, "load_policy")
        except AttributeError as exc:
            raise RuntimeError(
                "La bibliothèque Zetris ne fournit pas la fonction 'load_policy'. Vérifiez la version installée."
            ) from exc

        self._policy = load_policy(policy_path)

    def decide(self, board: np.ndarray, queue: Iterable[str], hold: str | None = None) -> Decision:
        # Delegates to the model; the expected API is `policy.plan(board, queue, hold)`
        try:
            actions: List[str] = list(self._policy.plan(board=board, queue=list(queue), hold=hold))
        except AttributeError as exc:  # pragma: no cover - depends on third-party implementation
            raise RuntimeError(
                "L'objet de politique Zetris ne possède pas la méthode 'plan'. Vérifiez la version installée."
            ) from exc
        return Decision(actions=actions)
