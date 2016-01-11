import codecs
import os
import random
import re

from cloudbot import hook

@hook.on_start()
def load_jokes(bot):
    """
    :type bot: cloudbot.bot.Cloudbot
    """
    global yo_momma, do_it, pun, confucious, one_liner, wisdom, book_puns, lawyerjoke

    with codecs.open(os.path.join(bot.data_dir, "yo_momma.txt"), encoding="utf-8") as f:
        yo_momma = [line.strip() for line in f.readlines() if not line.startswith("//")]

    with codecs.open(os.path.join(bot.data_dir, "do_it.txt"), encoding="utf-8") as f:
        do_it = [line.strip() for line in f.readlines() if not line.startswith("//")]

    with codecs.open(os.path.join(bot.data_dir, "puns.txt"), encoding="utf-8") as f:
        pun = [line.strip() for line in f.readlines() if not line.startswith("//")]

    with codecs.open(os.path.join(bot.data_dir, "confucious.txt"), encoding="utf-8") as f:
        confucious = [line.strip() for line in f.readlines() if not line.startswith("//")]

    with codecs.open(os.path.join(bot.data_dir, "one_liners.txt"), encoding="utf-8") as f:
        one_liner = [line.strip() for line in f.readlines() if not line.startswith("//")]

    with codecs.open(os.path.join(bot.data_dir, "wisdom.txt"), encoding="utf-8") as f:
        wisdom = [line.strip() for line in f.readlines() if not line.startswith("//")]
    
    with codecs.open(os.path.join(bot.data_dir, "book_puns.txt"), encoding="utf-8") as f:
        book_puns = [line.strip() for line in f.readlines() if not line.startswith("//")]

    with codecs.open(os.path.join(bot.data_dir, "lawyerjoke.txt"), encoding="utf-8") as f:
        lawyerjoke = [line.strip() for line in f.readlines() if not line.startswith("//")]

@hook.command()
def yomomma(text, message, conn):
    """input <nick>, tells a yo momma joke to <nick>"""
    target = text.strip()
    message('{}, {}'.format(target, random.choice(yo_momma).lower()))

@hook.command(autohelp=False)
def doit(message, conn):
    """prints a do it line, example: mathmaticians do with a pencil"""
    message(random.choice(do_it))


@hook.command(autohelp=False)
def pun(message, conn):
    """Come on everyone loves puns right?"""
    message(random.choice(pun))

@hook.command(autohelp=False)
def confucious(message, conn):
    """confucious say man standing on toilet is high on pot."""
    message('Confucious say {}'.format(random.choice(confucious).lower()))

@hook.command(autohelp=False)
def dadjoke(message, conn):
    """love em or hate em, bring on the dad jokes."""
    message(random.choice(one_liner))

@hook.command(autohelp=False)
def wisdom(message, conn):
    """words of wisdom from various bathroom stalls."""
    message(random.choice(wisdom))

@hook.command(autohelp=False)
def bookpun(message, conn):
    """Suggests a pun of a book title/author."""
    #suggestions = ["Why not try", "You should read", "You gotta check out"]
    book = random.choice(book_puns)
    title = book.split(':')[0].strip()
    author = book.split(':')[1].strip()
    message("{} by {}".format(title, author))

@hook.command("boobs", "boobies")
def boobies(text, conn):
    """prints boobies!"""
    boob = "\u2299"
    out = text.strip()
    out = out.replace('o', boob).replace('O', boob).replace('0', boob)
    if out == text.strip():
        return "Sorry I couldn't turn anything in '{}' into boobs for you.".format(out)
    return out

@hook.command("awesome", "iscool", "cool")
def awesome(text, message):
    """Prints a webpage to show <nick> how awesome they are."""
    nick_re = re.compile("^[A-Za-z0-9_|.\-\]\[]*$", re.I)
    link = 'http://{}.is-awesome.cool/{}'
    nick = text.split(' ')[0]
    if nick_re.match(nick):
        message("{}: I am blown away by your recent awesome action(s). Please read \x02{}\x02".format(nick, link.format(nick, nick)))
    else:
        return "Sorry I can't tell {} how awesome they are.".format(nick)

@hook.command(autohelp=False)
def triforce(message):
    """returns a triforce!"""
    top = ["\u00a0\u25b2","\u00a0\u00a0\u25b2", "\u25b2", "\u00a0\u25b2"]
    bottom = ["\u25b2\u00a0\u25b2", "\u25b2 \u25b2", "\u25b2\u25b2"]
    message(random.choice(top))
    message(random.choice(bottom))

