import string
import asyncio
import re

from sqlalchemy import Table, Column, String, PrimaryKeyConstraint
from collections import defaultdict
import requests

from cloudbot import hook
from cloudbot.util import database, colors, web


# below is the default factoid in every channel you can modify it however you like
default_dict = {"commands": "https://snoonet.org/gonzobot"}

re_lineends = re.compile(r'[\r\n]*')

FACTOID_CHAR = "?"  # TODO: config

table = Table(
    "factoids",
    database.metadata,
    Column("word", String(25)),
    Column("data", String(500)),
    Column("nick", String(25)),
    Column("chan", String(65)),
    PrimaryKeyConstraint('word', 'chan')
)


def _load_cache_db(db):
    query = db.execute(table.select())
    return [(row["word"], row["data"], row["chan"]) for row in query]


@asyncio.coroutine
@hook.on_start()
def load_cache(async, db):
    """
    :type db: sqlalchemy.orm.Session
    """
    global factoid_cache
    factoid_cache = defaultdict(lambda: default_dict) 
    for word, data, chan in (yield from async(_load_cache_db, db)):
        # nick = row["nick"]
        if chan not in factoid_cache:
            factoid_cache.update({chan:{word:data}})
        elif word not in factoid_cache[chan]:
            factoid_cache[chan].update({word:data})
        else:
            factoid_cache[chan][word] = data


@asyncio.coroutine
def add_factoid(async, db, word, chan, data, nick):
    """
    :type db: sqlalchemy.orm.Session
    :type word: str
    :type data: str
    :type nick: str
    """
    if word in factoid_cache[chan]:
        # if we have a set value, update
        yield from async(db.execute, table.update().values(data=data, nick=nick, chan=chan).where(table.c.word == word and table.c.chan == chan))
    else:
        # otherwise, insert
        yield from async(db.execute, table.insert().values(word=word, data=data, nick=nick, chan=chan))
    yield from async(db.commit)
    yield from load_cache(async, db)


@asyncio.coroutine
def del_factoid(async, db, chan, word):
    """
    :type db: sqlalchemy.orm.Session
    :type word: str
    """
    yield from async(db.execute, table.delete().where(table.c.word == word and table.c.chan == chan))
    yield from async(db.commit)
    yield from load_cache(async, db)


@asyncio.coroutine
@hook.command("r","remember", permissions=["op"])
def remember(text, nick, db, chan, notice, async):
    """<word> [+]<data> - remembers <data> with <word> - add + to <data> to append"""
    global factoid_cache
    try:
        word, data = text.split(None, 1)
    except ValueError:
        return remember.__doc__

    word = word.lower()
    try:
        old_data = factoid_cache[chan].get(word)
    except:
        old_data = ""
        pass

    if data.startswith('+') and old_data:
        # remove + symbol
        new_data = data[1:]
        # append new_data to the old_data
        if len(new_data) > 1 and new_data[1] in (string.punctuation + ' '):
            data = old_data + new_data
        else:
            data = old_data + ' ' + new_data
        notice("Appending \x02{}\x02 to \x02{}\x02".format(new_data, old_data))
    else:
        notice('Remembering \x02{0}\x02 for \x02{1}\x02. Type {2}{1} to see it.'.format(data, word, FACTOID_CHAR))
        if old_data:
            notice('Previous data was \x02{}\x02'.format(old_data))

    yield from add_factoid(async, db, word, chan, data, nick)


@asyncio.coroutine
@hook.command("f","forget", permissions=["op"])
def forget(text, chan, db, async, notice):
    """<word> - forgets previously remembered <word>"""
    global factoid_cache
    data = factoid_cache[chan].get(text.lower())

    if data:
        yield from del_factoid(async, db, chan, text)
        notice('"{}" has been forgotten.'.format(data.replace('`', "'")))
        return
    else:
        notice("I don't know about that.")
        return


@asyncio.coroutine
@hook.command()
def info(text, chan, notice):
    """<factoid> - shows the source of a factoid"""

    text = text.strip().lower()

    if text in factoid_cache:
        notice(factoid_cache[chan][text])
    else:
        notice("Unknown Factoid.")


factoid_re = re.compile(r'^{} ?(.+)'.format(re.escape(FACTOID_CHAR)), re.I)


@asyncio.coroutine
@hook.regex(factoid_re)
def factoid(match, async, chan, event, message, action):
    """<word> - shows what data is associated with <word>"""

    # split up the input
    split = match.group(1).strip().split(" ")
    factoid_id = split[0].lower()

    if len(split) >= 1:
        arguments = " ".join(split[1:])
    else:
        arguments = ""

    if factoid_id in factoid_cache[chan]:
        data = factoid_cache[chan][factoid_id]
        result = data

        # factoid post-processors
        result = colors.parse(result)

        if result.startswith("<act>"):
            result = result[5:].strip()
            action(result)
        else:
            message(result)


@asyncio.coroutine
@hook.command("listfacts", autohelp=False)
def listfactoids(notice, chan):
    """- lists all available factoids"""
    reply_text = []
    reply_text_length = 0
    for word in factoid_cache[chan].keys():
        added_length = len(word) + 2
        if reply_text_length + added_length > 400:
            notice(", ".join(reply_text))
            reply_text = []
            reply_text_length = 0
        else:
            reply_text.append(word)
            reply_text_length += added_length
    notice(", ".join(reply_text))
