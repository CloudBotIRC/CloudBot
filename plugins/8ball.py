from util import hook
import random

color_codes = {
    "<r>": "\x02\x0305",
    "<g>": "\x02\x0303",
    "<y>": "\x02"
}

with open("plugins/data/8ball_responses.txt") as f:
    responses = [line.strip() for line in f.readlines()
            if not line.startswith("//")]


@hook.command('8ball')
def eightball(input, me=None):
    "8ball <question> -- The all knowing magic eight ball, " \
    "in electronic form. Ask and it shall be answered!"

    out = random.choice(responses)
    for code in color_codes:
        out = out.replace(code, color_codes[code])
    me("shakes the magic 8 ball... %s" % out)
