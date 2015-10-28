import asyncio
from cloudbot import hook
from cloudbot.bot import CloudBot
from cloudbot.clients.irc import IrcClient
from cloudbot.event import Event


@asyncio.coroutine
@hook.irc_raw('004')
def on_connect(bot, conn):
    """
    :type bot: CloudBot
    :type conn: IrcClient
    """
    m = conn.memory
    if 'CAP_lock' not in m:
        m['CAP_lock'] = asyncio.Lock()
    if 'CAP_negotiated' not in m:
        m['CAP_negotiated'] = asyncio.Event()

    if not conn.capabilities:
        return

    while not conn.ready:
        yield from asyncio.sleep(3)

    with (yield from m['CAP_lock']):
        m['CAP_LS_future'] = asyncio.Future()
        conn.send('CAP LS')
        server_accepts = yield from m['CAP_LS_future']

        m['CAP_LIST_future'] = asyncio.Future()
        conn.send('CAP LIST')
        we_have = yield from m['CAP_LIST_future']

        we_want = conn.capabilities

        rejected = we_want - we_have - server_accepts
        if rejected:
            bot.logger.warning('[{}|CAP] Server rejected: {}'.format(conn.name, rejected))

        missing = (we_want - we_have) & server_accepts
        conn.send('CAP REQ :{}'.format(' '.join(missing)))

        m['CAP_ACK_future'] = asyncio.Future()
        accepted = yield from m['CAP_ACK_future']
        if accepted is None:
            bot.logger.warning('[{}|CAP] Failed to negotiate with the server')

        if accepted:
            bot.logger.info('[{}|CAP] Successfully negotiated for: {}'.format(conn.name, accepted))

        conn.send('CAP END')
        m['CAP_negotiated'].set()


@asyncio.coroutine
@hook.irc_raw('CAP')
def on_cap(conn, event):
    """
    :type conn: Client | IrcClient
    :type event: Event
    """

    type = event.irc_paramlist[1].upper()
    if type == 'LS':
        caps = set(event.irc_paramlist[2][1:].split())
        future = conn.memory.get('CAP_LS_future')
        if future and not future.done():
            future.set_result(caps)
    elif type == 'LIST':
        caps = set(event.irc_paramlist[2][1:].split())
        future = conn.memory.get('CAP_LIST_future')
        if future and not future.done():
            future.set_result(caps)
    elif type == 'ACK':
        caps = set(event.irc_paramlist[2][1:].split())
        future = conn.memory.get('CAP_ACK_future')
        if future and not future.done():
            future.set_result(caps)
    elif type == 'NAK':
        future = conn.memory.get('CAP_ACK_future')
        if future and not future.done():
            future.set_result(None)
