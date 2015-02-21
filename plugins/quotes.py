import codecs
import json
import os
import random
import asyncio
import re

from cloudbot import hook
from cloudbot.util import textgen


@hook.on_start()
def load_foods(bot):
    """
    :type bot: cloudbot.bot.CloudBot
    """
    
    global basic_data
    global funday_data

    with codecs.open(os.path.join(bot.data_dir, "basic.json"), encoding="utf-8") as bData:
        basic_data = json.load(bData)
    
    with codecs.open(os.path.join(bot.data_dir, "funday.json"), encoding="utf-8") as fData:
        funday_data = json.load(fData)

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
def funday(text, conn, nick, notice, action):
    """<user> - give a bollywood funda to <user>
    :type text: str
    :type conn: cloudbot.client.Client
    :type nick: str
    """
    target = text.strip()

    if " " in target:
        notice("Invalid username!")
        return

    generator = textgen.TextGenerator(funday_data["templates"], funday_data["parts"],
                                      variables={"user": target})

    # act out the message
    action(generator.generate_string())


@asyncio.coroutine
@hook.command()
def basic(text, conn, nick, notice, action):
    """<user> - show how basic you are to <user>
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
    
    generator = textgen.TextGenerator(basic_data["templates"], basic_data["parts"],
                                        variables={"user": target})

    # act out the message
    action(generator.generate_string())
