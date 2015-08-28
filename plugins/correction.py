import re

from cloudbot import hook

from cloudbot.util.formatting import ireplace

correction_re = re.compile(r"^[sS]/(.*/.*(?:/[igx]{,4})?)\S*$")


@hook.regex(correction_re)
def correction(match, conn, chan, message):
    """
    :type match: re.__Match
    :type conn: cloudbot.client.Client
    :type chan: str
    """
    groups = [b.replace("\/", "/") for b in re.split(r"(?<!\\)/", match.groups()[0])]
    find = groups[0]
    replace = groups[1].replace("\n","\\n").replace("\r","\\r")

    for item in conn.history[chan].__reversed__():
        nick, timestamp, msg = item
        if correction_re.match(msg):
            # don't correct corrections, it gets really confusing
            continue
        msg = msg.replace("\n","\\n").replace("\r","\\r")

        if find.lower() in msg.lower():
            if "\x01ACTION" in msg:
                msg = msg.replace("\x01ACTION", "").replace("\x01", "")
                mod_msg = ireplace(msg, find, "\x02" + replace + "\x02")
                message("Correction, * {} {}".format(nick, mod_msg))
            else:
                mod_msg = ireplace(msg, find, "\x02" + replace + "\x02")
                message("Correction, <{}> {}".format(nick, mod_msg))

            msg = ireplace(msg, find, replace)
            conn.history[chan].append((nick, timestamp, msg))
            return
        else:
            continue
