# Written by Scaevolus 2010
from util import hook, http, text, execute
import string
import re

re_lineends = re.compile(r'[\r\n]*')

# some simple "shortcodes" for formatting purposes
shortcodes = {
    '[b]': '\x02',
    '[/b]': '\x02',
    '[u]': '\x1F',
    '[/u]': '\x1F',
    '[i]': '\x16',
    '[/i]': '\x16'}


def db_init(db):
    db.execute("create table if not exists mem(word, data, nick,"
               " primary key(word))")
    db.commit()


def get_memory(db, word):
    row = db.execute("select data from mem where word=lower(?)",
                     [word]).fetchone()
    if row:
        return row[0]
    else:
        return None


@hook.command("r", permissions=["addfactoid"])
@hook.command(permissions=["addfactoid"])
def remember(inp, nick='', db=None, notice=None):
    """remember <word> [+]<data> -- Remembers <data> with <word>. Add +
    to <data> to append."""
    db_init(db)

    append = False

    try:
        word, data = inp.split(None, 1)
    except ValueError:
        return remember.__doc__

    old_data = get_memory(db, word)

    if data.startswith('+') and old_data:
        append = True
        # remove + symbol
        new_data = data[1:]
        # append new_data to the old_data
        if len(new_data) > 1 and new_data[1] in (string.punctuation + ' '):
            data = old_data + new_data
        else:
            data = old_data + ' ' + new_data

    db.execute("replace into mem(word, data, nick) values"
               " (lower(?),?,?)", (word, data, nick))
    db.commit()

    if old_data:
        if append:
            notice("Appending \x02{}\x02 to \x02{}\x02".format(new_data, old_data))
        else:
            notice('Remembering \x02{}\x02 for \x02{}\x02. Type ?{} to see it.'.format(data, word, word))
            notice('Previous data was \x02{}\x02'.format(old_data))
    else:
        notice('Remembering \x02{}\x02 for \x02{}\x02. Type ?{} to see it.'.format(data, word, word))


@hook.command("f", permissions=["delfactoid"])
@hook.command(permissions=["delfactoid"])
def forget(inp, db=None, notice=None):
    """forget <word> -- Forgets a remembered <word>."""

    db_init(db)
    data = get_memory(db, inp)

    if data:
        db.execute("delete from mem where word=lower(?)",
                   [inp])
        db.commit()
        notice('"%s" has been forgotten.' % data.replace('`', "'"))
        return
    else:
        notice("I don't know about that.")
        return


@hook.command
def info(inp, notice=None, db=None):
    """info <factoid> -- Shows the source of a factoid."""

    db_init(db)

    # attempt to get the factoid from the database
    data = get_memory(db, inp.strip())

    if data:
        notice(data)
    else:
        notice("Unknown Factoid.")


@hook.regex(r'^\? ?(.+)')
def factoid(inp, message=None, db=None, bot=None, action=None, conn=None, input=None):
    "?<word> -- Shows what data is associated with <word>."
    try:
        prefix_on = bot.config["plugins"]["factoids"].get("prefix", False)
    except KeyError:
        prefix_on = False

    db_init(db)

    # split up the input
    split = inp.group(1).strip().split(" ")
    factoid_id = split[0]

    if len(split) >= 1:
        arguments = " ".join(split[1:])
    else:
        arguments = ""

    data = get_memory(db, factoid_id)

    if data:
        # factoid preprocessors
        if data.startswith("<py>"):
            code = data[4:].strip()
            variables = 'input="""{}"""; nick="{}"; chan="{}"; bot_nick="{}";'.format(arguments.replace('"', '\\"'),
                                                                                  input.nick, input.chan,
                                                                                  input.conn.nick)
            result = execute.eval_py(variables + code)
        else:
            result = data

        # factoid postprocessors
        result = text.multiword_replace(result, shortcodes)

        if result.startswith("<act>"):
            result = result[5:].strip()
            action(result)
        elif result.startswith("<url>"):
            url = result[5:].strip()
            try:
                message(http.get(url))
            except http.HttpError:
                message("Could not fetch URL.")
        else:
            if prefix_on:
                message("\x02[{}]:\x02 {}".format(factoid_id, result))
            else:
                message(result)
