import re

from util import hook


CORRECTION_RE = r'^[sS]/.*/.*/?\S*$'


@hook.regex(CORRECTION_RE)
def correction(match, input=None, conn=None, message=None):
    """
    :type match: re.__Match
    :type input: core.main.Input
    :type conn: core.irc.BotConnection
    """
    split = input.msg.split("/")

    if len(split) == 4:
        nick = split[3].lower()
    else:
        nick = None

    find = split[1]
    find_re = re.compile("(?i){}".format(re.escape(find)))
    replace = split[2]

    for item in conn.history[input.chan].__reversed__():
        name, timestamp, msg = item
        if msg.startswith("s/"):
            # don't correct corrections, it gets really confusing
            continue
        if nick:
            if nick != name.lower():
                continue
        if find_re.search(msg):
            if "\x01ACTION" in msg:
                msg = msg.replace("\x01ACTION ", "/me ").replace("\x01", "")
            message("Correction, <{}> {}".format(name, find_re.sub("\x02" + replace + "\x02", msg)))
            return
        else:
            continue

    return "Did not find {} in any recent messages.".format(find)
