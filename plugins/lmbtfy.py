import requests

from cloudbot import hook
from cloudbot.util import web


@hook.command("lmbtfy", "bfy")
def lmbtfy(text):
    """[phrase] - gets a bing.lmgtfy.com link for the specified phrase"""

    link = "bing.lmgtfy.com/?q={}".format(requests.utils.quote(text))

    return web.try_shorten(link)
