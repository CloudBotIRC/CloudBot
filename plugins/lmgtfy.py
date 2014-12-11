import requests

from cloudbot import hook
from cloudbot.util import web


@hook.command("lmgtfy", "gfy")
def lmgtfy(text):
    """[phrase] - gets a lmgtfy.com link for the specified phrase"""

    link = "http://lmgtfy.com/?q={}".format(requests.utils.quote(text))

    return web.try_shorten(link)
