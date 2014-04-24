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


def main():
    cloudbot = bot.CloudBot()

    # whether we are killed while restarting
    stopped_while_restarting = False

    # store the original SIGINT handler
    original_sigint = signal.getsignal(signal.SIGINT)

    # define closure for signal handling
    def exit_gracefully(signum, frame):
        nonlocal stopped_while_restarting
        if not cloudbot:
            # we are currently in the process of restarting
            stopped_while_restarting = True
        else:
            cloudbot.stop()

        # restore the original handler so if they do it again it triggers
        signal.signal(signal.SIGINT, original_sigint)

    signal.signal(signal.SIGINT, exit_gracefully)

    while True:
        # start the bot master
        cloudbot.start_bot()

        if cloudbot.do_restart:
            # if cloudbot should restart, create a new bot object
            cloudbot = None
            print("Restarting")
            time.sleep(2)  # sleep two seconds for timeouts to timeout
            if stopped_while_restarting:
                print("Recieved stop signal, no longer restarting")
                return
            cloudbot = bot.CloudBot()
            continue
        else:
            # if it isn't restarting, exit the program
            break


if __name__ == "__main__":
    main()
