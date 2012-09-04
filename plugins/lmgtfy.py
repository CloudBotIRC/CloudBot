from util import hook, web, http


@hook.command('gfy')
@hook.command
def lmgtfy(inp, bot=None):
    "lmgtfy [phrase] - Posts a google link for the specified phrase"

    url = "http://lmgtfy.com/?q=%s" % http.quote_plus(inp)
    return web.isgd(url)
