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
        mode = "mode {}".format(irc_paramlist[-1])
        conn.send(mode)
        conn.join(irc_paramlist[-1])

@hook.irc_raw('324')
def check_mode(irc_paramlist, conn, message):
    #message(", ".join(irc_paramlist), "bloodygonzo")
    mode = irc_paramlist[2]
    require_reg = conn.config.get('require_registered_channels', False)
    if not "r" in mode and conn.name == "snoonet" and require_reg:
        message("I do not stay in unregistered channels", irc_paramlist[1])
        out = "PART {}".format(irc_paramlist[1])
        conn.send(out)
        

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

    # Should we oper up?
    oper_pw = conn.config.get('oper_pw', False)
    oper_user = conn.config.get('oper_user', False)
    if oper_pw and oper_user:
        out = "oper {} {}".format(oper_user, oper_pw)
        conn.send(out)

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
        if conn.name == "snoonet":
            mode = "mode {}".format(channel)
            conn.send(mode)

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
