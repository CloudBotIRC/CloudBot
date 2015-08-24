import re
import random

from collections import defaultdict
from sqlalchemy import Table, Column, String, Boolean, DateTime
from sqlalchemy.sql import select
from cloudbot import hook
from cloudbot.util import database

search_pages = defaultdict(list)

table = Table(
    'grab',
    database.metadata,
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

def two_lines(bigstring, chan):
    """Receives a string with new lines. Groups the string into a list of strings with up to 3 new lines per string element. Returns first string element then stores the remaining list in search_pages."""
    global search_pages
    temp = bigstring.split('\n')
    for i in range(0, len(temp), 2):
        search_pages[chan].append('\n'.join(temp[i:i+2]))
    search_pages[chan+"index"] = 0
    return search_pages[chan][0]


def smart_truncate(content, length=355, suffix='...\n'):
    if len(content) <= length:
        return content
    else:
        return content[:length].rsplit(' \u2022 ', 1)[0]+ suffix + content[:length].rsplit(' \u2022 ', 1)[1] + smart_truncate(content[length:])


@hook.command("moregrab", autohelp=False)
def moregrab(text, chan):
    """if a grab search has lots of results the results are pagintated. If the most recent search is paginated the pages are stored for retreival. If no argument is given the next page will be returned else a page number can be specified."""
    if not search_pages[chan]:
        return "There are grabsearch pages to show."
    if text:
        index = ""
        try:
            index = int(text)
        except:
            return "Please specify an integer value."
        if abs(int(index)) > len(search_pages[chan]) or index == 0:
            return "please specify a valid page number between 1 and {}.".format(len(search_pages[chan]))
        else:
            return "{}(page {}/{})".format(search_pages[chan][index-1], index, len(search_pages[chan]))
    else:
        search_pages[chan+"index"] += 1
        if search_pages[chan+"index"] < len(search_pages[chan]):
            return "{}(page {}/{})".format(search_pages[chan][search_pages[chan+"index"]], search_pages[chan+"index"] + 1, len(search_pages[chan]))
        else:
            return "All pages have been shown you can specify a page number or do a new search."

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
    search_pages[chan] = []
    search_pages[chan+"index"] = 0
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
        out = smart_truncate(out)
        out = out[:-2]
        out = two_lines(out, chan)
        if len(search_pages[chan]) > 1:
            return "{}(page {}/{}) .moregrab".format(out, search_pages[chan+"index"] + 1 , len(search_pages[chan]))
        return out
    else:
        return "I couldn't find any matches for {}.".format(text)
