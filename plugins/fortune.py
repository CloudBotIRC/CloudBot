import os
import random
import asyncio

from cloudbot import hook


@hook.onload()
def load_fortunes(bot):
    path = os.path.join(bot.data_dir, "fortunes.txt")
    global fortunes
    with open(path) as f:
        fortunes = [line.strip() for line in f.readlines()
                    if not line.startswith("//")]


@hook.command(autohelp=False)
@asyncio.coroutine
def fortune():
    """fortune -- Fortune cookies on demand."""
    return random.choice(fortunes)
