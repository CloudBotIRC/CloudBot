from util import hook, text
import hashlib

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

