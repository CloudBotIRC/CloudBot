"""
log.py: written by Scaevolus 2009
"""

import os
import codecs
import time
import re

from util import hook


log_fds = {}  # '%(net)s %(chan)s': (filename, fd)

timestamp_format = '%H:%M:%S'

formats = {
    'PRIVMSG': '<%(nick)s> %(msg)s',
    'PART': '-!- %(nick)s [%(user)s@%(host)s] has left %(chan)s',
    'JOIN': '-!- %(nick)s [%(user)s@%(host)s] has joined %(param0)s',
    'MODE': '-!- mode/%(chan)s [%(param_tail)s] by %(nick)s',
    'KICK': '-!- %(param1)s was kicked from %(chan)s by %(nick)s [%(msg)s]',
    'TOPIC': '-!- %(nick)s changed the topic of %(chan)s to: %(msg)s',
    'QUIT': '-!- %(nick)s has quit [%(msg)s]',
    'PING': '',
    'NOTICE': '-%(nick)s- %(msg)s'
}

ctcp_formats = {
'ACTION': '* %(nick)s %(ctcpmsg)s'
'VERSION': '%(nick)s has requested CTCP %(ctcpcmd)s from %(chan)s: %(ctcpmsg)s'
'PING': '%(nick)s has requested CTCP %(ctcpcmd)s from %(chan)s: %(ctcpmsg)s'
'TIME': '%(nick)s has requested CTCP %(ctcpcmd)s from %(chan)s: %(ctcpmsg)s'
'FINGER': '%(nick)s has requested CTCP %(ctcpcmd)s from %(chan)s: %(ctcpmsg)s'
}

irc_color_re = re.compile(r'(\x03(\d+,\d+|\d)|[\x0f\x02\x16\x1f])')


def get_log_filename(dir, server, chan):
    return os.path.join(dir, 'log', gmtime('%Y'), server, chan,
            (gmtime('%%s.%m-%d.log') % chan).lower())


def gmtime(format):
    return time.strftime(format, time.gmtime())


def beautify(input):
    format = formats.get(input.command, '%(raw)s')
    args = dict(input)

    leng = len(args['paraml'])
    for n, p in enumerate(args['paraml']):
        args['param' + str(n)] = p
        args['param_' + str(abs(n - leng))] = p

    args['param_tail'] = ' '.join(args['paraml'][1:])
    args['msg'] = irc_color_re.sub('', args['msg'])

    if input.command == 'PRIVMSG' and input.msg.count('\x01') >= 2:
        ctcp = input.msg.split('\x01', 2)[1].split(' ', 1)
        if len(ctcp) == 1:
            ctcp += ['']
        args['ctcpcmd'], args['ctcpmsg'] = ctcp
        format = ctcp_formats.get(args['ctcpcmd'],
                '%(nick)s [%(user)s@%(host)s] requested unknown CTCP '
                '%(ctcpcmd)s from %(chan)s: %(ctcpmsg)s')

    return format % args


def get_log_fd(dir, server, chan):
    fn = get_log_filename(dir, server, chan)
    cache_key = '%s %s' % (server, chan)
    filename, fd = log_fds.get(cache_key, ('', 0))

    if fn != filename:  # we need to open a file for writing
        if fd != 0:     # is a valid fd
            fd.flush()
            fd.close()
        dir = os.path.split(fn)[0]
        if not os.path.exists(dir):
            os.makedirs(dir)
        fd = codecs.open(fn, 'a', 'utf-8')
        log_fds[cache_key] = (fn, fd)

    return fd


@hook.singlethread
@hook.event('*')
def log(paraml, input=None, bot=None):
    timestamp = gmtime(timestamp_format)

    fd = get_log_fd(bot.persist_dir, input.server, 'raw')
    fd.write(timestamp + ' ' + input.raw + '\n')

    if input.command == 'QUIT':  # these are temporary fixes until proper
        input.chan = 'quit'      # presence tracking is implemented
    if input.command == 'NICK':
        input.chan = 'nick'

    beau = beautify(input)

    if beau == '':  # don't log this
        return

    if input.chan:
        fd = get_log_fd(bot.persist_dir, input.server, input.chan)
        fd.write(timestamp + ' ' + beau + '\n')

    print timestamp, input.chan, beau.encode('utf8', 'ignore')
