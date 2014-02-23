# -*- coding: utf-8 -*-
""" formatting.py - handy functions for formatting text
    this file contains code from the following URL:
    <http://code.djangoproject.com/svn/django/trunk/django/utils/text.py>
"""

import re

from HTMLParser import HTMLParser
import htmlentitydefs


class HTMLTextExtractor(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.result = []

    def handle_data(self, d):
        self.result.append(d)

    def handle_charref(self, number):
        codepoint = int(number[1:], 16) if number[0] in (u'x', u'X') else int(number)
        self.result.append(unichr(codepoint))

    def handle_entityref(self, name):
        codepoint = htmlentitydefs.name2codepoint[name]
        self.result.append(unichr(codepoint))

    def get_text(self):
        return u''.join(self.result)


def strip_html(html):
    s = HTMLTextExtractor()
    s.feed(html)
    return s.get_text()


def munge(text, munge_count=0):
    """munges up text."""
    reps = 0
    for n in xrange(len(text)):
        rep = character_replacements.get(text[n])
        if rep:
            text = text[:n] + rep.decode('utf8') + text[n + 1:]
            reps += 1
            if reps == munge_count:
                break
    return text


character_replacements = {
    'a': 'ä',
    'b': 'Б',
    'c': 'ċ',
    'd': 'đ',
    'e': 'ë',
    'f': 'ƒ',
    'g': 'ġ',
    'h': 'ħ',
    'i': 'í',
    'j': 'ĵ',
    'k': 'ķ',
    'l': 'ĺ',
    'm': 'ṁ',
    'n': 'ñ',
    'o': 'ö',
    'p': 'ρ',
    'q': 'ʠ',
    'r': 'ŗ',
    's': 'š',
    't': 'ţ',
    'u': 'ü',
    'v': '',
    'w': 'ω',
    'x': 'χ',
    'y': 'ÿ',
    'z': 'ź',
    'A': 'Å',
    'B': 'Β',
    'C': 'Ç',
    'D': 'Ď',
    'E': 'Ē',
    'F': 'Ḟ',
    'G': 'Ġ',
    'H': 'Ħ',
    'I': 'Í',
    'J': 'Ĵ',
    'K': 'Ķ',
    'L': 'Ĺ',
    'M': 'Μ',
    'N': 'Ν',
    'O': 'Ö',
    'P': 'Р',
    'Q': 'Ｑ',
    'R': 'Ŗ',
    'S': 'Š',
    'T': 'Ţ',
    'U': 'Ů',
    'V': 'Ṿ',
    'W': 'Ŵ',
    'X': 'Χ',
    'Y': 'Ỳ',
    'Z': 'Ż'}


def capitalize_first(line):
    """
    capitalises the first letter of words
    (keeps other letters intact)
    """
    return ' '.join([s[0].upper() + s[1:] for s in line.split(' ')])


def multiword_replace(text, wordDic):
    """
    take a text and replace words that match a key in a dictionary with
    the associated value, return the changed text
    """
    rc = re.compile('|'.join(map(re.escape, wordDic)))

    def translate(match):
        return wordDic[match.group(0)]
    return rc.sub(translate, text)


def truncate_words(content, length=10, suffix='...'):
    """Truncates a string after a certain number of words."""
    nmsg = content.split(" ")
    out = None
    x = 0
    for i in nmsg:
        if x <= length:
            if out:
                out = out + " " + nmsg[x]
            else:
                out = nmsg[x]
        x += 1
    if x <= length:
        return out
    else:
        return out + suffix


# from <http://stackoverflow.com/questions/250357/smart-truncate-in-python>
def truncate_str(content, length=100, suffix='...'):
    """Truncates a string after a certain number of chars.
    @rtype : str
    """
    if len(content) <= length:
        return content
    else:
        return content[:length].rsplit(' ', 1)[0] + suffix


# ALL CODE BELOW THIS LINE IS COVERED BY THE FOLLOWING AGREEMENT:

# Copyright (c) Django Software Foundation and individual contributors.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#  1. Redistributions of source code must retain the above copyright notice,
#     this list of conditions and the following disclaimer.
#
#  2. Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#
#  3. Neither the name of Django nor the names of its contributors may be used
#     to endorse or promote products derived from this software without
#     specific prior written permission.
#
#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"AND
#ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
#WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#DISCLAIMED.IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
#ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
#(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
#LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
#ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# Expression to match some_token and some_token="with spaces" (and similarly
# for single-quoted strings).

split_re = re.compile(r"""((?:[^\s'"]*(?:(?:"(?:[^"\\]|\\.)*" | '(?:["""
                      r"""^'\\]|\\.)*')[^\s'"]*)+) | \S+)""", re.VERBOSE)


def smart_split(text):
    r"""
    Generator that splits a string by spaces, leaving quoted phrases together.
    Supports both single and double quotes, and supports escaping quotes with
    backslashes. In the output, strings will keep their initial and trailing
    quote marks and escaped quotes will remain escaped (the results can then
    be further processed with unescape_string_literal()).

    >>> list(smart_split(r'This is "a person\'s" test.'))
    [u'This', u'is', u'"a person\\\'s"', u'test.']
    >>> list(smart_split(r"Another 'person\'s' test."))
    [u'Another', u"'person\\'s'", u'test.']
    >>> list(smart_split(r'A "\"funky\" style" test.'))
    [u'A', u'"\\"funky\\" style"', u'test.']
    """
    for bit in split_re.finditer(text):
        yield bit.group(0)


def get_text_list(list_, last_word='or'):
    """
    >>> get_text_list(['a', 'b', 'c', 'd'])
    u'a, b, c or d'
    >>> get_text_list(['a', 'b', 'c'], 'and')
    u'a, b and c'
    >>> get_text_list(['a', 'b'], 'and')
    u'a and b'
    >>> get_text_list(['a'])
    u'a'
    >>> get_text_list([])
    u''
    """
    if len(list_) == 0:
        return ''
    if len(list_) == 1:
        return list_[0]
    return '%s %s %s' % (
        # Translators: This string is used as a separator between list elements
        ', '.join([i for i in list_][:-1]),
        last_word, list_[-1])
