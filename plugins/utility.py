"""
utility.py

Provides a number of simple commands for working with strings.

Created By:
    - Luke Rogers <https://github.com/lukeroge>
    - Dabo Ross <https://github.com/daboross>

Special Thanks:
    - Fletcher Boyd <https://github.com/thenoodle68>

License: GPL v3
"""

import base64
import hashlib
import collections
import re
import os
import json
import codecs
import urllib.parse
import random
import binascii

from cloudbot import hook
from cloudbot.util import formatting, web, colors


COLORS = collections.OrderedDict([
    ('red', '\x0304'),
    ('orange', '\x0307'),
    ('yellow', '\x0308'),
    ('green', '\x0309'),
    ('cyan', '\x0303'),
    ('ltblue', '\x0310'),
    ('rylblue', '\x0312'),
    ('blue', '\x0302'),
    ('magenta', '\x0306'),
    ('pink', '\x0313'),
    ('maroon', '\x0305')
])

# helper functions

strip_re = re.compile("(\x03|\x02|\x1f|\x0f)(?:,?\d{1,2}(?:,\d{1,2})?)?")


def strip(string):
    return strip_re.sub('', string)


def translate(text, dic):
    for i, j in dic.items():
        text = text.replace(i, j)
    return text


# on_start

@hook.on_start()
def load_text(bot):
    """
    :type bot: cloudbot.bot.CloudBot
    """
    global leet

    with codecs.open(os.path.join(bot.data_dir, "leet.json"), encoding="utf-8") as f:
        leet = json.load(f)


# misc

@hook.command("qrcode", "qr")
def qrcode(text):
    """<link> - returns a link to a QR code image for <link>"""

    args = {
        "cht": "qr",  # chart type (QR)
        "chs": "200x200",  # dimensions
        "chl": text  # data
    }

    argstring = urllib.parse.urlencode(args)

    link = "http://chart.googleapis.com/chart?{}".format(argstring)
    return web.try_shorten(link)


# basic text tools

@hook.command("capitalize", "capitalise")
def capitalize(text):
    """<string> -- Capitalizes <string>.
    :type text: str
    """
    return ". ".join([sentence.capitalize() for sentence in text.split(". ")])


@hook.command
def upper(text):
    """<string> -- Convert string to uppercase."""
    return text.upper()


@hook.command
def lower(text):
    """<string> -- Convert string to lowercase."""
    return text.lower()


@hook.command
def titlecase(text):
    """<string> -- Convert string to title case."""
    return text.title()


@hook.command
def swapcase(text):
    """<string> -- Swaps the capitalization of <string>."""
    return text.swapcase()


# encoding

@hook.command("rot13")
def rot13_encode(text):
    """<string> -- Encode <string> with rot13."""
    encoder = codecs.getencoder("rot-13")
    return encoder(text)[0]


@hook.command("base64")
def base64_encode(text):
    """<string> -- Encode <string> with base64."""
    return base64.b64encode(text.encode()).decode()


@hook.command("debase64", "unbase64")
def base64_decode(text, notice):
    """<string> -- Decode <string> with base64."""
    try:
        return base64.b64decode(text.encode()).decode()
    except binascii.Error:
        notice("Invalid base64 string '{}'".format(text))


@hook.command("isbase64", "checkbase64")
def base64_check(text):
    """<string> -- Checks if <string> is a valid base64 encoded string"""
    try:
        base64.b64decode(text.encode())
    except binascii.Error:
        return "'{}' is not a valid base64 encoded string".format(text)
    else:
        return "'{}' is a valid base64 encoded string".format(text)


@hook.command
def unescape(text):
    """<string> -- Unicode unescapes <string>."""
    decoder = codecs.getdecoder("unicode_escape")
    return decoder(text)[0].replace("\r", "").replace("\n", "")


@hook.command
def escape(text):
    """<string> -- Unicode escapes <string>."""
    encoder = codecs.getencoder("unicode_escape")
    return encoder(text)[0].decode()


# length


@hook.command
def length(text):
    """<string> -- Gets the length of <string>"""
    return "The length of that string is {} characters.".format(len(text))


# reverse


@hook.command
def reverse(text):
    """<string> -- Reverses <string>."""
    return text[::-1]


