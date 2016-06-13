"""
formatting.py

Contains functions for formatting and working with strings.

The licensing for this module isn't solid, because I started working on this module before I had a proper
system for tracking code licences. If your code is in this file and you have any queries, contact me by
email at <lukeroge@gmail.com>!

Maintainer:
    - Luke Rogers <https://github.com/lukeroge>

License:
    GPL v3

License for final section (all code after the "DJANGO LICENCE" comment):
    BSD license

    Copyright (c) Django Software Foundation and individual contributors.
    All rights reserved.

    Redistribution and use in source and binary forms, with or without modification,
    are permitted provided that the following conditions are met:

        1. Redistributions of source code must retain the above copyright notice,
           this list of conditions and the following disclaimer.

        2. Redistributions in binary form must reproduce the above copyright
           notice, this list of conditions and the following disclaimer in the
           documentation and/or other materials provided with the distribution.

        3. Neither the name of Django nor the names of its contributors may be used
           to endorse or promote products derived from this software without
           specific prior written permission.

    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
    ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
    WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
    DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
    ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
    (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
    LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
    ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
    (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
    SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import re
import html.entities

from html.parser import HTMLParser

from cloudbot.util.colors import strip_irc


# Constants

IRC_COLOR_RE = re.compile(r"(\x03(\d+,\d+|\d)|[\x0f\x02\x16\x1f])")

REPLACEMENTS = {
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
    'Z': 'Ż'
}


# Classes

class HTMLTextExtractor(HTMLParser):
    """
    Takes HTML and provides cleaned and stripped text.
    """
    def __init__(self):
        HTMLParser.__init__(self)
        self.result = []

    def handle_data(self, d):
        self.result.append(d)

    def handle_charref(self, number):
        codepoint = int(number[1:], 16) if number[0] in ('x', 'X') else int(number)
        self.result.append(chr(codepoint))

    def handle_entityref(self, name):
        codepoint = html.entities.name2codepoint[name]
        self.result.append(chr(codepoint))

    def get_text(self):
        return ''.join(self.result)


# Functions

def strip_html(to_strip):
    """
    Takes HTML and returns cleaned and stripped text.
    :rtype str
    """
    s = HTMLTextExtractor()
    s.feed(to_strip)
    return s.get_text()


def munge(text, count=0):
    """
    Replaces characters in a string with visually similar characters to avoid pinging users in IRC.
    Count sets how many characters are replaced, defaulting to all characters.
    :rtype str
    """
    reps = 0
    for n in range(len(text)):
        rep = REPLACEMENTS.get(text[n])
        if rep:
            text = text[:n] + rep + text[n + 1:]
            reps += 1
            if reps == count:
                break
    return text


def ireplace(text, old, new, count=None):
    """
    A case-insensitive replace() clone. Return a copy of text with all occurrences of substring
    old replaced by new. If the optional argument count is given, only the first count
    occurrences are replaced.
    """
    pattern = re.compile(re.escape(old), re.IGNORECASE)

    if count:
        return pattern.sub(new, text, count=count)
    else:
        return pattern.sub(new, text)


def multi_replace(text, word_dic):
    """
    Takes a string and replace words that match a key in a dictionary with the associated value,
    then returns the changed text
    :rtype str
    """
    rc = re.compile('|'.join(map(re.escape, word_dic)))

    def translate(match):
        return word_dic[match.group(0)]

    return rc.sub(translate, text)

# compatibility
multiword_replace = multi_replace


def truncate_words(content, length=10, suffix='...'):
    """
    Truncates a string after a certain number of words.
    :rtype str
    """
    split = content.split()
    if len(split) <= length:
        return " ".join(split[:length])
    else:
        return " ".join(split[:length]) + suffix


def truncate(content, length=100, suffix='...'):
    """
    Truncates a string after a certain number of characters.
    Function always tries to truncate on a word boundary.
    :rtype str
    """
    if len(content) <= length:
        return content
    else:
        return content[:length].rsplit(' ', 1)[0] + suffix

# compatibility
truncate_str = truncate
strip_colors = strip_irc


def chunk_str(content, length=420):
    """
    Chunks a string into smaller strings of given length. Returns chunks.
    :rtype list
    """
    def chunk(c, l):
        while c:
            out = (c+' ')[:l].rsplit(' ', 1)[0]
            c = c[len(out):].strip()
            yield out
    return list(chunk(content, length))


def pluralize(num=0, text=''):
    """
    Takes a number and a string, and pluralizes that string using the number and combines the results.
    :rtype: str
    """
    return "{:,} {}{}".format(num, text, "s"[num == 1:])

# alternate form
pluralise = pluralize


def dict_format(args, formats):
    """
    :type args: dict[unknown, unknown]
    :type formats: list[str]
    :rtype: str
    """
    matches = {}
    for f in formats:
        try:
            # Check if values can be mapped
            m = f.format(**args)
            # Insert match and number of matched values (max matched values if already in dict)
            matches[m] = max([matches.get(m, 0), len(re.findall(r'(\{.*?\})', f))])
        except Exception:
            continue

    # Return most complete match, ranked by values matched and then my match length or None
    try:
        return max(matches.items(), key=lambda x: (x[1], len(x[0])))[0]
    except Exception:
        return None


# DJANGO LICENCE

split_re = re.compile(r"""((?:[^\s'"]*(?:(?:"(?:[^"\\]|\\.)*" | '(?:["""
                      r"""^'\\]|\\.)*')[^\s'"]*)+) | \S+)""", re.VERBOSE)


def smart_split(text):
    """
    Generator that splits a string by spaces, leaving quoted phrases together.
    Supports both single and double quotes, and supports escaping quotes with
    backslashes. In the output, strings will keep their initial and trailing
    quote marks and escaped quotes will remain escaped (the results can then
    be further processed with unescape_string_literal()).

    >> list(smart_split(r'This is "a person\'s" test.'))
    ['This', 'is', '"a person\\\'s"', 'test.']
    >> list(smart_split(r"Another 'person\'s' test."))
    ['Another', "'person\\'s'", 'test.']
    >> list(smart_split(r'A "\"funky\" style" test.'))
    ['A', '"\\"funky\\" style"', 'test.']
    """
    for bit in split_re.finditer(text):
        yield bit.group(0)


def get_text_list(list_, last_word='or'):
    """
    >> get_text_list(['a', 'b', 'c', 'd'])
    'a, b, c or d'
    >> get_text_list(['a', 'b', 'c'], 'and')
    'a, b and c'
    >> get_text_list(['a', 'b'], 'and')
    'a and b'
    >> get_text_list(['a'])
    'a'
    >> get_text_list([])
    ''
    """
    if len(list_) == 0:
        return ''
    if len(list_) == 1:
        return list_[0]
    return '%s %s %s' % (
        # Translators: This string is used as a separator between list elements
        ', '.join([i for i in list_][:-1]),
        last_word, list_[-1])
