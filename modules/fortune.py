import os
import random

from util import hook


@hook.onload()
def load_fortunes(bot):
    path = os.path.join(bot.data_dir, "fortunes.txt")
    global fortunes
    with open(path) as f:
        fortunes = [line.strip() for line in f.readlines()
                    if not line.startswith("//")]


@hook.command(autohelp=False)
def fortune():
    """fortune -- Fortune cookies on demand."""
    return random.choice(fortunes)