@hook.command("kero", "kerowhack")
def kero(text, message):
    """Returns the text input the way kerouac5 would say it."""
    saying = ["PRIUS JIMMY BUFFET!!!", "DISNEY APPLE BEARDS, FUCK COFFEE!", "FUCK THINGS THAT ARE GOOD AND NICE!", "RED ZONE SCHMED ZONE!", "i DONT USE APPLE CPMPUTERS!!!!", "???!??!?  YOU CLEARLY DONT LISTEN!", "WHY ARE PEOPLE CALLING ME A NERD I WAS ON THE iPHONE AND DONT GET IT!!!!", "OH MAN FUCK BEARDS!", "I AM GOING DOWN THE HALL TO A MEETING UNDER MY OWN POWER RIGHT NOW!!!", "NOT A VEGETABLE!!!!!!!", "i think thats a vulva euphemism, PW.", "THEY START SHOVING CAKES IN EACH OTHERS FACES LIKE ITS A MANATEE WEDDING HOLY SHIT!", "I DONT MAKE THE NEWS I JUST REPORT IT!", "HURR DURR YOU ARE OLD WITH PRINTED PAGES", "pants on head mouthbreather.", "HELLO I AM BACK WHAT IS NEW?", "YOU ARE A HORRIBLE DEAD FAN!", "i try not to be racist, but seriously.  there's a mexican guy in our neighborhood.  on the 4th like 40 people in his family came over and shot off fireworks and they sat in lawn chairs in the front yard.", "there's an old asian woman in our neighborhood who hides in her house and walks 10 feet  behind her husband and is a bad driver.", "HOW AM I NOT SUPPOSED TO BE RACIST WITH THAT OVERWHELMING EVIDENCE EXACTLY!?!?", "???? WTF IS", "NO I NEVER THINK THAT I AM VERY HAPPY", "HORSES CANT TALK IDIOTS", "I WENT TO ZERO STRIP CLUBS AND HAD ZERO STREET BEER", "I FUCKING WRITE CURRICULUM ON HOW TO SELL AND NETWORK AND RUN A BUSINESS ALL FUCKING DAY LONG", "you gentlemen are hilarious.  theres certainly nothing in what you're doing that could be considered \"ball busting\" or \"trolling.\"", "YOU CAN EMAIL FROM YOUR PHONE? MAGIC MAN FROM THE FUTURE, DO THEY HAVE RUBBER VAGINAS MEN CAN PUT THEIR DICKS INTO AS WELL?", "really who the fuck cares who the third president was?", "why dont you just bore your candidat to tears with talk about subarus and guns and talk about the recruiters that have been calling *you*? Itll be just like irc.", "DONT TAKE AWAY MY FUN.", "I may beat off on the notes afterward because that turns me on, DONT JUDGE ME ITS NORMAL.", "wtf is a homeless guyy gonna do with a speaker SURE WOULD LIKE TO EAT BUT AT LEAST I HAVE MY KOOL JAMZ", "thanks for overexplaining that one", "Really.  I say ejaculating on pictures is weird and somehow that translates to OMG WAT A PRUDE", "Had someone ejaculate on a picture of me.  Gotta try it once.", "apparently theres a thing where people ejaculate on pictures i bet you could monetize that.", "'Hey you can talk to this chick and maybe get laid or cum on a picture,' only complete social retards pick the latter.", "Hahaha those weirdos with tentacle porn excuse me I need to whack it on a picture and put it on the Internet.", "enjoy your penis salad sandwich", "im pretty sure ive never said 'OH MY GOODNESS LOOK AT HIS PENIS I WISH I HAD THAT PENIS' then went searching for it to show someone else 24 hours later because i couldn't stop thinking about teddy bridgewater's beautiful penis <3", "i don't think \"we\" have ever \"talked a lot of dick.\"", "OMG DID YOU SEE THE BALLS TOO?", "be as weird as you want. i dont understand why its so cool now to go \"OOOO THATS JUST WHO HE IS DONT JUDGE.\" if you like to have your balls hit with a hammer while you ejaculate onto pictures of horses i think you should be called fucking weird."]
    keror = random.choice(saying).upper()
    if keror == "???? WTF IS":
        out = keror + " " + text.upper()
    else:
        out = text.upper() + " " + keror
    message(out)

@hook.command(autohelp=False)
def lawyerjoke(message, conn):
    """returns a lawyer joke, so lawyers know how much we hate them"""
    message(random.choice(lawyerjoke))
