import re
import string
import random
from collections import defaultdict

from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Table
from sqlalchemy import and_

from cloudbot import hook
from cloudbot.util import database

category_re = r"[A-Za-z0-9]+"
data_re = re.compile(r"({})\s(.+)".format(category_re))

# borrowed pagination code from grab.py
cat_pages = defaultdict(dict)
cat_page_index = defaultdict(dict)
confirm_keys = defaultdict(dict)

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


# modified from grab.py
def two_lines(bigstring, chan, nick):
    """Receives a string with new lines. Groups the string into a list of strings with up to 3 new lines per string element. Returns first string element then stores the remaining list in search_pages."""
    global cat_pages
    global cat_page_index
    if nick not in cat_pages[chan]:
        cat_pages[chan][nick] = []
    temp = bigstring.split('\n')
    print("Temp:", len(temp))
    for i in range(0, len(temp), 2):
        cat_pages[chan][nick].append('\n'.join(temp[i:i + 2]))
    cat_page_index[chan][nick] = 0
    return cat_pages[chan][nick][0]


# modified from grab.py
def smart_truncate(content, length=355, suffix='...\n'):
    if len(content) <= length:
        return content
    else:
        return content[:length].rsplit(', ', 1)[0] + suffix + \
               content[:length].rsplit(', ', 1)[1] + smart_truncate(content[length:])


def format_profile(nick, category, text):
    # Add zwsp to avoid pinging users
    nick = "{}{}{}".format(nick[0], "\u200B", nick[1:])
    msg = "{}->{}: {}".format(nick, category, text)
    return msg


# modified from grab.py
@hook.command("moreprofile", autohelp=False)
def moreprofile(text, chan, nick, notice):
    """If a category search has lots of results the results are paginated. If the most recent search is paginated the pages are stored for retrieval. If no argument is given the next page will be returned else a page number can be specified."""
    if nick not in cat_pages[chan] or not cat_pages[chan][nick]:
        notice("There are no category pages to show.")
        return

    if text:
        index = ""
        if text.isnumeric():
            index = int(text)
        else:
            notice("Please specify a positive integer value")
            return

        if index > len(cat_pages[chan][nick]) or index == 0:
            notice("Please specify a valid page number between 1 and {}.".format(len(cat_pages[chan][nick])))
            return
        else:
            msg = "{}(page {}/{})".format(cat_pages[chan][nick][index - 1], index, len(cat_pages[chan][nick]))
            for line in msg.splitlines():
                notice(line)
            return
    else:
        cat_page_index[chan][nick] += 1
        if cat_page_index[chan][nick] < len(cat_pages[chan][nick]):
            msg = "{}(page {}/{})".format(cat_pages[chan][nick][cat_page_index[chan][nick]],
                                           cat_page_index[chan][nick] + 1, len(cat_pages[chan][nick]))
            for line in msg.splitlines():
                notice(line)
            return
        else:
            notice("All pages have been shown. You can specify a page number or start a new search")
            return


@hook.command()
def profile(text, chan, notice, nick):
    """<nick> [category] Returns a user's saved profile data from \"<category>\", or lists all available profile categories for the user if no category specified"""
    global cat_pages
    global cat_page_index

    # Check if we are in a PM with the user
    if nick.lower() == chan.lower():
        return "Profile data not available outside of channels"

    # Split the text in to the nick and requested category
    unpck = text.split(None, 1)

    # Check if the caller specified a profile category, if not, send a NOTICE with the users registered categories
    if len(unpck) < 2:
        cats = []
        cat_pages[chan][nick] = []
        cat_page_index[chan][nick] = 0
        pnick = unpck[0].lower()
        if len(profile_cache.get(chan, {}).get(pnick, {})) == 0:
            notice("User {} has no profile data saved in this channel".format(pnick))
            return

        for e in profile_cache.get(chan, {}).get(pnick, {}):
            cats.append(e)

        out = "Categories: "
        for cat in cats:
            out += "{}, ".format(cat)
        out = smart_truncate(out)
        out = out[:-2]
        out = two_lines(out, chan, nick)
        print(len(cat_pages[chan].get(nick, [])))
        if len(cat_pages[chan].get(nick, [])) > 1:
            msg = "{}(page {}/{}) .moreprofile".format(out, cat_page_index[chan][nick] + 1, len(cat_pages[chan][nick]))
            for line in msg.splitlines():
                notice(line)
            return

        for line in out.splitlines():
            notice(line)
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
    """<category> Deletes \"<category>\" from a user's profile"""
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


@hook.command(autohelp=False)
def profileclear(nick, chan, text, notice, db):
    """Clears all of your profile data in the current channel"""
    if nick.lower() == chan.lower():
        return "Profile data can not be set outside of channels"

    if text:
        if nick in confirm_keys[chan] and text == confirm_keys[chan][nick]:
            del confirm_keys[chan][nick]
            db.execute(table.delete().where((and_(table.c.nick == nick.lower(),
                                                  table.c.chan == chan.lower()))))
            db.commit()
            load_cache(db)
            return "Profile data cleared for {}.".format(nick)
        else:
            notice("Invalid confirm key")
            return
    else:
        confirm_keys[chan][nick] = "".join(random.choice(string.ascii_letters + string.digits) for i in range(10))
        notice("Are you sure you want to clear all of your profile data in {}? use \".profileclear {}\" to confirm"
               .format(chan, confirm_keys[chan][nick]))
        return

