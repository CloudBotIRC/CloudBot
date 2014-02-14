import random

from util import hook, text


color_codes = {
    "<r>": "\x02\x0305",
    "<g>": "\x02\x0303",
    "<y>": "\x02"
}

with open("plugins/data/8ball_responses.txt") as f:
    responses = [line.strip() for line in
                 f.readlines() if not line.startswith("//")]


@hook.command('8ball')
def eightball(inp, action=None):
    """8ball <question> -- The all knowing magic eight ball,
    in electronic form. Ask and it shall be answered!"""

    magic = text.multiword_replace(random.choice(responses), color_codes)
    action("shakes the magic 8 ball... {}".format(magic))
