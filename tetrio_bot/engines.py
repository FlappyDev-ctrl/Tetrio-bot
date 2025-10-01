"""Abstractions for decision engines used by the bot."""
from __future__ import annotations

import importlib
import inspect
from dataclasses import dataclass
from typing import Any, Callable, Iterable, Protocol, Sequence

import numpy as np

from .decision import Decision
from .zetris_wrapper import ZetrisAdapter


class DecisionProvider(Protocol):
    """Protocol implemented by decision engines."""

    def decide(self, board: np.ndarray, queue: Iterable[str], hold: str | None = None) -> Decision:
        ...


@dataclass
class _CallableProvider:
    """Wrap a callable so it behaves like a decision provider."""

    func: Callable[[np.ndarray, Iterable[str], str | None], Any]

    def decide(self, board: np.ndarray, queue: Iterable[str], hold: str | None = None) -> Decision:
        result = self.func(board, queue, hold)
        return _normalise_result(result)


def _normalise_result(result: Any) -> Decision:
    if isinstance(result, Decision):
        return result
    if isinstance(result, (str, bytes)):
        raise TypeError("Une chaîne isolée ne peut pas représenter une séquence d'actions.")

    if isinstance(result, Sequence) and all(isinstance(item, str) for item in result):
        return Decision(actions=list(result))
    if hasattr(result, "actions"):
        actions = getattr(result, "actions")
        if isinstance(actions, Sequence):
            return Decision(actions=list(actions))
    raise TypeError(
        "Le moteur externe doit retourner soit un objet Decision, soit une séquence de chaînes représentant les actions."
    )


def _wrap_object(obj: Any) -> DecisionProvider:
    if callable(obj):
        return _CallableProvider(obj)

    if hasattr(obj, "decide") and callable(obj.decide):
        return _CallableProvider(obj.decide)

    if hasattr(obj, "plan") and callable(obj.plan):
        return _CallableProvider(obj.plan)

    raise TypeError(
        "L'entrée du moteur externe doit être un appelable ou exposer une méthode 'decide'/'plan'."
    )


def _invoke_factory(factory: Callable[..., Any], policy_path: str | None) -> Any:
    try:
        signature = inspect.signature(factory)
    except (TypeError, ValueError):
        return factory(policy_path=policy_path)

    parameters = list(signature.parameters.values())
    accepts_kwargs = any(param.kind == param.VAR_KEYWORD for param in parameters)
    has_named_argument = any(param.name == "policy_path" for param in parameters)

    if accepts_kwargs or has_named_argument:
        return factory(policy_path=policy_path)

    if policy_path is not None:
        try:
            return factory(policy_path)
        except TypeError:
            pass

    return factory()


def create_decision_provider(engine: str, *, policy_path: str | None = None) -> DecisionProvider:
    """Create the decision provider corresponding to *engine*.

    The default engine ``"zetris"`` utilise le modèle Zetris officiel. Pour
    utiliser un moteur personnalisé, fournissez un chemin de type
    ``"package.module:factory"``. La fabrique peut être soit une fonction qui
    retourne un objet compatible, soit une classe instanciable.
    """

    if engine == "zetris":
        return ZetrisAdapter(policy_path=policy_path)

    module_name, sep, attr = engine.partition(":")
    if not sep:
        raise ValueError(
            "Moteur inconnu. Utilisez 'zetris' ou un point d'entrée de type 'package.module:fabrique'."
        )

    module = importlib.import_module(module_name)
    try:
        factory = getattr(module, attr)
    except AttributeError as exc:
        raise RuntimeError(f"Le module '{module_name}' ne fournit pas l'attribut '{attr}'.") from exc

    obj = _invoke_factory(factory, policy_path) if callable(factory) else factory
    return _wrap_object(obj)


__all__ = ["DecisionProvider", "create_decision_provider"]

