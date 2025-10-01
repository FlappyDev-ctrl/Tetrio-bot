"""Entry point to start the GUI bot."""
from __future__ import annotations

import argparse

from tetrio_bot.gui import BotGUI


def main() -> None:
    parser = argparse.ArgumentParser(description="TETR.IO auto-player powered by Zetris")
    parser.add_argument("--policy", help="Chemin vers le modèle Zetris (optionnel)", default=None)
    args = parser.parse_args()

    gui = BotGUI(policy_path=args.policy)
    gui.run()


if __name__ == "__main__":
    main()
