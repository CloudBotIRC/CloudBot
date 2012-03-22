import thread
import traceback


thread.stack_size(1024 * 512)  # reduce vm size


class Input(dict):
    def __init__(self, conn, raw, prefix, command, params,
                    nick, user, host, mask, paraml, msg):

        chan = paraml[0].lower()
        if chan == conn.nick.lower():  # is a PM
            chan = nick

        def say(msg):
            conn.msg(chan, msg)

        def pm(msg):
            conn.msg(nick, msg)

        def reply(msg):
            if chan == nick:  # PMs don't need prefixes
                conn.msg(chan, msg)
            else:
                conn.msg(chan, '(' + nick + ') ' + msg)

        def set_nick(nick):
            conn.set_nick(nick)

        def me(msg):
            conn.msg(chan, "\x01%s %s\x01" % ("ACTION", msg))

        def notice(msg):
            conn.cmd('NOTICE', [nick, msg])

        dict.__init__(self, conn=conn, raw=raw, prefix=prefix, command=command,
                    params=params, nick=nick, user=user, host=host, mask=mask,
                    paraml=paraml, msg=msg, server=conn.server, chan=chan,
                    notice=notice, say=say, reply=reply, pm=pm, bot=bot,
                    me=me, set_nick=set_nick, lastparam=paraml[-1])

    # make dict keys accessible as attributes
    def __getattr__(self, key):
        return self[key]

    def __setattr__(self, key, value):
        self[key] = value


def run(func, input):
    args = func._args

    if 'inp' not in input:
        input.inp = input.paraml

    if args:
        if 'db' in args and 'db' not in input:
            input.db = get_db_connection(input.conn)
        if 'input' in args:
            input.input = input
        if 0 in args:
            out = func(input.inp, **input)
        else:
            kw = dict((key, input[key]) for key in args if key in input)
            out = func(input.inp, **kw)
    else:
        out = func(input.inp)
    if out is not None:
        input.reply(unicode(out))


def do_sieve(sieve, bot, input, func, type, args):
    try:
        return sieve(bot, input, func, type, args)
    except Exception:
        print 'sieve error',
        traceback.print_exc()
        return None


class Handler(object):
    '''Runs plugins in their own threads (ensures order)'''
    def __init__(self, func):
        self.func = func
        self.input_queue = Queue.Queue()
        thread.start_new_thread(self.start, ())

    def start(self):
        uses_db = 'db' in self.func._args
        db_conns = {}
        while True:
            input = self.input_queue.get()

            if input == StopIteration:
                break

            if uses_db:
                db = db_conns.get(input.conn)
                if db is None:
                    db = bot.get_db_connection(input.conn)
                    db_conns[input.conn] = db
                input.db = db

            run(self.func, input)

    def stop(self):
        self.input_queue.put(StopIteration)

    def put(self, value):
        self.input_queue.put(value)


def dispatch(input, kind, func, args, autohelp=False):
    for sieve, in bot.plugs['sieve']:
        input = do_sieve(sieve, bot, input, func, kind, args)
        if input == None:
            return

    if autohelp and args.get('autohelp', True) and not input.inp \
      and func.__doc__ is not None:
        input.notice(func.__doc__)
        return

    if func._thread:
        bot.threads[func].put(input)
    else:
        thread.start_new_thread(run, (func, input))


def match_command(command):
    commands = list(bot.commands)

    # do some fuzzy matching
    prefix = filter(lambda x: x.startswith(command), commands)
    if len(prefix) == 1:
        return prefix[0]
    elif prefix and command not in prefix:
        return prefix

    return command


def main(conn, out):
    inp = Input(conn, *out)
    commandprefix = conn.conf.get('command_prefix')

    # EVENTS
    for func, args in bot.events[inp.command] + bot.events['*']:
        dispatch(Input(conn, *out), "event", func, args)

    if inp.command == 'PRIVMSG':
        # COMMANDS
        if inp.chan == inp.nick:  # private message, no command prefix
            prefix = r'^(?:[' + commandprefix + ']?|'
        else:
            prefix = r'^(?:[' + commandprefix + ']|'

        command_re = prefix + inp.conn.nick
        command_re += r'[,;:]+\s+)(\w+)(?:$|\s+)(.*)'

        m = re.match(command_re, inp.lastparam)

        if m:
            trigger = m.group(1).lower()
            command = match_command(trigger)

            if isinstance(command, list):  # multiple potential matches
                input = Input(conn, *out)
                input.notice("Did you mean %s or %s?" %
                            (', '.join(command[:-1]), command[-1]))
            elif command in bot.commands:
                input = Input(conn, *out)
                input.trigger = trigger
                input.inp_unstripped = m.group(2)
                input.inp = input.inp_unstripped.strip()

                func, args = bot.commands[command]
                dispatch(input, "command", func, args, autohelp=True)

        # REGEXES
        for func, args in bot.plugs['regex']:
            m = args['re'].search(inp.lastparam)
            if m:
                input = Input(conn, *out)
                input.inp = m

                dispatch(input, "regex", func, args)
