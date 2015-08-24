import asyncio
from fnmatch import fnmatch

from sqlalchemy import Table, Column, UniqueConstraint, PrimaryKeyConstraint, String, Boolean

from cloudbot import hook
from cloudbot.util import database

logchannel = ""

table = Table(
    "ignored",
    database.metadata,
    Column("connection", String(25)),
    Column("channel", String(25)),
    Column("mask", String(250)),
    Column("status", Boolean, default=True),
    UniqueConstraint("connection", "channel", "mask", "status"),
    PrimaryKeyConstraint("connection", "channel", "mask")
)


@hook.on_start
def load_cache(db):
    """
    :type db: sqlalchemy.orm.Session
    """
    global ignore_cache
    ignore_cache = []
    for row in db.execute(table.select()):
        conn = row["connection"]
        chan = row["channel"]
        mask = row["mask"]
        ignore_cache.append((conn, chan, mask))


def add_ignore(db, conn, chan, mask):
    if (conn, chan) in ignore_cache:
        pass
    else:
        db.execute(table.insert().values(connection=conn, channel=chan, mask=mask))

    db.commit()
    load_cache(db)


def remove_ignore(db, conn, chan, mask):
    db.execute(table.delete().where(table.c.connection == conn).where(table.c.channel == chan)
               .where(table.c.mask == mask))
    db.commit()
    load_cache(db)

def is_ignored(conn, chan, mask):
    for _conn, _chan, _mask in ignore_cache:
        if _chan == "*":
            # this is a global ignore
            if fnmatch(mask, _mask):
                return True
        else:
            # this is a channel-specific ignore
            if not (conn, chan) == (_conn, _chan):
                continue
            if fnmatch(mask, _mask):
                return True


# noinspection PyUnusedLocal
@asyncio.coroutine
@hook.sieve(priority=50)
def ignore_sieve(bot, event, _hook):
    """
    :type bot: cloudbot.bot.CloudBot
    :type event: cloudbot.event.Event
    :type _hook: cloudbot.plugin.Hook
    """
    # don't block event hooks
    if _hook.type in ("irc_raw", "event"):
        return event

    # don't block an event that could be unignoring
    if _hook.type == "command" and event.triggered_command in ("unignore", "global_unignore"):
        return event

    if event.mask is None:
        # this is a server message, we don't need to check it
        return event

    mask = event.mask.lower()
    if is_ignored(event.conn.name, event.chan, mask):
        return None

    return event


@hook.command(permissions=["ignore"])
def ignore(text, db, chan, conn, notice, message, nick):
    """<nick|mask> -- ignores all input from <nick|mask> in this channel."""
    target = text.lower()
    if "!" not in target or "@" not in target:
        target = "{}!*@*".format(target)

    if is_ignored(conn.name, chan, target):
        notice("{} is already ignored in {}.".format(target, chan))
    else:
        if logchannel:
            message("{} used IGNORE to make me ignore {} in {}".format(nick, target, chan), logchannel)
        notice("{} has been ignored in {}.".format(target, chan))
        add_ignore(db, conn.name, chan, target)


@hook.command(permissions=["ignore"])
def unignore(text, db, chan, conn, notice, nick, message):
    """<nick|mask> -- un-ignores all input from <nick|mask> in this channel."""
    target = text.lower()
    if "!" not in target or "@" not in target:
        target = "{}!*@*".format(target)

    if not is_ignored(conn.name, chan, target):
        notice("{} is not ignored in {}.".format(target, chan))
    else:
        if logchannel:
            message("{} used UNIGNORE to make me stop ignoring {} in {}".format(nick, target, chan), logchannel)
        notice("{} has been un-ignored in {}.".format(target, chan))
        remove_ignore(db, conn.name, chan, target)


@hook.command(permissions=["botcontrol"])
def global_ignore(text, db, conn, notice):
    """<nick|mask> -- ignores all input from <nick|mask> in ALL channels."""
    target = text.lower()
    if "!" not in target or "@" not in target:
        target = "{}!*@*".format(target)

    if is_ignored(conn.name, "*", target):
        notice("{} is already globally ignored.".format(target))
    else:
        notice("{} has been globally ignored.".format(target))
        add_ignore(db, conn.name, "*", target)


@hook.command(permissions=["botcontrol"])
def global_unignore(text, db, conn, notice):
    """<nick|mask> -- un-ignores all input from <nick|mask> in ALL channels."""
    target = text.lower()
    if "!" not in target or "@" not in target:
        target = "{}!*@*".format(target)

    if not is_ignored(conn.name, "*", target):
        notice("{} is not globally ignored.".format(target))
    else:
        notice("{} has been globally un-ignored.".format(target))
        remove_ignore(db, conn.name, "*", target)
