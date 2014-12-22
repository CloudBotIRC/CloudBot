import asyncio
import time

from cloudbot import hook
import cloudbot


@asyncio.coroutine
@hook.regex(r'^\x01VERSION\x01$')
def ctcp_version(notice):
    notice("\x01VERSION: Obr v{}".format(cloudbot.__version__))


@asyncio.coroutine
@hook.regex(r'^\x01PING\x01$')
def ctcp_ping(notice):
    notice('\x01PING: PONG')


@asyncio.coroutine
@hook.regex(r'^\x01TIME\x01$')
def ctcp_time(notice):
    notice('\x01TIME: The time is: {}'.format(time.strftime("%r", time.localtime())))
