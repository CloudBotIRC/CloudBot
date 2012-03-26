from util import hook
import re
import random

fortunes = []

with open("plugins/data/fortunes.txt") as f:
    for line in f.readlines():
        if line.startswith("//"):
            continue
        fortunes.append(line.strip())


@hook.command
def fortune(inp):
    ".fortune -- Fortune cookies on demand."
    return random.choice(fortunes)
