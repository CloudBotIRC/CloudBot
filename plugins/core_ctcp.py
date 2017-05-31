import asyncio
import time

import cloudbot
from cloudbot import hook
from cloudbot.event import EventType


# CTCP responses
@asyncio.coroutine
<<<<<<< HEAD
@hook.regex(r'^\x01VERSION\x01$')
def ctcp_version(notice):
    notice("\x01VERSION: xsBot {} - https://github.com/xshotD/xsbot".format(cloudbot.__version__))
=======
@hook.event(EventType.other)
def ctcp_version(notice, irc_ctcp_text):
    if irc_ctcp_text is not None and irc_ctcp_text.lower().strip() == "version":
        notice("\x01VERSION: CloudBot {} - https://git.io/CloudBot".format(cloudbot.__version__))
>>>>>>> db7efe8da7a5881ad8c0feefe92f2795dc557092


@asyncio.coroutine
@hook.event(EventType.other)
def ctcp_ping(notice, irc_ctcp_text):
    if irc_ctcp_text is not None and irc_ctcp_text.lower().strip() == "ping":
        notice('\x01PING: PONG')


@asyncio.coroutine
<<<<<<< HEAD
@hook.regex(r'^\x01TIME\x01$')
def ctcp_time(notice):
    notice('\x01TIME: According to my sources, the time is: {}'.format(time.strftime("%r", time.localtime())))
=======
@hook.event(EventType.other)
def ctcp_time(notice, irc_ctcp_text):
    if irc_ctcp_text is not None and irc_ctcp_text.lower().strip() == "time":
        notice('\x01TIME: The time is: {}'.format(time.strftime("%r", time.localtime())))
>>>>>>> db7efe8da7a5881ad8c0feefe92f2795dc557092
