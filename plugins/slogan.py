from util import hook, http, misc
import re
import string


def sloganize(word):
    bytes = http.get('http://www.sloganizer.net/en/outbound.php', slogan=word)
    return bytes


@hook.command("slogan")
def sloganizr(inp, nick=None, say=None, input=None):
    ".slogan <word> -- Makes a slogan for <word>."
    slogan = sloganize(inp)

    slogan = misc.strip_html(slogan)

    if inp.islower():
        slogan = slogan.split()
        slogan[0] = slogan[0].capitalize()
        slogan = " ".join(slogan)

    return slogan
