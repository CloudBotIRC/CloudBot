from util import hook
import re
import random

insults = ["You are the son of a motherless ogre.",
        "Your mother was a hamster and your father smelled of elderberries.",
        "I once owned a dog that was smarter than you. ",
        "Go climb a wall of dicks.",
        "You fight like a dairy farmer.",
        "I've spoken to apes more polite than you.",
        "Go and boil your bottom! Son of a silly person! ",
        "I fart in your general direction.",
        "Go away or I shall taunt you a second time. ",
        "Shouldn't you have a license for being that ugly?",
        "Calling you an idiot would be an insult to all the stupid people.",
        "Why don't you slip into something more comfortable...like a coma.",
        "Well, they do say opposites attract...so I sincerely hope you meet somebody who is attractive, honest, intelligent, and cultured..",
        "Are you always this stupid or are you just making a special effort today?",
        "Yo momma so fat when she sits around the house she sits AROUND the house.",
        "Yo momma so ugly she made an onion cry.",
        "Is your name Maple Syrup? It should be, you sap.",
        "Bite my shiny metal ass!",
        "Up yours, meatbag.",
        "Jam a bastard in it you crap!",
        "Don't piss me off today, I'm running out of places to hide the bodies",
        "Why don't you go outside and play hide and go fuck yourself",
        "I'll use small words you're sure to understand, you warthog-faced buffoon.",
        "You are a sad, strange little man, and you have my pity.",
        "Sit your five dollar ass down before I make change.",
        "What you've just said is one of the most insanely idiotic things I've ever heard. Everyone in this room is now dumber for having listened to it. May God have mercy on your soul.",
        "Look up Idiot in the dictionary. Know what you'll find? The definition of the word IDIOT, which you are.",
        "You're dumber than a bag of hammers.",
        "Why don't you go back to your home on Whore Island?",
        "If I had a dick this is when I'd tell you to suck it.",
        "Go play in traffic.",
        "The village called, they want their idiot back."]

flirts = ["I bet your name's Mickey, 'cause you're so fine.",
        "Hey, pretty mama. You smell kinda pretty, wanna smell me?",
        "I better get out my library card, 'cause I'm checkin' you out.",
        "If you were a booger, I'd pick you.",
        "If I could rearrange the alphabet, I would put U and I together.",
        "I've been bad, take me to your room.",
        "I think Heaven's missing an angel.",
        "That shirt looks good on you, it'd look better on my bedroom floor.",
        "I cant help to notice but you look a lot like my next girlfriend.",
        "Aren't your feet tired? Because you've been running through my mind all day.",
        "I must be asleep, 'cause you are a dream come true. Also, I'm slightly damp.",
        "I like large posteriors and I cannot prevaricate.",
        "How you doin'?",
        "If I said you had a good body, would you hold it against me?",
        "Hey, baby cakes.",
        "Nice butt.",
        "I love you like a fat kid loves cake.",
        "Do you believe in love at first sight? Or should I walk by again...?",
        "Want to see my good side? Hahaha, that was a trick question, all I have are good sides.",
        "You look like a woman who appreciates the finer things in life. Come over here and feel my velour bedspread.",
        "Now you're officially my woman. Kudos! I can't say I don't envy you.",
        "I find that the most erotic part of a woman is the boobies.",
        "If you want to climb aboard the Love Train, you've got to stand on the Love Tracks. But you might just get smushed by a very sensual cow-catcher.",
        "Lets say you and I knock some very /sensual/ boots.",
        "I lost my phone number, can I have yours?",
        "Does this rag smell like chloroform to you? ",
        "I'm here, where are your other two wishes?",
        "Apart from being sexy, what do you do for a living?",
        "Hi, I'm Mr. Right. Someone said you were looking for me.",
        "You got something on your chest: My eyes.",
        "Are you from Tennessee? Cause you're the only TEN I see.",
        "Are you an alien? Because you just abducted my heart.",
        "Excuse me, but I think you dropped something!!! MY JAW!!!",
        "If I followed you home, would you keep me?",
        "Where have you been all my life?",
        "I'm just a love machine, and I don't work for nobody but you.",
        "Do you live on a chicken farm? Because you sure know how to raise cocks.",
        "Are you wearing space pants? Because your ass is out of this world.",
        "Nice legs. What time do they open?",
        "Your daddy must have been a baker, because you've got a nice set of buns."]


@hook.command(autohelp=False)
def insult(inp, nick=None, me=None, input=None):
    ".insult <user> -- Makes the bot insult <user>."
    inp = inp.strip()

    if not re.match("^[A-Za-z0-9_|.-\]\[]*$", inp.lower()):
        notice("Invalid username!")
        return

    target = nick
    if inp.lower() and inp != "":
        target = inp
    if inp == input.conn.nick.lower() or inp == "itself":
        target = nick
    msg = "insults " + target + "... \"" + random.choice(insults) + "\""
    me(msg)


@hook.command(autohelp=False)
def flirt(inp, nick=None, me=None, input=None):
    ".flirt <user> -- Make the bot flirt with <user>."
    inp = inp.strip()

    if not re.match("^[A-Za-z0-9_|.-\]\[]*$", inp.lower()):
        notice("Invalid username!")
        return

    target = nick
    if inp.lower() and inp != "":
        target = inp
    if inp == input.conn.nick.lower() or inp == "itself":
        target = "itself"
    msg = "flirts with " + target + "... \"" + random.choice(flirts) + "\""
    me(msg)
