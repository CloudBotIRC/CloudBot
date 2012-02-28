'''
# mute plugin by lukeroge and neersighted
from util import hook

def mute(chan, db):
    db.execute("create table if not exists mute(channel, activated)")
    db.execute("insert or replace into mute(channel, activated) values(?, ?)", (chan, 1))
    db.commit()

def unmute(chan, db):
    db.execute("create table if not exists mute(channel, activated)")
    db.execute("insert or replace into mute(channel, activated) values(?, ?)", (chan, 0))
    db.commit()


def is_muted(chan, db):
    indb = db.execute("select activated from mute where channel=lower(?)", [chan]).fetchone();
    if indb == 0:
        if activated == 1:
            return True
        else:
            return False
    else:
        db.execute("insert or replace into mute(channel, activated) values(?, ?)", (chan, "0"))
        db.commit()
        return False

#@hook.sieve
def mutesieve(bot, input, func, kind, args, db):
    if kind == "event":
        return input
    if is_muted(input.chan,input.conn.db):
        if input.command == "PRIVMSG" and input.lastparam[1:] == "unmute":
            return input
        else:
            return None
    return input

@hook.command
def mute(inp, input=None, db=None):
    ".mute <channel> -- Mutes the bot in <channel>. If no channel is specified, it is muted in the current channel."
    if inp:
        channel = inp
    else:
        channel = input.chan
        
    if input.nick in input.bot.config["admins"]:
        mute(channel, db)
        input.notice("Muted")
    else:
        input.notice("Only bot admins can use this command!")

@hook.command
def unmute(inp, input=None, db=None):
    ".unmute <channel> -- Unmutes the bot in <channel>. If no channel is specified, it is unmuted in the current channel."
    if inp:
        channel = inp
    else:
        channel = input.chan
        
    if input.nick in input.bot.config["admins"]:
        if is_muted(channel, db):
            input.notice("Already muted!")
        else:
           mute(channel, db)
           input.notice("Muted")
    else:
        input.notice("Only bot admins can use this command!")
'''