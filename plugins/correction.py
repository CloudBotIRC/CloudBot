import asyncio
import re

from cloudbot import hook

correction_re = re.compile(r"^[sS]/(.*/.*/[igx]{,4})\S*$")


@asyncio.coroutine
@hook.regex(correction_re)
def correction(match, conn, chan, message):
    """
    :type match: re.__Match
    :type conn: cloudbot.client.Client
    :type chan: str
    """
    find, replacement, flags = tuple([b.replace("\/", "/") for b in re.split(r"(?<!\\)/", match.groups()[0])])

    find_re = re.compile("{}{}".format("(?{})".format(flags.replace("g", "")) if flags.replace("g", "") != "" else "", find))

    for item in conn.history[chan].__reversed__():
        nick, timestamp, msg = item
        if correction_re.match(msg):
            # don't correct corrections, it gets really confusing
            continue
        if find_re.search(msg):
            if "\x01ACTION" in msg:
                msg = msg.replace("\x01ACTION ", "/me ").replace("\x01", "")
            message("Correction, <{}> {}".format(nick, find_re.sub("\x02" + replacement + "\x02", msg, count=int(not "g" in flags))))
            return
        else:
            continue
    return "Did not find {} in any recent messages.".format(to_find)

