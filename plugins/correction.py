from util import hook

import re

CORRECTION_RE = re.compile(r'^(s|S)/.*/.*/\S*$')


@hook.regex(r'^(s|S)/.*/.*/\S*$')
def correction(inp, input=None, bot=None, message=None):
    split = input.msg.split("/")

    find = split[1]
    replace = split[2]

    for item in bot.history[input.chan].__reversed__():
        name, timestamp, msg = item
        if "/" in msg:
            if re.match(CORRECTION_RE, msg):
                # don't correct corrections, it gets really confusing
                continue
        if find in msg:
            if "\x01ACTION" in msg:
                msg = msg.replace("\x01ACTION ", "/me ").replace("\x01", "")
            message(u"Correction, <{}> {}".format(name, msg.replace(find, "\x02" + replace + "\x02")))
            return
        else:
            continue

    return "Did not find {} in any recent messages.".format(find)

