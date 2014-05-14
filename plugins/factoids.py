# Written by Scaevolus 2010
import string
import re

from sqlalchemy import Table, Column, String

from cloudbot import botvars, hook, http, formatting, pyexec

re_lineends = re.compile(r'[\r\n]*')


# some simple "shortcodes" for formatting purposes
shortcodes = {
    '[b]': '\x02',
    '[/b]': '\x02',
    '[u]': '\x1F',
    '[/u]': '\x1F',
    '[i]': '\x16',
    '[/i]': '\x16'
}

table = Table(
    "mem",
    botvars.metadata,
    Column("word", String, primary_key=True),
    Column("data", String),
    Column("nick", String)
)

@hook.onload()
def load_cache(db):
    """
    :type db: sqlalchemy.orm.Session
    """
    global factoid_cache
    factoid_cache = {}
    for row in db.execute(table.select()):
        word = row["word"]
        data = row["data"]
        # nick = row["nick"]
        factoid_cache[word] = data  # we might want (data, nick) sometime later


def add_factoid(db, word, data, nick):
    """
    :type db: sqlalchemy.orm.Session
    :type word: str
    :type data: str
    :type nick: str
    """
    if word in factoid_cache:
        # if we have a set value, update
        db.execute(table.update().values(data=data, nick=nick).where(table.c.word == word))
    else:
        # otherwise, insert
        db.execute(table.insert().values(word=word, data=data, nick=nick))
    db.commit()
    load_cache(db)


def del_factoid(db, word):
    """
    :type db: sqlalchemy.orm.Session
    :type word: str
    """
    db.execute(table.delete().where(table.c.word == word))
    db.commit()
    load_cache(db)


@hook.command(["r", "remember"], permissions=["addfactoid"])
def remember(text, nick, db, notice):
    """remember <word> [+]<data> -- Remembers <data> with <word>. Add + to <data> to append."""

    append = False

    try:
        word, data = text.split(None, 1)
    except ValueError:
        return remember.__doc__

    old_data = factoid_cache.get(word)

    if data.startswith('+') and old_data:
        append = True
        # remove + symbol
        new_data = data[1:]
        # append new_data to the old_data
        if len(new_data) > 1 and new_data[1] in (string.punctuation + ' '):
            data = old_data + new_data
        else:
            data = old_data + ' ' + new_data

    add_factoid(db, word, data, nick)

    if old_data:
        if append:
            notice("Appending \x02{}\x02 to \x02{}\x02".format(new_data, old_data))
        else:
            notice('Remembering \x02{}\x02 for \x02{}\x02. Type ?{} to see it.'.format(data, word, word))
            notice('Previous data was \x02{}\x02'.format(old_data))
    else:
        notice('Remembering \x02{}\x02 for \x02{}\x02. Type ?{} to see it.'.format(data, word, word))


@hook.command(["f", "forget"], permissions=["delfactoid"])
def forget(text, db, notice):
    """forget <word> -- Forgets a remembered <word>."""

    data = factoid_cache.get(text)

    if data:
        del_factoid(db, text)
        notice('"%s" has been forgotten.' % data.replace('`', "'"))
        return
    else:
        notice("I don't know about that.")
        return


@hook.command
def info(text, notice):
    """info <factoid> -- Shows the source of a factoid."""

    text = text.strip()

    if text in factoid_cache:
        notice(factoid_cache[text])
    else:
        notice("Unknown Factoid.")


@hook.regex(r'^\? ?(.+)')
def factoid(inp, input, db, message, action):
    """?<word> -- Shows what data is associated with <word>."""

    # split up the input
    split = inp.group(1).strip().split(" ")
    factoid_id = split[0]

    if len(split) >= 1:
        arguments = " ".join(split[1:])
    else:
        arguments = ""

    if factoid_id in factoid_cache:
        data = factoid_cache[factoid_id]
        # factoid preprocessors
        if data.startswith("<py>"):
            code = data[4:].strip()
            variables = 'input="""{}"""; nick="{}"; chan="{}"; bot_nick="{}";'.format(arguments.replace('"', '\\"'),
                                                                                      input.nick, input.chan,
                                                                                      input.conn.nick)
            result = pyexec.eval_py(variables + code)
        else:
            result = data

        # factoid postprocessors
        result = formatting.multiword_replace(result, shortcodes)

        if result.startswith("<act>"):
            result = result[5:].strip()
            action(result)
        elif result.startswith("<url>"):
            url = result[5:].strip()
            try:
                message(http.get(url))
            except http.HTTPError:
                message("Could not fetch URL.")
        else:
            message(result)


@hook.command(autohelp=False, permissions=["listfactoids"])
def listfactoids(reply):
    reply_text = []
    reply_text_length = 0
    for word in factoid_cache.keys():
        added_length = len(word) + 2
        if reply_text_length + added_length > 400:
            reply(", ".join(reply_text))
            reply_text = []
            reply_text_length = 0
        else:
            reply_text.append(word)
            reply_text_length += added_length
    return ", ".join(reply_text)
