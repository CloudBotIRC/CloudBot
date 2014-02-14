import random

from util import hook


with open("plugins/data/fortunes.txt") as f:
    fortunes = [line.strip() for line in f.readlines()
                if not line.startswith("//")]


@hook.command(autohelp=False)
def fortune(inp):
    """fortune -- Fortune cookies on demand."""
    return random.choice(fortunes)
