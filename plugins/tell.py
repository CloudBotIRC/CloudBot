import re
from datetime import datetime
from sqlalchemy import Table, Column, String, Boolean, DateTime

from sqlalchemy.sql import select

from cloudbot import hook
from cloudbot.util import timeformat, database
from cloudbot.event import EventType

table = Table(
    'tells',
    database.metadata,
    Column('connection', String(25)),
    Column('sender', String(25)),
    Column('target', String(25)),
    Column('message', String(500)),
    Column('is_read', Boolean),
    Column('time_sent', DateTime),
    Column('time_read', DateTime)
)

@hook.on_start
def load_cache(db):
    """
    :type db: sqlalchemy.orm.Session
    """
    global tell_cache
    tell_cache = []
    for row in db.execute(table.select().where(table.c.is_read == 0)):
        conn = row["connection"]
        target = row["target"]
        tell_cache.append((conn, target))


def get_unread(db, server, target):
    query = select([table.c.sender, table.c.message, table.c.time_sent]) \
        .where(table.c.connection == server.lower()) \
        .where(table.c.target == target.lower()) \
        .where(table.c.is_read == 0) \
        .order_by(table.c.time_sent)
    return db.execute(query).fetchall()


def count_unread(db, server, target):
    query = select([table]) \
        .where(table.c.connection == server.lower()) \
        .where(table.c.target == target.lower()) \
        .where(table.c.is_read == 0) \
        .alias("count") \
        .count()
    return db.execute(query).fetchone()[0]


def read_all_tells(db, server, target):
    query = table.update() \
        .where(table.c.connection == server.lower()) \
        .where(table.c.target == target.lower()) \
        .where(table.c.is_read == 0) \
        .values(is_read=1)
    db.execute(query)
    db.commit()
    load_cache(db)

def read_tell(db, server, target, message):
    query = table.update() \
        .where(table.c.connection == server.lower()) \
        .where(table.c.target == target.lower()) \
        .where(table.c.message == message) \
        .values(is_read=1)
    db.execute(query)
    db.commit()
    load_cache(db)


def add_tell(db, server, sender, target, message):
    query = table.insert().values(
        connection=server.lower(),
        sender=sender.lower(),
        target=target.lower(),
        message=message,
        is_read=False,
        time_sent=datetime.today()
    )
    db.execute(query)
    db.commit()
    load_cache(db)

def tell_check(conn, nick):
    for _conn, _target in tell_cache:
        if (conn, nick.lower()) == (_conn, _target):
            return True
        else:
            continue

@hook.event(EventType.message, singlethread=True)
def tellinput(event, conn, db, nick, notice):
    """
    :type event: cloudbot.event.Event
    :type conn: cloudbot.client.Client
    :type db: sqlalchemy.orm.Session
    """
    if 'showtells' in event.content.lower():
        return

    if tell_check(conn.name, nick): 
        tells = get_unread(db, conn.name, nick)
    else:
        return

    if tells:
        user_from, message, time_sent = tells[0]
        reltime = timeformat.time_since(time_sent)

        if reltime == 0:
            reltime_formatted = "just a moment"
        else:
            reltime_formatted = reltime

        reply = "{} sent you a message {} ago: {}".format(user_from, reltime_formatted, message)
        if len(tells) > 1:
            reply += " (+{} more, {}showtells to view)".format(len(tells) - 1, conn.config["command_prefix"][0])

        read_tell(db, conn.name, nick, message)
        notice(reply)


@hook.command(autohelp=False)
def showtells(nick, notice, db, conn):
    """showtells -- View all pending tell messages (sent in a notice)."""

    tells = get_unread(db, conn.name, nick)

    if not tells:
        notice("You have no pending messages.")
        return

    for tell in tells:
        sender, message, time_sent = tell
        past = timeformat.time_since(time_sent)
        notice("{} sent you a message {} ago: {}".format(sender, past, message))

    read_all_tells(db, conn.name, nick)


@hook.command("tell")
def tell_cmd(text, nick, db, notice, conn):
    """tell <nick> <message> -- Relay <message> to <nick> when <nick> is around."""
    query = text.split(' ', 1)
    if query[0].lower() == "paradox":
        return "Paradox doesn't want to hear from me. Just send him a fucking message."
    if len(query) != 2:
        prefix = conn.config("command_prefix")
        notice(prefix[0] + tell_cmd.__doc__)
        return

    target = query[0].lower()
    message = query[1].strip()
    sender = nick

    if target == sender.lower():
        notice("Have you looked in a mirror lately?")
        return

    if target.lower() == conn.nick.lower():
        # we can't send messages to ourselves
        notice("Invalid nick '{}'.".format(target))
        return

    if not re.match("^[a-z0-9_|.\-\]\[]*$", target.lower()):
        notice("Invalid nick '{}'.".format(target))
        return

    if count_unread(db, conn.name, target) >= 10:
        notice("Sorry, {} has too many messages queued already.".format(target))
        return

    add_tell(db, conn.name, sender, target, message)
    notice("Your message has been saved, and {} will be notified once they are active.".format(target))
