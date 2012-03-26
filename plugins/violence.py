from util import hook
import re
import random


slaps = []
slap_items = []

with open("plugins/data/slaps.txt") as f:
    for line in f.readlines():
        if line.startswith("//"):
            continue
        slaps.append(line)

with open("plugins/data/slap_items.txt") as f:
    for line in f.readlines():
        if line.startswith("//"):
            continue
        items.append(line)

larts = ["swaps <who>'s shampoo with glue.",
        "installs Windows on <who>'s computer.",
        "forces <who> to use perl for 3 weeks.",
        "registers <who>'s name with 50 known spammers.",
        "resizes <who>'s console to 40x24.",
        "takes <who>'s drink.",
        "dispenses <who>'s email address to a few hundred 'bulk mailing services'.",
        "pokes <who> in the eye.",
        "beats <who> senseless with a 50lb Linux manual.",
        "cats /dev/random into <who>'s ear.",
        "signs <who> up for AOL.",
        "downvotes <who> on Reddit.",
        "enrolls <who> in Visual Basic 101.",
        "sporks <who>.",
        "drops a truckload of support tickets on <who>.",
        "judo chops <who>.",
        "sets <who>'s resolution to 800x600.",
        "formats <who>'s harddrive to fat12.",
        "rm -rf's <who>.",
        "stabs <who>.",
        "makes <who> learn C++.",
        "steals <who>'s mojo.",
        "strangles <who> with a doohicky mouse cord.",
        "whacks <who> with the cluebat.",
        "sells <who> on EBay.",
        "drops creepers on <who>'s house.",
        "throws all of <who>'s diamond gear into lava.",
        "uses <who> as a biological warfare study.",
        "uses the 'Customer Appreciation Bat' on <who>.",
        "puts <who> in the Total Perspective Vortex.",
        "casts <who> into the fires of Mt. Doom.",
        "gives <who> a melvin.",
        "turns <who> over to the Fun Police.",
        "turns over <who> to Agent Smith to be 'bugged'.",
        "takes away <who>'s internet connection.",
        "pushes <who> past the Shoe Event Horizon.",
        "counts '1, 2, 5... er... 3!' and hurls the Holy Handgrenade Of Antioch at <who>.",
        "puts <who> in a nest of camel spiders.",
        "makes <who> read slashdot at -1.",
        "puts 'alias vim=emacs' in <who>'s /etc/profile.",
        "uninstalls every web browser from <who>'s system.",
        "locks <who> in the Chateau d'If.",
        "signs <who> up for getting hit on the head lessons.",
        "makes <who> try to set up a Lexmark printer.",
        "fills <who>'s eyedrop bottle with lime juice.",
        "casts <who> into the fires of Mt. Doom.",
        "gives <who> a Flying Dutchman.",
        "rips off <who>'s arm, and uses it to beat them to death.",
        "pierces <who>'s nose with a rusty paper hole puncher.",
        "pokes <who> with a rusty nail.",
        "puts sugar between <who>'s bedsheets.",
        "pours sand into <who>'s breakfast.",
        "mixes epoxy into <who>'s toothpaste.",
        "puts Icy-Hot in <who>'s lube container.",
        "straps <who> to a chair, and plays a endless low bitrate MP3 loop of \"the world's most annoying sound\" from \"Dumb and Dumber\".",
        "tells Dr. Dre that <who> was talking smack.",
        "forces <who> to use a Commodore 64 for all their word processing.",
        "smacks <who> in the face with a burlap sack full of broken glass.",
        "puts <who> in a room with several heavily armed manic depressives.",
        "makes <who> watch reruns of \"Blue's Clues\".",
        "puts lye in <who>'s coffee.",
        "introduces <who> to the clue-by-four.",
        "tattoos the Windows symbol on <who>'s ass.",
        "lets Borg have his way with <who>.",
        "signs <who> up for line dancing classes at the local senior center.",
        "wakes <who> out of a sound sleep with some brand new nipple piercings.",
        "gives <who> a 2 gauge Prince Albert.",
        "forces <who> to eat all their veggies.",
        "covers <who>'s toilet paper with lemon-pepper.",
        "fills <who>'s ketchup bottle with Dave's Insanity sauce.",
        "forces <who> to stare at an incredibly frustrating and seemingly never-ending IRC political debate.",
        "knocks two of <who>'s teeth out with a 2x4.",
        "removes Debian from <who>'s system.",
        "switches <who> over to CentOS.",
        "uses <who>'s iPod for skeet shooting practice.",
        "gives <who>'s phone number to Borg.",
        "posts <who>'s IP, username(s), and password(s) on 4chan.",
        "forces <who> to use words like 'irregardless' and 'administrate' (thereby sounding like a real dumbass).",
        "tickles <who> until they wet their pants and pass out.",
        "replaces <who>'s KY with elmer's clear wood glue.",
        "replaces <who>'s TUMS with alka-seltzer tablets.",
        "squeezes habanero pepper juice into <who>'s tub of vaseline.",
        "forces <who> to learn the Win32 API.",
        "gives <who> an atomic wedgie.",
        "ties <who> to a chair and forces them to listen to 'N Sync at full blast.",
        "forces <who> to use notepad for text editing.",
        "frowns at <who> really, really hard.",
        "jabs a hot lighter into <who>'s eye sockets.",
        "forces <who> to browse the web with IE6.",
        "takes <who> out at the knees with a broken pool cue.",
        "forces <who> to listen to emo music.",
        "lets a few creepers into <who>'s house.",
        "signs <who> up for the Iowa State Ferret Legging Championship.",
        "attempts to hotswap <who>'s RAM.",
        "dragon punches <who>.",
        "puts railroad spikes into <who>'s side.",
        "replaces <who>'s Astroglide with JB Weld.",
        "replaces <who>'s stress pills with rat poison pellets.",
        "replaces <who>'s crotch itch cream with Nair.",
        "does the Australian Death Grip on <who>.",
        "dances upon the grave of <who>'s ancestors.",
        "farts in <who>'s general direction.",
        "flogs <who> with stinging nettle.",
        "intoduces <who> to the Knights who say Ni.",
        "assigns all of the permissions tickets on the BeastNode support system to <who>.",
        "hands <who> a poison ivy joint."]


