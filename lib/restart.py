#!/usr/bin/env python
# Tiny little restarter by neersighted
import subprocess, sys, os

if os.path.isfile("./control.sh"):
    restart = "./control.sh restart"
elif os.path.isfile("./bot.sh"):
    restart = "./bot.sh restart"
else:
    restart = "./bot.py"

subprocess.call(restart, shell=True)
sys.exit()
