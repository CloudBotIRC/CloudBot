from util import hook, text
import hashlib
import collections
import re

# variables

colors = collections.OrderedDict([
  ('red',    '\x0304'),
  ('ornage', '\x0307'),
  ('yellow', '\x0308'),
  ('green',  '\x0309'),
  ('cyan',   '\x0303'),
  ('ltblue', '\x0310'),
  ('rylblue','\x0312'),
  ('blue',   '\x0302'),
  ('magenta','\x0306'),
  ('pink',   '\x0313'),
  ('maroon', '\x0305')
])

# helper functions

strip_re = re.compile("(\x03|\x02|\x1f)(?:,?\d{1,2}(?:,\d{1,2})?)?", re.UNICODE)

def strip(text):
  return strip_re.sub('', text)

# basic text tools

## TODO: make this capitalize sentences correctly
@hook.command("capitalise")
@hook.command
def capitalize(inp):
    """capitalize <string> -- Capitalizes <string>."""
    return inp.capitalize()

@hook.command
def upper(inp):
    """upper <string> -- Convert string to uppercase."""
    return inp.upper()

@hook.command
def lower(inp):
    """lower <string> -- Convert string to lowercase."""
    return inp.lower()

@hook.command
def titlecase(inp):
    """title <string> -- Convert string to title case."""
    return inp.title()

@hook.command
def swapcase(inp):
    """swapcase <string> -- Swaps the capitalization of <string>."""
    return inp.swapcase()

# encoding

@hook.command
def rot13(inp):
    """rot13 <string> -- Encode <string> with rot13."""
    return inp.encode('rot13')

@hook.command
def unescape(inp):
    """unescape <string> -- Unescapes <string>."""
    return inp.decode('unicode-escape')

@hook.command
def escape(inp):
    """escape <string> -- escapes <string>."""
    return inp.encode('unicode-escape')

# length

@hook.command
def length(inp):
    """length <string> -- gets the length of <string>"""
    return "The length of that string is {} characters.".format(len(inp))

# hashing

@hook.command
def hash(inp):
    """hash <string> -- Returns hashes of <string>."""
    return ', '.join(x + ": " + getattr(hashlib, x)(inp).hexdigest()
                     for x in ['md5', 'sha1', 'sha256'])

# novelty

@hook.command
def munge(inp):
    """munge <text> -- Munges up <text>."""
    return text.munge(inp)

# colors - based on code by Reece Selwood - <https://github.com/hitzler/homero>

@hook.command
def rainbow(inp):
    inp = unicode(inp)
    inp = strip(inp)
    col = colors.items()
    out = ""
    l = len(colors)
    for i, t in enumerate(inp):
        out += col[i % l][1] + t
    return out

@hook.command
def wrainbow(inp):
    inp = unicode(inp)
    col = colors.items()
    inp = strip(inp).split(' ')
    out = []
    l = len(colors)
    for i, t in enumerate(inp):
        out.append(col[i % l][1] + t)
    return ' '.join(out)

@hook.command
def usa(inp):
    inp = strip(inp)
    c = [colors['red'], '\x0300', colors['blue']]
    l = len(c)
    out = ''
    for i, t in enumerate(inp):
        out += c[i % l] + t
    return out

