"""
remember.py: written by Scaevolus 20101
"""

from util import hook
import re


def db_init(db):
    db.execute("create table if not exists mem(word, data, nick,"
               " primary key(word))")
    db.commit()


def get_memory(db, word):

    row = db.execute("select data from mem where word=lower(?)", [word]).fetchone()
    if row:
        return row[0]
    else:
        return None


@hook.regex(r'^\+ ?(.*)')
@hook.command("r")
def remember(inp, nick='', db=None, say=None, input=None, notice=None):
    "+<word> [+]<data> -- maps word to data in the memory"
    if input.nick not in input.bot.config["admins"]:
        return
    binp = inp.group(0)
    bind = binp.replace('+', '', 1)
    db_init(db)


    append = False

    try:
        head, tail = bind.split(None, 1)
    except ValueError:
        return remember.__doc__

    data = get_memory(db, head)

    if tail[0] == '+':
        append = True
        # ignore + symbol
        new = tail[1:]
        _head, _tail = data.split(None, 1)
        # data is stored with the input so ignore it when re-adding it
        import string
        if len(tail) > 1 and tail[1] in (string.punctuation + ' '):
            tail = _tail + new
        else:
            tail = _tail + ' ' + new

    db.execute("replace into mem(word, data, nick) values"
               " (lower(?),?,?)", (head, tail, nick))
    db.commit()

    if data:
        if append:
            notice("Appending %s to %s" % (new, data.replace('"', "''")))
        else:
            notice('Forgetting existing data (%s), remembering this instead!' % \
                    data.replace('"', "''"))
            return
    else:
        notice('Remembered!')
        return


@hook.command
def forget(inp, db=None):
    "-<word> -- forgets the mapping that word had"

    binp = inp.group(0)
    bind = binp.replace('-', '', 1)
    print bind

    try:
        head, tail = bind.split(None, 1)
    except ValueError:
        return remember.__doc__

    db_init(db)
    data = get_memory(db, binp)

    if data:
        db.execute("delete from mem where word=lower(?)",
                   (inp))
        db.commit()
        return 'forgot `%s`' % data.replace('`', "'")
    else:
        return "I don't know about that."

@hook.command("info")
@hook.regex(r'^\? ?(.+)')
def question(inp, say=None, db=None):
    "?<word> -- shows what data is associated with word"
    db_init(db)

    data = get_memory(db, inp.group(1).strip())
    if data:
        say(data)
