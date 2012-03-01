#!/usr/bin/env python
# Tiny little stoper by neersighted
import sys
import os
import subprocess

stop = "./cloudbot stop"
subprocess.call(stop, shell=True)
sys.exit()
