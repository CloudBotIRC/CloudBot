# Password generation code by <TheNoodle>
from util import hook
import string
import random


def gen_password(types):
    # Password Generator - The Noodle http://bowlofnoodles.net

    okay = []
    # find the length needed for the password
    numb = types.split(" ")
    
    try:
        length = int(numb[0])
    except ValueError:
        length = 10

    # add alpha characters
    if "alpha" in types or "letter" in types:
        okay = okay + string.ascii_lowercase
        #adds capital characters if not told not to
        if "no caps" not in types:
            okay = okay + string.ascii_uppercase

    # add numbers
    if "numeric" in types or "numbers" in types:
        okay = okay + [str(x) for x in range(0, 10)]

    # add symbols
    if "symbols" in types:
        sym = ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '-', '=', '_', '+', '[', ']', '{', '}', '\\', '|', ';', ':', "'", '.', '>', ',', '<', '/', '?', '`', '~', '"']
        okay += okay + sym

    # defaults to lowercase alpha password if the okay list is empty
    if not okay:
        okay = okay + string.ascii_lowercase

    password = ""
    
    # generates password
    for x in range(length):
        password = password + random.choice(okay)
    return password


@hook.command
def password(inp, notice=None):
    "password <length> [types] -- Generates a password of <length> (default 10). [types] can include 'alpha', 'no caps', 'numeric', 'symbols' or any combination of the types, eg. 'numbers symbols'"
    password = gen_password(inp)
    notice(password)
