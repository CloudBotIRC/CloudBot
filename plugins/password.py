# TODO: Add some kind of pronounceable password generation
# TODO: Improve randomness
import string
import random

from util import hook


@hook.command
def password(inp, notice=None):
    """password <length> [types] -- Generates a password of <length> (default 10).
    [types] can include 'alpha', 'no caps', 'numeric', 'symbols' or any combination of the inp, eg. 'numbers symbols'"""
    okay = []

    # find the length needed for the password
    numb = inp.split(" ")

    try:
        length = int(numb[0])
    except ValueError:
        length = 10

    # add alpha characters
    if "alpha" in inp or "letter" in inp:
        okay = okay + list(string.ascii_lowercase)
        #adds capital characters if not told not to
        if "no caps" not in inp:
            okay = okay + list(string.ascii_uppercase)

    # add numbers
    if "numeric" in inp or "number" in inp:
        okay = okay + [str(x) for x in xrange(0, 10)]

    # add symbols
    if "symbol" in inp:
        sym = ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '-', '=', '_', '+', '[', ']', '{', '}', '\\', '|', ';',
               ':', "'", '.', '>', ',', '<', '/', '?', '`', '~', '"']
        okay += okay + sym

    # defaults to lowercase alpha password if the okay list is empty
    if not okay:
        okay = okay + list(string.ascii_lowercase)

    pw = ""

    # generates password
    for x in range(length):
        pw = pw + random.choice(okay)

    notice(pw)
