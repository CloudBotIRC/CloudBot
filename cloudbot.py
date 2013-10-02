#!/usr/bin/env python
# we import bot as _bot for now, for legacy reasons
from core import bot as _bot
from core import loader, main

import os
import Queue
import sys
import time

# set up enviroment
os.chdir(sys.path[0] or '.')  # do stuff relative to the install directory

print 'CloudBot REFRESH <http://git.io/cloudbotirc>'

# create new bot object
bot = _bot.Bot("cloudbot")
bot.logger.debug("Bot initalized.")

bot.logger.debug("Starting main loop.")
while True:
    loader.reload(bot)  # these functions only do things

    for connection in bot.connections.itervalues():
        try:
            out = connection.out.get_nowait()
            main.main(bot, connection, out)
        except Queue.Empty:
            pass
    while all(connection.out.empty() for connection in bot.connections.itervalues()):
        time.sleep(.1)
