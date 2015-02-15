import asyncio
import re

from cloudbot import hook

correction_re = re.compile(r"^[sS]/(.*/.*(?:/[igx]{,4})?)\S*$")


@asyncio.coroutine
@hook.regex(correction_re)
def correction(match, conn, chan, message):
    """
    :type match: re.__Match
    :type conn: cloudbot.client.Client
    :type chan: str
    """
    groups = [b.replace("\/", "/") for b in re.split(r"(?<!\\)/", match.groups()[0])]
    find = groups[0]
    replacement = groups[1]
    flags = groups[2] if len(groups) == 3 else ""
    find_re = re.compile("{}{}".format("(?{})".format(flags.replace("g", ""))
                                       if flags.replace("g", "") != "" else "", find))

    for item in conn.history[chan].__reversed__():
        nick, timestamp, msg = item
        if correction_re.match(msg):
            # don't correct corrections, it gets really confusing
            continue
        if find_re.search(msg):
            is_action = False
            if "\x01ACTION" in msg:
                is_action = True
                msg = msg.replace("\x01ACTION", "").replace("\x01", "")
            mod_msg = find_re.sub("\x02" + replacement + "\x02", msg, count=int("g" not in flags))
            message("Correction, {}".format(("<{}> " if not is_action else "* {}").format(nick) + mod_msg))
            # append to end of history file
            msg = find_re.sub(replacement, msg, count=int("g" not in flags))
            conn.history[chan].append((nick, timestamp, msg))
            return
        else:
            continue
