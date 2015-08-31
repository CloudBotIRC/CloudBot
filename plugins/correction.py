import re

from cloudbot import hook

from cloudbot.util.formatting import ireplace

correction_re = re.compile(r"^[sS]/(.*/.*(?:/[igx]{,4})?)\S*$")


@hook.regex(correction_re)
def correction(match, conn, nick, chan, message):
    """
    :type match: re.__Match
    :type conn: cloudbot.client.Client
    :type chan: str
    """
    groups = [b.replace("\/", "/") for b in re.split(r"(?<!\\)/", match.groups()[0])]
    find = groups[0]
    replace = groups[1]
    if find == replace:
        return "really dude? you want me to replace {} with {}?".format(find, replace)

    for item in conn.history[chan].__reversed__():
        name, timestamp, msg = item
        if correction_re.match(msg):
            # don't correct corrections, it gets really confusing
            continue

        if find.lower() in msg.lower():
            if "\x01ACTION" in msg:
                msg = msg.replace("\x01ACTION", "").replace("\x01", "")
                mod_msg = ireplace(msg, find, "\x02" + replace + "\x02")
                message("Correction, * {} {}".format(name, mod_msg))
            else:
                mod_msg = ireplace(msg, find, "\x02" + replace + "\x02")
                message("Correction, <{}> {}".format(name, mod_msg))

            msg = ireplace(msg, find, replace)
            if nick.lower() in name.lower():
                conn.history[chan].append((name, timestamp, msg))
            return
        else:
            continue
    # return("No matches for \"\x02{}\x02\" in recent messages from \x02{}\x02. You can only correct your own messages.".format(find, nick))
