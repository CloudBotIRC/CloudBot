"""
gaming.py

Dice, coins, and random generation for gaming.

Modified By:
    - Luke Rogers <https://github.com/lukeroge>

License:
    GPL v3
"""

import asyncio
import random
import re

from cloudbot import hook


whitespace_re = re.compile(r'\s+')
valid_diceroll = re.compile(r'^([+-]?(?:\d+|\d*d(?:\d+|F))(?:[+-](?:\d+|\d*d(?:\d+|F)))*)( .+)?$', re.I)
sign_re = re.compile(r'[+-]?(?:\d*d)?(?:\d+|F)', re.I)
split_re = re.compile(r'([\d+-]*)d?(F|\d*)', re.I)


def n_rolls(count, n):
    """roll an n-sided die count times
    :type count: int
    :type n: int | str
    """
    if n == "F":
        return [random.randint(-1, 1) for x in range(min(count, 100))]
    if n < 2:  # it's a coin
        if count < 100:
            return [random.randint(0, 1) for x in range(count)]
        else:  # fake it
            return [int(random.normalvariate(.5 * count, (.75 * count) ** .5))]
    else:
        if count < 100:
            return [random.randint(1, n) for x in range(count)]
        else:  # fake it
            return [int(random.normalvariate(.5 * (1 + n) * count,
                                             (((n + 1) * (2 * n + 1) / 6. -
                                               (.5 * (1 + n)) ** 2) * count) ** .5))]


@asyncio.coroutine
@hook.command("roll", "dice")
def dice(text, notice):
    """<dice roll> - simulates dice rolls. Example: 'dice 2d20-d5+4 roll 2': D20s, subtract 1D5, add 4
    :type text: str
    """

    if hasattr(text, "groups"):
        text, desc = text.groups()
    else:  # type(text) == str
        match = valid_diceroll.match(whitespace_re.sub("", text))
        if match:
            text, desc = match.groups()
        else:
            notice("Invalid dice roll '{}'".format(text))
            return

    if "d" not in text:
        return

    spec = whitespace_re.sub('', text)
    if not valid_diceroll.match(spec):
        notice("Invalid dice roll '{}'".format(text))
        return
    groups = sign_re.findall(spec)

    total = 0
    rolls = []

    for roll in groups:
        count, side = split_re.match(roll).groups()
        count = int(count) if count not in " +-" else 1
        if side.upper() == "F":  # fudge dice are basically 1d3-2
            for fudge in n_rolls(count, "F"):
                if fudge == 1:
                    rolls.append("\x033+\x0F")
                elif fudge == -1:
                    rolls.append("\x034-\x0F")
                else:
                    rolls.append("0")
                total += fudge
        elif side == "":
            total += count
        else:
            side = int(side)
            try:
                if count > 0:
                    d = n_rolls(count, side)
                    rolls += list(map(str, d))
                    total += sum(d)
                else:
                    d = n_rolls(-count, side)
                    rolls += [str(-x) for x in d]
                    total -= sum(d)
            except OverflowError:
                # I have never seen this happen. If you make this happen, you win a cookie
                return "Thanks for overflowing a float, jerk >:["

    if desc:
        return "{}: {} ({})".format(desc.strip(), total, ", ".join(rolls))
    else:
        return "{} ({})".format(total, ", ".join(rolls))


@asyncio.coroutine
@hook.command
def choose(text, notice):
    """<choice1>, [choice2], [choice3], etc. - randomly picks one of the given choices
    :type text: str
    """
    choices = re.findall(r'([^,]+)', text)
    if len(choices) == 1:
        choices = choices[0].split(' or ')
        if len(choices) == 1:
            notice(choose.__doc__)
            return
    return random.choice(choices)


@asyncio.coroutine
@hook.command(autohelp=False)
def coin(text, notice, action):
    """[amount] - flips [amount] coins
    :type text: str
    """

    if text:
        try:
            amount = int(text)
        except (ValueError, TypeError):
            notice("Invalid input '{}': not a number".format(text))
            return
    else:
        amount = 1

    if amount == 1:
        action("flips a coin and gets {}.".format(random.choice(["heads", "tails"])))
    elif amount == 0:
        action("makes a coin flipping motion")
    else:
        heads = int(random.normalvariate(.5 * amount, (.75 * amount) ** .5))
        tails = amount - heads
        action("flips {} coins and gets {} heads and {} tails.".format(amount, heads, tails))
