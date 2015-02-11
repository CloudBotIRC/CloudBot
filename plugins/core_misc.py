import asyncio
import socket

from cloudbot import hook

socket.setdefaulttimeout(10)


# Auto-join on Invite (Configurable, defaults to True)
@asyncio.coroutine
@hook.irc_raw('INVITE')
def invite(irc_paramlist, conn):
    """
    :type irc_paramlist: list[str]
    :type conn: cloudbot.client.Client
    """
    invite_join = conn.config.get('invite_join', True)
    if invite_join:
        conn.join(irc_paramlist[-1])


# Identify to NickServ (or other service)
@asyncio.coroutine
@hook.irc_raw('004')
def onjoin(conn, bot):
    """
    :type conn: cloudbot.clients.clients.IrcClient
    :type bot: cloudbot.bot.CloudBot
    """
    bot.logger.info("[{}|misc] Bot is sending join commands for network.".format(conn.name))
    nickserv = conn.config.get('nickserv')
    if nickserv and nickserv.get("enabled", True):
        bot.logger.info("[{}|misc] Bot is authenticating with NickServ.".format(conn.name))
        nickserv_password = nickserv.get('nickserv_password', '')
        nickserv_name = nickserv.get('nickserv_name', 'nickserv')
        nickserv_account_name = nickserv.get('nickserv_user', '')
        nickserv_command = nickserv.get('nickserv_command', 'IDENTIFY')
        if nickserv_password:
            if "censored_strings" in bot.config and nickserv_password in bot.config['censored_strings']:
                bot.config['censored_strings'].remove(nickserv_password)
            if nickserv_account_name:
                conn.message(nickserv_name, "{} {} {}".format(nickserv_command,
                                                              nickserv_account_name, nickserv_password))
            else:
                conn.message(nickserv_name, "{} {}".format(nickserv_command, nickserv_password))
            if "censored_strings" in bot.config:
                bot.config['censored_strings'].append(nickserv_password)
            yield from asyncio.sleep(1)

    # Set bot modes
    mode = conn.config.get('mode')
    if mode:
        bot.logger.info("[{}|misc] Bot is setting mode on itself: {}".format(conn.name, mode))
        conn.cmd('MODE', conn.nick, mode)

    # Join config-defined channels
    bot.logger.info("[{}|misc] Bot is joining channels for network.".format(conn.name))
    for channel in conn.channels:
        conn.join(channel)
        yield from asyncio.sleep(0.4)

    conn.ready = True
    bot.logger.info("[{}|misc] Bot has finished sending join commands for network.".format(conn.name))


@asyncio.coroutine
@hook.irc_raw('004')
def keep_alive(conn):
    """
    :type conn: cloudbot.clients.clients.IrcClient
    """
    keepalive = conn.config.get('keep_alive', False)
    if keepalive:
        while True:
            conn.cmd('PING', conn.nick)
            yield from asyncio.sleep(60)
