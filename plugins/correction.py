import asyncio
import re

from cloudbot import hook

correction_re = re.compile(r"^[sS]/(.*/.*(?:/[igx]{,4})?)\S*$")


def ireplace(text, old, new, count=None):
    """
    A case-insensitive replace() clone. Return a copy of text with all occurrences of substring
    old replaced by new. If the optional argument count is given, only the first count
    occurrences are replaced.
    This function also checks the casing of the words it is replacing, and attempts to maintain
    the same casing the word had before.
    """
    idx = 0
    num = 0
    while idx < len(text):
        index_l = text.lower().find(old.lower(), idx)
        if index_l == -1:
            return text

        to_replace = text[index_l:index_l + len(old)]
        if to_replace.isupper():
            text = text[:index_l] + "\x02" + new.upper() + "\x02" + text[index_l + len(old):]
        elif to_replace.islower():
            text = text[:index_l] + "\x02" + new.lower() + "\x02" + text[index_l + len(old):]
        elif to_replace[0].isupper():
            text = text[:index_l] + "\x02" + new.capitalize() + "\x02" + text[index_l + len(old):]
        else:
            text = text[:index_l] + "\x02" + new + "\x02" + text[index_l + len(old):]

        idx = index_l + len(old)
        num += 1
        if count and num >= count:
            break
    return text


@hook.regex(correction_re)
def correction(match, conn, chan, message):
    """
    :type match: re.__Match
    :type conn: cloudbot.client.Client
    :type chan: str
    """
    groups = [b.replace("\/", "/") for b in re.split(r"(?<!\\)/", match.groups()[0])]
    find = groups[0]
    replace = groups[1]

    for item in conn.history[chan].__reversed__():
        nick, timestamp, msg = item
        if correction_re.match(msg):
            # don't correct corrections, it gets really confusing
            continue

        if find.lower() in msg.lower():
            if "\x01ACTION" in msg:
                msg = msg.replace("\x01ACTION", "").replace("\x01", "")
                mod_msg = ireplace(msg, find, replace)
                message("Correction, * {} {}".format(nick, mod_msg))
            else:
                mod_msg = ireplace(msg, find, replace)
                message("Correction, <{}> {}".format(nick, mod_msg))

            # append to end of history
            msg = ireplace(msg, find, replace)
            conn.history[chan].append((nick, timestamp, msg))
            return
        else:
            continue
