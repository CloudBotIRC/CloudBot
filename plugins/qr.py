# Plugin by https://github.com/Mu5tank05
from util import hook, web, http


@hook.command('qr')
@hook.command
def qrcode(inp, bot=None):
    "qrcode [link] returns a link for a QR code."

    link = "http://blny.tk/qr.php?q=%s" % http.quote_plus(inp)
    
    return web.try_isgd(link)


