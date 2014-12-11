import codecs
import json
import os
import random

from cloudbot import hook


@hook.onload()
def load_text(bot):
    """
    :type bot: cloudbot.bot.CloudBot
    """
    global leet

    with codecs.open(os.path.join(bot.data_dir, "leet.json"), encoding="utf-8") as f:
        leet = json.load(f)


@hook.command("leet")
def leet(text):
    output = ''.join(random.choice(leet[ch]) if ch.isalpha() else ch for ch in text.lower())
    return output