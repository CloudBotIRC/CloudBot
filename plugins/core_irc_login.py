import asyncio
import logging

from cloudbot import hook

logger = logging.getLogger('cloudbot')

# Identify to NickServ (or other service)
@asyncio.coroutine
@hook.irc_raw('004')
def onjoin(conn):
    """
    :type conn: cloudbot.clients.irc.IrcClient
    """
    nickserv = conn.config.get('nickserv')
    if nickserv and nickserv.get('enabled', True):
        nickserv_password = nickserv.get('nickserv_password', '')
        nickserv_name = nickserv.get('nickserv_name', 'nickserv')
        nickserv_account_name = nickserv.get('nickserv_user', '')
        nickserv_command = nickserv.get('nickserv_command', 'IDENTIFY')
        if nickserv_password:
            if nickserv_account_name:
                conn.message(nickserv_name,
                             "{} {} {}".format(nickserv_command, nickserv_account_name, nickserv_password),
                             log_hide=nickserv_password)
            else:
                conn.message(nickserv_name, "{} {}".format(nickserv_command, nickserv_password),
                             log_hide=nickserv_password)
            yield from asyncio.sleep(1)

    # Set bot modes
    mode = conn.config.get('mode')
    if mode:
        logger.info("Setting bot mode: '{}'".format(mode))
        conn.cmd('MODE', conn.nick, mode)

    # Join config-defined channels
    logger.info("Joining channels.")
    for channel in conn.channels:
        conn.join(channel)
        yield from asyncio.sleep(1)

    logger.info("Startup complete. Bot ready.")


@asyncio.coroutine
@hook.irc_raw('004')
def keep_alive(conn):
    """
    :type conn: cloudbot.clients.irc.IrcClient
    """

    if not conn.config.get('keep_alive', False):
        return

    while True:
        conn.cmd('PING', conn.nick)
        yield from asyncio.sleep(60)
