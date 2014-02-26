import os
import sys
import re
import json
import time
import subprocess

from util import hook


@hook.command(autohelp=False, permissions=["permissions_users"])
def permissions(inp, bot=None, notice=None):
    """permissions [group] -- lists the users and their permission level who have permissions."""
    permissions = bot.config.get("permissions", [])
    groups = []
    if inp:
        for k in permissions:
            if inp == k:
                groups.append(k)
    else:
        for k in permissions:
            groups.append(k)
    if not groups:
        notice("{} is not a group with permissions".format(inp))
        return None

    for v in groups:
        members = ""
        for value in permissions[v]["users"]:
            members = members + value + ", "
        if members:
            notice("the members in the {} group are..".format(v))
            notice(members[:-2])
        else:
            notice("there are no members in the {} group".format(v))


@hook.command(permissions=["permissions_users"])
def deluser(inp, bot=None, notice=None):
    """deluser [user] [group] -- removes elevated permissions from [user].
    If [group] is specified, they will only be removed from [group]."""
    permissions = bot.config.get("permissions", [])
    inp = inp.split(" ")
    groups = []
    try:
        specgroup = inp[1]
    except IndexError:
        specgroup = None
        for k in permissions:
            groups.append(k)
    else:
        for k in permissions:
            if specgroup == k:
                groups.append(k)
    if not groups:
        notice("{} is not a group with permissions".format(inp[1]))
        return None

    removed = 0
    for v in groups:
        users = permissions[v]["users"]
        for value in users:
            if inp[0] == value:
                users.remove(inp[0])
                removed = 1
                notice("{} has been removed from the group {}".format(inp[0], v))
                json.dump(bot.config, open('config', 'w'), sort_keys=True, indent=2)
    if specgroup:
        if removed == 0:
            notice("{} is not in the group {}".format(inp[0], specgroup))
    else:
        if removed == 0:
            notice("{} is not in any groups".format(inp[0]))


@hook.command(permissions=["permissions_users"])
def adduser(inp, bot=None, notice=None):
    """adduser [user] [group] -- adds elevated permissions to [user].
    [group] must be specified."""
    permissions = bot.config.get("permissions", [])
    inp = inp.split(" ")
    try:
        user = inp[0]
        targetgroup = inp[1]
    except IndexError:
        notice("the group must be specified")
        return None
    if not re.search('.+!.+@.+', user):
        notice("the user must be in the form of \"nick!user@host\"")
        return None
    try:
        users = permissions[targetgroup]["users"]
    except KeyError:
        notice("no such group as {}".format(targetgroup))
        return None
    if user in users:
        notice("{} is already in {}".format(user, targetgroup))
        return None

    users.append(user)
    notice("{} has been added to the group {}".format(user, targetgroup))
    users.sort()
    json.dump(bot.config, open('config', 'w'), sort_keys=True, indent=2)


@hook.command("quit", autohelp=False, permissions=["botcontrol"])
@hook.command(autohelp=False, permissions=["botcontrol"])
def stop(inp, nick=None, conn=None):
    """stop [reason] -- Kills the bot with [reason] as its quit message."""
    if inp:
        conn.cmd("QUIT", ["Killed by {} ({})".format(nick, inp)])
    else:
        conn.cmd("QUIT", ["Killed by {}.".format(nick)])
    time.sleep(5)
    os.execl("./cloudbot", "cloudbot", "stop")


@hook.command(autohelp=False, permissions=["botcontrol"])
def restart(inp, nick=None, conn=None, bot=None):
    """restart [reason] -- Restarts the bot with [reason] as its quit message."""
    for botcon in bot.conns:
        if inp:
            bot.conns[botcon].cmd("QUIT", ["Restarted by {} ({})".format(nick, inp)])
        else:
            bot.conns[botcon].cmd("QUIT", ["Restarted by {}.".format(nick)])
    time.sleep(5)
    #os.execl("./cloudbot", "cloudbot", "restart")
    args = sys.argv[:]
    args.insert(0, sys.executable)
    os.execv(sys.executable, args)


@hook.command(autohelp=False, permissions=["botcontrol"])
def clearlogs(inp, input=None):
    """clearlogs -- Clears the bots log(s)."""
    subprocess.call(["./cloudbot", "clear"])


@hook.command(permissions=["botcontrol"])
def join(inp, conn=None, notice=None):
    """join <channel> -- Joins <channel>."""
    for target in inp.split(" "):
        if not target.startswith("#"):
            target = "#{}".format(target)
        notice("Attempting to join {}...".format(target))
        conn.join(target)


@hook.command(autohelp=False, permissions=["botcontrol"])
def part(inp, conn=None, chan=None, notice=None):
    """part <channel> -- Leaves <channel>.
    If [channel] is blank the bot will leave the
    channel the command was used in."""
    if inp:
        targets = inp
    else:
        targets = chan
    for target in targets.split(" "):
        if not target.startswith("#"):
            target = "#{}".format(target)
        notice("Attempting to leave {}...".format(target))
        conn.part(target)


@hook.command(autohelp=False, permissions=["botcontrol"])
def cycle(inp, conn=None, chan=None, notice=None):
    """cycle <channel> -- Cycles <channel>.
    If [channel] is blank the bot will cycle the
    channel the command was used in."""
    if inp:
        target = inp
    else:
        target = chan
    notice("Attempting to cycle {}...".format(target))
    conn.part(target)
    conn.join(target)


@hook.command(permissions=["botcontrol"])
def nick(inp, notice=None, conn=None):
    """nick <nick> -- Changes the bots nickname to <nick>."""
    if not re.match("^[A-Za-z0-9_|.-\]\[]*$", inp.lower()):
        notice("Invalid username!")
        return
    notice("Attempting to change nick to \"{}\"...".format(inp))
    conn.set_nick(inp)


@hook.command(permissions=["botcontrol"])
def raw(inp, conn=None, notice=None):
    """raw <command> -- Sends a RAW IRC command."""
    notice("Raw command sent.")
    conn.send(inp)


@hook.command(permissions=["botcontrol"])
def say(inp, conn=None, chan=None):
    """say [channel] <message> -- Makes the bot say <message> in [channel].
    If [channel] is blank the bot will say the <message> in the channel
    the command was used in."""
    inp = inp.split(" ")
    if inp[0][0] == "#":
        message = u" ".join(inp[1:])
        out = u"PRIVMSG {} :{}".format(inp[0], message)
    else:
        message = u" ".join(inp[0:])
        out = u"PRIVMSG {} :{}".format(chan, message)
    conn.send(out)


@hook.command("act", permissions=["botcontrol"])
@hook.command(permissions=["botcontrol"])
def me(inp, conn=None, chan=None):
    """me [channel] <action> -- Makes the bot act out <action> in [channel].
    If [channel] is blank the bot will act the <action> in the channel the
    command was used in."""
    inp = inp.split(" ")
    if inp[0][0] == "#":
        message = ""
        for x in inp[1:]:
            message = message + x + " "
        message = message[:-1]
        out = u"PRIVMSG {} :\x01ACTION {}\x01".format(inp[0], message)
    else:
        message = ""
        for x in inp[0:]:
            message = message + x + " "
        message = message[:-1]
        out = u"PRIVMSG {} :\x01ACTION {}\x01".format(chan, message)
    conn.send(out)
