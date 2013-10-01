#!/usr/bin/env python
# we import bot as _bot for now, for legacy reasons
from core import bot as _bot

import os
import Queue
import sys
import time

# set up enviroment
sys.path += ['plugins', 'lib']  # add stuff to the sys.path for easy imports
os.chdir(sys.path[0] or '.')  # do stuff relative to the install directory

print 'CloudBot REFRESH <http://git.io/cloudbotirc>'

# create new bot object
bot = _bot.Bot("cloudbot")
bot.logger.debug("Bot initalized.")

# bootstrap the reloader
bot.logger.debug("Bootstrapping reloader.")
eval(compile(open(os.path.join('core', 'reload.py'), 'U').read(),
             os.path.join('core', 'reload.py'), 'exec'))
reload(init=True)

bot.logger.debug("Starting main loop.")
while True:
    reload()  # these functions only do things

    for connection in bot.connections.itervalues():
        try:
            out = connection.out.get_nowait()
            main(connection, out)
        except Queue.Empty:
            pass
    while all(connection.out.empty() for connection in bot.connections.itervalues()):
        time.sleep(.1)
