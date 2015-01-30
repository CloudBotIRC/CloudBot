import codecs
import json
import os
import random
import asyncio
import re

from cloudbot import hook
from cloudbot.util import textgen


@hook.on_start()
def load_attacks(bot):
    """
    :type bot: cloudbot.bot.CloudBot
    """
    global larts, insults, flirts, kills, slaps, moms

    with codecs.open(os.path.join(bot.data_dir, "larts.json"), encoding="utf-8") as f:
        larts = json.load(f)

    with codecs.open(os.path.join(bot.data_dir, "flirts.json"), encoding="utf-8") as f:
        flirts = json.load(f)

    with codecs.open(os.path.join(bot.data_dir, "moms.json"), encoding="utf-8") as f:
        moms = json.load(f)

    with codecs.open(os.path.join(bot.data_dir, "kills.json"), encoding="utf-8") as f:
        kills = json.load(f)

    with codecs.open(os.path.join(bot.data_dir, "slaps.json"), encoding="utf-8") as f:
        slaps = json.load(f)


def is_self(conn, target):
    """
    :type conn: cloudbot.client.Client
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

    generator = textgen.TextGenerator(larts["templates"], larts["parts"], variables={"user": target})

    # act out the message
    action(generator.generate_string())


@asyncio.coroutine
@hook.command()
def flirt(text, conn, nick, notice, message):
    """<user> - flirts with <user>
    :type text: str
    :type conn: cloudbot.client.Client
    :type nick: str
    """
    target = text.strip()

    # if the user is trying to make the bot target itself, target them
    if " " in target:
        notice("Invalid username!")
        return


	# if the user is trying to make the bot target itself, target them
    if is_self(conn, target):
        target = nick
	
    generator = textgen.TextGenerator(flirts["templates"], flirts["parts"], variables={"user": target})

    # act out the message
    message(generator.generate_string())


@asyncio.coroutine
@hook.command()
def kill(text, conn, nick, notice, action):
    """<user> - kills <user>
    :type text: str
    :type conn: cloudbot.client.Client
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


@hook.command
def slap(text, action, nick, conn, notice):
    """slap <user> -- Makes the bot slap <user>."""
    target = text.strip()

    if " " in target:
        notice("Invalid username!")
        return

    # if the user is trying to make the bot slap itself, slap them
    if target.lower() == conn.nick.lower() or target.lower() == "itself":
        target = nick

    variables = {
        "user": target
    }
    generator = textgen.TextGenerator(slaps["templates"], slaps["parts"], variables=variables)

    # act out the message
    action(generator.generate_string())


@asyncio.coroutine
@hook.command()
def insult(text, conn, nick, notice, message):
    """<user> - insults <user>
    :type text: str
    :type conn: cloudbot.client.Client
    :type nick: str
    """
    target = text.strip()

    # if the user is trying to make the bot target itself, target them
    if " " in target:
        notice("Invalid username!")
        return

    if is_self(conn, target):
        target = nick
    
    generator = textgen.TextGenerator(moms["templates"], moms["parts"], variables={"user": target})

    # act out the message
    message(generator.generate_string())
