from util import hook
import random
import re

r = "\x02\x0305"  # red
g = "\x02\x0303"  # green
y = "\x02"  # yellow (not really)

answers = [g + "As I see it, yes",
        g + "It is certain",
        g + "It is decidedly so",
        g + "Most likely",
        g + "Outlook good",
        g + "Signs point to yes",
        g + "One would be wise to think so",
        g + "Naturally",
        g + "Without a doubt",
        g + "Yes",
        g + "Yes, definitely",
        g + "You may rely on it",
        y + "Reply hazy, try again",
        y + "Ask again later",
        y + "Better not tell you now",
        y + "Cannot predict now",
        y + "Concentrate and ask again",
        y + "You know the answer better than I",
        y + "Maybe...",
        r + "You're kidding, right?",
        r + "Don't count on it",
        r + "In your dreams",
        r + "My reply is no",
        r + "My sources say no",
        r + "Outlook not so good",
        r + "Very doubtful"]


@hook.command('8ball')
def eightball(inp, me=None):
    ".8ball <question> -- The all knowing magic eight ball, " \
    "in electronic form. Ask and it shall be answered!"
    global nextresponsenumber
    inp = inp.strip()
    if re.match("[a-zA-Z0-9]", inp[-1]):
        inp += "?"
    me("shakes the magic 8 ball... %s" % (random.choice(answers)))
