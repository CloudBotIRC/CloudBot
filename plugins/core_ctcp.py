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
            notice("\x01VERSION: gonzobot a fork of Cloudbot {} - https://snoonet.org/gonzobot".format(cloudbot.__version__))
        elif irc_ctcp_text.startswith("PING"):
            notice('\x01PING: PONG')
        elif irc_ctcp_text.startswith("TIME"):
           notice('\x01TIME: The time is: {}'.format(time.strftime("%r", time.localtime())))
