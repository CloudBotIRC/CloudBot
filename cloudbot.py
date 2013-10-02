#!/usr/bin/env python
from core import bot

import os
import sys
import signal

# set up enviroment
os.chdir(sys.path[0] or '.')  # do stuff relative to the install directory

print 'CloudBot REFRESH <http://git.io/cloudbotirc>'

def exit_gracefully(signum, frame):
    cloudbot.stop()

# store the original SIGINT handler
original_sigint = signal.getsignal(signal.SIGINT)
signal.signal(signal.SIGINT, exit_gracefully)

# create new bot object
cloudbot = bot.Bot()
cloudbot.logger.debug("Bot initalized, starting main loop.")

while cloudbot.running:
    cloudbot.loop()

cloudbot.logger.debug("Stopped main loop.")
