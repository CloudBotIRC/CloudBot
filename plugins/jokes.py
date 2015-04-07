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
    global yo_momma, do_it, pun, confucious, one_liner, wisdom, book_puns

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
