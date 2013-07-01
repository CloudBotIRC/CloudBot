import math
import re
import time

from util import hook, urlnorm, timesince


expiration_period = 60 * 60 * 24  # 1 day

ignored_urls = [urlnorm.normalize("http://google.com"),]


def db_init(db):
    db.execute("create table if not exists urlhistory"
                 "(chan, url, nick, time)")
    db.commit()


def insert_history(db, chan, url, nick):
    now = time.time()
    db.execute("insert into urlhistory(chan, url, nick, time) "
                 "values(?,?,?,?)", (chan, url, nick, time.time()))
    db.commit()


def get_history(db, chan, url):
    db.execute("delete from urlhistory where time < ?",
                 (time.time() - expiration_period,))
    return db.execute("select nick, time from urlhistory where "
            "chan=? and url=? order by time desc", (chan, url)).fetchall()


def nicklist(nicks):
    nicks = sorted(dict(nicks), key=unicode.lower)
    if len(nicks) <= 2:
        return ' and '.join(nicks)
    else:
        return ', and '.join((', '.join(nicks[:-1]), nicks[-1]))


def format_reply(history):
    if not history:
        return

    last_nick, recent_time = history[0]
    last_time = timesince.timesince(recent_time)

    if len(history) == 1:
        return #"%s linked that %s ago." % (last_nick, last_time)

    hour_span = math.ceil((time.time() - history[-1][1]) / 3600)
    hour_span = '%.0f hours' % hour_span if hour_span > 1 else 'hour'

    hlen = len(history)
    ordinal = ["once", "twice", "%d times" % hlen][min(hlen, 3) - 1]

    if len(dict(history)) == 1:
        last = "last linked %s ago" % last_time
    else:
        last = "last linked by %s %s ago" % (last_nick, last_time)

    return #"that url has been posted %s in the past %s by %s (%s)." % (ordinal,

@hook.command
def url(inp, nick='', chan='', db=None, bot=None):
    db_init(db)
    url = urlnorm.normalize(inp.group().encode('utf-8'))
    if url not in ignored_urls:
        url = url.decode('utf-8')
        history = get_history(db, chan, url)
        insert_history(db, chan, url, nick)

        inp = match.string.lower()

        for name in dict(history):
            if name.lower() in inp:  # person was probably quoting a line
                return               # that had a link. don't remind them.

        if nick not in dict(history):
            return format_reply(history)
