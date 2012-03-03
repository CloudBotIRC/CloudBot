from util import hook
import re
import random

slaps = ["slaps <who> with a <item>.",
        "slaps <who> around a bit with a <item>.",
        "throws a <item> at <who>.",
        "grabs a <item> and throws it in <who>'s face.",
        "holds <who> down and repeatedly whacks them with a <item>.",
        "prods <who> with a flaming <item>.",
        "picks up a <item>, and whacks <who> with it.",
        "ties <who> to a chair and throws a <item> at them.",
        "hits <who> on the head with a <item>."]

items = ["cast iron skillet",
        "large trout",
        "baseball bat",
        "wooden cane",
        "CRT monitor",
        "diamond sword",
        "physics textbook",
        "television",
        "mau5head",
        "five ton truck",
        "roll of duct tape",
        "book",
        "cobblestone block",
        "lava bucket",
        "rubber chicken",
        "gold block",
        "fire extinguisher",
        "heavy rock",
        "chunk of dirt"]

@hook.command
def slap(inp, me=None, nick=None, input=None, notice=None):
    ".slap <user> -- Makes the bot slap <user>."
    inp = inp.strip()

    if not re.match("^[A-Za-z0-9_|.-\]\[]*$", inp.lower()):
        notice("Invalid username!")
        return

    if inp == input.conn.nick.lower() or inp == "itself":
        slap = random.choice(slaps)
        slap = re.sub ('<who>', nick, slap)
        msg = re.sub ('<item>', random.choice(items), slap)
    else:
        slap = random.choice(slaps)
        slap = re.sub ('<who>', inp, slap)
        msg = re.sub ('<item>', random.choice(items), slap)

    me(msg)
