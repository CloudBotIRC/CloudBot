import re
import time
from cloudbot import hook
from cloudbot.event import EventType
from plugins import grab

import random

db_ready = []
opt_out = []
delay = 10
floodcheck = {}

def db_init(db, conn_name):
    """Check to see if the DB has the herald table. Connection name is for caching the result per connection.
    :type db: sqlalchemy.orm.Session
    """
    global db_ready
    if db_ready.count(conn_name) < 1:
        db.execute(
            "create table if not exists herald(name, chan, quote, primary key(name, chan))")
        db.commit()
        db_ready.append(conn_name)


@hook.command()
def herald(text, nick, chan, db, conn):
    """herald [message] adds a greeting for your nick that will be announced everytime you join the channel. Using .herald show will show your current herald and .herald delete will remove your greeting."""

    db_init(db, conn.name)

    if text.lower() == "show":
        greeting = db.execute("select quote from herald where name = :name and chan = :chan", {
                              'name': nick.lower(), 'chan': chan}).fetchone()
        if greeting:
            return greeting[0]
        else:
            return "you don't have a herald set try .herald <message> to set your greeting."
    elif text.lower() in ["delete", "remove"]:
        greeting = db.execute("select quote from herald where name = :name and chan = :chan", {
                              'name': nick.lower(), 'chan': chan}).fetchone()[0]
        db.execute("delete from herald where name = :name and chan = :chan", {'name': nick.lower(), 'chan': chan})
        db.commit()
        return ("greeting \'{}\' for {} has been removed".format(greeting, nick))
    else:
        db.execute("insert or replace into herald(name, chan, quote) values(:name, :chan, :quote)", {
                   'name': nick.lower(), 'chan': chan, 'quote': text})
        db.commit()
        return("greeting successfully added")

@hook.command(permissions=["botcontrol", "snoonetstaff"])
def deleteherald(text, chan, db, conn):
    """deleteherald [nickname] Delete [nickname]'s herald."""

    db_init(db, conn.name)
    tnick = db.execute("select name from herald where name = :name and chan = :chan", {'name': text.lower(), 'chan': chan.lower()}).fetchone()

    if tnick:
        db.execute("delete from herald where name = :name and chan = :chan", {'name': text.lower(), 'chan': chan})
        db.commit()
        return "greeting for {} has been removed".format(text.lower())
    else:
        return "{} does not have a herald".format(text.lower())

@hook.irc_raw("JOIN", singlethread=True)
def welcome(nick, action, message, chan, event, db, conn):
    # For some reason chan isn't passed correctly. The below hack is sloppy and may need to be adjusted for different networks.
    # If someone knows how to get the channel a better way please fix this.
    # freenode uncomment then next line
    # chan = event.irc_raw.split('JOIN ')[1].lower()
    # snoonet
    decoy = re.compile('[o○O0öøóóȯôőŏᴏōο](<|>|＜)')
    colors_re = re.compile("\x02|\x03(?:\d{1,2}(?:,\d{1,2})?)?", re.UNICODE)
    bino_re = re.compile('b+i+n+o+', re.IGNORECASE)
    offensive_re = re.compile('卐')

    try:
        chan = event.irc_raw.split(':')[2].lower()
    except:
        return
    if chan in opt_out:
        return

    if chan in floodcheck:
        if time.time() -  floodcheck[chan] <= delay:
            return
    else:
        floodcheck[chan] = time.time()

    welcome = db.execute("select quote from herald where name = :name and chan = :chan", {
                         'name': nick.lower(), 'chan': chan.lower()}).fetchone()
    if welcome:
        greet = welcome[0]
        greet = re.sub(bino_re, 'flenny', greet)
        greet = re.sub(offensive_re, ' freespeech oppression ', greet)
        if greet.lower().split(' ')[0] == ".grabrandom":
            text = ""
            if len(greet.split(' ')) >= 2:
                candidates = greet.lower().split(' ')[1:]
                text = random.choice(candidates)
            out = grab.grabrandom(text, chan, message)
            message(out, chan)
        elif decoy.search(colors_re.sub("", greet.replace('\u200b', '').replace(' ', '').replace('\u202f','').replace('\x02', ''))):
            message("DECOY DUCK --> {}".format(greet), chan)
        else:
            message("\u200b {}".format(greet), chan)
        floodcheck[chan] = time.time()
    # Saying something whenever someone joins can get really spammy
    # else:
        # action("welcomes {} to {}".format(nick, chan), chan)
