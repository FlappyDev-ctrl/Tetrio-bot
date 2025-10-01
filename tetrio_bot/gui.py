"""Tkinter interface for controlling the bot."""
from __future__ import annotations

import threading
import tkinter as tk
from tkinter import messagebox

from .calibration import calibrate
from .config import Settings, load_settings, save_settings
from .runner import BotRunner


class BotGUI:
    def __init__(self, *, policy_path: str | None = None, engine: str = "zetris"):
        self._settings = load_settings()
        self._policy_path = policy_path
        self._engine = engine
        self._runner = BotRunner(self._settings, policy_path=policy_path, engine=engine)
        self._running = False

        self._root = tk.Tk()
        self._root.title("TETR.IO Bot")
        self._root.geometry("360x220")

        self._status_var = tk.StringVar(value="Bot arrêté.")

        self._start_button = tk.Button(self._root, text="▶️ Lancer", command=self._toggle_start)
        self._start_button.pack(pady=12)

        self._calibrate_button = tk.Button(self._root, text="🧭 Calibration", command=self._launch_calibration)
        self._calibrate_button.pack(pady=12)

        self._status_label = tk.Label(self._root, textvariable=self._status_var, wraplength=320)
        self._status_label.pack(pady=12)

        self._root.protocol("WM_DELETE_WINDOW", self._on_close)

    def run(self) -> None:
        self._root.mainloop()

    def _toggle_start(self) -> None:
        if not self._running:
            try:
                self._runner.start()
            except ValueError as exc:
                messagebox.showerror("Configuration manquante", str(exc))
                return
            except RuntimeError as exc:
                messagebox.showerror("Erreur", str(exc))
                return
            self._running = True
            self._status_var.set("Bot en cours d'exécution.")
            self._start_button.configure(text="⏹️ Arrêter")
        else:
            self._runner.stop()
            self._running = False
            self._status_var.set("Bot arrêté.")
            self._start_button.configure(text="▶️ Lancer")

    def _launch_calibration(self) -> None:
        def task() -> None:
            try:
                calibrate(self._settings, status_callback=self._status_var.set)
                save_settings(self._settings)
                self._runner = BotRunner(
                    self._settings,
                    policy_path=self._policy_path,
                    engine=self._engine,
                )
            except Exception as exc:  # pragma: no cover - manual workflow
                messagebox.showerror("Erreur", str(exc))

        threading.Thread(target=task, daemon=True).start()

    def _on_close(self) -> None:
        if self._running:
            self._runner.stop()
        self._root.destroy()
