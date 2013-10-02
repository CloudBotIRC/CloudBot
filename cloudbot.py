#!/usr/bin/env python
# we import bot as _bot for now, for legacy reasons
from core import bot as _bot

import os
import sys

# set up enviroment
os.chdir(sys.path[0] or '.')  # do stuff relative to the install directory

print 'CloudBot REFRESH <http://git.io/cloudbotirc>'

# create new bot object
bot = _bot.Bot("cloudbot")
bot.logger.debug("Bot initalized.")

bot.logger.debug("Starting main loop.")
while True:
    bot.loop()
