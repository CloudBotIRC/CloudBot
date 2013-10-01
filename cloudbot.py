#!/usr/bin/env python

import os
import Queue
import sys
import time
import re

sys.path += ['plugins', 'lib']  # add stuff to the sys.path for easy imports
os.chdir(sys.path[0] or '.')  # do stuff relative to the install directory


class Bot(object):
    pass

print 'CloudBot DEV <http://git.io/cloudbotirc>'

# create new bot object
bot = Bot()
bot.vars = {}

# record start time for the uptime command
bot.start_time = time.time()

print 'Begin Plugin Loading.'

# bootstrap the reloader
eval(compile(open(os.path.join('core', 'reload.py'), 'U').read(),
             os.path.join('core', 'reload.py'), 'exec'))
reload(init=True)

config()
if not hasattr(bot, 'config'):
    exit()

print 'Connecting to IRC...'

bot.conns = {}

try:
    for name, conf in bot.config['connections'].iteritems():
        # strip all spaces and capitalization from the connection name
        name = name.replace(" ", "_")
        name = re.sub('[^A-Za-z0-9_]+', '', name)
        print 'Connecting to server: %s' % conf['server']
        if conf.get('ssl'):
            bot.conns[name] = SSLIRC(name, conf['server'], conf['nick'], conf=conf,
                                     port=conf.get('port', 6667), channels=conf['channels'],
                                     ignore_certificate_errors=conf.get('ignore_cert', True))
        else:
            bot.conns[name] = IRC(name, conf['server'], conf['nick'], conf=conf,
                                  port=conf.get('port', 6667), channels=conf['channels'])
except Exception as e:
    print 'ERROR: malformed config file', e
    sys.exit()

bot.persist_dir = os.path.abspath('persist')
if not os.path.exists(bot.persist_dir):
    os.mkdir(bot.persist_dir)

print 'Connection(s) made, starting main loop.'

while True:
    reload()  # these functions only do things
    config()  # if changes have occured

    for conn in bot.conns.itervalues():
        try:
            out = conn.out.get_nowait()
            main(conn, out)
        except Queue.Empty:
            pass
    while all(conn.out.empty() for conn in bot.conns.itervalues()):
        time.sleep(.1)
