from util import hook, text
import random


with open("plugins/data/slogans.txt") as f:
    slogans = [line.strip() for line in f.readlines()
               if not line.startswith("//")]


@hook.command
def slogan(inp):
    "slogan <word> -- Makes a slogan for <word>."
    out = random.choice(slogans)
    if inp.lower() and out.startswith("<text>"):
        inp = text.capitalize_first(inp)

    return out.replace('<text>', inp)
