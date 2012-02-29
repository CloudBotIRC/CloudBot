#!/usr/bin/env python
# Tiny little restarter by neersighted
import sys
import os
import subprocess

if os.path.isfile("./cloudbot"):
    restart = "./cloudbot restart"
else:
    restart = "./bot.py"

subprocess.call(restart, shell=True)
sys.exit()
