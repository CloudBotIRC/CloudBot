from util import hook
import re
import random

larts = ["swaps <who>'s shampoo with glue",
        "installs windows on <who>'s machine",
        "forces <who> to use perl for 3 weeks",
        "registers <who>'s name with 50 known spammers",
        "resizes <who>'s  to 40x24",
        "takes <who>'s drink",
        "dispenses <who>'s email address to a few hundred 'bulk mailing services'",
        "pokes <who> in the eye",
        "beats <who> senseless with a 50lb Linux manual",
        "cats /dev/random into <who>'s ear",
        "signs <who> up for AOL",
        "enrolls <who> in Visual Basic 101",
        "sporks <who>",
        "drops a truckload of support tickets on <who>",
        "judo chops <who>",
        "sets <who>'s resolution to 800x600",
        "formats <who>'s harddrive to fat12",
        "rm -rf's <who>",
        "stabs <who>",
        "steals <who>'s mojo",
        "strangles <who> with a doohicky mouse cord",
        "whacks <who> with the cluebat",
        "sells <who> on EBay",
        "uses <who> as a biological warfare study",
        "uses the 'Customer Appreciation Bat' on <who>",
        "puts <who> in the Total Perspective Vortex",
        "casts <who> into the fires of Mt. Doom",
        "gives <who> a melvin",
        "turns over <who> to Agent Smith to be 'bugged'",
        "takes away <who>'s internet connection",
        "pushes <who> past the Shoe Event Horizon",
        "counts '1, 2, 5... er... 3!' and hurls the Holy Handgrenade Of Antioch at <who>",
        "puts <who> in a nest of camel spiders",
        "makes <who> read slashdot at -1",
        "puts 'alias vim=emacs' in <who>'s /etc/profile",
        "uninstalls every web browser from <who>'s system",
        "locks <who> in the Chateau d'If",
        "signs <who> up for getting hit on the head lessons",
        "makes <who> try to set up a Lexmark printer",
        "fills <who>'s eyedrop bottle with lime juice",
        "casts <who> into the fires of Mt. Doom.",
        "gives <who> a Flying Dutchman",
        "rips off <who>'s arm, and uses it to beat them to death",
        "pierces <who>'s nose with a rusty paper hole puncher",
        "pokes <who> with a rusty nail",
        "puts sugar between <who>'s bedsheets",
        "pours sand into <who>'s breakfast",
        "mixes epoxy into <who>'s toothpaste",
        "puts Icy-Hot in <who>'s lube container",
        "straps <who> to a chair, and plays a endless low bitrate MP3 loop of \"the world's most annoying sound\" from \"Dumb and Dumber\"",
        "tells Dr. Dre that <who> was talking smack",
        "forces <who> to use a Commodore 64 for all their word processing",
        "smacks <who> in the face with a burlap sack full of broken glass",
        "puts <who> in a room with several heavily armed manic depressives",
        "makes <who> watch reruns of \"Blue's Clues\"",
        "puts lye in <who>'s coffee",
        "tattoos the Windows symbol on <who>'s ass",
        "lets Borg have his way with <who>",
        "signs <who> up for line dancing classes at the local senior center",
        "wakes <who> out of a sound sleep with some brand new nipple piercings",
        "gives <who> a 2 guage Prince Albert",
        "forces <who> to eat all their veggies",
        "covers <who>'s toilet paper with lemon-pepper",
        "fills <who>'s ketchup bottle with Dave's Insanity sauce",
        "forces <who> to stare at an incredibly frustrating and seemingly neverending IRC political debate",
        "knocks two of <who>'s teeth out with a 2x4",
        "removes debian from <who>'s system",
        "uses <who>'s iPod for skeet shooting practice",
        "gives <who>'s phone number to Borg",
        "posts <who>'s IP, username, and password on 4chan",
        "forces <who> to use words like 'irregardless' and 'administrate' (thereby sounding like a real dumbass)",
        "tickles <who> until they wet their pants and pass out",
        "replaces <who>'s KY with elmer's clear wood glue",
        "replaces <who>'s TUMS with alka-seltzer tablets",
        "squeezes habanero pepper juice into <who>'s tub of vaseline",
        "Forces <who> to learn the Win32 API",
        "gives <who> an atomic wedgie",
        "ties <who> to a chair and forces them to listen to 'N Sync at full blast",
        "forces <who> to use notepad for text editing",
        "frowns at <who> really really hard",
        "jabs a hot lighter into <who>'s eye sockets",
        "forces <who> to browse the web with IE6",
        "takes <who> out at the knees with a broken pool cue",
        "forces <who> to listen to emo music",
        "lets a few creepers into <who>'s house",
        "signs <who> up for the Iowa State Ferret Legging Championship",
        "attempts to hotswap <who>'s RAM",
        "dragon punches <who>",
        "puts track spikes into <who>'s side",
        "replaces <who>'s Astroglide with JB Weld",
        "replaces <who>'s stress pills with rat poison pellets",
        "replaces <who>s crotch itch cream with Nair",
        "does the Australian Death Grip on <who>",
        "dances upon the grave of <who>'s ancestors.",
        "farts in <who>'s general direction",
        "flogs <who> with stinging neddle",
        "assigns all of the permissions tickets on the BeastNode support system to <who>",
        "hands <who> a poison ivy joint"]

