import random

from util import hook


with open("plugins/data/larts.txt") as f:
    larts = [line.strip() for line in f.readlines()
             if not line.startswith("//")]

with open("plugins/data/insults.txt") as f:
    insults = [line.strip() for line in f.readlines()
               if not line.startswith("//")]

with open("plugins/data/flirts.txt") as f:
    flirts = [line.strip() for line in f.readlines()
              if not line.startswith("//")]


@hook.command
def lart(inp, action=None, nick=None, conn=None, notice=None):
    """lart <user> -- LARTs <user>."""
    target = inp.strip()

    if " " in target:
        notice("Invalid username!")
        return

    # if the user is trying to make the bot slap itself, slap them
    if target.lower() == conn.nick.lower() or target.lower() == "itself":
        target = nick

    values = {"user": target}
    phrase = random.choice(larts)

    # act out the message
    action(phrase.format(**values))


@hook.command
def insult(inp, nick=None, action=None, conn=None, notice=None):
    """insult <user> -- Makes the bot insult <user>."""
    target = inp.strip()

    if " " in target:
        notice("Invalid username!")
        return

    if target == conn.nick.lower() or target == "itself":
        target = nick
    else:
        target = inp

    out = 'insults {}... "{}"'.format(target, random.choice(insults))
    action(out)


@hook.command
def flirt(inp, action=None, conn=None, notice=None):
    """flirt <user> -- Make the bot flirt with <user>."""
    target = inp.strip()

    if " " in target:
        notice("Invalid username!")
        return

    if target == conn.nick.lower() or target == "itself":
        target = 'itself'
    else:
        target = inp

    out = 'flirts with {}... "{}"'.format(target, random.choice(flirts))
    action(out)
