"""seen.py: written by sklnd in about two beers July 2009"""

import time
import re

from util import hook, timesince

db_ready = False


def db_init(db):
    """check to see that our db has the the seen table and return a connection."""
    db.execute("create table if not exists seen_user(name, time, quote, chan, host, "
               "primary key(name, chan))")
    db.commit()
    db_ready = True


@hook.singlethread
@hook.event('PRIVMSG', ignorebots=False)
def seen_sieve(paraml, input=None, db=None):
    if not db_ready:
        db_init(db)
        # keep private messages private
    if input.chan[:1] == "#" and not re.findall('^s/.*/.*/$', input.msg.lower()):
        db.execute("insert or replace into seen_user(name, time, quote, chan, host)"
                   "values(?,?,?,?,?)", (input.nick.lower(), time.time(), input.msg,
                                         input.chan, input.mask))
        db.commit()


@hook.command
def seen(inp, nick='', chan='', db=None, input=None):
    """seen <nick> <channel> -- Tell when a nickname was last in active in one of this bot's channels."""
    
    if input.conn.nick.lower() == inp.lower():
        return "You need to get your eyes checked."

    if inp.lower() == nick.lower():
        return "Have you looked in a mirror lately?"

    if not re.match("^[A-Za-z0-9_|.\-\]\[]*$", inp.lower()):
        return "I can't look up that name, its impossible to use!"

    if not db_ready:
        db_init(db)

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
