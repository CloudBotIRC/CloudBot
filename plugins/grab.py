import re
import random

from sqlalchemy import Table, Column, String, Boolean, DateTime
from sqlalchemy.sql import select
from cloudbot import hook
from cloudbot.util import botvars

#db_ready = []

table = Table(
    'grab',
    botvars.metadata,
    Column('name', String),
    Column('time', String),
    Column('quote', String),
    Column('chan', String)
)

@hook.on_start()
def load_cache(db):
    """
    :type db: sqlalchemy.orm.Session
    """
    global grab_cache
    grab_cache = {}
    for row in db.execute(table.select().order_by(table.c.time)):
        name = row["name"].lower()
        quote = row["quote"]
        chan = row["chan"]
        if chan not in grab_cache:
            grab_cache.update({chan:{name:[chan]}})
        elif name not in grab_cache[chan]:
            grab_cache[chan].update({name:[quote]})
        else:
            grab_cache[chan][name].append(quote)

def check_grabs(name, quote, chan):
    try:
        if quote in grab_cache[chan][name]:
            return True
        else:
            return False
    except:
        return False

def grab_add(nick, time, msg, chan, db, conn):
    # Adds a quote to the grab table
    db.execute(table.insert().values(name=nick, time=time, quote=msg, chan=chan))
    db.commit()
    load_cache(db)


@hook.command()
def grab(text, nick, chan, db, conn):
    """grab <nick> grabs the last message from the
    specified nick and adds it to the quote database"""
    if text.lower() == nick.lower():
        return "Didn't your mother teach you not to grab yourself?"
    
    for item in conn.history[chan].__reversed__():
        name, timestamp, msg = item
        if text.lower() == name.lower():
            # check to see if the quote has been added
            if check_grabs(name.lower(), msg, chan):
                return "I already have that quote from {} in the database".format(text)
                break
            else:
                # the quote is new so add it to the db. 
                grab_add(name.lower(),timestamp, msg, chan, db, conn)
                if check_grabs(name.lower(), msg, chan):
                    return "the operation succeeded."
                break
    return "I couldn't find anything from {} in recent history.".format(text)

def format_grab(name, quote):
    if quote.startswith("\x01ACTION") or quote.startswith("*"):
        quote = quote.replace("\x01ACTION", "").replace("\x01", "")
        out = "* {}{}".format(name, quote)
        return out
    else:
        out = "<{}> {}".format(name, quote)
        return out

@hook.command("lastgrab", "lgrab")
def lastgrab(text, chan, message):
    """prints the last grabbed quote from <nick>."""
    lgrab = ""
    try:
        lgrab = grab_cache[chan][text.lower()][-1]
    except:
        return "<{}> has never been grabbed.".format(text)
    if lgrab:
        quote = lgrab
        message(format_grab(text, quote),chan)


@hook.command("grabrandom", "grabr", autohelp=False)
def grabrandom(text, chan, message):
    """grabs a random quote from the grab database"""
    grab = ""
    name = ""
    if text:
        name = text.split(' ')[0]
    else:
        try:
            name = random.choice(list(grab_cache[chan].keys()))
        except:
            return "I couldn't find any grabs in {}.".format(chan)
    try:
        grab = random.choice(grab_cache[chan][name.lower()])
    except:
        return "it appears {} has never been grabbed in {}".format(name, chan)
    if grab:
        message(format_grab(name, grab), chan)
    else:
        return "Hmmm try grabbing a quote first."


@hook.command("grabsearch", "grabs", autohelp=False)
def grabsearch(text, chan):
    """.grabsearch <text> matches "text" against nicks or grab strings in the database"""
    out = ""
    result = []
    try:
        quotes = grab_cache[chan][text.lower()]
        for grab in quotes:
            result.append((text, grab))
    except:
       pass
    for name in grab_cache[chan]:
        for grab in grab_cache[chan][name]:
            if name != text.lower():
                if text.lower() in grab.lower():
                    result.append((name, grab))
    if result:
        for grab in result:
            name = grab[0]
            if text.lower() == name:
                name = text
            quote = grab[1]
            out += "{} {} ".format(format_grab(name, quote), u'\u2022')
        out = out[:-2]
        return out
    else:
        return "I couldn't find any matches for {}.".format(text)
