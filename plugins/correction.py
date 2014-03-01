from util import hook

import re

CORRECTION_RE = r'^(s|S)/.*/.*/?\S*$'


@hook.regex(CORRECTION_RE)
def correction(match, input=None, conn=None, message=None):
    split = input.msg.split("/")

    if len(split) == 4:
        nick = split[3].lower()
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

