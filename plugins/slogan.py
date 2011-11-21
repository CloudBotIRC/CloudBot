from util import hook, http, misc
import re

def sloganize(word):
    bytes = http.get('http://www.sloganizer.net/en/outbound.php', slogan=word)
    return bytes

@hook.command("slogan")
def sloganizr(inp, nick=None, say=None, input=None):
    ".slogan <word> -- make a solgan for <word>!"
    slogan = sloganize(inp)

    slogan = misc.strip_html(slogan)

    return slogan
