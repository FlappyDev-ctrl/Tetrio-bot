# TETR.IO Bot

Ce projet fournit une interface graphique qui s'accroche automatiquement à la fenêtre TETR.IO active et délègue les coups à l'IA [Zetris](https://github.com/ZetrisAI/Zetris).

## Installation

1. Créez un environnement virtuel Python 3.10 ou plus récent.
2. Installez les dépendances :

   ```bash
   pip install -r requirements.txt
   ```
3. Installez ensuite l'IA Zetris (l'archive officielle est nécessaire) :

   ```bash
   pip install git+https://github.com/ZetrisAI/Zetris
   ```

> ⚠️ Si votre réseau bloque l'accès direct à GitHub, clonez le dépôt Zetris manuellement et installez-le en local (`pip install .`).

## Calibration

Avant la première utilisation, effectuez la calibration pour apprendre au bot où se trouvent la matrice de jeu et l'aperçu des prochaines pièces :

1. Lancez TETR.IO et assurez-vous que la fenêtre est bien visible.
2. Exécutez le lanceur du bot :

   ```bash
   python scripts/run_bot.py
   ```
3. Dans l'interface, cliquez sur **🧭 Calibration**.
4. Suivez les instructions : positionnez le curseur sur les coins du plateau et de l'aperçu puis appuyez sur `F8` à chaque étape.
5. La configuration est enregistrée dans `~/.config/tetrio-bot/config.json`.

## Utilisation

1. Assurez-vous que TETR.IO est lancé et que la partie est prête à commencer (mode solo recommandé).
2. Ouvrez l'interface (`python scripts/run_bot.py`).
3. Cliquez sur **▶️ Lancer**. Le bot active automatiquement la fenêtre TETR.IO, capture l'écran, reconstruit la grille puis demande à Zetris le meilleur coup à jouer.
4. Cliquez sur **⏹️ Arrêter** pour reprendre la main.

### Utiliser un moteur d'IA tiers

Le bot supporte désormais plusieurs moteurs de décision. Par défaut il s'appuie sur Zetris, mais vous pouvez brancher un moteur externe (par exemple celui du dépôt [UndoneMajor/tetrio-bot](https://github.com/UndoneMajor/tetrio-bot)) tant qu'il expose une fabrique retournant un objet ou une fonction capable de fournir des actions.

```bash
python scripts/run_bot.py --engine "mon_module:create_bot"
```

Le point d'entrée `module:fabrique` doit retourner soit:

- un objet possédant une méthode `decide(board, queue, hold=None)` ou `plan(...)` qui renvoie la liste des actions ;
- une fonction directement appelable avec les mêmes paramètres.

Dans le cas du dépôt externe, exposez simplement une fabrique (par exemple `create_bot`) puis indiquez son chemin en argument `--engine`. Le paramètre `--policy` reste disponible si le moteur a besoin d'un chemin vers un modèle.

## Personnalisation

- Le fichier de configuration permet d'ajuster les touches envoyées (`keymap`) ainsi que la cadence (`tick_rate`).
- Les touches par défaut correspondent au schéma TETR.IO standard (flèches, espace pour hard drop, `Z`/`Up` pour les rotations, `C` pour le hold).

## Dépannage

- Si un message indique que `load_policy` ou `plan` est introuvable, vérifiez la version de Zetris installée.
- Les captures d'écran reposent sur l'API `mss`. Sur macOS, pensez à autoriser l'accès à l'enregistrement d'écran pour votre terminal Python.
- Sur Linux, l'envoi de touches nécessite généralement d'exécuter le script avec les permissions d'accès au serveur d'affichage (`xhost +` dans certains cas).
- Sur Windows, `pygetwindow` nécessite l'installation des dépendances `pywin32` qui sont installées automatiquement par `pip`.

## Licence

Ce projet est fourni tel quel, sans garantie. Respectez les conditions d'utilisation de TETR.IO et de Zetris lorsque vous utilisez ce bot.
