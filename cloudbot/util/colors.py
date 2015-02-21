"""
colours.py

Pretty colours, colours everywhere
Parses colours using a $(colour) or $(formatting) template.
Supports both the American and British spellings of many colours and words.

Created By:
    - Zarthus <zarthus@zarth.us>

Maintainer:
    - Luke Rogers <https://github.com/lukeroge>

License:
    MIT License (MIT)
    Copyright Zarthus <zarthus@zarth.us> - 2014-2015

    Permission is hereby granted, free of charge, to any person
    obtaining a copy of this software and associated documentation files
    (the "Software"), to deal in the Software without restriction,
    including without limitation the rights to use, copy, modify, merge,
    publish, distribute, sublicense, and/or sell copies of the Software,
    and to permit persons to whom the Software is furnished to do so,
    subject to the following conditions:

    The above copyright notice and this permission notice shall be
    included in all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
    EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
    MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
    NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
    BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
    ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
    CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.
"""

import re
from random import randint


IRC_COLOUR_DICT = {
    "white": "00",
    "black": "01",
    "dblue": "02",
    "dark_blue": "02",
    "dark_green": "03",
    "dgreen": "03",
    "red": "04",
    "dark_red": "05",
    "dred": "05",
    "brown": "05",  # Note: This appears to show up as brown for some clients, dark red for others.
    "purple": "06",
    "orange": "07",
    "yellow": "08",
    "green": "09",
    "lime": "09",
    "cyan": "10",
    "teal": "11",
    "blue": "12",
    "pink": "13",
    "dgrey": "14",
    "dark_grey": "14",
    "dgray": "14",
    "dark_gray": "14",
    "grey": "15",
    "gray": "15",
    "random": ""  # Special keyword, generate a random number.
}

IRC_FORMATTING_DICT = {
    "colour": "\x03",
    "color": "\x03",

    "bold": "\x02",
    "b": "\x02",

    "underlined": "\x1F",
    "underline": "\x1F",
    "ul": "\x1F",

    "italics": "\x1D",
    "italic": "\x1D",
    "i": "\x1D",

    "reverse": "\x16",

    "reset": "\x0F",
    "clear": "\x0F"
}


COLOR_RE = re.compile(r"\$\(.*?\)", re.I)
IRC_COLOR_RE = re.compile(r"(\x03(\d+,\d+|\d)|[\x0f\x02\x16\x1f])", re.I)


def get_color(colour, return_formatted=True):
    """
    Return numeric in string format of human readable colour formatting.
    Set return_formatted to False to get just the numeric.
    Throws KeyError if colour is not found.
    """
    colour = colour.lower()

    if colour not in IRC_COLOUR_DICT:
        raise KeyError("The colour '{}' is not in the list of available colours.".format(colour))

    if colour == "random":  # Special keyword for a random colour
        rand = randint(0, 15)
        if rand < 10:  # Prepend '0' before colour so it always is double digits.
            rand = "0" + str(rand)
        rand = str(rand)

        if return_formatted:
            return get_format("colour") + rand
        return rand

    if return_formatted:
        return get_format("colour") + IRC_COLOUR_DICT[colour]
    return IRC_COLOUR_DICT[colour]


def get_format(formatting):
    """
    Return hex-character in string format of human readable formatting.
    Throws KeyError if formatting is not found.
    """

    if formatting.lower() not in IRC_FORMATTING_DICT:
        raise KeyError("The formatting '{}' is not found in the list of available formats.".format(formatting))

    return IRC_FORMATTING_DICT[formatting.lower()]


def get_available_formats():
    """List the formats you can use in self.getFormat in a comma separated list (string)"""

    ret = ""
    for formats in IRC_FORMATTING_DICT:
        ret += formats + ", "

    return ret[:-2]


def get_available_colours():
    """List the colours you can use in self.getColour in a comma separated list (string)"""

    ret = ""
    for colours in IRC_COLOUR_DICT:
        ret += colours + ", "

    return ret[:-2]


def parse(string):
    """
    parse: Formats a string, replacing words wrapped in $( ) with actual colours or formatting.
    example:
    parse("The quick $(brown)brown$(clear) fox jumps over the$(bold) lazy dog$(clear).")
    This method will not throw any KeyErrors, but will instead ignore input between $() if it doesn't know what to
    replace it with.
    """

    formatted = string
    regex = COLOR_RE.findall(string)
    for match in regex:
        formatted = formatted.replace(match, _convert(match), 1)
    return formatted


# Formatting stripping.

def strip(string):
    """
    Removes all $() syntax formatting codes from the input string and returns it.
    :rtype str
    """

    stripped = ""

    regex = COLOR_RE.split(string)
    for match in regex:
        stripped += match

    return stripped.strip()


def strip_irc(string):
    """
    Removes all raw MIRC formatting codes from the input string and returns it.
    :rtype str
    """

    return IRC_COLOR_RE.sub('', string)


def strip_all(string):
    """
    Removes all $() syntax and MIRC formatting codes from the input string and returns it.
    :rtype str
    """

    # we run strip_irc twice to avoid people putting a $() formatting code inside a MIRC one
    return strip_irc(strip(strip_irc(string)))


# Internal use

def _convert(string):
    if not string.startswith("$(") and not string.endswith(")"):
        return string
    string = string[2:-1]
    ret = ""
    count = 1
    formattings = string.lower().replace(" ", "").split(",")
    for formatting in formattings:
        if formatting in IRC_COLOUR_DICT:
            if count % 2 == 0:
                ret += "," + get_color(formatting, False)
            else:
                ret += get_color(formatting)
            count += 1
        elif formatting in IRC_FORMATTING_DICT:
            ret += get_format(formatting)

    return ret.strip()
