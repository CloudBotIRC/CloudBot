#!/usr/bin/env python
# Tiny little restarter by neersighted
import sys
import subprocess

restart = "./cloudbot restart"

subprocess.call(restart, shell=True)
sys.exit()
