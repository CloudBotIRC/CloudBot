#!/usr/bin/env python
#
# molecular.py
# Copyright (c) 2001, Chris Gonnerman
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without 
# modification, are permitted provided that the following conditions
# are met:
# 
# Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer. 
# 
# Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution. 
# 
# Neither the name of the author nor the names of any contributors
# may be used to endorse or promote products derived from this software
# without specific prior written permission. 
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# AUTHOR OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""molecular.py -- molecular (ngenoid) name generator

Modified for CloudBot by Lukeroge.

This module knows how to generate "random" names for RPG characters.
It uses the same method as the "ngen" name generator by Kimmo Kulovesi,
and in fact it can use the same name files.  molecular.py knows how
to merge multiple tables also, which can be handy...

If run as a command-line program, use the following options:

    -r namefile    -- read the given name file and add to the
                      current name table.
    nnn            -- generate nnn (a number) names and print
                      on standard output.

To generate names from a name file:

    python molecular.py -r file 10

As a module (to be imported) you get the following classes and functions:

    NameFile (class)    -- a file wrapper with a disabled close() method,
                           used internally and probably not useful otherwise.
    nameopen (function) -- opens a file; takes filename and mode options,
                           searches the default name file directory if not
                           found in current directory, handles "-" filenames,
                           and uses NameFile to disable closing of sys.stdin/
                           sys.stdout.
    Molecule (class)    -- the meat of the matter.  A Molecule instance has
                           the following methods:

                                .load(file)    -- loads a name file, 
                                                  which may be a file-like
                                                  object with a .readline()
                                                  method or a filename as a
                                                  string.
                                .name()        -- generate one name and
                                                  return it.
"""

__version__ = "1.0"

import string, re, sys, random, os

NAMEDIR = os.path.dirname(__file__) + "/namefiles"
NAMESECTIONS = [ "inf", "first", "mid", "final", "notes", "end" ]

class NameFile:
    __file_attributes = ('closed','mode','name','softspace')
    def __init__(self, file):
        self.fd = file
    def close(self):
        pass
    def flush(self):
        return self.fd.flush()
    def isatty(self):
        return self.fd.isatty()
    def fileno(self):
        return self.fd.fileno()
    def read(self, *args):
        return apply(self.fd.read, args)
    def readline(self, *args):
        return apply(self.fd.readline, args)
    def readlines(self, *args):
        return apply(self.fd.readlines, args)
    def seek(self, *args):
        return apply(self.fd.seek, args)
    def tell(self):
        return self.fd.tell()
    def write(self, str):
        return self.fd.write(str)
    def writelines(self, list):
        return self.fd.writelines(list)
    def __repr__(self): 
        return repr(self.fd)
    def __getattr__(self, name):
        if name in self.__file_attributes:
            return getattr(self.fd, name)
        else:
            return self.__dict__[name]
    def __setattr__(self, name, value):
        if name in self.__file_attributes:
            setattr(self.fd, name, value)
        else:
            self.__dict__[name] = value
    def __cmp__(self, file):
        """I'm not sure what the correct behavior is, and therefore 
        this implementation is just a guess."""
        if type(file) == type(self.fd):
            return cmp(self.fd, file)
        else:
            return cmp(self.fd, file.fd)


class NameReader:
    def __init__(self, file):
        self.file = file
        self.line = ""
    def next(self):
        self.line = self.file.readline()
        return self.line
    def close(self):
        return self.file.close()


def safeopen(filename, mode):
    try:
        return open(filename, mode)
    except IOError:
        return None

def nameopen(filename, mode):
    if filename == "-":
        if "r" in mode:
            return NameFile(sys.stdin)
        else:
            return NameFile(sys.stdout)
    fp = safeopen(filename, mode)
    if fp is None:
        fp = safeopen(filename + ".nam", mode)
    if "r" in mode and fp is None:
        fp = safeopen(NAMEDIR + "/" + filename, mode)
        # last call is open() instead of safeopen() to finally raise
        # the exception if we just can't find the file.
        if fp is None:
            fp = open(NAMEDIR + "/" + filename + ".nam", mode)
    return fp
    

class Molecule:

    def __init__(self):
        self.nametbl = {}
        for i in NAMESECTIONS:
            self.nametbl[i] = []
        self.nametbl[""] = []
        self.cursection = self.nametbl[""]

    def load(self, fp):
        if type(fp) is type(""):
            fp = nameopen(fp, "r")
        else:
            fp = NameFile(fp)
        rdr = NameReader(fp)
        while rdr.next():
            line = rdr.line[:-1]
            if len(line) > 0 and line[0] == '[' and line[-1] == ']':
                line = string.strip(line)[1:-1]
                if not self.nametbl.has_key(line):
                    self.nametbl[line] = []
                self.cursection = self.nametbl[line]
            else:
                self.cursection.append(line)
        fp.close()

    def list_modules(self):
        files = os.listdir(NAMEDIR)
        modules = []
        for i in files:
            modules.append(os.path.splitext(i)[0])
        return modules

    def name(self):
        n = []
        if len(self.nametbl["first"]) > 0:
            n.append(random.choice(self.nametbl["first"]))
        if len(self.nametbl["mid"]) > 0:
            n.append(random.choice(self.nametbl["mid"]))
        if len(self.nametbl["final"]) > 0:
            n.append(random.choice(self.nametbl["final"]))
        return string.join(n, "")
