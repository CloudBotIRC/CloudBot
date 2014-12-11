# Plugin by https://github.com/Mu5tank05
import urllib.parse

from cloudbot import hook
from cloudbot.util import web


@hook.command("qrcode", "qr")
def qrcode(text):
    """[link] - returns a link to a QR code image for [link]"""

    args = {
        "cht": "qr",  # chart type (QR)
        "chs": "200x200",  # dimensions
        "chl": text  # data
    }

    argstring = urllib.parse.urlencode(args)

    link = "http://chart.googleapis.com/chart?{}".format(argstring)
    return web.try_shorten(link)
