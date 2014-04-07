#!/usr/bin/env python3
import os
import sys
import time
import signal

from core import bot


# check python version 
if sys.version_info < (3, 2, 0):
    print("CloudBot3 requires Python 3.2 or newer.")
    sys.exit(1)

# set up environment
os.chdir(sys.path[0] or '.')  # do stuff relative to the install directory

# this is not the code you are looking for
if os.path.exists(os.path.abspath('lib')):
    sys.path += ['lib']

print('CloudBot3 <http://git.io/cloudbotirc>')


class CloudBotWrapper():
    def __init__(self):
        # create the master cloudbot
        self.cloudbot = bot.CloudBot()

        self.original_sigint = None

    def set_signals(self):
        # store the original SIGINT handler
        self.original_sigint = signal.getsignal(signal.SIGINT)
        signal.signal(signal.SIGINT, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        # this doesn't really work at all
        self.cloudbot.stop()

        # restore the original handler so if they do it again it triggers
        signal.signal(signal.SIGINT, self.original_sigint)

    def run(self):
        # start the bot master
        self.cloudbot.start()

        # watch to see if the bot stops running or needs a restart
        while True:
            if self.cloudbot.running:
                time.sleep(.1)
            else:
                if self.cloudbot.do_restart:
                    # create a new bot thread and start it
                    del self.cloudbot
                    print("Restarting")
                    time.sleep(1)  # sleep one second for timeouts
                    self.cloudbot = bot.CloudBot()
                    self.cloudbot.start()
                    continue
                else:
                    break


if __name__ == "__main__":
    main_wrapper = CloudBotWrapper()
    main_wrapper.set_signals()
    main_wrapper.run()
