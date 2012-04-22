# Plugin by neersighted
import time
import getpass
from util import hook


# CTCP responses
@hook.regex(r'^\x01VERSION\x01$')
def ctcp_version(inp, notice=None):
    notice('\x01VERSION: CloudBot - http://git.io/cloudbotirc')


@hook.regex(r'^\x01PING\x01$')
def ctcp_ping(inp, notice=None):
    notice('\x01PING: PONG')


@hook.regex(r'^\x01TIME\x01$')
def ctcp_time(inp, notice=None):
    notice('\x01TIME: The time is: %s' % time.strftime("%r", time.localtime()))


@hook.regex(r'^\x01FINGER\x01$')
def ctcp_finger(inp, notice=None):
    notice('\x01FINGER: Username is: $s' % getpass.getuser())
