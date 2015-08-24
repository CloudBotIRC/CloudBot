import string
import asyncio
import re

from sqlalchemy import Table, Column, String
import requests

from cloudbot import hook
from cloudbot.util import database, colors, web


re_lineends = re.compile(r'[\r\n]*')

FACTOID_CHAR = "?"  # TODO: config

table = Table(
    "mem",
    database.metadata,
    Column("word", String(25), primary_key=True),
    Column("data", String(500)),
    Column("nick", String(25))
)


def _load_cache_db(db):
    query = db.execute(table.select())
    return [(row["word"], row["data"]) for row in query]


@asyncio.coroutine
@hook.on_start()
def load_cache(async, db):
    """
    :type db: sqlalchemy.orm.Session
    """
    global factoid_cache
    factoid_cache = {}
    for word, data in (yield from async(_load_cache_db, db)):
        # nick = row["nick"]
        factoid_cache[word] = data  # we might want (data, nick) sometime later


@asyncio.coroutine
def add_factoid(async, db, word, data, nick):
    """
    :type db: sqlalchemy.orm.Session
    :type word: str
    :type data: str
    :type nick: str
    """
    if word in factoid_cache:
        # if we have a set value, update
        yield from async(db.execute, table.update().values(data=data, nick=nick).where(table.c.word == word))
    else:
        # otherwise, insert
        yield from async(db.execute, table.insert().values(word=word, data=data, nick=nick))
    yield from async(db.commit)
    yield from load_cache(async, db)


@asyncio.coroutine
def del_factoid(async, db, word):
    """
    :type db: sqlalchemy.orm.Session
    :type word: str
    """
    yield from async(db.execute, table.delete().where(table.c.word == word))
    yield from async(db.commit)
    yield from load_cache(async, db)


@asyncio.coroutine
@hook.command("r", "remember", permissions=["addfactoid"])
def remember(text, nick, db, notice, async):
    """<word> [+]<data> - remembers <data> with <word> - add + to <data> to append"""

    try:
        word, data = text.split(None, 1)
    except ValueError:
        return remember.__doc__

    word = word.lower()

    old_data = factoid_cache.get(word)

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

    yield from add_factoid(async, db, word, data, nick)


@asyncio.coroutine
@hook.command("f", "forget", permissions=["delfactoid"])
def forget(text, db, async, notice):
    """<word> - forgets previously remembered <word>"""

    data = factoid_cache.get(text.lower())

    if data:
        yield from del_factoid(async, db, text)
        notice('"{}" has been forgotten.'.format(data.replace('`', "'")))
        return
    else:
        notice("I don't know about that.")
        return


@asyncio.coroutine
@hook.command()
def info(text, notice):
    """<factoid> - shows the source of a factoid"""

    text = text.strip().lower()

    if text in factoid_cache:
        notice(factoid_cache[text])
    else:
        notice("Unknown Factoid.")


factoid_re = re.compile(r'^{} ?(.+)'.format(re.escape(FACTOID_CHAR)), re.I)


@asyncio.coroutine
@hook.regex(factoid_re)
def factoid(match, async, event, message, action):
    """<word> - shows what data is associated with <word>"""

    # split up the input
    split = match.group(1).strip().split(" ")
    factoid_id = split[0].lower()

    if len(split) >= 1:
        arguments = " ".join(split[1:])
    else:
        arguments = ""

    if factoid_id in factoid_cache:
        data = factoid_cache[factoid_id]
        # factoid pre-processors
        if data.startswith("<py>"):
            code = data[4:].strip()
            variables = 'input="""{}"""; nick="{}"; chan="{}"; bot_nick="{}";'.format(arguments.replace('"', '\\"'),
                                                                                      event.nick, event.chan,
                                                                                      event.conn.nick)
            result = yield from async(web.pyeval, variables + code)
        else:
            result = data

        # factoid post-processors
        result = colors.parse(result)

        if result.startswith("<act>"):
            result = result[5:].strip()
            action(result)
        elif result.startswith("<url>"):
            url = result[5:].strip()
            response = requests.get(url)
            if response.status_code != requests.codes.ok:
                message("Failed to fetch resource.")
            else:
                message(response.text)
        else:
            message(result)


@asyncio.coroutine
@hook.command(autohelp=False, permissions=["listfactoids"])
def listfactoids(notice):
    """- lists all available factoids"""
    reply_text = []
    reply_text_length = 0
    for word in factoid_cache.keys():
        added_length = len(word) + 2
        if reply_text_length + added_length > 400:
            notice(", ".join(reply_text))
            reply_text = []
            reply_text_length = 0
        else:
            reply_text.append(word)
            reply_text_length += added_length
    notice(", ".join(reply_text))
