#-*- coding: utf-8 -*-

# Copyright (C) 2011 by Guilherme Pinto Gonçalves, Ivan Sichmman Freitas

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from util import hook
import sys
import subprocess
from functools import partial

fortunes = {
    'fortunes': 'fortunes',
    'fortune': 'fortunes',
    'quotes': 'literature',
    'quote': 'literature',
    'riddle': 'riddles',
    'riddles': 'riddles',
    'cookie': 'cookie',
    'cookies': 'cookie',
    'disclaimer': 'disclaimer',
    'f': 'fortunes',
    'q': 'literature',
    'r': 'riddles'
    }

# Use this later to replace the fortunes list workaaround
def get_installed_fortunes():
    try:
        proc = subprocess.Popen(("/usr/bin/fortune", "-f"),
                                stderr = subprocess.PIPE)
    except OSError:
        return set()

    return set(proc.stderr)

# Use this later to replace the fortunes list workaaround
def get_fortune(inp):
    try:
        proc = subprocess.Popen(("fortune", "-a", inp),
                                stderr = subprocess.PIPE,
                                stdout = subprocess.PIPE)
    except OSError:
        return set()

    return set(proc.stderr)

@hook.command()
def get(inp, say=None):
    ".get <what> -- uses fortune-mod to get something. <what> can be riddle, quote or fortune"
    fortune = get_fortune(fortune[inp])

    while fortune.length()  =< 5:
        fortune = get_fortune(fortune[inp])

    if proc.wait() == 0:

        for line in proc.stdout:
            say(line.lstrip())
    else:
        return "Fortune failed: " + proc.stderr.read()
