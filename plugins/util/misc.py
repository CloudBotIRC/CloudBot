from htmlentitydefs import name2codepoint
from time import time as unix_time
from HTMLParser import HTMLParser
from datetime import datetime
import tempfile
import logging as log
import errno
import re
import sys
import os

class HTMLStripper(HTMLParser):

    def __init__(self, data):
        HTMLParser.__init__(self)
        self._stripped = []
        self.feed(data)

    def handle_starttag(self, tag, attrs):
        if tag.lower() == 'br':
            self._stripped.append('\n')

    def handle_charref(self, name):
        try:
            if name.lower().startswith('x'):
                char = int(name[1:], 16)
            else:
                char = int(name)
            self._stripped.append(unichr(char))
        except Exception, error:
            log.warn('invalid entity: %s' % error)

    def handle_entityref(self, name):
        try:
            char = unichr(name2codepoint[name])
        except Exception, error:
            log.warn('unknown entity: %s' % error)
            char = u'&%s;' % name
        self._stripped.append(char)

    def handle_data(self, data):
        self._stripped.append(data)

    @property
    def stripped(self):
        return ''.join(self._stripped)

def superscript(text):
    if isinstance(text, str):
        text = decode(text, 'utf-8')
    return text.translate(SUPER_MAP)

def strip_html(data):
    return HTMLStripper(data).stripped
