import codecs
import json
import os
import random
import asyncio
import re

from cloudbot import hook
from cloudbot.util import textgen

nick_re = re.compile("^[A-Za-z0-9_|.\-\]\[\{\}]*$", re.I)


def is_valid(target):
    """ Checks if a string is a valid IRC nick. """
    if nick_re.match(target):
        return True
    else:
        return False


def is_self(conn, target):
    """ Checks if a string is "****self" or contains conn.name. """
    if re.search("(^..?.?.?self|{})".format(re.escape(conn.nick)), target, re.I):
        return True
    else:
        return False


@hook.on_start()
def load_attacks(bot):
    """
    :type bot: cloudbot.bot.CloudBot
    """
    global larts, flirts, kills, slaps, north_korea, insults

    with codecs.open(os.path.join(bot.data_dir, "larts.txt"), encoding="utf-8") as f:
        larts = [line.strip() for line in f.readlines() if not line.startswith("//")]

    with codecs.open(os.path.join(bot.data_dir, "flirts.txt"), encoding="utf-8") as f:
        flirts = [line.strip() for line in f.readlines() if not line.startswith("//")]

    with codecs.open(os.path.join(bot.data_dir, "insults.txt"), encoding="utf-8") as f:
        insults = [line.strip() for line in f.readlines() if not line.startswith("//")]

    with codecs.open(os.path.join(bot.data_dir, "kills.json"), encoding="utf-8") as f:
        kills = json.load(f)

    with codecs.open(os.path.join(bot.data_dir, "slaps.json"), encoding="utf-8") as f:
        slaps = json.load(f)

    with codecs.open(os.path.join(bot.data_dir, "north_korea.txt"), encoding="utf-8") as f:
        north_korea = [line.strip() for line in f.readlines() if not line.startswith("//")]


@asyncio.coroutine
@hook.command
def lart(text, conn, nick, action):
    """<user> - LARTs <user>"""
    target = text.strip()

    if not is_valid(target):
        return "I can't attack that."

    if is_self(conn, target):
        # user is trying to make the bot attack itself!
        target = nick

    phrase = random.choice(larts)

    # act out the message
    action(phrase.format(user=target))


@asyncio.coroutine
@hook.command("flirt", "sexup", "jackmeoff")
def flirt(text, conn, nick, message):
    """<user> - flirts with <user>"""
    target = text.strip()

    if not is_valid(target):
        return "I can't attack that."

    if is_self(conn, target):
        # user is trying to make the bot attack itself!
        target = nick

    message('{}, {}'.format(target, random.choice(flirts)))


@asyncio.coroutine
@hook.command
def kill(text, conn, nick, action):
    """<user> - kills <user>"""
    target = text.strip()

    if not is_valid(target):
        return "I can't attack that."

    if is_self(conn, target):
        # user is trying to make the bot attack itself!
        target = nick

    generator = textgen.TextGenerator(kills["templates"], kills["parts"], variables={"user": target})

    # act out the message
    action(generator.generate_string())


@asyncio.coroutine
@hook.command
def slap(text, action, nick, conn, notice):
    """<user> -- Makes the bot slap <user>."""
    target = text.strip()

    if not is_valid(target):
        return "I can't attack that."

    if is_self(conn, target):
        # user is trying to make the bot attack itself!
        target = nick

    variables = {
        "user": target
    }
    generator = textgen.TextGenerator(slaps["templates"], slaps["parts"], variables=variables)

    # act out the message
    action(generator.generate_string())

@hook.command(autohelp=False)
def nk(chan, message):
    """outputs a random North Korea propoganda slogan"""
    index = random.randint(0,len(north_korea)-1)
    slogan = north_korea[index]
    message(slogan, chan)

@asyncio.coroutine
@hook.command()
def insult(text, conn, nick, notice, message):
    """<user> - insults <user>
    :type text: str
    :type conn: cloudbot.client.Client
    :type nick: str
    """
    target = text.strip()

    if " " in target:
        notice("Invalid username!")
        return

    # if the user is trying to make the bot target itself, target them
    if is_self(conn, target):
        target = nick

    message("{}, {}".format(target, random.choice(insults)))

