import os
import asyncio
import random

from cloudbot import hook, formatting

color_codes = {
    "<r>": "\x02\x0305",
    "<g>": "\x02\x0303",
    "<y>": "\x02"
}


@hook.onload()
def load_responses(bot):
    path = os.path.join(bot.data_dir, "8ball_responses.txt")
    global responses
    with open(path) as f:
        responses = [line.strip() for line in
                     f.readlines() if not line.startswith("//")]


@asyncio.coroutine
@hook.command("8ball", "8", "eightball")
def eightball(action):
    """<question> - asks the all knowing magic electronic eight ball <question>"""

    magic = formatting.multiword_replace(random.choice(responses), color_codes)
    action("shakes the magic 8 ball... {}".format(magic))
