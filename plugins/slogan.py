import random

from cloudbot import hook
from cloudbot.util import formatting

with open("./data/slogans.txt") as f:
    slogans = [line.strip() for line in f.readlines()
               if not line.startswith("//")]


@hook.command()
def slogan(text):
    """slogan <word> -- Makes a slogan for <word>."""
    out = random.choice(slogans)
    if text.lower() and out.startswith("<text>"):
        text = formatting.capitalize_first(text)

    return out.replace('<text>', text)
