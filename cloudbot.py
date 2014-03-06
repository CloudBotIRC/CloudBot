#!/usr/bin/env python
from core import bot

import os
import sys
import time
import signal

# check python version 
if sys.version_info < (3, 2, 0):
    print("CloudBot3 requires Python 3.2 or newer.")
    sys.exit(1)

# set up enviroment
os.chdir(sys.path[0] or '.')  # do stuff relative to the install directory

# this is not the code you are looking for
if os.path.exists(os.path.abspath('lib')):
    sys.path += ['lib'] 

print('CloudBot3 <http://git.io/cloudbotirc>')

def exit_gracefully(signum, frame):
    # this doesn't really work at all
    cloudbot.stop()

    # restore the original handler so if they do it again it triggers
    signal.signal(signal.SIGINT, original_sigint)

# store the original SIGINT handler
original_sigint = signal.getsignal(signal.SIGINT)
signal.signal(signal.SIGINT, exit_gracefully)

# create a bot thread and start it
cloudbot = bot.Bot()
cloudbot.start()

# watch to see if the bot stops running or needs a restart
while True:
    if cloudbot.running:
        time.sleep(.1)
    else:
        if cloudbot.do_restart:
            # create a new bot thread and start it
            # THIS DOES NOT WORK
            del cloudbot
            cloudbot = bot.Bot()
            cloudbot.start()
            continue
        else:
            break