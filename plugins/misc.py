import re
import socket
import subprocess
import time

from util import hook, http

socket.setdefaulttimeout(10)

@hook.event('KICK')
def rejoin(paraml, conn=None):
    autorejoin = conn.conf.get('autorejoin', False)
    if autorejoin:
        conn.join(paraml[0])
    else:
        return None

@hook.event('INVITE')
def invite(paraml, conn=None):
    conn.join(paraml[-1])

@hook.event('004')
def onjoin(paraml, conn=None, bot=None):
    nickserv_password = conn.conf.get('nickserv_password', '')
    nickserv_name = conn.conf.get('nickserv_name', 'nickserv')
    nickserv_command = conn.conf.get('nickserv_command', 'IDENTIFY %s')
    if nickserv_password:
        if nickserv_password in bot.config['censored_strings']:
	    bot.config['censored_strings'].remove(nickserv_password)
        conn.msg(nickserv_name, nickserv_command % nickserv_password)
        bot.config['censored_strings'].append(nickserv_password)
        time.sleep(1)
    mode = conn.conf.get('mode')

    if mode:
        conn.cmd('MODE', [conn.nick, mode])

    for channel in conn.channels:
        conn.join(channel)
        time.sleep(1) 

    http.ua_skybot = 'CloudBot - http://git.io/cloudbot'

    stayalive = conn.conf.get('stayalive')
    if stayalive:
        while True:
            time.sleep(conn.conf.get('stayalive_delay', 20))
            conn.cmd('PING', [conn.nick])

@hook.regex(r'^\x01VERSION\x01$')
def ctcpversion(inp, notice=None):
    notice('\x01VERSION: CloudBot - http://git.io/cloudbot')

@hook.regex(r'^\x01PING\x01$')
def ctcpping(inp, notice=None):
    notice('\x01PING: PONG')

@hook.regex(r'^\x01TIME\x01$')
def ctcptime(inp, notice=None):
    notice('\x01TIME: GET A WATCH')

@hook.regex(r'^\x01FINGER\x01$')
def ctcpfinger(inp, notice=None):
    notice('\x01FINGER: WHERE ARE YOU PUTTING THAT')

