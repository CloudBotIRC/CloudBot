import random
import re

from cloudbot import hook

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
def lart(text, conn, nick, notice, action):
    """lart <user> -- LARTs <user>.
    :type text: str
    :type conn: core.irc.BotConnection
    :type nick: str
    """
    target = text.strip()

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
def insult(text, conn, nick, notice, message):
    """insult <user> -- Makes the bot insult <user>.
    :type text: str
    :type conn: core.irc.BotConnection
    :type nick: str
    """
    target = text.strip()

    if " " in target:
        notice("Invalid username!")
        return

    # if the user is trying to make the bot target itself, target them
    if is_self(conn, target):
        target = nick

    message("{}, {}".format(target, random.choice(insults)))


@hook.command
def flirt(text, conn, nick, notice, message):
    """flirt <user> -- Makes the bot flirt with <user>.
    :type text: str
    :type conn: core.irc.BotConnection
    :type nick: str
    """
    target = text.strip()

    # if the user is trying to make the bot target itself, target them
    if " " in target:
        notice("Invalid username!")
        return

    if is_self(conn, target):
        target = nick

    message('{}, {}'.format(target, random.choice(flirts)))
