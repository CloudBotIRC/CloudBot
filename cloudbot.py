#!/usr/bin/env python
# we import bot as _bot for now, for legacy reasons
from core import bot as _bot

import os
import Queue
import sys
import re
import time

sys.path += ['plugins', 'lib', 'core']  # add stuff to the sys.path for easy imports
os.chdir(sys.path[0] or '.')  # do stuff relative to the install directory

print 'CloudBot DEV <http://git.io/cloudbotirc>'

# create new bot object
bot = _bot.Bot("cloudbot")
bot.logger.debug("Bot initalized.")

# bootstrap the reloader
eval(compile(open(os.path.join('core', 'reload.py'), 'U').read(),
             os.path.join('core', 'reload.py'), 'exec'))
reload(init=True)


bot.persist_dir = os.path.abspath('persist')
if not os.path.exists(bot.persist_dir):
    os.mkdir(bot.persist_dir)

print 'Connection(s) made, starting main loop.'

while True:
    reload()  # these functions only do things
      # if changes have occured

    for connection in bot.connections.itervalues():
        try:
            out = connection.out.get_nowait()
            main(connection, out)
        except Queue.Empty:
            pass
    while all(connection.out.empty() for connection in bot.connections.itervalues()):
        time.sleep(.1)
