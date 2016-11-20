import codecs
import json
import os
import random
import asyncio

from cloudbot import hook
from cloudbot.util import textgen

@hook.on_start()
def load_clintons(bot):
    """
    :type bot: cloudbot.bot.CloudBot
    """
    global clinton_data

    with codecs.open(os.path.join(bot.data_dir, "clinton.json"), encoding="utf-8") as f:
        clinton_data = json.load(f)

@asyncio.coroutine
@hook.command
def clinton(text, action):
    """clinton a user."""
    user = text.strip()
    generator = textgen.TextGenerator(clinton_data["templates"], clinton_data["parts"], variables={"user": user})
    action(generator.generate_string())
