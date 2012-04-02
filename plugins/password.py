# Password generation code by <TheNoodle>
from util import hook
import string
import random


def gen_password(types):
    #Password Generator - The Noodle http://bowlofnoodles.net

    okay = []
    #find the length needed for the password
    numb = types.split(" ")

    for x in numb[0]:
        #if any errors are found defualt to 10
        if x not in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
            numb[0] = 10
    length = int(numb[0])
    needs_def = 0
    #alpha characters
    if "alpha" in types or "letter" in types:
        for x in string.ascii_lowercase:
            okay.append(x)
        #adds capital characters if not told not to
        if "no caps" not in types:
            for x in string.ascii_uppercase:
                okay.append(x)
    else:
        needs_def = 1
    #adds numbers
    if "numeric" in types or "numbers" in types:
        for x in range(0, 10):
            okay.append(str(x))
    else:
        needs_def = 1
    #adds symbols
    if "symbols" in types:
        sym = ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '-', '=', '_', '+', '[', ']', '{', '}', '\\', '|', ';', ':', "'", '.', '>', ',', '<', '/', '?', '`', '~', '"']
        for x in sym:
            okay.append(x)
    else:
        needs_def = 1
    #defaults to lowercase alpha password if no arguments are found
    if needs_def == 1:
        for x in string.ascii_lowercase:
            okay.append(x)
    password = ""
    #generates password
    for x in range(length):
        password = password + random.choice(okay)
    return password


@hook.command
def password(inp, notice=None):
    ".password <length> [types] -- Generates a password of <length> (default 10). [types] can include 'alpha', 'no caps', 'numeric', 'symbols' or any combination of the types, eg. 'numbers symbols'"
    password = gen_password(inp)
    notice(password)