loves = ["hugs <who>",
        "gives <who> some love",
        "gives <who> a cookie",
        "makes a balloon animal for <who>",
        "shares a slice of cake with <who>",
        "slaps <who> heartily on the back",
        "tickles <who>"]

slaps = ["slaps <who> with a <item>",
        "slaps <who> around a bit with a <item>",
        "throws a <item> at <who>",
        "grabs a <item> and throws it in <who>'s face",
        "holds <who> down and repeatedly whacks them with a <item>",
        "prods <who> with a flaming <item>",
        "picks up a <item>, and whacks <who> with it",
        "ties <who> to a chair and throws a <item> at them",
        "hits <who> on the head with a <item>"]

items = ["cast iron skillet",
        "large trout",
        "baseball bat",
        "wooden cane",
        "CRT monitor",
        "physics textbook",
        "television",
        "five tonne truck",
        "roll of duct tape",
        "book",
        "rubber chicken",
        "fire extinguisher",
        "heavy rock",
        "chunk of dirt"]

@hook.command
def lart(inp, me = None,  nick = None, input=None, notice=None):
    ".lart <user> - LARTs a user of your choice"
    inp = inp.strip()

    if not re.match("^[A-Za-z0-9_|.-\]\[]*$", inp.lower()):
        notice("Invalid username!")
        return

    if inp == input.conn.nick.lower() or inp == "itself":
        msg = 'slaps ' + nick + ' in the face!'
    else:
        msg = re.sub ('<who>', inp, random.choice(larts))

    me(msg)

@hook.command
def love(inp, me = None, input=None, notice=None):
    ".love <user> - gives a user a nice comment"
    inp = inp.strip()

    if not re.match("^[A-Za-z0-9_|.-\]\[]*$", inp.lower()):
        notice("Invalid username!")
        return

    if inp == input.conn.nick.lower() or inp == "itself":
        msg = 'hugs themself!'
    else:
        msg = re.sub ('<who>', inp, random.choice(loves))

    me(msg)

@hook.command
def slap(inp, me = None, nick = None, input=None, notice=None):
    ".slap <user> - slap a user"
    inp = inp.strip()

    if not re.match("^[A-Za-z0-9_|.-\]\[]*$", inp.lower()):
        notice("Invalid username!")
        return

    if inp == input.conn.nick.lower() or inp == "itself":
        msg = 'slaps ' + nick + ' in the face!'
    else:
        slap = random.choice(slaps)
        slap = re.sub ('<who>', inp, slap)
        msg = re.sub ('<item>', random.choice(items), slap)

    me(msg)

