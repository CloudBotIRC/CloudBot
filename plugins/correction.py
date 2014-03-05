from util import hook

import re

<<<<<<< HEAD
@hook.regex(r'^(s|S)/.*/.*/\S*$')
def correction(inp, message=None, input=None, notice=None, db=None):
    splitinput = input.msg.split("/")
    if splitinput[3]:
        nick = splitinput[3]
    else:
        nick = input.nick
    last_message = db.execute("select name, quote from seen_user where name"
                              " like :nick and chan = :chan", {'nick': nick.lower(),
                                                               'chan': input.chan.lower()}).fetchone()

    if last_message:
        splitinput = input.msg.split("/")
        find = splitinput[1]
        replace = splitinput[2]
        if find in last_message[1]:
            if "\x01ACTION" in last_message[1]:
                msg = last_message[1].replace("\x01ACTION ", "/me ").replace("\x01", "")
            else:
                msg = last_message[1]
            message(u"Correction, <{}> {}".format(nick, msg.replace(find, "\x02" + replace + "\x02")))
        else:
            notice(u"{} can't be found in your last message".format(find))
=======
CORRECTION_RE = r'^(s|S)/.*/.*/?\S*$'


@hook.regex(CORRECTION_RE)
def correction(match, input=None, conn=None, message=None):
    split = input.msg.split("/")

    if len(split) == 4:
        nick = split[3].lower()
>>>>>>> develop
    else:
        nick = None

    find = split[1]
    replace = split[2]

    for item in conn.history[input.chan].__reversed__():
        name, timestamp, msg = item
        if msg.startswith("s/"):
            # don't correct corrections, it gets really confusing
            continue
        if nick:
            if nick != name.lower():
                continue
        if find in msg:
            if "\x01ACTION" in msg:
                msg = msg.replace("\x01ACTION ", "/me ").replace("\x01", "")
            message(u"Correction, <{}> {}".format(name, msg.replace(find, "\x02" + replace + "\x02")))
            return
        else:
            continue

    return u"Did not find {} in any recent messages.".format(find)

