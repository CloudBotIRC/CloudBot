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
    global sandwhich_data
    global mirchi_data
    global dhokla_data
    global basic_data

    with codecs.open(os.path.join(bot.data_dir, "sandwich.json"), encoding="utf-8") as f:
        sandwhich_data = json.load(f)

    with codecs.open(os.path.join(bot.data_dir, "mirchi.json"), encoding="utf-8") as mData:
        mirchi_data = json.load(mData)
        
    with codecs.open(os.path.join(bot.data_dir, "dhokla.json"), encoding="utf-8") as dData:
        dhokla_data = json.load(dData)

    with codecs.open(os.path.join(bot.data_dir, "basic.json"), encoding="utf-8") as bData:
        basic_data = json.load(bData)

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
def dhokla(text, conn, nick, notice, action):
    """<user> - give a tasty dhokla to <user>                                                                                                                      
    :type text: str                                                                                                                                                
    :type conn: cloudbot.client.Client                                                                                                                             
    :type nick: str                                                                                                                                                
    """
    target = text.strip()
    if " " in target:
        notice("Invalid username!")
        return
    generator = textgen.TextGenerator(dhokla_data["templates"], dhokla_data["parts"],
                                      variables={"user": target})
    # act out the message                                                                                                                                          
    action(generator.generate_string())



@asyncio.coroutine
@hook.command()
def mirchi(text, conn, nick, notice, action):
    """<user> - give a tasty mirchi to <user>
    :type text: str
    :type conn: cloudbot.client.Client
    :type nick: str
    """
    target = text.strip()

    if " " in target:
        notice("Invalid username!")
        return

    generator = textgen.TextGenerator(mirchi_data["templates"], mirchi_data["parts"],
                                      variables={"user": target})

    # act out the message
    action(generator.generate_string())

@asyncio.coroutine
@hook.command()
def sandwich(text, conn, nick, notice, action):
    """<user> - give a tasty sandwich to <user>
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

    generator = textgen.TextGenerator(sandwhich_data["templates"], sandwhich_data["parts"],
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
