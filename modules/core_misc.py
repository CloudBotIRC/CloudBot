import socket
import time

from util import hook

socket.setdefaulttimeout(10)


# Auto-join on Invite (Configurable, defaults to True)
@hook.event('INVITE')
def invite(paramlist, conn):
    """
    :type paramlist: list[str]
    :type conn: core.irc.BotConnection
    """
    invite_join = conn.config.get('invite_join', True)
    if invite_join:
        conn.join(paramlist[-1])


# Identify to NickServ (or other service)
@hook.event('004')
def onjoin(conn, bot):
    """
    :type conn: core.irc.BotConnection
    :type bot: core.bot.CloudBot
    """
    bot.logger.info("ONJOIN hook triggered.")
    nickserv = conn.config.get('nickserv')
    if nickserv and nickserv.get("enabled", True):
        nickserv_password = nickserv.get('nickserv_password', '')
        nickserv_name = nickserv.get('nickserv_name', 'nickserv')
        nickserv_account_name = nickserv.get('nickserv_user', '')
        nickserv_command = nickserv.get('nickserv_command', 'IDENTIFY')
        if nickserv_password:
            if "censored_strings" in bot.config and nickserv_password in bot.config['censored_strings']:
                bot.config['censored_strings'].remove(nickserv_password)
            if nickserv_account_name:
                conn.msg(nickserv_name, "{} {} {}".format(nickserv_command, nickserv_account_name, nickserv_password))
            else:
                conn.msg(nickserv_name, "{} {}".format(nickserv_command, nickserv_password))
            if "censored_strings" in bot.config:
                bot.config['censored_strings'].append(nickserv_password)
            time.sleep(1)

    # Set bot modes
    mode = conn.config.get('mode')
    if mode:
        bot.logger.info('Setting bot mode: "{}"'.format(mode))
        conn.cmd('MODE', [conn.nick, mode])

    # Join config-defined channels
    bot.logger.info('Joining channels.')
    for channel in conn.channels:
        conn.join(channel)
        time.sleep(1)

    bot.logger.info("ONJOIN hook completed. Bot ready.")


@hook.event('004', singlethread=True)
def keep_alive(conn):
    """
    :type conn: core.irc.BotConnection
    """
    keepalive = conn.config.get('keep_alive', False)
    if keepalive:
        while True:
            conn.cmd('PING', [conn.nick])
            time.sleep(60)
