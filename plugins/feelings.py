from util import hook
import re
import random

nick_re = re.compile(r"^[A-Za-z0-9_|.-\]\[]*$")

insults = []
flirts = []

with open("plugins/data/insults.txt") as f:
    for line in f.readlines():
        if line.startswith("//"):
            continue
        insults.append(line.strip())

with open("plugins/data/flirts.txt") as f:
    for line in f.readlines():
        if line.startswith("//"):
            continue
        flirts.append(line.strip())


@hook.command
def insult(inp, nick=None, me=None, conn=None):
    ".insult <user> -- Makes the bot insult <user>."
    target = inp.strip()

    if not re.match(nick_re, target):
        notice("Invalid username!")
        return

    if target == conn.nick.lower() or target == "itself":
        target = nick
    else:
        target = inp
    out = "insults " + target + "... \"" + random.choice(insults) + "\""
    me(out)


@hook.command
def flirt(inp, nick=None, me=None, conn=None):
    ".flirt <user> -- Make the bot flirt with <user>."
    target = inp.strip()

    if not re.match(nick_re, target):
        notice("Invalid username!")
        return

    if target == conn.nick.lower() or target == "itself":
        target = 'itself'
    else:
        target = inp
    out = "flirts with " + target + "... \"" + random.choice(flirts) + "\""
    me(out)
