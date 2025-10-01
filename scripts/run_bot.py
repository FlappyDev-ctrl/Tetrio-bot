"""Entry point to start the GUI bot."""
from __future__ import annotations

import argparse

from tetrio_bot.gui import BotGUI


def main() -> None:
    parser = argparse.ArgumentParser(description="TETR.IO auto-player powered by Zetris")
    parser.add_argument("--policy", help="Chemin vers le modèle Zetris (optionnel)", default=None)
    parser.add_argument(
        "--engine",
        default="zetris",
        help=(
            "Moteur de décision à utiliser. Par défaut 'zetris'. "
            "Vous pouvez fournir un point d'entrée 'module:fabrique' pour un moteur tiers, par exemple "
            "'mon_bot.adapter:factory'."
        ),
    )
    args = parser.parse_args()

    gui = BotGUI(policy_path=args.policy, engine=args.engine)
    gui.run()


if __name__ == "__main__":
    main()
