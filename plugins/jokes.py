import codecs
import os
import random

from cloudbot import hook

@hook.on_start()
def load_jokes(bot):
    """
    :type bot: cloudbot.bot.Cloudbot
    """
    global yo_momma, do_it, pun, confucious, one_liner, wisdom

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

@hook.command()
def yomomma(text, message, conn):
    """input <nick>, tells a yo momma joke to <nick>"""
    target = text.strip()
    message('{}, {}'.format(target, random.choice(yo_momma)))

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
