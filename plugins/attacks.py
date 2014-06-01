import codecs
import json
import os
import random
import asyncio
import re

from cloudbot import hook
from cloudbot.util import textgen


@hook.onload()
def load_attacks(bot):
    """
    :type bot: cloudbot.core.bot.CloudBot
    """
    global larts, insults, flirts, kills

    with codecs.open(os.path.join(bot.data_dir, "larts.txt"), encoding="utf-8") as f:
        larts = [line.strip() for line in f.readlines() if not line.startswith("//")]

    with codecs.open(os.path.join(bot.data_dir, "insults.txt"), encoding="utf-8") as f:
        insults = [line.strip() for line in f.readlines() if not line.startswith("//")]

    with codecs.open(os.path.join(bot.data_dir, "flirts.txt"), encoding="utf-8") as f:
        flirts = [line.strip() for line in f.readlines() if not line.startswith("//")]

    with codecs.open(os.path.join(bot.data_dir, "kills.json"), encoding="utf-8") as f:
        kills = json.load(f)


def is_self(conn, target):
    """
    :type conn: cloudbot.core.connection.BotConnection
    :type target: str
    """
    if re.search("(^..?.?.?self|{})".format(re.escape(conn.nick.lower())), target.lower()):
        return True
    else:
        return False


@asyncio.coroutine
@hook.command()
def lart(text, conn, nick, notice, action):
    """<user> - LARTs <user>
    :type text: str
    :type conn: cloudbot.core.irc.BotConnection
    :type nick: str
    """
    target = text.strip()

    if " " in target:
        notice("Invalid username!")
        return

    # if the user is trying to make the bot target itself, target them
    if is_self(conn, target):
        target = nick

    phrase = random.choice(larts)

    # act out the message
    action(phrase.format(user=target))


@asyncio.coroutine
@hook.command()
def insult(text, conn, nick, notice, message):
    """<user> - insults <user>
    :type text: str
    :type conn: core.irc.BotConnection
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


@asyncio.coroutine
@hook.command()
def flirt(text, conn, nick, notice, message):
    """<user> - flirts with <user>
    :type text: str
    :type conn: core.irc.BotConnection
    :type nick: str
    """
    target = text.strip()

    # if the user is trying to make the bot target itself, target them
    if " " in target:
        notice("Invalid username!")
        return

    if is_self(conn, target):
        target = nick

    message('{}, {}'.format(target, random.choice(flirts)))


@asyncio.coroutine
@hook.command()
def kill(text, conn, nick, notice, action):
    """<user> - kills <user>
    :type text: str
    :type conn: core.irc.BotConnection
    :type nick: str
    """
    target = text.strip()

    if " " in target:
        notice("Invalid username!")
        return

    # if the user is trying to make the bot kill itself, kill them
    if is_self(conn, target):
        target = nick

    generator = textgen.TextGenerator(kills["templates"], kills["parts"], variables={"user": target})

    # act out the message
    action(generator.generate_string())
