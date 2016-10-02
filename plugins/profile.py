import re

from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Table
from sqlalchemy import and_

from cloudbot import hook
from cloudbot.util import database

category_re = r"[A-Za-z0-9]+"
data_re = re.compile(r"({})\s(.+)".format(category_re))

table = Table(
    'profile',
    database.metadata,
    Column('chan', String),
    Column('nick', String),
    Column('category', String),
    Column('text', String)
)

profile_cache = {}


@hook.on_start()
def load_cache(db):
    """
    :type db: sqlalchemy.orm.Session
    """
    global profile_cache
    profile_cache = {}
    for row in db.execute(table.select().order_by(table.c.category)):
        nick = row["nick"].lower()
        cat = row["category"]
        text = row["text"]
        chan = row["chan"]
        profile_cache.setdefault(chan, {}).setdefault(nick, {})[cat] = text


def format_profile(nick, category, text):
    # Add zwsp to avoid pinging users
    nick = "{}{}{}".format(nick[0], "\u200B", nick[1:])
    msg = "{}->{}: {}".format(nick, category, text)
    return msg


@hook.command()
def profile(text, chan, notice, nick):
    """<nick> [category] Returns a user's saved profile data from \"<category>\", or lists all available profile categories for the user if no category specified"""
    # Check if we are in a PM with the user
    if nick.lower() == chan.lower():
        return "Profile data not available outside of channels"

    # Split the text in to the nick and requested category
    unpck = text.split(None, 1)

    # Check if the caller specified a profile category, if not, send a NOTICE with the users registered categories
    if len(unpck) < 2:
        cats = []
        pnick = unpck[0].lower()
        if len(profile_cache.get(chan, {}).get(pnick, {})) == 0:
            notice("User {} has no profile data saved in this channel".format(pnick))
            return

        for e in profile_cache.get(chan, {}).get(pnick, {}):
            cats.append(e)

        notice("Categories: " + ", ".join(cats))
        return

    pnick, category = unpck
    if category.lower() not in profile_cache.get(chan, {}).get(pnick.lower(), {}):
        notice("User {} has no profile data for category {} in this channel".format(pnick, category))

    else:
        content = profile_cache[chan][pnick.lower()][category.lower()]
        return format_profile(pnick, category, content)


@hook.command()
def profileadd(text, chan, nick, notice, db):
    """<category> <content> Adds data to your profile in the current channel under \"<category>\""""
    if nick.lower() == chan.lower():
        return "Profile data can not be set outside of channels"

    match = data_re.match(text)

    if not match:
        notice("Invalid data")
    else:
        cat, data = match.groups()
        if cat.lower() not in profile_cache.get(chan, {}).get(nick, {}):
            db.execute(table.insert().values(chan=chan.lower(), nick=nick.lower(), category=cat.lower(), text=data))
            db.commit()
            load_cache(db)
            return "Created new profile category {}".format(cat)

        else:
            db.execute(table.update().values(text=data).where((and_(table.c.nick == nick.lower(),
                                                                    table.c.chan == chan.lower(),
                                                                    table.c.category == cat.lower()))))
            db.commit()
            load_cache(db)
            return "Updated profile category {}".format(cat)


@hook.command()
def profiledel(nick, chan, text, notice, db):
    """<category> Deletes \"<category>\" from a users profile"""
    if nick.lower() == chan.lower():
        return "Profile data can not be set outside of channels"

    category = text.split()[0]
    if category.lower() not in profile_cache.get(chan.lower(), {}).get(nick.lower(), {}):
        notice("That category does not exist in your profile")
        return

    db.execute(table.delete().where((and_(table.c.nick == nick.lower(),
                                          table.c.chan == chan.lower(),
                                          table.c.category == category.lower()))))
    db.commit()
    load_cache(db)
    return "Deleted profile category {}".format(category)
