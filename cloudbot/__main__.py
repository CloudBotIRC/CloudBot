import asyncio
import logging
import os
import sys
import time
import signal

# store the original working directory, for use when restarting
original_wd = os.path.realpath(".")

# set up environment - we need to make sure we are in the install directory
path0 = os.path.realpath(sys.path[0] or '.')
install_dir = os.path.realpath(os.path.dirname(__file__))
if path0 == install_dir:
    sys.path[0] = path0 = os.path.dirname(install_dir)
os.chdir(path0)

# import bot
from cloudbot.bot import CloudBot


def main():
    # Logging optimizations, doing it here because we only want to change this if we're the main file
    logging._srcfile = None
    logging.logThreads = 0
    logging.logProcesses = 0

    logger = logging.getLogger("cloudbot")
    logger.info("Starting CloudBot.")

    # create the bot
    _bot = CloudBot()

    # whether we are killed while restarting
    stopped_while_restarting = False

    # store the original SIGINT handler
    original_sigint = signal.getsignal(signal.SIGINT)

    # define closure for signal handling
    def exit_gracefully():
        nonlocal stopped_while_restarting
        if not _bot:
            # we are currently in the process of restarting
            stopped_while_restarting = True
        else:
            _bot.loop.call_soon_threadsafe(lambda: asyncio.async(_bot.stop("Killed"), loop=_bot.loop))

        # restore the original handler so if they do it again it triggers
        signal.signal(signal.SIGINT, original_sigint)

    signal.signal(signal.SIGINT, exit_gracefully)

    # start the bot master

    # CloudBot.run() will return True if it should restart, False otherwise
    restart = _bot.run()

    # the bot has stopped, do we want to restart?
    if restart:
        # remove reference to cloudbot, so exit_gracefully won't try to stop it
        _bot = None
        # sleep one second for timeouts
        time.sleep(1)
        if stopped_while_restarting:
            logger.info("Received stop signal, no longer restarting")
        else:
            # actually restart
            os.chdir(original_wd)
            args = sys.argv
            logger.info("Restarting Bot")
            logger.debug("Restart arguments: {}".format(args))
            for f in [sys.stdout, sys.stderr]:
                f.flush()
            # close logging, and exit the program.
            logger.debug("Stopping logging engine")
            logging.shutdown()
            os.execv(sys.executable, [sys.executable] + args)

    # close logging, and exit the program.
    logger.debug("Stopping logging engine")
    logging.shutdown()


main()
