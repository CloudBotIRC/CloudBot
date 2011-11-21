import re
import socket
import subprocess
import time

from util import hook, http

socket.setdefaulttimeout(10)  # global setting


#autorejoin channels
#@hook.event('KICK')
#def rejoin(paraml, conn=None):
#    if paraml[1] == conn.nick:
#        if paraml[0].lower() in conn.channels:
#            conn.join(paraml[0])


#join channels when invited
@hook.event('INVITE')
def invite(paraml, conn=None):
    conn.join(paraml[-1])


@hook.event('004')
def onjoin(paraml, conn=None, bot=None):
    # identify to services
    nickserv_password = conn.conf.get('nickserv_password', '')
    nickserv_name = conn.conf.get('nickserv_name', 'nickserv')
    nickserv_command = conn.conf.get('nickserv_command', 'IDENTIFY %s')
    if nickserv_password:
        if nickserv_password in bot.config['censored_strings']:
	    bot.config['censored_strings'].remove(nickserv_password)
        conn.msg(nickserv_name, nickserv_command % nickserv_password)
        bot.config['censored_strings'].append(nickserv_password)
        time.sleep(1)

    # set mode on self
    mode = conn.conf.get('mode')
    if mode:
        conn.cmd('MODE', [conn.nick, mode])

    # join channels
    for channel in conn.channels:
        conn.join(channel)
        time.sleep(1)  # don't flood JOINs

    # set user-agent

    http.ua_skybot = 'CloudBot'


@hook.regex(r'^\x01VERSION\x01$')
def version(inp, notice=None):
    notice('\x01VERSION CloudBot/DEV - https://github.com/lukeroge/CloudBot')
