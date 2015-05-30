import codecs
import json
import os
import random
import asyncio

from cloudbot import hook
from cloudbot.util import textgen

def is_valid(target):
    """ Checks if a string is a valid IRC nick. """
    if nick_re.match(target):
        return True
    else:
        return False


@hook.on_start()
def load_spanks(bot):
    """
    :type bot: cloudbot.bot.CloudBot
    """
    global spank_data

    with codecs.open(os.path.join(bot.data_dir, "spank.json"), encoding="utf-8") as f:
        spank_data = json.load(f)

@asyncio.coroutine
@hook.command
def spank(text, action):
    """<user> - give tea to <user>"""
    user = text.strip()

    #if not is_valid(user):
    #    return "I can't give tea to that user."

    generator = textgen.TextGenerator(spank_data["templates"], spank_data["parts"],
                                      variables={"user": user})
    # act out the message
    action(generator.generate_string())
