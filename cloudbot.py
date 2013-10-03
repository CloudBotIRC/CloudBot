#!/usr/bin/env python
from core import bot

import os
import sys
import signal

# check python version 
if sys.version_info < (2, 7, 0):
    print "CloudBot requires Python 2.7 or newer."
    sys.stderr.write(os.linesep)
    sys.exit(1)

# set up enviroment
os.chdir(sys.path[0] or '.')  # do stuff relative to the install directory

# this is not the code you are looking for
if os.path.exists(os.path.abspath('lib')):
    sys.path += ['lib'] 

print 'CloudBot2 <http://git.io/cloudbotirc>'

def exit_gracefully(signum, frame):
    cloudbot.stop()

# store the original SIGINT handler
original_sigint = signal.getsignal(signal.SIGINT)
signal.signal(signal.SIGINT, exit_gracefully)

# little restart loop
while True:
    # create new bot object
    cloudbot = bot.Bot()

    cloudbot.run()
    if cloudbot.do_restart:
        # this kills the bot
        # TODO: make it not just kill the bot
        sys.exit()
    else:
        sys.exit()
