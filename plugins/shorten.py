# Plugin by Lukeroge

from util import hook
from urllib2 import HTTPError
from util.web import isgd


@hook.command
def shorten(inp):
    "shorten <url> - Makes an is.gd shortlink to the url provided."

    try:
        return isgd(inp)
    except (HTTPError):
        return "Could not shorten '%s'!" % inp
