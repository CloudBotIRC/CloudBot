import re
from cloudbot import hook
from cloudbot.event import EventType

OPT_IN = ["#yelling"]
YELL_RE = re.compile('[^a-zA-Z]')
URL_RE = re.compile('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+~]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')

@hook.event([EventType.message, EventType.action])
def YELL_CHECK(event, conn):
    """THIS IS A CUSTOM PLUGIN FOR #YELLING TO MAKE SURE PEOPLE FOLLOW THE RULES."""
    if event.chan not in OPT_IN:
        return
    TESTY = URL_RE.sub('', event.content)
    TESTY = YELL_RE.sub('', TESTY)
    CAPS_COUNT = sum(1 for c in TESTY if c.isupper())
    if CAPS_COUNT/len(TESTY) < .75:
        KICK_THEM = "KICK {} {} :USE MOAR CAPS YOU TROGLODYTE!".format(event.chan, event.nick)
        conn.send(KICK_THEM)
