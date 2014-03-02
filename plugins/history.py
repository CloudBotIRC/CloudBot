from collections import deque
from util import hook, timesince
import time
import re

db_ready = []


def db_init(db, conn_name):
    """check to see that our db has the the seen table (connection name is for caching the result per connection)"""
    global db_ready
    if db_ready.count(conn_name) < 1:
        db.execute("create table if not exists seen_user(name, time, quote, chan, host, "
                   "primary key(name, chan))")
        db.commit()
        db_ready.append(conn_name)


def track_seen(input, message_time, db, conn):
    """ Tracks messages for the .seen command """
    db_init(db, conn)
    # keep private messages private
    if input.chan[:1] == "#" and not re.findall('^s/.*/.*/$', input.msg.lower()):
        db.execute("insert or replace into seen_user(name, time, quote, chan, host)"
                   "values(?,?,?,?,?)", (input.nick.lower(), message_time, input.msg,
                                         input.chan, input.mask))
        db.commit()


def track_history(input, message_time, conn):
    try:
        history = conn.history[input.chan]
    except KeyError:
        conn.history[input.chan] = deque(maxlen=100)
        history = conn.history[input.chan]

    data = (input.nick, message_time, input.msg)
    history.append(data)


@hook.singlethread
@hook.event('PRIVMSG', ignorebots=False)
def chat_tracker(paraml, input=None, db=None, conn=None):
    message_time = time.time()
    track_seen(input, message_time, db, conn)
    track_history(input, message_time, conn)


@hook.command(autohelp=False)
def resethistory(inp, input=None, conn=None):
    """resethistory - Resets chat history for the current channel"""
    try:
        conn.history[input.chan].clear()
        return "Reset chat history for current channel."
    except KeyError:
        # wat
        return "There is no history for this channel."

"""seen.py: written by sklnd in about two beers July 2009"""

@hook.command
def seen(inp, nick='', chan='', db=None, input=None, conn=None):
    """seen <nick> <channel> -- Tell when a nickname was last in active in one of this bot's channels."""

    if input.conn.nick.lower() == inp.lower():
        return "You need to get your eyes checked."

    if inp.lower() == nick.lower():
        return "Have you looked in a mirror lately?"

    if not re.match("^[A-Za-z0-9_|.\-\]\[]*$", inp.lower()):
        return "I can't look up that name, its impossible to use!"

    db_init(db, conn.name)

    last_seen = db.execute("select name, time, quote from seen_user where name"
                           " like ? and chan = ?", (inp, chan)).fetchone()

    if last_seen:
        reltime = timesince.timesince(last_seen[1])
        if last_seen[0] != inp.lower():  # for glob matching
            inp = last_seen[0]
        if last_seen[2][0:1] == "\x01":
            return '{} was last seen {} ago: * {} {}'.format(inp, reltime, inp,
                                                             last_seen[2][8:-1])
        else:
            return '{} was last seen {} ago saying: {}'.format(inp, reltime, last_seen[2])
    else:
        return "I've never seen {} talking in this channel.".format(inp)
