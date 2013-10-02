#!/usr/bin/env python
# we import bot as _bot for now, for legacy reasons
from core import bot as _bot

import os
import sys
import signal

# set up enviroment
os.chdir(sys.path[0] or '.')  # do stuff relative to the install directory

print 'CloudBot REFRESH <http://git.io/cloudbotirc>'

def exit_gracefully(signum, frame):
    bot.stop()

# store the original SIGINT handler
original_sigint = signal.getsignal(signal.SIGINT)
signal.signal(signal.SIGINT, exit_gracefully)

# create new bot object
bot = _bot.Bot("cloudbot")
bot.logger.debug("Bot initalized, starting main loop.")

while bot.running:
    bot.loop()

bot.logger.debug("Stopped main loop.")
