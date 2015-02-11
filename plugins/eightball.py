import os
import asyncio
import codecs
import random

from cloudbot import hook
from cloudbot.util import colors


@hook.on_start()
def load_responses(bot):
    path = os.path.join(bot.data_dir, "8ball_responses.txt")
    global responses
    with codecs.open(path, encoding="utf-8") as f:
        responses = [line.strip() for line in
                     f.readlines() if not line.startswith("//")]


@asyncio.coroutine
@hook.command("8ball", "8", "eightball")
def eightball(action):
    """<question> - asks the all knowing magic electronic eight ball <question>"""
    magic = random.choice(responses)
    message = colors.parse("shakes the magic 8 ball... {}".format(magic))

    action(message)
