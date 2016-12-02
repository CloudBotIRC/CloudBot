import codecs
import os
import random
import re

from cloudbot import hook

@hook.on_start()
def load_fmk(bot):
    """
    :type bot: cloudbot.bot.Cloudbot
    """
    global fmklist

    with codecs.open(os.path.join(bot.data_dir, "fmk.txt"), encoding="utf-8") as f:
        fmklist = [line.strip() for line in f.readlines() if not line.startswith("//")]

@hook.command("fmk", autohelp=False)
def fmk(text, message):
    """Fuck, Marry, Kill"""
    message(" {} FMK - {}, {}, {}".format((text.strip() if text.strip() else ""), random.choice(fmklist), random.choice(fmklist), random.choice(fmklist)))
