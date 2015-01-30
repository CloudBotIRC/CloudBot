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

def get_attack_string(text, conn, nick, notice, attack_json):
    """
    :type text: str
    :type conn: cloudbot.client.Client
    :type nick: str
    """
    
    target = text.strip()
    
    if " " in target:
        notice("Invalid username!")
        return None

    # if the user is trying to make the bot target itself, target them
    if is_self(conn, target):
        target = nick

    generator = textgen.TextGenerator(attack_json["templates"], attack_json["parts"], variables={"user": target})
    return generator.generate_string()

@asyncio.coroutine
@hook.command()
def lart(text, conn, nick, notice, action):
    """<user> - LARTs <user>
    :type text: str
    :type conn: cloudbot.client.Client
    :type nick: str
    """
    
    phrase = get_attack_string(text, conn, nick, notice, larts) 
    if phrase is not None:
        action(phrase)


@asyncio.coroutine
@hook.command()
def flirt(text, conn, nick, notice, message):
    """<user> - flirts with <user>
    :type text: str
    :type conn: cloudbot.client.Client
    :type nick: str
    """
    
    phrase = get_attack_string(text, conn, nick, notice, flirts) 
    if phrase is not None:
        message(phrase)


@asyncio.coroutine
@hook.command()
def kill(text, conn, nick, notice, action):
    """<user> - kills <user>
    :type text: str
    :type conn: cloudbot.client.Client
    :type nick: str
    """
    
    phrase = get_attack_string(text, conn, nick, notice, kills) 
    if phrase is not None:
        action(phrase)


@hook.command
def slap(text, action, nick, conn, notice):
    """slap <user> -- Makes the bot slap <user>."""
    
    phrase = get_attack_string(text, conn, nick, notice, slaps) 
    if phrase is not None:
        action(phrase)


@asyncio.coroutine
@hook.command()
def insult(text, conn, nick, notice, message):
    """<user> - insults <user>
    :type text: str
    :type conn: cloudbot.client.Client
    :type nick: str
    """
    
    phrase = get_attack_string(text, conn, nick, notice, moms) 
    if phrase is not None:
        message(phrase)