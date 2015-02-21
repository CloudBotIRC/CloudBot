import codecs
import json
import os
import random
import asyncio
import re

from cloudbot import hook
from cloudbot.util import textgen

nick_re = re.compile("^[A-Za-z0-9_|.\-\]\[]*$", re.I)

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

def get_attack_string(text, conn, nick, notice, attack_json, message):
    """
    :type text: str
    :type conn: cloudbot.client.Client
    :type nick: str
    """
    
    target = text.strip()
    
    if not is_valid(target):
        notice("Invalid username!")
        return None

    # if the user is trying to make the bot target itself, target them
    if is_self(conn, target):
        target = nick

    permission_manager = conn.permissions
    if permission_manager.has_perm_nick(target, "unattackable"):
        generator = textgen.TextGenerator(flirts["templates"], flirts["parts"], variables={"user": target})
        message(generator.generate_string())
        return None
    else:
        generator = textgen.TextGenerator(attack_json["templates"], attack_json["parts"], variables={"user": target})
        return generator.generate_string()

@asyncio.coroutine
@hook.command()
def lart(text, conn, nick, notice, action, message):
    """<user> - LARTs <user>
    :type text: str
    :type conn: cloudbot.client.Client
    :type nick: str
    """
    
    phrase = get_attack_string(text, conn, nick, notice, larts, message) 
    if phrase is not None:
        action(phrase)


@asyncio.coroutine
@hook.command()
def flirt(text, conn, nick, notice, action, message):
    """<user> - flirts with <user>
    :type text: str
    :type conn: cloudbot.client.Client
    :type nick: str
    """
    
    phrase = get_attack_string(text, conn, nick, notice, flirts, message) 
    if phrase is not None:
        message(phrase)


@asyncio.coroutine
@hook.command()
def kill(text, conn, nick, notice, action, message):
    """<user> - kills <user>
    :type text: str
    :type conn: cloudbot.client.Client
    :type nick: str
    """
    
    phrase = get_attack_string(text, conn, nick, notice, kills, message) 
    if phrase is not None:
        action(phrase)


@hook.command
def slap(text, nick, conn, notice, action, message):
    """slap <user> -- Makes the bot slap <user>."""
    
    phrase = get_attack_string(text, conn, nick, notice, slaps, message) 
    if phrase is not None:
        action(phrase)


@asyncio.coroutine
@hook.command()
def insult(text, conn, nick, notice, action, message):
    """<user> - insults <user>
    :type text: str
    :type conn: cloudbot.client.Client
    :type nick: str
    """
    
    phrase = get_attack_string(text, conn, nick, notice, moms, message) 
    if phrase is not None:
        message(phrase)