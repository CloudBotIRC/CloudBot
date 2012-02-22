from util import hook
import re
import random

kills = ["rips off <who>'s <body> and leaves them to die.",
        "grabs <who>'s head and rips it clean off their body.",
        "grabs a machine gun and riddles <who>'s body with bullets.",
        "gags and ties <who> then throws them off a bridge.",
        "crushes <who> with a huge spiked boulder.",
        "rams a rocket launcher up <who>'s ass and lets off a few rounds.",
        "crushes <who>'s skull in with a spiked mace.",
        "feeds <who> to an owlbear.",
        "puts <who> into a sack, throws the sack in the river, and hurls the river into space.",
        "goes bowling with <who>'s head.",
        "sends <who> to /dev/null!",
        "feeds <who> coke and mentos till they pop!"]

body = ['head',
        'arms',
        'leg',
        'arm',
        '"special parts"']

@hook.command
def kill(inp, me = None, nick = None, input=None, notice=None):
    ".kill <user> - kill a user"
    inp = inp.strip()

    if not re.match("^[A-Za-z0-9_|.-\]\[]*$", inp.lower()):
        notice("Invalid username!")
        return

    if inp == input.conn.nick.lower() or inp == "itself":
        msg = 'kills ' + nick + ' and rakes their corpse (:3)'
    else:
        kill = random.choice(kills)
        kill = re.sub ('<who>', inp, kill)
        msg = re.sub ('<body>', random.choice(body), kill)

    me(msg)

