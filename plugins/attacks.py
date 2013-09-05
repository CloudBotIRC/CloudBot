from util import hook
import random

with open("plugins/data/larts.txt") as f:
    larts = [line.strip() for line in f.readlines()
             if not line.startswith("//")]

with open("plugins/data/slaps.txt") as f:
    slaps = [line.strip() for line in f.readlines()
             if not line.startswith("//")]

with open("plugins/data/slap_items.txt") as f:
    items = [line.strip() for line in f.readlines()
             if not line.startswith("//")]

with open("plugins/data/kills.txt") as f:
    kills = [line.strip() for line in f.readlines()
             if not line.startswith("//")]

with open("plugins/data/insults.txt") as f:
    insults = [line.strip() for line in f.readlines()
               if not line.startswith("//")]

with open("plugins/data/flirts.txt") as f:
    flirts = [line.strip() for line in f.readlines()
              if not line.startswith("//")]


@hook.command
def slap(inp, me=None, nick=None, conn=None, notice=None):
    """slap <user> -- Makes the bot slap <user>."""
    target = inp.strip()

    if " " in target:
        notice("Invalid username!")
        return

    # if the user is trying to make the bot slap itself, slap them
    if target.lower() == conn.nick.lower() or target.lower() == "itself":
        target = nick

    values = {"item": random.choice(items), "user": target}
    phrase = random.choice(slaps)

    # act out the message
    me(phrase.format(**values))


@hook.command
def lart(inp, me=None, nick=None, conn=None, notice=None):
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
    me(phrase.format(**values))


@hook.command
def kill(inp, me=None, nick=None, conn=None, notice=None):
    """kill <user> -- Makes the bot kill <user>."""
    target = inp.strip()

    if " " in target:
        notice("Invalid username!")
        return

    # if the user is trying to make the bot slap itself, slap them
    if target.lower() == conn.nick.lower() or target.lower() == "itself":
        target = nick

    values = {"user": target}
    phrase = random.choice(kills)

    # act out the message
    me(phrase.format(**values))


@hook.command
def insult(inp, nick=None, me=None, conn=None, notice=None):
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
    me(out)


@hook.command
def flirt(inp, me=None, conn=None, notice=None):
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
    me(out)
