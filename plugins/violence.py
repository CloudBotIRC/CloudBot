from util import hook
import re
import random

nick_re = re.compile(r"^[A-Za-z0-9_|.-\]\[]*$")

# define lists for messages
larts = []
kills = []
kill_bodyparts = []
slaps = []
slap_items = []

with open("plugins/data/larts.txt") as f:
    for line in f.readlines():
        if line.startswith("//"):
            continue
        larts.append(line.strip())

with open("plugins/data/slaps.txt") as f:
    for line in f.readlines():
        if line.startswith("//"):
            continue
        slaps.append(line.strip())

with open("plugins/data/slap_items.txt") as f:
    for line in f.readlines():
        if line.startswith("//"):
            continue
        slap_items.append(line.strip())

with open("plugins/data/kills.txt") as f:
    for line in f.readlines():
        if line.startswith("//"):
            continue
        kills.append(line.strip())

with open("plugins/data/kill_bodyparts.txt") as f:
    for line in f.readlines():
        if line.startswith("//"):
            continue
        kill_bodyparts.append(line.strip())


@hook.command
def slap(inp, me=None, nick=None, conn=None, notice=None):
    ".slap <user> -- Makes the bot slap <user>."
    target = inp.lower()

    if not re.match(nick_re, target):
        notice("Invalid username!")
        return

    # if the user is trying to make the bot slap itself, slap them
    if target == conn.nick.lower() or target == "itself":
        target = nick
    else:
        target = inp

    out = random.choice(slaps)
    out = out.replace('<who>', target)
    out = out.replace('<item>', random.choice(slap_items))

    # act out the message
    me(out)


@hook.command
def lart(inp, me=None, nick=None, conn=None, notice=None):
    ".lart <user> -- LARTs <user>."
    target = inp.lower()

    if not re.match(nick_re, target):
        notice("Invalid username!")
        return

    if target == conn.nick.lower() or target == "itself":
        target = nick
    else:
        target = inp

    out = random.choice(larts)
    out = out.replace('<who>', target)
    out = out.replace('<item>', random.choice(slap_items))
    me(out)


@hook.command
def kill(inp, me=None, nick=None, conn=None, notice=None):
    ".kill <user> -- Makes the bot kill <user>."
    target = inp.lower()

    if not re.match(nick_re, target):
        notice("Invalid username!")
        return

    if target == conn.nick.lower() or target == "itself":
        target = nick
    else:
        target = inp

    out = random.choice(kills)
    out = out.replace('<who>', target)
    out = out.replace('<body>', random.choice(kill_bodyparts))
    me(out)