kills = ["rips off <who>'s <body> and leaves them to die.",
        "grabs <who>'s head and rips it clean off their body.",
        "grabs a machine gun and riddles <who>'s body with bullets.",
        "sends The Terminator on a mission to retrieve <who>'s <body>.",
        "gags and ties <who> then throws them off a bridge.",
        "crushes <who> with a huge spiked boulder.",
        "glares at <who> until they die of boredom.",
        "stuffs a few TNT blocks under <who>'s bed and sets them off.",
        "shivs <who> in the <body>.",
        "rams a rocket launcher up <who>'s ass and lets off a few rounds.",
        "crushes <who>'s skull in with a spiked mace.",
        "unleashes the armies of Isengard on <who>.",
        "packs <who> into a SVN repo.",
        "slices <who>'s <body> off with a Katana.",
        "throws <who> to Cthulu!",
        "feeds <who> to an owlbear.",
        "turns <who> into a snail and salts them.",
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
def slap(inp, me=None, nick=None, input=None, notice=None):
    ".slap <user> -- Makes the bot slap <user>."
    inp = inp.strip()

    if not re.match("^[A-Za-z0-9_|.-\]\[]*$", inp.lower()):
        notice("Invalid username!")
        return

    if inp == input.conn.nick.lower() or inp == "itself":
        target = re.sub ('<who>', nick, random.choice(slaps))
    else:
        target = re.sub ('<who>', inp, random.choice(slaps))
    msg = re.sub ('<item>', random.choice(items), target)
    me(msg)



@hook.command
def lart(inp, me=None, nick=None, input=None, notice=None):
    ".lart <user> -- Makes the bot LART <user>."
    inp = inp.strip()

    if not re.match("^[A-Za-z0-9_|.-\]\[]*$", inp.lower()):
        notice("Invalid username!")
        return

    if inp == input.conn.nick.lower() or inp == "itself":
        target = nick
    else:
        target = inp
    msg = re.sub ('<who>', target, random.choice(larts))
    me(msg)



@hook.command
def kill(inp, me=None, nick=None, input=None, notice=None):
    ".kill <user> -- Makes the bot kill <user>."
    inp = inp.strip()

    if not re.match("^[A-Za-z0-9_|.-\]\[]*$", inp.lower()):
        notice("Invalid username!")
        return

    if inp == input.conn.nick.lower() or inp == "itself":
        target = nick
    else:
        target = inp
    msg = random.choice(kills)
    msg = re.sub ('<who>', target, msg)
    msg = re.sub ('<body>', random.choice(body), msg)
    me(msg)
