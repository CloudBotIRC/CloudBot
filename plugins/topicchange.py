import codecs
import os
import random
import re

from cloudbot import hook

@hook.on_start()
def load_topicchange(bot):
    """
    :type bot: cloudbot.bot.Cloudbot
    """
    global topicchange

    with codecs.open(os.path.join(bot.data_dir, "topicchange.txt"), encoding="utf-8") as f:
        topicchange = [line.strip() for line in f.readlines() if not line.startswith("//")]

@hook.command("changetopic", "discuss", "question", autohelp=False)
def topicchange(message, conn):
    """generates a random question to help start a conversation or change a topic"""
    message(random.choice(topicchange))
