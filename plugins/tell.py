import time
import re

from sqlalchemy import Table, Column, String, Boolean, DateTime, MetaData

from util import hook, timesince


# define DB tables
metadata = MetaData()
tells = Table('tells', metadata,
              Column('connection', String),
              Column('sender', String),
              Column('target', String),
              Column('message', String),
              Column('is_read', Boolean),
              Column('time_sent', DateTime),
              Column('time_read', DateTime))


def db_init(db):
    metadata.bind = db
    metadata.create_all()


def get_tells(db, user_to):
    return db.execute("select user_from, message, time, chan from tell where"
                      " user_to=lower(:user) order by time", {'user': user_to}).fetchall()


@hook.event('PRIVMSG', singlethread=True)
def tellinput(input, notice, db, nick, conn):
    if 'showtells' in input.msg.lower():
        return

    db_init(db)

    tells = get_tells(db, conn, nick)

    if tells:
        user_from, message, time, chan = tells[0]
        reltime = timesince.timesince(time)

        reply = "{} sent you a message {} ago from {}: {}".format(user_from, reltime, chan,
                                                                  message)
        if len(tells) > 1:
            reply += " (+{} more, {}showtells to view)".format(len(tells) - 1, conn.conf["command_prefix"])

        db.execute("delete from tell where user_to=lower(:user) and message=:message",
                   {'user': nick, 'message': message})
        db.commit()
        notice(reply)


@hook.command(autohelp=False)
def showtells(nick, notice, db, conn):
    """showtells -- View all pending tell messages (sent in a notice)."""

    db_init(db)

    tells = get_tells(db, conn, nick)

    if not tells:
        notice("You have no pending tells.")
        return

    for tell in tells:
        user_from, message, time, chan = tell
        past = timesince.timesince(time)
        notice("{} sent you a message {} ago from {}: {}".format(user_from, past, chan, message))

    db.execute("delete from tell where user_to=lower(?)",
               (nick,))
    db.commit()


@hook.command
def tell(inp, nick='', chan='', db=None, input=None, notice=None, conn=None):
    """tell <nick> <message> -- Relay <message> to <nick> when <nick> is around."""
    query = inp.split(' ', 1)

    if len(query) != 2:
        notice(tell.__doc__)
        return

    user_to = query[0].lower()
    message = query[1].strip()
    user_from = nick

    if chan.lower() == user_from.lower():
        chan = 'a pm'

    if user_to == user_from.lower():
        notice("Have you looked in a mirror lately?")
        return

    if user_to.lower() == input.conn.nick.lower():
        # user is looking for us, being a smart-ass
        notice("Thanks for the message, {}!".format(user_from))
        return

    if not re.match("^[A-Za-z0-9_|.\-\]\[]*$", user_to.lower()):
        notice("I can't send a message to that user!")
        return

    db_init(db, conn)

    if db.execute("select count() from tell where user_to=?",
                  (user_to,)).fetchone()[0] >= 10:
        notice("That person has too many messages queued.")
        return

    try:
        db.execute("insert into tell(user_to, user_from, message, chan,"
                   "time) values(?,?,?,?,?)", (user_to, user_from, message,
                                               chan, time.time()))
        db.commit()
    except db.IntegrityError:
        notice("Message has already been queued.")
        return

    notice("Your message has been sent!")
