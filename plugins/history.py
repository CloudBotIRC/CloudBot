from collections import deque
import time
import asyncio
import re

from cloudbot import hook
from cloudbot.util import timeformat
from cloudbot.event import EventType

db_ready = []


def db_init(db, conn_name):
    """check to see that our db has the the seen table (connection name is for caching the result per connection)
    :type db: sqlalchemy.orm.Session
    """
    global db_ready
    if db_ready.count(conn_name) < 1:
        db.execute("create table if not exists seen_user(name, time, quote, chan, host, primary key(name, chan))")
        db.commit()
        db_ready.append(conn_name)


def track_seen(event, db, conn):
    """ Tracks messages for the .seen command
    :type event: cloudbot.event.Event
    :type db: sqlalchemy.orm.Session
    :type conn: cloudbot.client.Client
    """
    db_init(db, conn)
    # keep private messages private
    if event.chan[:1] == "#" and not re.findall('^s/.*/.*/$', event.content.lower()):
        db.execute(
            "insert or replace into seen_user(name, time, quote, chan, host) values(:name,:time,:quote,:chan,:host)",
            {'name': event.nick.lower(), 'time': time.time(), 'quote': event.content, 'chan': event.chan,
             'host': event.mask})
        db.commit()


def track_history(event, message_time, conn):
    """
    :type event: cloudbot.event.Event
    :type conn: cloudbot.client.Client
    """
    try:
        history = conn.history[event.chan]
    except KeyError:
        conn.history[event.chan] = deque(maxlen=100)
        # what are we doing here really
        # really really
        history = conn.history[event.chan]

    data = (event.nick, message_time, event.content)
    history.append(data)


@hook.event([EventType.message, EventType.action], singlethread=True)
def chat_tracker(event, db, conn):
    """
    :type db: sqlalchemy.orm.Session
    :type event: cloudbot.event.Event
    :type conn: cloudbot.client.Client
    """
    if event.type is EventType.action:
        event.content = "\x01ACTION {}\x01".format(event.content)

    message_time = time.time()
    track_seen(event, db, conn)
    track_history(event, message_time, conn)


@asyncio.coroutine
@hook.command(autohelp=False)
def resethistory(event, conn):
    """- resets chat history for the current channel
    :type event: cloudbot.event.Event
    :type conn: cloudbot.client.Client
    """
    try:
        conn.history[event.chan].clear()
        return "Reset chat history for current channel."
    except KeyError:
        # wat
        return "There is no history for this channel."


@hook.command()
def seen(text, nick, chan, db, event, conn):
    """<nick> <channel> - tells when a nickname was last in active in one of my channels
    :type db: sqlalchemy.orm.Session
    :type event: cloudbot.event.Event
    :type conn: cloudbot.client.Client
    """

    if event.conn.nick.lower() == text.lower():
        return "You need to get your eyes checked."

    if text.lower() == nick.lower():
        return "Have you looked in a mirror lately?"

    if not re.match("^[A-Za-z0-9_|.\-\]\[]*$", text.lower()):
        return "I can't look up that name, its impossible to use!"

    db_init(db, conn.name)

    last_seen = db.execute("select name, time, quote from seen_user where name like :name and chan = :chan",
                           {'name': text, 'chan': chan}).fetchone()

    if last_seen:
        reltime = timeformat.time_since(last_seen[1])
        if last_seen[0] != text.lower():  # for glob matching
            text = last_seen[0]
        if last_seen[2][0:1] == "\x01":
            return '{} was last seen {} ago: * {} {}'.format(text, reltime, text, last_seen[2][8:-1])
        else:
            return '{} was last seen {} ago saying: {}'.format(text, reltime, last_seen[2])
    else:
        return "I've never seen {} talking in this channel.".format(text)
