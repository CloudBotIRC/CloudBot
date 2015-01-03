import codecs
import json
import os
import random
import asyncio
import re

from cloudbot import hook
from cloudbot.util import textgen


@hook.onload()
def load_foods(bot):
    """
    :type bot: cloudbot.bot.CloudBot
    """
    global sandwhich_data

    with codecs.open(os.path.join(bot.data_dir, "sandwich.json"), encoding="utf-8") as f:
        sandwhich_data = json.load(f)


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
