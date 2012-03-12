#  Shitty plugin made by iloveportalz0r
#  Broken by The Noodle
#  Improved by Lukeroge
#  Further improved by neersighted
from util import hook
import os
import sys
import subprocess
import time


@hook.command("owners", autohelp=False)
@hook.command(autohelp=False)
def admins(inp, bot=None):
    admins = bot.config["admins"]
    return ", ".join(admins)


@hook.command("quit", autohelp=False)
@hook.command("exit", autohelp=False)
@hook.command(autohelp=False)
def stop(inp, input=None, db=None, notice=None):
    ".stop [reason] -- Kills the bot, with [reason] as its quit message."
    if not input.nick in input.bot.config["admins"]:
        notice("Only bot admins can use this command!")
        return
    if inp:
        input.conn.send("QUIT :Killed by " + input.nick + " (" + inp + ")")
    else:
        input.conn.send("QUIT :Killed by " + input.nick + " (no reason)")
    time.sleep(5)
    subprocess.call("./cloudbot stop", shell=True)


@hook.command("reboot", autohelp=False)
@hook.command(autohelp=False)
def restart(inp, input=None, db=None, notice=None):
    ".restart [reason] -- Restarts the bot, with [reason] as its quit message."
    if not input.nick in input.bot.config["admins"]:
        notice("Only bot admins can use this command!")
        return
    if inp:
        input.conn.send("QUIT :Restarted by " + input.nick + " (" + inp + ")")
    else:
        input.conn.send("QUIT :Restarted by " + input.nick + " (no reason)")
    time.sleep(5)
    os.execl("./cloudbot", "restart")

@hook.command("clearlogs", autohelp=False)
@hook.command(autohelp=False)
def clear(inp, input=None, db=None, notice=None):
    ".clear -- Clears the bot's log(s)."
    if not input.nick in input.bot.config["admins"]:
        notice("Only bot admins can use this command!")
        return
    time.sleep(5)
    subprocess.call("./cloudbot clear", shell=True)


@hook.command
def join(inp, input=None, db=None, notice=None):
    ".join <channel> -- Joins <channel>."
    if not input.nick in input.bot.config["admins"]:
        notice("Only bot admins can use this command!")
        return
    notice("Attempting to join " + inp + "...")
    input.conn.send("JOIN " + inp)


@hook.command
def cycle(inp, input=None, db=None, notice=None):
    ".cycle <channel> -- Cycles <channel>."
    if not input.nick in input.bot.config["admins"]:
        notice("Only bot admins can use this command!")
        return
    notice("Attempting to cycle " + inp + "...")
    input.conn.send("PART " + inp)
    input.conn.send("JOIN " + inp)


@hook.command
def part(inp, input=None, notice=None):
    ".part <channel> -- Parts from <channel>."
    if not input.nick in input.bot.config["admins"]:
        notice("Only bot admins can use this command!")
        return
    notice("Attempting to part from " + inp + "...")
    input.conn.send("PART " + inp)


@hook.command
def nick(inp, input=None, notice=None):
    ".nick <nick> -- Changes the bots nickname to <nick>."
    if not input.nick in input.bot.config["admins"]:
        notice("Only bot admins can use this command!")
        return
    notice("Changing nick to " + inp + ".")
    input.conn.send("NICK " + inp)


@hook.command
def raw(inp, input=None, notice=None):
    ".raw <command> -- Sends a RAW IRC command."
    if not input.nick in input.bot.config["admins"]:
        notice("Only bot admins can use this command!")
        return
    notice("Raw command sent.")
    input.conn.send(inp)


@hook.command
def kick(inp, input=None, notice=None):
    ".kick [channel] <user> [reason] -- kicks a user."
    if not input.nick in input.bot.config["admins"]:
        notice("Only bot admins can use this command!")
        return
    split = inp.split(" ")
    if split[0][0] == "#":
        chan = split[0]
        user = split[1]
        out = "KICK %s %s" % (chan, user)
        if len(split) > 2:
            reason = ""
            for x in split[2:]:
                reason = reason + x + " "
            reason = reason[:-1]
            out = out + " :" + reason
    else:
        chan = input.chan
        user = split[0]
        out = "KICK %s %s" % (input.chan, split[0])
        if len(split) > 1:
            reason = ""
            for x in split[1:]:
                reason = reason + x + " "
            reason = reason[:-1]
            out = out + " :" + reason

    notice("Attempting to kick %s from %s..." % (user, chan))
    input.conn.send(out)


@hook.command
def say(inp, input=None, notice=None):
    ".say [channel] <message> -- Makes the bot say <message> in [channel]. "\
    "If [channel] is blank the bot will say the <message> in "\
    "the channel the command was used in."
    if not input.nick in input.bot.config["admins"]:
        notice("Only bot admins can use this command!")
        return
    split = inp.split(" ")
    if split[0][0] == "#":
        message = ""
        for x in split[1:]:
            message = message + x + " "
        message = message[:-1]
        out = "PRIVMSG %s :%s" % (split[0], message)
    else:
        message = ""
        for x in split[0:]:
            message = message + x + " "
        message = message[:-1]
        out = "PRIVMSG %s :%s" % (input.chan, message)
    input.conn.send(out)


@hook.command("me")
@hook.command
def act(inp, input=None, notice=None):
    ".act [channel] <action> -- Makes the bot act out <action> in [channel] "\
    "If [channel] is blank the bot will act the <action> in "\
    "the channel the command was used in."
    if not input.nick in input.bot.config["admins"]:
        notice("Only bot admins can use this command!")
        return
    split = inp.split(" ")
    if split[0][0] == "#":
        message = ""
        for x in split[1:]:
            message = message + x + " "
        message = message[:-1]
        out = "PRIVMSG %s :\x01ACTION %s\x01" % (split[0], message)
    else:
        message = ""
        for x in split[0:]:
            message = message + x + " "
        message = message[:-1]
        out = "PRIVMSG %s :\x01ACTION %s\x01" % (input.chan, message)
    input.conn.send(out)


@hook.command
def topic(inp, input=None, notice=None):
    ".topic [channel] <topic> -- Change the topic of a channel."
    if not input.nick in input.bot.config["admins"]:
        notice("Only bot admins can use this command!")
        return
    split = inp.split(" ")
    if split[0][0] == "#":
        out = "PRIVMSG %s :%s" % (split[0], message)
    else:
        out = "TOPIC %s :%s" % (input.chan, message)
    input.conn.send(out)
