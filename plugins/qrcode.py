# Plugin by https://github.com/Mu5tank05
from util import hook, web, http


@hook.command('qr')
@hook.command
def qrcode(inp):
    """qrcode [link] returns a link for a QR code."""

    args = {
        "cht": "qr",  # chart type (QR)
        "chs": "200x200",  # dimensions
        "chl": inp  # data
    }

    link = http.prepare_url("http://chart.googleapis.com/chart", args)

    return web.try_isgd(link)
