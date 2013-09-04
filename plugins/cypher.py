"""
Plugin which (de)cyphers a string
Doesn't cypher non-alphanumeric strings yet.
by instanceoftom
All character cyphering added - TheNoodle
"""

from util import hook


@hook.command
def cypher(inp):
    """cypher <pass> <string> -- Cyphers <string> with <password>."""

    passwd = inp.split(" ")[0]
    len_passwd = len(passwd)
    inp = " ".join(inp.split(" ")[1:])

    out = ""
    passwd_index = 0
    for character in inp:
        chr_index = ord(character)
        passwd_chr_index = ord(passwd[passwd_index])

        out_chr_index = (chr_index + passwd_chr_index) % 255
        out_chr = chr[out_chr_index]

        out += out_chr

        passwd_index = (passwd_index + 1) % len_passwd
    return out


@hook.command
def decypher(inp):
    """decypher <pass> <string> -- Decyphers <string> with <password>."""

    passwd = inp.split(" ")[0]
    len_passwd = len(passwd)
    inp = " ".join(inp.split(" ")[1:])

    passwd_index = 0
    for character in inp:
        passwd_index = (passwd_index + 1) % len_passwd

    passwd_index -= 1
    reversed_message = inp[::-1]

    out = ""
    for character in reversed_message:
        try:
            chr_index = ord(character)
            passwd_chr_index = ord(passwd[passwd_index])

            out_chr_index = (chr_index - passwd_chr_index) % 255
            out_chr = chars[out_chr_index]

            out += out_chr

            passwd_index = (passwd_index - 1) % len_passwd
        except ValueError:
            out += character
            continue

    return out[::-1]