# hashing


@hook.command("hash")
def hash_command(text):
    """<string> -- Returns hashes of <string>."""
    return ', '.join(x + ": " + getattr(hashlib, x)(text.encode("utf-8")).hexdigest()
                     for x in ['md5', 'sha1', 'sha256'])


# novelty


@hook.command
def munge(text):
    """<text> -- Munges up <text>."""
    return formatting.munge(text)


@hook.command
def leet(text):
    """<text> -- Makes <text> more 1337h4x0rz."""
    output = ''.join(random.choice(leet[ch]) if ch.isalpha() else ch for ch in text.lower())
    return output


# Based on plugin by FurCode - <https://github.com/FurCode/RoboCop2>
@hook.command
def derpify(text):
    """<text> - returns some amusing responses from your input."""
    string = text.upper()
    pick_the = random.choice(["TEH", "DA"])
    pick_e = random.choice(["E", "3", "A"])
    pick_qt = random.choice(["?!?!??", "???!!!!??", "?!??!?", "?!?!?!???"])
    pick_ex = random.choice(["1111!11", "1!11", "!!1!", "1!!!!111", "!1!111!1", "!11!111"])
    pick_end = random.choice(["", "OMG", "LOL", "WTF", "WTF LOL", "OMG LOL"])
    rules = {"YOU'RE": "UR", "YOUR": "UR", "YOU": "U", "WHAT THE HECK": "WTH", "WHAT THE HELL": "WTH",
             "WHAT THE FUCK": "WTF",
             "WHAT THE": "WT", "WHAT": "WUT", "ARE": "R", "WHY": "Y", "BE RIGHT BACK": "BRB", "BECAUSE": "B/C",
             "OH MY GOD": "OMG", "O": "OH", "THE": pick_the, "TOO": "2", "TO": "2", "BE": "B", "CK": "K", "ING": "NG",
             "PLEASE": "PLS", "SEE YOU": "CYA", "SEE YA": "CYA", "SCHOOL": "SKOOL", "AM": "M",
             "AM GOING TO": "IAM GOING TO", "THAT": "DAT", "ICK": "IK",
             "LIKE": "LIEK", "HELP": "HALP", "KE": "EK", "E": pick_e, "!": pick_ex, "?": pick_qt}
    output = translate(string, rules) + " " + pick_end

    return output


# colors
@hook.command
def color_parse(text):
    return colors.parse(text)


# colors - based on code by Reece Selwood - <https://github.com/hitzler/homero>
@hook.command
def rainbow(text):
    """<text> -- Gives <text> rainbow colors."""
    text = str(text)
    text = strip(text)
    col = list(COLORS.items())
    out = ""
    l = len(COLORS)
    for i, t in enumerate(text):
        if t == " ":
            out += t
        else:
            out += col[i % l][1] + t
    return out


@hook.command
def wrainbow(text):
    """<text> -- Gives each word in <text> rainbow colors."""
    text = str(text)
    col = list(COLORS.items())
    text = strip(text).split(' ')
    out = []
    l = len(COLORS)
    for i, t in enumerate(text):
        out.append(col[i % l][1] + t)
    return ' '.join(out)


@hook.command
def usa(text):
    """<text> -- Makes <text> more patriotic."""
    text = strip(text)
    c = [COLORS['red'], '\x0300', COLORS['blue']]
    l = len(c)
    out = ''
    for i, t in enumerate(text):
        out += c[i % l] + t
    return out


@hook.command
def superscript(text):
    """<text> -- Makes <text> superscript."""
    regular = "abcdefghijklmnoprstuvwxyzABDEGHIJKLMNOPRTUVW0123456789+-=()"
    super_script = "ᵃᵇᶜᵈᵉᶠᵍʰⁱʲᵏˡᵐⁿᵒᵖʳˢᵗᵘᵛʷˣʸᶻᴬᴮᴰᴱᴳᴴᴵᴶᴷᴸᴹᴺᴼᴾᴿᵀᵁⱽᵂ⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾"
    result = []
    for char in text:
        index = regular.find(char)
        if index != -1:
            result.append(super_script[index])
        else:
            result.append(char)
    return "".join(result)
