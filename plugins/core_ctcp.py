import asyncio
import time

from cloudbot import hook
from cloudbot.event import EventType
import cloudbot

# CTCP responses
@asyncio.coroutine
@hook.event([EventType.other])
def ctcp_version(notice, irc_ctcp_text):
    if irc_ctcp_text:
        if irc_ctcp_text.startswith("VERSION"):
            notice("\x01VERSION gonzobot a fork of Cloudbot {} - https://snoonet.org/gonzobot\x01".format(cloudbot.__version__))
        elif irc_ctcp_text.startswith("PING"):
            notice('\x01{}\x01'.format(irc_ctcp_text))  # Bot should return exactly what the user sends as the ping parameter
        elif irc_ctcp_text.startswith("TIME"):
           notice('\x01TIME {}\x01'.format(time.asctime()))  # General convention is to return the asc time
