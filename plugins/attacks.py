import random
import re

from util import hook


with open("data/larts.txt") as f:
    larts = [line.strip() for line in f.readlines()
             if not line.startswith("//")]

with open("data/insults.txt") as f:
    insults = [line.strip() for line in f.readlines()
               if not line.startswith("//")]

with open("data/flirts.txt") as f:
    flirts = [line.strip() for line in f.readlines()
              if not line.startswith("//")]


def is_self(conn, target):
    """
    :type conn: core.irc.BotConnection
    :type target: str
    """
    if re.search("(^..?.?.?self|{})".format(re.escape(conn.nick.lower())), target.lower()):
        return True
    else:
        return False


@hook.command
def lart(inp, conn=None, nick=None, notice=None, action=None):
    """lart <user> -- LARTs <user>.
    :type inp: str
    :type conn: core.irc.BotConnection
    :type nick: str
    """
    target = inp.strip()

    if " " in target:
        notice("Invalid username!")
        return

    # if the user is trying to make the bot target itself, target them
    if is_self(conn, target):
        target = nick

    phrase = random.choice(larts)

    # act out the message
    action(phrase.format(user=target))


@hook.command
def insult(inp, conn=None, nick=None, notice=None, message=None):
    """insult <user> -- Makes the bot insult <user>.
    :type inp: str
    :type conn: core.irc.BotConnection
    :type nick: str
    """
    target = inp.strip()

    if " " in target:
        notice("Invalid username!")
        return

    # if the user is trying to make the bot target itself, target them
    if is_self(conn, target):
        target = nick

    message("{}, {}".format(target, random.choice(insults)))


@hook.command
def flirt(inp, conn=None, nick=None, notice=None, message=None):
    """flirt <user> -- Makes the bot flirt with <user>.
    :type inp: str
    :type conn: core.irc.BotConnection
    :type nick: str
    """
    target = inp.strip()

    # if the user is trying to make the bot target itself, target them
    if " " in target:
        notice("Invalid username!")
        return

    if is_self(conn, target):
        target = nick

    message('{}, {}'.format(target, random.choice(flirts)))
