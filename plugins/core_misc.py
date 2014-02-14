import socket
import time
import re

from util import hook


socket.setdefaulttimeout(10)

nick_re = re.compile(":(.+?)!")


# Auto-join on Invite (Configurable, defaults to True)
@hook.event('INVITE')
def invite(paraml, conn=None):
    invite_join = conn.conf.get('invite_join', True)
    if invite_join:
        conn.join(paraml[-1])


# Identify to NickServ (or other service)
@hook.event('004')
def onjoin(paraml, conn=None, bot=None):
    nickserv_password = conn.conf.get('nickserv_password', '')
    nickserv_name = conn.conf.get('nickserv_name', 'nickserv')
    nickserv_account_name = conn.conf.get('nickserv_user', '')
    nickserv_command = conn.conf.get('nickserv_command', 'IDENTIFY')
    if nickserv_password:
        if nickserv_password in bot.config['censored_strings']:
            bot.config['censored_strings'].remove(nickserv_password)
        if nickserv_account_name:
            conn.msg(nickserv_name, "{} {} {}".format(nickserv_command, nickserv_account_name, nickserv_password))
        else:
            conn.msg(nickserv_name, "{} {}".format(nickserv_command, nickserv_password))
        bot.config['censored_strings'].append(nickserv_password)
        time.sleep(1)

# Set bot modes
    mode = conn.conf.get('mode')
    if mode:
        conn.cmd('MODE', [conn.nick, mode])

# Join config-defined channels
    for channel in conn.channels:
        conn.join(channel)
        time.sleep(1)

    print "Bot ready."


@hook.event("KICK")
def onkick(paraml, conn=None, chan=None):
    # if the bot has been kicked, remove from the channel list
    if paraml[1] == conn.nick:
        conn.channels.remove(chan)
        auto_rejoin = conn.conf.get('auto_rejoin', False)
        if auto_rejoin:
            conn.join(paraml[0])


@hook.event("NICK")
def onnick(paraml, conn=None, raw=None):
    old_nick = nick_re.search(raw).group(1)
    new_nick = str(paraml[0])
    if old_nick == conn.nick:
        conn.nick = new_nick
        print "Bot nick changed from '{}' to '{}'.".format(old_nick, new_nick)


@hook.singlethread
@hook.event('004')
def keep_alive(paraml, conn=None):
    keepalive = conn.conf.get('keep_alive', False)
    if keepalive:
        while True:
            conn.cmd('PING', [conn.nick])
            time.sleep(60)
