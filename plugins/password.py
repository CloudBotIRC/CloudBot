import string

try:
    from Crypto.Random import random
except ImportError:
    # Just use the regular random module, not the strong one
    import random

from cloudbot import hook

with open("data/password_words.txt") as f:
    common_words = [line.strip() for line in f.readlines()]


@hook.command(autohelp=False)
def password(text, notice):
    """[length [types]] - generates a password of <length> (default 10). [types] can include 'alpha', 'no caps', 'numeric', 'symbols' or any combination: eg. 'numbers symbols'"""
    okay = []

    # find the length needed for the password
    numb = text.split(" ")

    try:
        length = int(numb[0])
    except ValueError:
        length = 10

    # add alpha characters
    if "alpha" in text or "letter" in text:
        okay = okay + list(string.ascii_lowercase)
        # adds capital characters if not told not to
        if "no caps" not in text:
            okay = okay + list(string.ascii_uppercase)

    # add numbers
    if "numeric" in text or "number" in text:
        okay = okay + [str(x) for x in range(0, 10)]

    # add symbols
    if "symbol" in text:
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


@hook.command("rpass", "rpassword", "readablepassword", autohelp=False)
def readable_password(text, notice):
    """[length] - generates an easy to remember password with [length] (default 4) commonly used words"""
    if text:
        try:
            length = int(text)
        except ValueError:
            notice("Invalid input '{}'".format(text))
            return
    else:
        length = 4
    words = []
    # generate password
    for x in range(length):
        words.append(random.choice(common_words))

    notice("Your password is '{}'. Feel free to remove the spaces when using it.".format(" ".join(words)))
