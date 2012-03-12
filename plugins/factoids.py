"""
remember.py: written by Scaevolus 20101
"""

from util import hook
import re


# some simple "shortcodes" for formatting purposes
shortcodes = {
'<b>': '\x02',
'</b>': '\x02',
'<u>': '\x1F',
'</u>': '\x1F',
'<i>': '\x16',
'</i>': '\x16'}


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


def multiwordReplace(text, wordDic):
    """
    take a text and replace words that match a key in a dictionary with
    the associated value, return the changed text
    """
    rc = re.compile('|'.join(map(re.escape, wordDic)))

    def translate(match):
        return wordDic[match.group(0)]
    return rc.sub(translate, text)


@hook.command("r")
@hook.command
def remember(inp, nick='', db=None, say=None, input=None, notice=None):
    ".remember <word> [+]<data> -- Remembers <data> with <word>. Add + to <data> to append."
    if input.nick not in input.bot.config["admins"]:
        notice("Only bot admins can use this command!")
        return
    db_init(db)

    append = False

    try:
        head, tail = inp.split(None, 1)
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


@hook.command("f")
@hook.command
def forget(inp, db=None, input=None, notice=None):
    ".forget <word> -- Forgets a remembered <word>."
    if input.nick not in input.bot.config["admins"]:
        notice("Only bot admins can use this command!")
        return

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


@hook.command("info")
@hook.regex(r'^\? ?(.+)')
def question(inp, say=None, db=None, bot=None):
    "?<word> -- Shows what data is associated with <word>."
    try:
        prefix_on = bot.config["plugins"]["factoids"]["prefix"]
    except KeyError:
        prefix_on = False

    db_init(db)

    data = get_memory(db, inp.group(1).strip())
    if data:
        out = multiwordReplace(data, shortcodes)
        if prefix_on:
            say("\x02[%s]:\x02 %s" % (inp.group(1).strip(), out))
        else:
            say(out)
