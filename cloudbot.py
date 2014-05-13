#!/usr/bin/env python3.4
import logging
import os
import sys
import time
import signal

from core import bot

if sys.version_info < (3, 4, 0):
    # check python version
    print("CloudBot3 requires Python 3.4 or newer.")
    sys.exit(1)

# set up environment
os.chdir(sys.path[0] or '.')  # do stuff relative to the install directory

# add 'lib' to path for libraries (currently unused)
if os.path.exists(os.path.abspath('lib')):
    sys.path += ['lib']

print('CloudBot3 <http://git.io/refresh>')


def main():
    # Logging optimizations, doing it here because we only want to change this if we're the main file, not if
    # we're being loaded by anything else.
    logging._srcfile = None
    logging.logThreads = 0
    logging.logProcesses = 0

    logger = logging.getLogger("cloudbot")

    # store the original working directory, for use when restarting
    original_wd = os.path.realpath(".")

    # create the bot
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
            cloudbot.loop.call_soon_threadsafe(cloudbot.stop, "Killed")

        # restore the original handler so if they do it again it triggers
        signal.signal(signal.SIGINT, original_sigint)

    signal.signal(signal.SIGINT, exit_gracefully)

    # start the bot master

    cloudbot.run()

    # the bot has stopped, do we want to restart?
    if cloudbot.do_restart:
        # remove reference to cloudbot, so exit_gracefully won't try to stop it
        cloudbot = None
        # sleep one second for timeouts
        time.sleep(1)
        if stopped_while_restarting:
            logger.info("Received stop signal, no longer restarting")
        else:
            # actually restart
            os.chdir(original_wd)
            args = sys.argv
            logger.info("Restarting CloudBot")
            logger.debug("Restarting - arguments {}".format(args))
            for f in [sys.stdout, sys.stderr]:
                f.flush()
            os.execv(sys.executable, [sys.executable] + args)

    # close logging, and exit the program.
    logger.debug("Stopping logging engine")
    logging.shutdown()


if __name__ == "__main__":
    main()
