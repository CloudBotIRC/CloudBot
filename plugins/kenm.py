import codecs
import os
import random
import re

from cloudbot import hook

@hook.on_start()
def load_kenm(bot):
    """
    :type bot: cloudbot.bot.Cloudbot
    """
    global kenm

    with codecs.open(os.path.join(bot.data_dir, "kenm.txt"), encoding="utf-8") as f:
        kenm = [line.strip() for line in f.readlines() if not line.startswith("//")]

@hook.command("kenm", autohelp=False)
def kenm(message, conn):
    """Wisdom from Ken M."""
    message(random.choice(kenm))
