from sqlalchemy import Table, Column, UniqueConstraint, String

from cloudbot import hook
from cloudbot.util import database

table = Table(
    "regex_chans",
    database.metadata,
    Column("connection", String),
    Column("channel", String),
    Column("status", String),
    UniqueConstraint("connection", "channel")
)

# Default value.
# If True, all channels without a setting will have regex enabled
# If False, all channels without a setting will have regex disabled
default_enabled = True


@hook.on_start()
def load_cache(db):
    """
    :type db: sqlalchemy.orm.Session
    """
    global status_cache
    status_cache = {}
    for row in db.execute(table.select()):
        conn = row["connection"]
        chan = row["channel"]
        status = row["status"]
        status_cache[(conn, chan)] = status


def set_status(db, conn, chan, status):
    """
    :type db: sqlalchemy.orm.Session
    :type conn: str
    :type chan: str
    :type status: str
    """
    if (conn, chan) in status_cache:
        # if we have a set value, update
        db.execute(
            table.update().values(status=status).where(table.c.connection == conn).where(table.c.channel == chan))
    else:
        # otherwise, insert
        db.execute(table.insert().values(connection=conn, channel=chan, status=status))
    db.commit()


def delete_status(db, conn, chan):
    db.execute(table.delete().where(table.c.connection == conn).where(table.c.channel == chan))
    db.commit()


@hook.sieve()
def sieve_regex(bot, event, _hook):
    if _hook.type == "regex" and event.chan.startswith("#") and _hook.plugin.title != "factoids":
        status = status_cache.get((event.conn.name, event.chan))
        if status != "ENABLED" and (status == "DISABLED" or not default_enabled):
            bot.logger.info("[{}] Denying {} from {}".format(event.conn.name, _hook.function_name, event.chan))
            return None
        bot.logger.info("[{}] Allowing {} to {}".format(event.conn.name, _hook.function_name, event.chan))

    return event


@hook.command(autohelp=False, permissions=["botcontrol"])
def enableregex(text, db, conn, chan, nick, message, notice):
    text = text.strip().lower()
    if not text:
        channel = chan
    elif text.startswith("#"):
        channel = text
    else:
        channel = "#{}".format(text)

    message("Enabling regex matching (youtube, etc) (issued by {})".format(nick), target=channel)
    notice("Enabling regex matching (youtube, etc) in channel {}".format(channel))
    set_status(db, conn.name, channel, "ENABLED")
    load_cache(db)


@hook.command(autohelp=False, permissions=["botcontrol"])
def disableregex(text, db, conn, chan, nick, message, notice):
    text = text.strip().lower()
    if not text:
        channel = chan
    elif text.startswith("#"):
        channel = text
    else:
        channel = "#{}".format(text)

    message("Disabling regex matching (youtube, etc) (issued by {})".format(nick), target=channel)
    notice("Disabling regex matching (youtube, etc) in channel {}".format(channel))
    set_status(db, conn.name, channel, "DISABLED")
    load_cache(db)


@hook.command(autohelp=False, permissions=["botcontrol"])
def resetregex(text, db, conn, chan, nick, message, notice):
    text = text.strip().lower()
    if not text:
        channel = chan
    elif text.startswith("#"):
        channel = text
    else:
        channel = "#{}".format(text)

    message("Resetting regex matching setting (youtube, etc) (issued by {})".format(nick), target=channel)
    notice("Resetting regex matching setting (youtube, etc) in channel {}".format(channel))
    delete_status(db, conn.name, channel)
    load_cache(db)


@hook.command(autohelp=False, permissions=["botcontrol"])
def regexstatus(text, conn, chan):
    text = text.strip().lower()
    if not text:
        channel = chan
    elif text.startswith("#"):
        channel = text
    else:
        channel = "#{}".format(text)
    status = status_cache.get((conn.name, chan))
    if status is None:
        if default_enabled:
            status = "ENABLED"
        else:
            status = "DISABLED"
    return "Regex status for {}: {}".format(channel, status)


@hook.command(autohelp=False, permissions=["botcontrol"])
def listregex(conn):
    values = []
    for (conn_name, chan), status in status_cache.values():
        if conn_name != conn.name:
            continue
        values.append("{}: {}".format(chan, status))
    return ", ".join(values)
