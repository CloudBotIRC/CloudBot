import base64
import codecs
import hashlib
import collections
import re
import binascii

from cloudbot import hook
from cloudbot.util import formatting

colors = collections.OrderedDict([
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


# basic text tools


@hook.command("capitalise", "capitalize")
def capitalize(text):
    """capitalize <string> -- Capitalizes <string>.
    :type text: str
    """
    return ". ".join([sentence.capitalize() for sentence in text.split(". ")])


@hook.command
def upper(text):
    """upper <string> -- Convert string to uppercase."""
    return text.upper()


@hook.command
def lower(text):
    """lower <string> -- Convert string to lowercase."""
    return text.lower()


@hook.command
def titlecase(text):
    """title <string> -- Convert string to title case."""
    return text.title()


@hook.command
def swapcase(text):
    """swapcase <string> -- Swaps the capitalization of <string>."""
    return text.swapcase()


# encoding

@hook.command("rot13")
def rot13_encode(text):
    """rot13 <string> -- Encode <string> with rot13."""
    encoder = codecs.getencoder("rot-13")
    return encoder(text)[0]


@hook.command("base64")
def base64_encode(text):
    """base64 <string> -- Encode <string> with base64."""
    return base64.b64encode(text.encode()).decode()


@hook.command("debase64", "unbase64")
def base64_decode(text, notice):
    """unbase64 <string> -- Decode <string> with base64."""
    try:
        return base64.b64decode(text.encode()).decode()
    except binascii.Error:
        notice("Invalid base64 string '{}'".format(text))


@hook.command("isbase64", "checkbase64")
def base64_check(text):
    """isbase64 <string> -- Checks if <string> is a valid base64 encoded string"""
    try:
        base64.b64decode(text.encode())
    except binascii.Error:
        return "'{}' is not a valid base64 encoded string".format(text)
    else:
        return "'{}' is a valid base64 encoded string".format(text)


@hook.command
def unescape(text):
    """unescape <string> -- Unicode unescapes <string>."""
    decoder = codecs.getdecoder("unicode_escape")
    return decoder(text)[0]


@hook.command
def escape(text):
    """escape <string> -- Unicode escapes <string>."""
    encoder = codecs.getencoder("unicode_escape")
    return encoder(text)[0].decode()


# length


@hook.command
def length(text):
    """length <string> -- Gets the length of <string>"""
    return "The length of that string is {} characters.".format(len(text))


# reverse


@hook.command
def reverse(text):
    """reverse <string> -- Reverses <string>."""
    return text[::-1]


# hashing


@hook.command("hash")
def hash_command(text):
    """hash <string> -- Returns hashes of <string>."""
    return ', '.join(x + ": " + getattr(hashlib, x)(text.encode("utf-8")).hexdigest()
                     for x in ['md5', 'sha1', 'sha256'])


# novelty


@hook.command
def munge(text):
    """munge <text> -- Munges up <text>."""
    return formatting.munge(text)


# colors - based on code by Reece Selwood - <https://github.com/hitzler/homero>


@hook.command
def rainbow(text):
    text = str(text)
    text = strip(text)
    col = list(colors.items())
    out = ""
    l = len(colors)
    for i, t in enumerate(text):
        if t == " ":
            out += t
        else:
            out += col[i % l][1] + t
    return out


@hook.command
def wrainbow(text):
    text = str(text)
    col = list(colors.items())
    text = strip(text).split(' ')
    out = []
    l = len(colors)
    for i, t in enumerate(text):
        out.append(col[i % l][1] + t)
    return ' '.join(out)


@hook.command
def usa(text):
    text = strip(text)
    c = [colors['red'], '\x0300', colors['blue']]
    l = len(c)
    out = ''
    for i, t in enumerate(text):
        out += c[i % l] + t
    return out


@hook.command
def superscript(text):
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
