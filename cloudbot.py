#!/usr/bin/env python3
import os
import sys
import time
import signal

from core import bot

if sys.version_info < (3, 2, 0):
    # check python version
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

        self.stopped_while_restarting = False

    def set_signals(self):
        # store the original SIGINT handler
        self.original_sigint = signal.getsignal(signal.SIGINT)
        signal.signal(signal.SIGINT, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        if not self.cloudbot:
            # we are currently in the process of restarting
            self.stopped_while_restarting = True
        else:
            self.cloudbot.stop()

        # restore the original handler so if they do it again it triggers
        signal.signal(signal.SIGINT, self.original_sigint)

    def run(self):
        while True:

            # start the bot master

            self.cloudbot.start_bot()

            if self.cloudbot.do_restart:
                # create a new bot thread and start it
                self.cloudbot = None
                print("Restarting")
                time.sleep(1)  # sleep one second for timeouts
                if self.stopped_while_restarting:
                    print("Recieved stop signal, no longer restarting")
                    return
                self.cloudbot = bot.CloudBot()
                continue
            else:
                # if it isn't restarting, exit the program
                break


if __name__ == "__main__":
    main_wrapper = CloudBotWrapper()
    main_wrapper.set_signals()
    main_wrapper.run()
