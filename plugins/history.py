from collections import deque
from util import hook
import time
import re

db_ready = False


def db_init(db):
    """check to see that our db has the the seen table and return a connection."""
    global db_ready
    if not db_ready:
        db.execute("create table if not exists seen_user(name, time, quote, chan, host, "
                   "primary key(name, chan))")
        db.commit()
        db_ready = True


def track_seen(input, message_time, db):
    """ Tracks messages for the .seen command """
    if not db_ready:
        db_init(db)
        # keep private messages private
    if input.chan[:1] == "#" and not re.findall('^s/.*/.*/$', input.msg.lower()):
        db.execute("insert or replace into seen_user(name, time, quote, chan, host)"
                   "values(?,?,?,?,?)", (input.nick.lower(), message_time, input.msg,
                                         input.chan, input.mask))
        db.commit()


def track_history(input, message_time, bot):
    try:
        history = bot.history[input.chan]
    except KeyError:
        bot.history[input.chan] = deque(maxlen=1000)
        history = bot.history[input.chan]

    data = (input.nick, message_time, input.msg)
    history.append(data)


@hook.singlethread
@hook.event('PRIVMSG', ignorebots=False)
def chat_tracker(paraml, input=None, db=None, bot=None):
    message_time = time.time()
    track_seen(input, message_time, db)
    track_history(input, message_time, bot)


@hook.command(autohelp=False)
def resethistory(inp, input=None, bot=None):
    """resethistory - Resets chat history for the current channel"""
    try:
        bot.history[input.chan].clear()
        return "Reset chat history for current channel."
    except KeyError:
        # wat
        return "There is no history for this channel."


