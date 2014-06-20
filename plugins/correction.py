import asyncio
import re

from cloudbot import hook

correction_re = re.compile(r"^[sS]/([^/]*)/([^/]*)(/.*)?\s*$")


@asyncio.coroutine
@hook.regex(correction_re)
def correction(match, conn, chan, message):
    """
    :type match: re.__Match
    :type conn: cloudbot.client.Client
    :type chan: str
    """
    print(match.groups())
    to_find, replacement, find_nick = match.groups()
    if find_nick:
        find_nick = find_nick[1:].lower()  # Remove the '/'

    find_re = re.compile("(?i){}".format(re.escape(to_find)))

    for item in conn.history[chan].__reversed__():
        nick, timestamp, msg = item
        if correction_re.match(msg):
            # don't correct corrections, it gets really confusing
            continue
        if find_nick:
            if find_nick != nick.lower():
                continue
        if find_re.search(msg):
            if "\x01ACTION" in msg:
                msg = msg.replace("\x01ACTION ", "/me ").replace("\x01", "")
            message("Correction, <{}> {}".format(nick, find_re.sub("\x02" + replacement + "\x02", msg)))
            return
        else:
            continue
    if find_nick:
        return "Did not find {} in any recent messages from {}.".format(to_find, find_nick)
    else:
        return "Did not find {} in any recent messages.".format(to_find)
