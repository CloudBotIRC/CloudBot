import re
from cloudbot import hook
from cloudbot.event import EventType

OPT_IN = ["#yelling"]
YELL_RE= re.compile('[^a-zA-Z]')

@hook.event([EventType.message, EventType.action])
def YELL_CHECK(event, conn):
    """THIS IS A CUSTOM PLUGIN FOR #YELLING TO MAKE SURE PEOPLE FOLLOW THE RULES."""
    if event.chan not in OPT_IN:
        return
    TESTY = YELL_RE.sub('', event.content)
    CAPS_COUNT = sum(1 for c in TESTY if c.isupper())
    if CAPS_COUNT/len(TESTY) < .75:
        KICK_THEM = "KICK {} {} :USE MOAR CAPS YOU TROGLODYTE!".format(event.chan, event.nick)
        conn.send(KICK_THEM)
