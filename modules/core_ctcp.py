import time

from cloudbot import hook


# CTCP responses
@hook.regex(r'^\x01VERSION\x01$')
def ctcp_version(notice):
    notice('\x01VERSION: CloudBot - http://git.io/cloudbotirc')


@hook.regex(r'^\x01PING\x01$')
def ctcp_ping(notice):
    notice('\x01PING: PONG')


@hook.regex(r'^\x01TIME\x01$')
def ctcp_time(notice):
    notice('\x01TIME: The time is: {}'.format(time.strftime("%r", time.localtime())))
