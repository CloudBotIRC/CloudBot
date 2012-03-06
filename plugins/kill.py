from util import hook
import re
import random

kills = ["rips off <who>'s <body> and leaves them to die.",
        "grabs <who>'s head and rips it clean off their body.",
        "grabs a machine gun and riddles <who>'s body with bullets.",
        "sends The Terminator on a mission to retrieve <who>'s <body>.",
        "gags and ties <who> then throws them off a bridge.",
        "crushes <who> with a huge spiked boulder.",
        "glares at <who> until they die of boredom.",
        "stuffs a few TNT blocks under <who>'s bed, and sets them off.",
        "shivs <who> in the <body>.",
        "rams a rocket launcher up <who>'s ass and lets off a few rounds.",
        "crushes <who>'s skull in with a spiked mace.",
        "unleashes the armies of Isengard on <who>.",
        "packs <who> into a SVN repo.",
        "slices <who>'s <body> off with a Katana",
        "throws <who> to Cthulu!",
        "feeds <who> to an owlbear.",
        "turns <who> into a snail, and then salts them.",
        "snacks on <who>'s <body>.",
        "puts <who> into a sack, throws the sack in the river, and hurls the river into space.",
        "goes bowling with <who>'s head.",
        "uses <who>'s <body> as a back-scratcher.",
        "sends <who> to /dev/null!",
        "feeds <who> coke and mentos till they pop!"]

body = ['head',
        'arms',
        'leg',
        'arm',
        '"special parts"']

@hook.command
def kill(inp, me=None, nick=None, input=None, notice=None):
    ".kill <user> -- Makes the bot kill <user>."
    inp = inp.strip()

    if not re.match("^[A-Za-z0-9_|.-\]\[]*$", inp.lower()):
        notice("Invalid username!")
        return

    if inp == input.conn.nick.lower() or inp == "itself":
        target = inp
    else:
        target = nick
    msg = random.choice(kills)
    msg = re.sub ('<who>', target, target)
    msg = re.sub ('<body>', random.choice(body), target)
    me(msg)
