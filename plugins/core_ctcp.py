import asyncio
import time

import cloudbot
from cloudbot import hook
from cloudbot.event import EventType


# CTCP responses
@asyncio.coroutine
@hook.event(EventType.other)
def ctcp_version(notice, irc_ctcp_text):
    if irc_ctcp_text is not None and irc_ctcp_text.lower().strip() == "version":
        notice("\x01VERSION: CloudBot {} - https://git.io/CloudBot".format(cloudbot.__version__))


@asyncio.coroutine
@hook.event(EventType.other)
def ctcp_ping(notice, irc_ctcp_text):
    if irc_ctcp_text is not None and irc_ctcp_text.lower().strip() == "ping":
        notice('\x01PING: PONG')


@asyncio.coroutine
@hook.event(EventType.other)
def ctcp_time(notice, irc_ctcp_text):
    if irc_ctcp_text is not None and irc_ctcp_text.lower().strip() == "time":
        notice('\x01TIME: The time is: {}'.format(time.strftime("%r", time.localtime())))
