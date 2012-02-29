#!/usr/bin/env python
# Tiny little log clearer by neersighted
import sys
import os
import subprocess

if os.path.isfile("./bot.log"):
    clear = ": >./bot.log"
else:
    clear = ":"

subprocess.call(clear, shell=True)
sys.exit()
