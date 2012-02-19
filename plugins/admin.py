#  Shitty plugin made by iloveportalz0r
#  Broken by The Noodle
from util import hook

@hook.command
def join(inp, input=None, db=None, notice=None):
    ".join <channel> -- joins a channel"
    if input.nick not in input.bot.config["admins"]:
        notice("Only bot admins can use this command!")
        return
    chan = inp.split(' ', 1)
    #if len(chan) != 1:
        #return "Usage: omg please join <channel>"
    notice("Attempting to join " + inp + "...")
    input.conn.send("JOIN " + inp)

@hook.command
def cycle(inp, input=None, db=None, notice=None):
    ".cycle <channel> -- cycles a channel"
    if input.nick not in input.bot.config["admins"]:
        notice("Only bot admins can use this command!")
        return
    notice("Attempting to cycle " + inp + "...")
    input.conn.send("PART " + inp)
    input.conn.send("JOIN " + inp)

@hook.command
def part(inp, input=None, notice=None):
    ".part <channel> -- leaves a channel"
    if input.nick not in input.bot.config["admins"]:
        notice("Only bot admins can use this command!")
        return
    chan = inp.split(' ', 1)
    #if len(chan) != 1:
        #return "Usage: omg please part <channel>"
    notice("Attempting to part from " + inp + "...")
    input.conn.send("PART " + inp)

@hook.command
def chnick(inp, input=None, notice=None):
    ".chnick <nick> - Change the nick!"
    if input.nick not in input.bot.config["admins"]:
        notice("Only bot admins can use this command!")
        return
    chan = inp.split(' ', 1)
    #if len(chan) != 1:
        #return "Usage: omg please part <channel>"
    notice("Changing nick to " + inp + ".")
    input.conn.send("NICK " + inp)

@hook.command
def raw(inp, input=None, notice=None):
    ".raw <command> - Send a RAW IRC command!"
    if input.nick not in input.bot.config["admins"]:
        notice("Only bot admins can use this command!")
        return
    chan = inp.split(' ', 1)
    notice("Raw command sent.")
    input.conn.send(inp)

@hook.command
def kick(inp, input=None, notice=None):
    ".kick [channel] <user> [reason] -- kick a user!"
    if input.nick not in input.bot.config["admins"]:
        notice("Only bot admins can use this command!")
        return
    stuff = inp.split(" ")
    if stuff[0][0] == "#":
        out = "KICK " + stuff[0] + " " + stuff[1]
        if len(stuff) > 2:
            reason = ""
            for x in stuff[2:]:
                reason = reason + x + " "
            reason = reason[:-1]
            out = out+" :"+reason
    else:
        out = "KICK " + input.chan + " " + stuff[0]
        if len(stuff) > 1:
            reason = ""
            for x in stuff[1:]:
                reason = reason + x + " "
            reason = reason[:-1]
            out = out + " :" + reason
    notice("Attempting to kick " + inp + "...")         
    input.conn.send(out)

@hook.command
def say(inp, input=None, notice=None):
    ".say [channel] <message> -- makes the bot say <message> in [channel]. if [channel] is blank the bot will say the <message> in the channel the command was used in."
    if input.nick not in input.bot.config["admins"]:
        notice("Only bot admins can use this command!")
        return
    stuff = inp.split(" ")
    if stuff[0][0] == "#":
        message = ""
        for x in stuff[1:]:
            message = message + x + " "
        message = message[:-1]
        out = "PRIVMSG " + stuff[0] + " :" + message
    else:
        message = ""
        for x in stuff[0:]:
            message = message + x + " "
        message = message[:-1]
        out = "PRIVMSG " + input.chan + " :" + message
    input.conn.send(out)

@hook.command
def act(inp, input=None, notice=None):
    ".act [channel] <action> -- makes the bot act <action> in [channel]. if [channel] is blank the bot will act the <action> in the channel the command was used in."
    if input.nick not in input.bot.config["admins"]:
        notice("Only bot admins can use this command!")
        return
    stuff = inp.split(" ")
    if stuff[0][0] == "#":
        message = ""
        for x in stuff[1:]:
            message = message + x + " "
        message = message[:-1]
        out = "PRIVMSG " + stuff[0] + " :\x01ACTION " + message + "\x01"
    else:
        message = ""
        for x in stuff[0:]:
            message = message + x + " "
        message = message[:-1]
        out = "PRIVMSG " + input.chan + " :\x01ACTION " + message + "\x01"
    input.conn.send(out)

@hook.command
def topic(inp, input=None, notice=None):
    ".topic [channel] <topic> -- change the topic of a channel"
    if input.nick not in input.bot.config["admins"]:
        notice("Only bot admins can use this command!")
        return
    stuff = inp.split(" ")
    if stuff[0][0] == "#":
        out = "TOPIC " + stuff[0] + " :" + stuff[1]
    else:
        out = "TOPIC " + input.chan + " :" + stuff[0]
    input.conn.send(out)
