from util import hook
import re
import random

fortunes = []

with open("plugins/data/fortunes.txt") as f:
    for line in f.readlines():
        if line.startswith("//"):
            continue
        fortunes.append(line.strip())


@hook.command(autohelp=False)
def fortune(inp, nick=None, say=None, input=None):
    ".fortune -- Fortune cookies on demand."

    msg = "(" + nick + ") " + random.choice(fortunes)
    if inp:
        msg = "(@" + inp + ") " + random.choice(fortunes)

    say(msg)
