"""
remind.py

Allows users to add reminders for various tasks.

Created By:
    - Pangea <https://github.com/PangeaCake>
    - Luke Rogers <https://github.com/lukeroge>

License:
    GPL v3
"""


from datetime import datetime

import time
import asyncio

from sqlalchemy import Table, Column, String, DateTime, PrimaryKeyConstraint

from cloudbot import hook
from cloudbot.util import database
from cloudbot.util.timeparse import time_parse
from cloudbot.util.timeformat import format_time, time_since
from cloudbot.util import colors


table = Table(
    'reminders',
    database.metadata,
    Column('network', String(50)),
    Column('added_user', String(30)),
    Column('added_time', DateTime),
    Column('added_chan', String(50)),
    Column('message', String(512)),
    Column('remind_time', DateTime),
    PrimaryKeyConstraint('network', 'added_user', 'added_time')
)


@asyncio.coroutine
def delete_reminder(async, db, network, remind_time, user):
    query = table.delete() \
        .where(table.c.network == network.lower()) \
        .where(table.c.remind_time == remind_time) \
        .where(table.c.added_user == user.lower())
    yield from async(db.execute, query)
    yield from async(db.commit)


@asyncio.coroutine
def delete_all(async, db, network, user):
    query = table.delete() \
        .where(table.c.network == network.lower()) \
        .where(table.c.added_user == user.lower())
    yield from async(db.execute, query)
    yield from async(db.commit)


@asyncio.coroutine
def add_reminder(async, db, network, added_user, added_chan, message, remind_time, added_time):
    query = table.insert().values(
        network=network.lower(),
        added_user=added_user.lower(),
        added_time=added_time,
        added_chan=added_chan.lower(),
        message=message,
        remind_time=remind_time
    )
    yield from async(db.execute, query)
    yield from async(db.commit)


@asyncio.coroutine
@hook.on_start()
def load_cache(async, db):
    global reminder_cache
    reminder_cache = []

    for network, remind_time, added_time, user, message in (yield from async(_load_cache_db, db)):
        reminder_cache.append((network, remind_time, added_time, user, message))


def _load_cache_db(db):
    query = db.execute(table.select())
    return [(row["network"], row["remind_time"], row["added_time"], row["added_user"], row["message"]) for row in query]


@asyncio.coroutine
@hook.periodic(30, initial_interval=30)
def check_reminders(bot, async, db):
    current_time = datetime.now()

    for reminder in reminder_cache:
        network, remind_time, added_time, user, message = reminder
        if remind_time <= current_time:
            if network not in bot.connections:
                # connection is invalid
                yield from add_reminder(async, db, network, remind_time, user)
                yield from load_cache(async, db)
                continue

            conn = bot.connections[network]

            if not conn.ready:
                return

            remind_text = colors.parse(time_since(added_time, count=2))
            alert = colors.parse("{}, you have a reminder from $(b){}$(clear) ago!".format(user, remind_text))

            conn.message(user, alert)
            conn.message(user, '"{}"'.format(message))

            delta = (remind_time-added_time).seconds
            if delta > (30*60):
                late_time = time_since(remind_time, count=2)
                late = "(I'm sorry for delivering this message $(b){}$(clear) late," \
                       " it seems I was unable to deliver it on time)".format(late_time)
                conn.message(user, colors.parse(late))

            yield from delete_reminder(async, db, network, remind_time, user)
            yield from load_cache(async, db)


@asyncio.coroutine
@hook.command('remind', 'reminder', 'in')
def remind(text, nick, chan, db, conn, notice, async):
    """<1 minute, 30 seconds>: <do task> -- reminds you to <do task> in <1 minute, 30 seconds>"""

    count = len([x for x in reminder_cache if x[0] == conn.name and x[3] == nick.lower()])

    if text == "clear":
        if count == 0:
            return "You have no reminders to delete."

        yield from delete_all(async, db, conn.name, nick)
        yield from load_cache(async, db)
        return "Deleted all ({}) reminders for {}!".format(count, nick)

    # split the input on the first ":"
    parts = text.split(":", 1)

    if len(parts) == 1:
        # user didn't add a message, send them help
        notice(remind.__doc__)
        return

    if count > 10:
        return "Sorry, you already have too many reminders queued (10), you will need to wait or " \
               "clear your reminders to add any more."

    time_string = parts[0].strip()
    message = colors.strip_all(parts[1].strip())

    # get the current time in both DateTime and Unix Epoch
    current_epoch = time.time()
    current_time = datetime.fromtimestamp(current_epoch)

    # parse the time input, return error if invalid
    seconds = time_parse(time_string)
    if not seconds:
        return "Invalid input."

    if seconds > 2764800 or seconds < 60:
        return "Sorry, remind input must be more then a minute, and less then one month."

    # work out the time to remind the user, and check if that time is in the past
    remind_time = datetime.fromtimestamp(current_epoch + seconds)
    if remind_time < current_time:
        return "I can't remind you in the past!"

    # finally, add the reminder and send a confirmation message
    yield from add_reminder(async, db, conn.name, nick, chan, message, remind_time, current_time)
    yield from load_cache(async, db)

    remind_text = format_time(seconds, count=2)
    output = "Alright, I'll remind you \"{}\" in $(b){}$(clear)!".format(message, remind_text)

    return colors.parse(output)
